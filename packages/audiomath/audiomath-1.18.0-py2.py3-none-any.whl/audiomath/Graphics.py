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
	
]

import sys

from . import Dependencies;         from .Dependencies import numpy
from . import DependencyManagement; from .DependencyManagement import LoadPyplot
from . import Base;                 from .Base import Sound

def Plot( self, zeroBased=False, maxDuration=None, envelope='auto', title=True, timeShift=0, timeScale=1, hold=False, finish=True ):
	"""
	Plot the sound waveform for each channel. The third-party
	Python package `matplotlib` is required to make this work---
	you may need to install this yourself.
	
	Args:
		zeroBased (bool):
			This determines whether the y-axis labels show
			zero-based channel numbers (Python's normal convention)
			or one-based channel numbers (the convention followed
			by almost every other audio software tool). In keeping
			with audiomath's slicing syntax, zero-based indices
			are expressed as integers whereas one-based channel
			indices are expressed as string literals.
		maxDuration (float, None):
			Long sounds can take a prohibitive amount of time
			and memory to plot. If `maxDuration` is not `None`,
			this method will plot no more than the first
			`maxDuration` seconds of the sound. If this means
			some of the sound has been omitted, a warning is
			printed to the console.
		envelope (bool, float, 'auto'):
			With `envelope=True`, plot the sound in "envelope
			mode", which is less veridical when zoomed-in but
			which uses much less time and memory in the graphics
			back end. With `envelope=False`, plot the sound
			waveform as a line. With the default value of
			`envelope='auto'`, only go into envelope mode when
			plotting more than 60 seconds' worth of sound.
			You can also supply a floating-point value, expressed
			in seconds: this explicitly enforces envelope mode
			with the specified bin width.
		title (bool, str):
			With `title=True`, the instance's `.label` attribute
			is used as the axes title. With `title=False` or
			`title=None`, the axes title is left unchanged. If a
			string is supplied explicitly, then that string is
			used as the axes title.
		timeShift (float):
			The x-axis (time) begins at this value, expressed
			in seconds.
		timeScale (float):
			After time-shifting, the time axis is multiplied
			by this number. For example, you can specify
			`timeScale=1000` to visualize your sound on a
			scale of milliseconds instead of seconds.
		hold (bool):
			With `hold=False`, the axes are cleared before
			plotting. With `hold=True`, the plot is superimposed
			on top of whatever is already plotted in the current
			axes.
	"""
	y = self.y
	if not self.nChannels: raise ValueError( '%s object has zero channels' % self.__class__.__name__ )
	if maxDuration is None: maxDuration = 'inf'
	maxDuration = float( maxDuration )
	plotDuration = min( self.duration, maxDuration )
	if numpy.isinf( plotDuration ): maxDuration = plotDuration = 60.0
	if envelope == 'auto': envelope = ( plotDuration > 60.0 )
	if isinstance( envelope, ( bool, int ) ) and envelope == True: envelope = numpy.ceil( plotDuration / 30.0 ) / 1000.0
		
	if self.duration > maxDuration:
		durationStr = 'infinite duration' if numpy.isinf( self.nSamples ) else 'nominal duration %g sec' % self.duration
		#typeStr = 'an array' if isinstance( y, numpy.ndarray ) else 'a ' + y.__class__.__name__
		typeStr = 'a %s' % self.__class__.__name__
		print( 'Plotting only the first %g seconds of %s of %s' % ( maxDuration, typeStr, durationStr ) )
		y = self[ :maxDuration ].y
	y = numpy.asarray( y ) / -2.0
	y = numpy.clip( y, -0.5, 0.5 )
	nChannels = Base.NumberOfChannels( y )
	offset = numpy.arange( nChannels )
	if not zeroBased: offset += 1
	y += offset
	
	plt = LoadPyplot()
	if envelope:
		t, lower, upper = Base.Envelope( y, granularity=envelope, fs=self.fs )
		t += timeShift
		t *= timeScale
		if not hold: plt.cla()
		for iChannel in range( nChannels ): plt.fill_between( t, lower[ :, iChannel ], upper[ :, iChannel ], edgecolor='none' )
	else:
		t = numpy.arange( 0, Base.NumberOfSamples( y ) ) / float( self.fs )
		t += timeShift
		t *= timeScale
		if not hold: plt.cla()
		h = plt.plot( t, y )
	ax = plt.gca()
	if not hold:
		ax.set_yticks( offset )
		fmt = '%g'
		if not zeroBased: fmt = "'%s'" % fmt
		fmt = '[:,%s]' % fmt
		ax.yaxis.set_major_formatter( plt.FormatStrFormatter( fmt ) )
		ax.set_ylim( offset.max() + 1, offset.min() - 1 )
		try: ax.set_xlim( t[ 0 ], t[ -1 ] )
		except: pass # copes with the edge-case of an empty Sound
	if title == True: title = self.label if self.label else ''
	if isinstance( title, str ): ax.set_title( title )
	ax.xaxis.grid( True )
	ax.yaxis.grid( True )
	#plt.draw()
	if finish:
		if not isinstance( finish, dict ): finish = { 'zoom' : True }
		FinishFigure( **finish )
Sound.Plot = Plot

def FinishFigure( maximize=False, raise_=False, pan=None, zoom=None, wait=None, savefig=None ):
	plt = DependencyManagement.LoadPyplot()
	if not plt or not plt.get_fignums(): return
	ipythonIsRunning = 'IPython' in sys.modules
	if wait is None: wait = not ipythonIsRunning
	if ipythonIsRunning: plt.ion()
	elif wait: plt.ioff()
	plt.draw()
	try: toolbar = plt.gcf().canvas.toolbar
	except: toolbar = None
	if toolbar is not None:
		try: panAlreadyOn = ( toolbar._active == 'PAN' )
		except: panAlreadyOn = False
		try: zoomAlreadyOn = ( toolbar._active == 'ZOOM' )
		except: zoomAlreadyOn = False
		if pan is not None:
			if pan and not panAlreadyOn: toolbar.pan( 'on' )
			if not pan and panAlreadyOn: toolbar.pan( 'off' )
		if zoom is not None:
			if zoom and not zoomAlreadyOn: toolbar.zoom( 'on' )
			if not zoom and zoomAlreadyOn: toolbar.zoom( 'off' )
	try: manager = plt.get_current_fig_manager()
	except: manager = None
	if maximize:
		try: plt.gcf().canvas._tkcanvas.master.wm_state( 'zoomed' )
		except: pass
		try: manager.window.state( 'zoomed' )
		except: pass
		try: manager.window.showMaximized()
		except: pass
		try: manager.frame.Maximize( True )
		except: pass
	if raise_:
		try: manager.window.raise_()
		except: pass
	if savefig: plt.gcf().savefig( savefig )
	if wait == 'block': plt.show( block=True )
	elif wait: plt.show()
