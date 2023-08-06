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
	'Require', 'RequireAudiomathVersion',
	'GetVersions',
	'ReportVersions',
	'LoadPyplot',
]

import os
import sys
import warnings
import platform
import operator
import collections

from . import Meta; from .Meta import GetRevision, PackagePath, __version__

# Force warnings.warn() to omit the source code line in the message
formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None, **k: formatwarning_orig( message, category, filename, lineno, line='' )

KNOWN = {}
IMPORTED = {}
VERSIONS = collections.OrderedDict()
_SPHINXDOC = any( os.environ.get( varName, '' ).lower() not in [ '', '0', 'false' ] for varName in [ 'SPHINX' ] )

class ModuleNotAvailable( object ):
	def __init__( self, name, packageName=None, broken=False ): self.__name, self.__packageName, self.__broken = name, packageName, broken
	def __bool__( self ): return False    # works in Python 3 but not 2
	def __nonzero__( self ): return False # works in Python 2 but not 3
	def __getattr__( self, attr ): raise ImportError( str( self ) )
	def __str__( self ):
		packageName = self.__packageName
		if packageName and not isinstance( packageName, ( tuple, list ) ): packageName = [ packageName ]
		packageName = ' or '.join( repr( name ) for name in packageName ) if packageName else repr( self.__name )
		if self.__broken:
			msg = 'module %r did not work as expected for this functionality - your installation of the %r package may be broken' % ( self.__name, packageName )
			if self.__broken != 1: msg += ' (%s)' % self.__broken
		else:
			msg = 'module %r could not be imported - you need to install the third-party %s package for this functionality' % ( self.__name, packageName )
		return msg
		
PRETEND_NOT_INSTALLED = []
def Sabotage( *pargs ):
	"""
	This is intended purely for debugging purposes in the hands of audiomath's
	maintainers, to get an idea of how audiomath behaves in the absence of one
	or more third-party dependencies without having to go to all the
	trouble of setting up a new virtual environment. Pass the names of one
	or more packages/modules and audiomath will pretend that they are not
	installed. For maximum effectiveness, hack your `Sabotage()` call into
	the very first line of `audiomath/__init__.py`
	"""
	global PRETEND_NOT_INSTALLED
	PRETEND_NOT_INSTALLED += pargs

def RequireAudiomathVersion( targetVersion, *furtherConditions ):
	"""
	Verify that the current version of audiomath is equal to, or later than,
	the specified `targetVersion`, which should be a string encoding three
	integers in 'X.Y.Z' format.
	
	Optionally, you may prefix `targetVersion` with one of the following
	operators, to customize the version comparison (the default
	comparator is `>=` )::
	
		<     <=    ==    !=    >=    >    
	
	"""
	package = 'audiomath'
	currentVersion = GetVersions()[ package ][ 0 ]
	currentNumbers = [ int( x ) for x in currentVersion.split( '.' ) ]
	ops = '>=:ge:must be at least\n<=:le:must be no later than\n>:gt:must be later than\n<:lt:must be earlier than\n==:eq:must be exactly\n!=:ne:cannot be'
	ops = [ term.split( ':', 3 ) for term in ops.split( '\n' ) ]
	for targetVersion in ( targetVersion, ) + furtherConditions:
		if isinstance( targetVersion, ( float, int ) ): targetVersion = '%g' % targetVersion
		targetVersion = targetVersion.strip()
		for symbol, cmpName, cmpText in ops: # NB:  <= and >= must be tested before < and > ...
			if targetVersion.startswith( symbol ):
				targetVersion = targetVersion[ len( symbol ): ].strip()
				break
		else:
			symbol, cmpName, cmpText = ops[ 0 ]
		cmp = getattr( operator, cmpName )
		targetNumbers = [ int( x ) for x in  targetVersion.split( '.' ) ]
		if not cmp( currentNumbers, targetNumbers ):
			msg = '%s version %s %s (current version is %s)' % ( package, cmpText, targetVersion, currentVersion )
			if cmpName in [ 'gt', 'ge' ]:
				if GetRevision().startswith( 'git ' ): msg += '\nTo upgrade your git-controlled installation, try:\n   cd "%s" && git pull' % PackagePath()
				else: msg += '\nTo upgrade an installation you downloaded via pip:\n    python -m pip install --upgrade %s --no-dependencies' % package
			raise RuntimeError( msg )
	
