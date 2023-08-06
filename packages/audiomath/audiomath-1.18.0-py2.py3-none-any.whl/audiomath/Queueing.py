# $BEGIN_AUDIOMATH_LICENSE$
# 
# This file is part of the audiomath project, a Python package for
# recording, manipulating and playing sound files.
# 
# Copyright (c) 2008-2023 Jeremy Hill
# 
# audiomath is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# The audiomath distribution includes binaries from the third-party
# AVbin and PortAudio projects, released under their own licenses.
# See the respective copyright, licensing and disclaimer information
# for these projects in the subdirectories `audiomath/_wrap_avbin`
# and `audiomath/_wrap_portaudio` . It also includes a fork of the
# third-party Python package `pycaw`, released under its original
# license (see `audiomath/pycaw_fork.py`).
# 
# $END_AUDIOMATH_LICENSE$
__all__ = [
	'Queue',
	'QueueTest',
	'QueueError',
]

import sys
import glob

from . import Base; from .Base import Sound

class Unspecified( object ): __repr__ = __str__ = lambda self: self.__class__.__name__
Unspecified = Unspecified()
generator = type( ( x for x in '' ) )

def _AsSound( x, **kwargs ):
	return x if ( x is None or isinstance( x, Sound ) ) else Sound( x, **kwargs )
	
def _SoundSequence( *sounds, **sound_kwargs ):
	return [
		_AsSound( sound, **sound_kwargs )
		for item in sounds
		for sound in (
			item if isinstance( item, ( tuple, list, generator, Queue ) ) \
			else sorted( glob.glob( item ) ) if isinstance( item, str ) and ( '*' in item or '?' in item ) \
			else [ item ]
		)
		if sound is not None
	]