def Require( *pargs, **kwargs ):
	"""
	Verify that the named third-party module(s) is/are available---if not,
	raise an exception whose message contains an understandable action
	item for the user. Return the module (or sequence of modules, if more
	than one is requested).
	
	Each positional argument can refer to one module or package, or you
	can request multiple modules in one space-delimited string. To
	optimize clarity of the potential error messages, optionally
	separate the module name (what you import) from the package name
	(what you would have to install) using a colon.  In either module
	name or package name, optionally supply alternative names delimited
	by a slash. For example, if neither `PIL` nor `pillow` is installed,
	then this::
	
	    Image = Require('Image/PIL.Image:PIL/pillow')
	
	raises an exception with the error message: `module 'Image' could
	not be imported - you need to install the third-party 'PIL' or
	'pillow' package for this functionality`.
	
	Pass keyword argument `registerVersion=True` to have the package
	included in the output of `ReportVersions()`.
	"""
	requirements = [ name for arg in pargs for name in arg.split() ]
	for i, name in enumerate( requirements ):
		if ':' in name:
			name, packageName = name.split( ':', 1 )
			kwargs_i = { 'packageName' : packageName }
		else:
			kwargs_i = {}
		kwargs_i.update( kwargs )
		requirements[ i ] = ( name.split( '/' ), kwargs_i )
	modules = [ Import( *names, **kwargs ) for names, kwargs in requirements ] 
	errors = []
	for module in modules:
		if not module: errors.append( str( module ) )
	if errors and not _SPHINXDOC:
		raise ImportError( '\n   '.join( [ '\n\nOne or more third-party requirements were not satisfied:' ] + errors ) )
	return modules[ 0 ] if len( modules ) == 1 else modules

def Define( canonicalName, alternativeNames=None, packageName=None, registerVersion=False ):
	rec = KNOWN.setdefault( canonicalName, {} )

	if alternativeNames is None: alternativeNames = []
	if isinstance( alternativeNames, str ): alternativeNames = alternativeNames.split()
	seq = rec.setdefault( 'alternativeNames', [] )
	for name in alternativeNames:
		if name not in seq: seq.append( name )

	if packageName is None: packageName = []
	if isinstance( packageName, str ): packageName = packageName.replace( '/', ' ' ).split()
	seq = rec.setdefault( 'packageName', [] )
	for name in packageName:
		if name not in seq: seq.append( name )

	rec.setdefault( 'registerVersion', False )
	if registerVersion: rec[ 'registerVersion' ] = registerVersion

	return rec[ 'alternativeNames' ], rec[ 'packageName' ], rec[ 'registerVersion' ]

def ImportAll():
	return [ Import( name ) for name in KNOWN ]
	
def Import( canonicalName, *alternativeNames, **kwargs ):
	alternativeNames, packageName, registerVersion = Define( canonicalName=canonicalName, alternativeNames=alternativeNames, **kwargs )
	names = [ canonicalName ] + list( alternativeNames )
	pretendNotInstalled = any( name in PRETEND_NOT_INSTALLED for name in names )
	for name in names:
		if pretendNotInstalled: name += '_NOT'
		module = IMPORTED.get( name, None )
		if module is not None: return module
		try: exec( 'import ' + name )
		except ImportError: module = ModuleNotAvailable( canonicalName, packageName )
		except: module = ModuleNotAvailable( canonicalName, packageName, broken=True )
		else:
			module = sys.modules[ name ]
			IMPORTED[ module.__name__ ] = module
			break
	if registerVersion: RegisterVersion( module )
	return module

def Unimport( *names ):
	names = [ getattr( name, '__name__', name ) for name in names ]
	prefixes = tuple( [ name + '.' for name in names ] )
	for registry in [ sys.modules, IMPORTED, VERSIONS ]:
		names = [ name for name in registry if name in names or name.startswith( prefixes ) ]
		for name in names: registry.pop( name )

def RegisterVersion( module=None, attribute='__version__', name=None, value=None ):
	if module and not name:
		name = module.__name__
		if attribute.strip( '_' ).lower() != 'version': name += '.' + attribute
	if module and not value:
		value = getattr( module, attribute, None )
	if name and value:
		VERSIONS[ name ] = value
	return module
	
def GetVersions():
	"""
	Retuns a `dict` containing system and package versioning
	information. Use `ReportVersions()` print a formatted
	version of the same information.
	"""
	versions = VERSIONS.__class__()
	for k, v in VERSIONS.items():
		if callable( v ): versions.update( v() )
		elif v: versions[ k ] = v
	return versions

def ReportVersions():
	"""
	Prints system and package versioning information, obtained
	from `GetVersions()`.
	"""
	for k, v in GetVersions().items():
		print( '%25s : %r' % ( k, v ) )

def LoadPyplot( interactive='auto' ):
	"""
	Attempts to imports and return `matplotlib.pyplot`,
	setting the `matplotlib.interactive()` setting along
	the way. If `matplotlib` is not installed, a virtual
	module is returned which will raise an informative
	error the first time you try to use it.
	"""
	matplotlib = plt = Import( 'matplotlib', registerVersion=True )
	if interactive == 'auto':
		if 'matplotlib.backends' in sys.modules: interactive = None
		else: interactive = ( 'IPython' in sys.modules )
	if matplotlib and interactive is not None: matplotlib.interactive( interactive )
	if matplotlib: import matplotlib.pyplot as plt
	return plt

RegisterVersion( name='sys', value=sys.version )
RegisterVersion( name='sys.platform', value=sys.platform )
RegisterVersion( name='platform.machine', value=platform.machine() )
RegisterVersion( name='platform.architecture', value=platform.architecture() )
for func in 'win32_ver mac_ver linux_distribution libc_ver'.split():
	try: result = getattr( platform, func )()
	except: result = ( '', )
	if result and result[ 0 ]:
		RegisterVersion( name='platform.' + func, value=result )


RegisterVersion( name=__package__, value=( __version__, GetRevision(), PackagePath( '.' ) ) )