class Queue(object):
	"""
	A `list`-like container for `Sound` instances, which
	keeps track of, and allows manipulation of, which
	element is considered "current".
	"""
	def __init__(self, *sounds):
		"""
		You probably do not need to create a `Queue`
		explicitly yourself. When you create a `Player`
		instance `p`, the property `p.queue` will
		automatically be initialized as a new `Queue`
		containing whatever sounds you specified in
		the `Player` constructor call. 
		"""
		self.__sounds = []
		self.__currentPosition = 0
		self.loop = False
		self.append(*sounds)

	@property
	def currentSound( self ):
		"""
		Return the current `Sound` as indexed
		by `.position`
		"""		
		return self.__sounds[ self.__currentPosition ] if 0 <= self.__currentPosition < len( self.__sounds ) else None
	@currentSound.setter
	def currentSound( self, value ):
		self.position = self.index( value )

	@property
	def position( self ):
		"""
		Zero-based numeric index of `.currentSound`
		within the list.
		
		When assigning, you may also use a `Sound`
		instance or its `.label`, provided that
		instance is in the list.
		"""
		return self.__currentPosition
	@position.setter
	def position( self, value ):
		nSounds = len( self.__sounds )
		value = self.index( value )
		if self.loop:
			self.__currentPosition = ( value % nSounds ) if nSounds else 0
		else:
			self.__currentPosition = max( 0, min( nSounds - 1, value ) ) if nSounds else 0
			if value < 0: raise QueueError( 'cannot go back before track 0' ) # NB: this is a relic---the condition will never be true as long as we're using self.index() above. This error is now raised elsewhere
			if value >= nSounds: raise QueueError( 'no more tracks after track %d' % ( nSounds -1 ) )

	def index( self, arg ):
		"""
		Given a `Sound` instance that is in the queue,
		or its `.label`, return its non-negative
		integer index within the queue. Raise a
		`ValueError` if no such instance is found in
		the queue.
		"""
		if isinstance( arg, Sound ):
			try: index = self.__sounds.index( arg )
			except ValueError: raise ValueError( '%s is not in the list' % object.__repr__( arg ) )
		elif isinstance( arg, str ):
			matched = [ i for i, sound in enumerate( self.__sounds ) if sound.label == arg ]
			if not matched: raise KeyError( 'could not find a sound with label %r' % arg )
			index = matched[ 0 ]
		elif isinstance( arg, slice ):
			index = slice(
				None if arg.start is None else self.index( arg.start ),
				None if arg.stop  is None else self.index( arg.stop  ),
				arg.step
			)
		else:
			index = int( arg )
			if index < 0: index += len( self.__sounds )
		return index
						
	
	def remove( self, item_or_index ):
		"""
		Given either a `Sound` instance, its label, or
		its index within the list, remove it from the
		queue. Return `self`.
		"""
		self.pop( item_or_index )
		return self
	
	def clear( self ):
		"""
		Empty the queue.
		"""
		del self[ : ]
		return self
	
	def insert(self, index, *sounds, **sound_kwargs):
		"""
		Insert one or more sounds into the queue at given `index`.

		Any arguments that are not already `Sound` instances
		(e.g. filenames) will be passed to the `Sound`
		constructor to create such instances, along with any
		additional keyword arguments.
		"""
		sounds = _SoundSequence( *sounds, **sound_kwargs )
		if not sounds: return self
		index = self.index( index )
		if index == 0 and not self.__sounds:
			self.__sounds.extend( sounds )
		else:
			if self.__currentPosition >= index:
				self.__currentPosition += len( sounds )
			self.__sounds[ index:index ] = sounds
		return self

	def append( self, *sounds, **sound_kwargs ):
		"""
		Add a variable number of sounds to the end of the
		queue.  Since nested lists are not allowed, `.add()`,
		`.extend()` and `.append()` are identical: any of
		them will accept a single `Sound` instance, *or* a
		sequence of `Sound` instances.

		Any arguments that are not already `Sound` instances
		(e.g. filenames) will be passed to the `Sound`
		constructor to create such instances, along with any
		additional keyword arguments.
		"""
		self.__sounds.extend( _SoundSequence( *sounds, **sound_kwargs ) )
		return self
		
	def pop( self, index, default=Unspecified ):
		"""
		Remove the `Sound` with the given label or index and
		return it. If it is not found in the list, return
		`default` if specified (otherwise raise a `KeyError`).
		"""
		try:
			index = self.index( index )
			if index < 0: raise IndexError( "index of sound to be removed is beyond the beginning of the queue" )
			if index >= len( self.__sounds ): raise IndexError( "index of sound to be removed is beyond the end of the queue" )
		except ( KeyError, IndexError ):
			if default is Unspecified: raise
			return default
		sound = self.__sounds.pop( index )
		if self.__currentPosition > index:  # stays at same index if equal (will point to new sound at that index)
			self.__currentPosition = max( 0, self.__currentPosition - 1 )
		return sound
			
	add = append
	extend = append # since nesting is not allowed, append() already unpacks sequences as necessary, so append and extend can safely be synonymous
	__iadd__ = extend
	__add__  = lambda self, other: self.__class__().__iadd__( self ).__iadd__( other )
	__radd__ = lambda self, other: self.__class__().__iadd__( other ).__iadd__( self )
	__bool__ = __nonzero__ = lambda self: bool( self.__sounds )
	__len__ = lambda self: len( self.__sounds )	
	def __getitem__( self, index ):
		index = self.index( index )
		value = self.__sounds[ index ]	
		if isinstance( index, slice ): value = self.__class__( value )
		return value
	def __setitem__( self, index, value ):
		index = self.index( index )
		if isinstance( index, slice ): value = _SoundSequence( value )
		self.__sounds.__setitem__( index, value )
		if not self.__sounds: self.__currentPosition = 0
		elif self.__currentPosition >= len( self.__sounds ):
			self.__currentPosition = len( self.__sounds ) - 1 # a bit of a kludge --- ideally the cursor would stick to the item it was previously on, if the item still survives
	def __delitem__( self, index ):
		if isinstance( index, slice ):
			index = self.index( index )
			for index in sorted( range( *index.indices( len( self.__sounds ) ) ), reverse=True ):
				self.pop( index )
		else:
			self.pop( index )
	
	def SwapSounds( self, firstIndex, secondIndex ):
		"""
		Swap sound at `firstIndex` with sound at `secondIndex`.
		Negative indices are acceptable.
		"""
		self[ firstIndex ], self[ secondIndex ] = self[ secondIndex ], self[ firstIndex ]
		return self

	def MoveSound(self, oldIndex, newIndex):
		"""
		Move sound from `oldIndex` to `newIndex`. Negative
		indices are acceptable.
		"""
		self.insert( newIndex, self.pop( oldIndex ) )
		return self

	def Restart(self):
		"""
		Move `.position` back to the first sound.
		"""
		return self.SetPosition( 0 )

	def SetPosition( self, position, allowNegative=True ):
		"""
		Move `.position` to the specified position.
		"""
		if isinstance( position, int ) and position < 0:
			if allowNegative == 'loop': allowNegative = self.loop
			if not allowNegative: raise QueueError( 'cannot go back before track 0' )
		self.position = position
		return self

	def Forward( self, count=1 ):
		"""
		Move the `.position` ahead by the given count
		(defaults to 1).

		If `self.loop` is False, and you try to skip past the
		end of the queue, a `QueueError` will be raised
		Otherwise, it will loop back around to the start of
		the queue.
		
		You probably will not want to call this method
		directly if this `Queue` is inside a `Player` instance,
		because it will not automatically update the player's
		`.sound` property. Instead, use the corresponding
		`Player` method, `.NextTrack()`
		"""
		return self.SetPosition( self.position + count, allowNegative='loop' )

	def Back( self, count=1 ):
		"""
		Move the `.position` backward by the given count
		(defaults to 1).

		If `self.loop` is False and you try to skip back past
		the beginning of the queue, a `QueueError` will
		be raised. Otherwise, it will loop around to the end
		of the queue.
		
		You probably will not want to call this method
		directly if this `Queue` is inside a `Player` instance,
		because it will not automatically update the player's
		`.sound` property. Instead, use the corresponding
		`Player` method, `.PreviousTrack()`
		"""
		return self.Forward( -count )

	_classNamePrefix = ''
	def __str__( self ):  return self._report( with_repr='short', indent='' )
	def __repr__( self ): return self._report( with_repr='short', indent='' )
	def _short_repr( self, *p ): return '<%s%s 0x%0*X>' % ( self._classNamePrefix, self.__class__.__name__, ( 16 if sys.maxsize > 2 ** 32 else 8 ), id( self ) )
	def _super_repr( self, *p ): return object.__repr__( self )
	def _report( self, with_repr='short', indent='', short=False ):
		s = ''
		if with_repr:
			if   with_repr in [ True, 'short' ]:   f = self._short_repr
			elif with_repr in [ 'super', 'long' ]: f = self._super_repr
			elif callable( with_repr ): f = with_repr
			else: f = object.__repr__
			s = indent + f( self ) + '\n'
			indent += '    '
		indent = ''.join( c if c.isspace() else ' ' for c in indent )
		name = lambda sound: sound.label if sound.label else sound.filename if sound.filename else '?'
		if   short and len( self.__sounds ) == 0: s = s.rstrip( '\n' ) + ' []'
		elif short and len( self.__sounds ) == 1: s = s.rstrip( '\n' ) + ' [ %s ]' % name( self.__sounds[ 0 ] )
		else:
			if self.__sounds:
				s += '{indent}[\n{items}\n{indent}]'.format( indent=indent, items='\n'.join(
					"{indent} {ptr} {i:2d}: {name}".format( indent=indent, i=i, name=name( sound ), ptr=( '->' if i == self.__currentPosition else '  ' ) )
					for i, sound in enumerate( self.__sounds )
				) )
			else: s += indent + '[]'
		return s.rstrip( '\n' )

	def Play( self, *pargs, **kwargs ):
		"""
		This quick-and-dirty method allows you to play a
		`Queue`. It creates a `Player` instance in verbose mode,
		configures it with `autoAdvance='play'` by default, then
		uses it to play a copy of the queue from the beginning,
		waits for it to finish (or for the user to press ctrl-C),
		and destroys the `Player` again.
		
		You will get a better user experience, and better
		performance, if you explicitly create a `Player`
		instance of your own and work with that.
		
		Arguments are passed through to the `Player.Play()`
		method.
		"""
		from . import BackEnd; from .BackEnd import CURRENT_BACK_END as impl
		p = impl.Player( self, verbose=True, autoAdvance='play' )
		p.Play( *pargs, **kwargs )
		p.Wait()
	
def QueueTest():
	"""
	Construct and return an example `Queue` containing
	example `Sound` instances. Initialize a `Player` with
	this to test management of multiple tracks by the `Player`
	class.
	"""
	return Queue( Base.TestSound( pair ) for pair in '12 34 56 78'.split() )

class QueueError( Exception ):
	"""Raised by the `Queue` class when something goes wrong."""
	pass

