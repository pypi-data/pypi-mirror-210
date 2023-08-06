# -*- coding: utf-8 -*-

# $BEGIN_RECRUITMENTCURVEFITTING_LICENSE$
# 
# This file is part of the RecruitmentCurveFitting project, a Python
# package for fitting sigmoid and bell-shaped functions to EMG
# recruitment-curve measurements.
# 
# Copyright (c) 2023 Jeremy Hill
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
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
# $END_RECRUITMENTCURVEFITTING_LICENSE$

"""
Python classes, and a command-line utility, for fitting sigmoid and
bell-shaped curves derived from EMG data.

Third-party requirements:

- `numpy`
- `scipy.optimize` (via the generic `CurveFitting` module)
- `matplotlib` if you want to plot

Example of use as a Python module::

    from RecruitmentCurveFitting import Sigmoid, HillCurve

    x = [1.50, 1.50, 2.00, 2.00, 2.50, 2.50, 3.00, 3.00, 3.50, 3.50, 4.00, 4.00, 4.50, 4.50, 5.00]
    m = [0.02, 0.04, 0.06, 0.03, 0.19, 0.13, 0.98, 1.11, 2.13, 2.17, 2.39, 2.39, 2.42, 2.45, 2.45]
    h = [0.12, 0.11, 0.99, 1.14, 1.53, 1.93, 1.15, 1.05, 0.17, 0.28, 0.14, 0.12, 0.12, 0.14, 0.13]

    mFit = Sigmoid( x, m )
    hFit = HillCurve( x, h )

    hMaxStim, hMax = hFit.Find( 'max' )
    mMax = mFit.uHeight.finalValue
    mThresholdStim = mFit.Backward( 0.1, scaled=False )

    mFit.Plot( markX=mThresholdStim, markY=mMax )
    hFit.Plot( markX=hMaxStim, markY=hMax, hold=True)

This module also contains a higher-level class, `RecruitmentCurve`, which
you construct using an array of EMG time-series, and use to extract both
`m` and `h` magnitudes and fit them, given their start and end points in
milliseconds::
    
    from RecruitmentCurveFitting import RecruitmentCurve, UnpackExamples

    UnpackExamples() # writes assorted example files to the current directory

    z = RecruitmentCurve('example-waveforms.csv') # that's one of the files
    z.Fit( boundsM=[8.1, 15.3], boundsH=[34.6, 42.1] )
    z.Plot() # try hovering the mouse pointer over each data-point, it's fun
	
This module can also be run as a standalone command-line utility. Input files
should be formatted as comma- or space-delimited numeric tables where the last
three columns are stimulation intensity, M-wave size and H-reflex size. Prior
columns, if present, are used to separate different conditions from each other
(each condition generates one pair of curve fits, and one figure if requested)
Column headings are optional. For example::

    # If you didn't already unpack the example files in the current directory,
    # then first do this:
    python -m RecruitmentCurveFitting --unpack-examples
    
    # Then the demo is:
    python -m RecruitmentCurveFitting example-data1.txt example-data2.txt -p -s out.pdf
    
    # Run this for further details:
    python -m RecruitmentCurveFitting --help

"""

__all__ = [
	'ModifiedBrinkworth',
	'HillCurve',
	'Sigmoid',
	
	'RecruitmentCurve',
	
	'ChooseTradeoff',
	'PlotTradeoff',
	
	'SavePDF',
	'UnpackExamples',
]

import copy
import weakref

import numpy; from numpy import exp, log, nan, inf

try: from . import CurveFitting
except ImportError: from  CurveFitting import Curve, Parameter, SavePDF
else:               from .CurveFitting import Curve, Parameter, SavePDF

@Parameter.Setup
class ModifiedBrinkworth( Curve ):	
	def Evaluate( self, x, a, b, c ):
		"""
		Adapted from:
		
		- Brinkworth RS, Tuncer ME, Tucker KJ, Jaberzadeh S & Türker KS (2007)
		  Standardization of H-reflex analyses.
		  Journal of Neuroscience Methods 162(1-2):1-7
		  https://doi.org/10.1016/j.jneumeth.2006.11.020
		
		Their original equation (2)::
		
		    a * exp( -0.5 * ( x**c - xbar/b ) ** 2.0 )
		    
		makes no sense at all, and indeed seems to get itself frequently stuck
		in local minima that involved tiny molehills centered on a low value
		`xbar/b` for some large `b`. It is surprising that there's no erratum
		correcting the formula.
		
		My correction raises `x` and `xbar` to the same power (so that they're
		at least on the same scale) and then divides their *difference* by `b`
		as would seem appropriate for a width parameter::
		
		    a * exp( -0.5 * ( (x**c - xbar**c)/b ) ** 2.0 )
		    
		Note that the optimization phase itself has only three free parameters,
		with the value of `xbar` being data-determined but fixed during a
		preliminary phase, at "the stimulation intensity that produces the largest
		response". Presumably the authors' intention was to assert the horizontal
		position of the empirical maximum as the peak at all costs (no
		interpolation allowed).
		"""
		return a * exp( -0.5 * ( ( x**c - self.xbar**c ) / b ) ** 2.0 )
		
	def Initialize( self, x, y ):
		ux = numpy.unique( self.x )
		uy = [ numpy.median( y[ x == xi ] ) for xi in ux ]
		self.xbar = ux[ numpy.nanargmax( uy ) ]
		return dict(
			a=y[ x == x[ numpy.nanargmax( y ) ] ].mean(), 
			b=x.std(),
			c=1.0, 
		)
	def SetBounds( self ):
		self.c.min = 0.0
		self.a.min = 0.0
		self.a.min = self.y.max() * 0.5
		#self.a.max = self.y.max() * 1.1
		
		

@Parameter.Setup
class HillCurve( Curve ):
	
	@staticmethod
	def Evaluate( x, uHeight, uShift, uLogSlope, vFloor, vShift, vAsymmetry ):
		"""
		Model the curve as the product of two sigmoids, `u` (left) and `v` (right).
		
		Considering each sigmoid in isolation with a normalized range of (0,1),
		its "shift" is the x-coordinate of the halfway point, and its "slope" is
		the gradient (in normalized units per x-axis unit) at the halfway point.
		
		The overall scaling factor `uHeight` is often roughly equal to the overall
		maximum of the curve (or somewhat more than the maximum, depending on how
		much the two sigmoids cross).
		
		A positive `vAsymmetry` value means right is steeper than left (normalized).
		A negative `vAsymmetry` value means left is steeper than right (normalized).
		
		The `vFloor` is the lower asymptote of the right sigmoid expressed as
		a proportion (i.e. in normalized units).
		
		NB: Parameters are carefully constrained.
		"""
		uSlope = +exp( uLogSlope )              # always positive
		vSlope = -exp( uLogSlope + vAsymmetry ) # always negative
		
		u =             uHeight     / ( 1 + exp( -4 * ( x - uShift ) * uSlope ) )
		v = vFloor + ( 1 - vFloor ) / ( 1 + exp( -4 * ( x - vShift ) * vSlope ) )
		return u * v
		# Shift and slope are defined at f0 = 0.5
		# => h0 = 0, k = 4   (hence the factor of 4 in the exp() argument, and for non-zero h0,  k*h0 would be added to that argument)
	     
	@staticmethod
	def Initialize( x, y ):
		ux = numpy.unique( x )
		averageXStepSize = numpy.diff( ux ).mean()
		xmin, xmax = x.min(), x.max()
		xpeak = x[ numpy.nanargmax( y ) ]
		
		uHeight = y[ x == xpeak ].mean()
		vFloor  = y[ x == xmax  ].mean() / uHeight
		vFloor = min( vFloor, 0.75 )
		uShift = max( xmin  * 0.5 + xpeak * 0.5, ux[ :2  ].mean() )
		vShift = min( xpeak * 0.5 + xmax  * 0.5, ux[ -2: ].mean() )
		uSlope = +1.0 / max( xpeak - uShift, averageXStepSize )
		vSlope = -1.0 / max( vShift - xpeak, averageXStepSize )
		return dict(
			uHeight=uHeight,
			uShift=uShift,
			uLogSlope=log( uSlope ),
			vFloor=vFloor,
			vShift=vShift,
			vAsymmetry=log( -vSlope / uSlope ),
		)

	def SetBounds( self ):
		xmin, xmax = self.x.min(), self.x.max()
		ymin, ymax = self.y.min(), self.y.max()
		ux = numpy.unique( self.x )
		averageXStepSize = numpy.diff( ux ).mean()
		self.uHeight.min = 0.0
		self.uHeight.max = ymax * 2.0
		self.uShift.min = ux[ :2  ].mean() # halfway between the first two points
		self.vShift.max = ux[ -2: ].mean() # halfway between the last two points
		self.uLogSlope.max = log( 1.0 / averageXStepSize )
		self.vAsymmetry.min = -log( 5.0 ) # negative vAsymmetry means LHS is steeper than RHS
		self.vAsymmetry.max = +log( 2.0 ) # positive vAsymmetry means RHS is steeper than LHS (more unusual)
		self.vFloor.min = 0.0
		self.vFloor.max = 1.0

	class SlopeFixer( object ):
		"""Assign this as the "fixed" value of vAsymmetry, to achieve a certain fixed vLogSlope"""
		def __init__( self, vLogSlope ):
			self.vLogSlope = vLogSlope
		def __call__( self, uLogSlope, **kwargs ):
			return self.vLogSlope - uLogSlope
		
@Parameter.Setup
class Sigmoid( Curve ):
	
	@staticmethod
	def Evaluate( x, uHeight, uShift, uLogSlope, uFloor ):
		"""
		- `uHeight` is the upper asymptote value.
		
		- `uShift` is the x-coordinate of the point of inflection.
		
		- `uLogSlope` is the natural log of the gradient at the point of inflection,
		   on a normalized vertical scale (i.e. disregarding `uHeight` and `uFloor`).
		   
		- `uFloor` is expressed as a proportion of `uHeight`.		
		"""
		unscaled = 1 / ( 1 + exp( -4 * ( x - uShift ) * exp( uLogSlope ) ) )
		return uHeight * ( uFloor + ( 1 - uFloor ) * unscaled )
		# Shift and slope are defined at f0 = 0.5
		# => h0 = 0, k = 4   (hence the factor of 4 in the exp() argument, and for non-zero h0,  k*h0 would be added to that argument)
	
	def Forward( self, x, *p, **kwargs ):
		"""
		Similar to the superclass `Curve.Forward()` method, but
		provides the `scaled` keyword arg. With `scaled=True`
		(which is the default) the output is scaled between
		`.uFloor` and `.uHeight`.  With `scaled=False`, the
		output is between 0 and 1.
		"""
		scaled = kwargs.pop( 'scaled', True )
		if kwargs: raise TypeError( 'Forward() got an unexpected keyword argument %r' % list( kwargs.keys() )[ 0 ] )
		p = self.ResolveParameters( p )
		if not scaled: p[ self.uFloor.index ], p[ self.uHeight.index ] = 0.0, 1.0
		return self.Evaluate( x, *p )
		
	def Backward( self, f, *p, **kwargs ):
		"""
		Similar to the superclass `Curve.Backward()` method, but
		provides the `scaled` keyword arg. With `scaled=True`
		(which is the default) the input is assumed to be
		expressed as a scaled value between `.uFloor` and
		`.uHeight`.  With `scaled=False`, the input is assumed to
		be unscaled, between 0 and 1.
		"""
		scaled = kwargs.pop( 'scaled', True )
		if kwargs: raise TypeError( 'Backward() got an unexpected keyword argument %r' % list( kwargs.keys() )[ 0 ] )
		p = self.ResolveParameters( p, asDict=True )
		f = numpy.asarray( f )
		if scaled: f_unscaled = ( f / p[ 'uHeight' ] - p[ 'uFloor' ] ) / ( 1 - p[ 'uFloor' ] )
		else: f_unscaled = f
		h = log( f_unscaled / ( 1 - f_unscaled ) ) / 4
		return h * exp( -p[ 'uLogSlope' ] ) + p[ 'uShift' ]
	
	@staticmethod
	def Initialize( x, y ):
		ux = numpy.unique( x )
		averageXStepSize = numpy.diff( ux ).mean()
		xmin, xmax = x.min(), x.max()
		
		uFloor = y[ x == xmin ].mean()
		uHeight = y[ x == xmax ].mean() - uFloor
		uShift = min( max( xmin  * 0.5 + xmax * 0.5, ux[ :2  ].mean() ), ux[ -2:  ].mean() )
		uSlope = 4.0 / max( xmax - uShift, averageXStepSize )
		return dict(
			uHeight=uHeight,
			uShift=uShift,
			uLogSlope=log( uSlope ),
			uFloor=uFloor,
		)

	def SetBounds( self ):
		xmin, xmax = self.x.min(), self.x.max()
		ymin, ymax = self.y.min(), self.y.max()
		ux = numpy.unique( self.x )
		averageXStepSize = numpy.diff( ux ).mean()
		self.uHeight.min = 0.0
		self.uHeight.max = ymax * 2.0
		self.uShift.min = ux[ :2  ].mean() # halfway between the first two points
		self.uShift.max = ux[ -2: ].mean() # halfway between the last two points
		self.uLogSlope.max = log( 4.0 / averageXStepSize )
		self.uFloor.min = 0.0
		self.uFloor.max = 1.0

def ChooseTradeoff( m, h=None, limits=( 0.1, 0.333 ) ):
	# TODO: not a good algorithm for reflex operant conditioning;
	#       actually we want to prefer the rising slope of the H curve,
	#       even if that means going below 10% M_max
	if h is None: curve = m; m, h = curve.m, curve.h
	hTitle = h.Describe( ' ' )
	mTitle = m.Describe( ' ' )
	if hTitle != mTitle: raise ValueError( 'mismatched H and M sessions' )
	xHmax, yHmax = h.Find( 'max' )
	xChosen, yChosen = h.Find( 'max', xLimits=m.Backward( limits, scaled=False ) )
	h.chosenX = xChosen
	h.chosenPercentHmax = 100.0 * yChosen / yHmax
	m.chosenX = xChosen
	m.chosenPercentMmax = 100.0 * m.Forward( xChosen, scaled=False )

def PlotTradeoff( m, h=None, hDenominator='M', hold=False, figure=None, axes=None, **kwargs ):
	if h is None: curve = m; m, h = curve.m, curve.h
	hTitle = h.Describe( ' ' )
	mTitle = m.Describe( ' ' )
	if hTitle != mTitle: raise ValueError( 'mismatched H and M sessions' )
	
	hDenominator = hDenominator.upper()[ 0 ]
	if   hDenominator == 'H': hDenominatorValue = h.Find( 'max' )[ 1 ]
	elif hDenominator == 'M': hDenominatorValue = m.uHeight.finalValue
	else: raise ValueError( "`hDenominator` should be either 'H' or 'M'" )
	
	x = numpy.linspace( h.x.min(), h.x.max(), 200 )
	mp = 100.0 * m.Forward( x, scaled=False )
	he = 100.0 * h.Forward( x ) / hDenominatorValue
	
	chosenX           = getattr( m, 'chosenX', nan )
	chosenPercentMmax = getattr( m, 'chosenPercentMmax', nan )
	chosenPercentHmax = getattr( h, 'chosenPercentHmax', nan )
	
	import matplotlib.pyplot as plt
	if axes is None: axes = ( plt.gcf() if figure is None else plt.figure( figure ) if isinstance( figure, int ) else plt.figure( figure.number ) ).gca()
	figure = axes.figure
	if not hold: axes.cla()
	hLine, = axes.plot( mp, he, **kwargs )
	kwargs.update( marker='*', color=hLine.get_color(), markersize=12, clip_on=False )
	axes.plot( chosenPercentMmax, chosenPercentHmax, **kwargs )
	axes.set( xlabel='% $M_{max}$', ylabel='% $' + hDenominator + '_{max}$', xlim=[ 0, 50 ], ylim=[ 0, 100 ] )
	axes.grid( True )
	axes.set_title( hTitle, fontsize=7, fontweight='bold' )		
	# TODO:
	# - plot raw data-points in this space too?

def UnpackExamples( overwrite=False ):
	import os, glob
	sources = [ match for pattern in [ 'example*.txt', 'example*.csv' ] for match in glob.glob( os.path.join( os.path.dirname( __file__ ), pattern ) ) ]
	for source in sources:
		fileName = os.path.basename( source )
		if os.path.isfile( fileName ) and not overwrite: print( '%s exists, not overwriting' % fileName ); continue
		print( 'writing %s' % fileName )
		fileContent = open( source, 'rt' ).read() # do this *before* opening the destination for writing, in case they are the same file
		open( fileName, 'wt' ).write( fileContent )
			
class RecruitmentCurve( object ):
	"""
	An object that takes EMG time-series (one per trial) and provides
	a `.Fit()` method that extracts M-wave and H-reflex magnitudes (given
	the bounds of these waveform components in milliseconds) and fits the
	two respective recruitment curves.
	"""
	def __init__( self, waveforms, timeBase=None, stimulationIntensities=None, excuses=None, **descriptors ):
		"""				
		Args:
		    waveforms (2D `numpy.array`, or sequence of sequences of values):
		        a two-dimensional array of voltage values: one row per
		        time sample, one column per trial. It is assumed that you
		        have preprocessed the waveforms appropriately, including
		        removal of the stimulation artifact (this module does not
		        yet contain any tools for artifact removal).
		        
		        Alternatively, `waveforms` may be a filename suitable for
		        passing to `numpy.loadtxt`. The content should be a text
		        representation of a 2-D numpy array numberOfSamples+1 by
		        numberOfTrials+1.   The first column (all but the first
		        element) will be assumed to denote the `timeBase`. The
		        first row (all but the first element) will be taken as
		        `stimulationIntensities`. This format is saved by
		        `.SaveArray()`.
		    
		    timeBase (float, or a 1D `numpy.array` or sequence of values):
		        if expressed as a scalar, this should simply be the
		        sampling frequency in Hz. If expressed as a sequence of
		        time values, the number of values should be equal to the
		        number of rows in `waveforms`.
		    
		    stimulationIntensities (1D `numpy.array` or sequence of values):
		        one stimulation-intensity value per column of `waveforms`.
		    
		    excuses (list, tuple):
		        an optional sequence of strings detailing reasons why
		        this dataset is disqualified from ordinary analysis. If
		        non-empty, curve-fitting will be skipped for this dataset.
		    
		    **descriptors:
		        any further keyword arguments are stored in the
		        `self.descriptors` dictionary to distinguish this
		        dataset from other datasets (subject name, experimental
		        condition, etc).
		"""
		# For PlotHoverCallback:
		self.clients = {}  # use Associate() to register a (weakref to a) Curve instance as a client
		self.overlayAxes = None
		self.lines = []
		self.m = self.h = None
		if isinstance( waveforms, str ):
			waveforms = numpy.loadtxt( waveforms, delimiter=',' )
			if timeBase is None: timeBase = waveforms[ 1:, 0 ]
			if stimulationIntensities is None: stimulationIntensities = waveforms[ 0, 1: ]
			waveforms = waveforms[ 1:, 1: ]
		
		if isinstance( waveforms, RecruitmentCurve ):
			other = waveforms
			self.waveforms = other.waveforms.copy()
			self.timeBase = other.timeBase.copy()
			self.stimulationIntensities = other.stimulationIntensities.copy()
			self.excuses = copy.deepcopy( other.excuses )
			self.descriptors = copy.deepcopy( other.descriptors )
			for attrName, fit in other.clients.values():
				fit = fit() # de-reference weakref.ref
				if fit is not None: self.Associate( **{ attrName : fit.__class__( fit ) } )
		else:
			self.waveforms = numpy.asarray( waveforms, dtype=float )
			nSamples, nWaveforms = self.waveforms.shape
			if timeBase is None: raise ValueError( 'must supply timeBase' )
			if stimulationIntensities is None: raise ValueError( 'must supply stimulationIntensities' )
			if isinstance( timeBase, ( int, float ) ):
				samplesPerSecond = float( timeBase )
				timeBase = 1000.0 * numpy.arange( nSamples )[ :, None ] / samplesPerSecond
			self.timeBase = numpy.asarray( timeBase, dtype=float ).ravel()
			self.stimulationIntensities = numpy.asarray( stimulationIntensities, dtype=float ).ravel()
			self.excuses = list( excuses ) if excuses else []
			self.descriptors = dict( descriptors )

			if self.timeBase.size != nSamples: raise ValueError( 'number of elements in `timeBase` should match the number of rows of `waveforms`' )
			if self.stimulationIntensities.size != nWaveforms: raise ValueError( 'number of elements in `stimulationIntensities` should match the number of columns in `waveforms`' )
			ud = numpy.unique( numpy.diff( self.timeBase ) )
			if ud.ptp() > 1e-10 or ud.mean() <= 0.0: raise ValueErrror( '`timeBase` should be a monotonically increasing array of millisecond timestamps with even spacing' )
			
	def SaveArray( self, fileName ):
		"""
		Save `self.waveforms`, `self.timeBase` and `self.stimulationIntensities` as
		a single 2-D numeric array in CSV format. The `fileName` of such a file can
		be used as a single argument to the constructor of a new object in future.
		"""
		compositeArray = numpy.concatenate( [ self.timeBase.ravel()[ :, None ], self.waveforms ], axis=1 )
		compositeArray = numpy.concatenate( [ [ [ 0 ] + list( self.stimulationIntensities.ravel() ) ], compositeArray ], axis=0 )
		numpy.savetxt( fileName, compositeArray, delimiter=',' )
		return self
		
	def Associate( self, *pargs, **kwargs ):
		"""
		For each argument `x` (assumed to be a `Curve` instance):
		
		- set `x.PlotHoverCallback = self.PlotHoverCallback`
		- store a `weakref.ref` to `x` in `self.clients` (for use
		  in `PlotHoverCallback()`)
		- if it was passed as a keyword argument, attach `x` as an
		  attribute of `self` under the specified name.
		
		This allows multiple `Curve` objects (presumably plotted on
		the same axes as each other) to end up calling the same
		centralized `PlotHoverCallback` handler.
		"""
		for attrName, fit in list( zip( [ None ] * len( pargs), pargs ) ) + list( kwargs.items() ):
			fit.PlotHoverCallback = self.PlotHoverCallback
			self.clients[ id( fit ) ] = ( attrName, weakref.ref( fit ) )
			if attrName: setattr( self, attrName, fit )
		return self
	
	def Excerpt( self, bounds, waveforms=None ):
		"""
		Given `bounds=[startTimeInMilliseconds, endTimeInMilliseconds]`, return
		the corresponding excerpt from `self.waveforms` (or optionally from some
		other array provided as the optional `waveforms` argument, provided the
		number of rows is the same as the number of elements of `self.timeBase`).
		
		If `waveforms` is equal to the string `'mask'` return a logical array
		instead, which can be used as a subscript into `self.waveforms` or
		`self.timeBase`.
		"""
		bounds = numpy.asarray( bounds, dtype=float ).ravel()
		mask = ( self.timeBase >= min( bounds ) ) & ( self.timeBase <= max( bounds ) )
		if isinstance( waveforms, str ) and waveforms == 'mask': return mask
		if waveforms is None: waveforms = self.waveforms
		subs = [ slice( None ) for dim in waveforms.shape ]
		subs[ 0 ] = mask
		return waveforms[ tuple( subs ) ]
		
	def Magnitudes( self, bounds ):
		"""
		Given `bounds=[startTimeInMilliseconds, endTimeInMilliseconds]`, return
		the mean (across time-samples) of the rectified voltages values from the
		corresponding `.Excerpt()` of each trial.
		"""
		waves = self.Excerpt( bounds )
		nSamples = len( waves )
		if len( waves ):  return numpy.abs( waves ).mean( axis=0 )
		else: return numpy.array( [ nan ] * waves.shape[ 1 ] )
	
	def Fit( self, boundsM=None, boundsH=None, robust=False, shapeM=Sigmoid, shapeH=HillCurve ):
		"""
		Given `boundsM=[mStartTimeInMilliseconds, mEndTimeInMilliseconds]`
		and   `boundsH=[hStartTimeInMilliseconds, hEndTimeInMilliseconds]`,
		extract the corresponding `.Magnitudes()` for M-wave and H-reflex
		components. Then fit a `Sigmoid` to the M magnitudes, and whichever
		class is specified (by default, `HillCurve`) for the H magnitudes.
		
		The resulting `Curve` objects are in `self.m` and `self.h`.
		
		If you have `matplotlib`, you may also wish to `.Plot()`.
		"""
		if boundsM is None and boundsH is None:
			raise ValueError( 'must supply `boundsM` or `boundsH` or both' )
			
		if boundsM is not None:
			boundsM = numpy.asarray( boundsM, dtype=float ).ravel()
			self.boundsM = [ boundsM.min(), boundsM.max() ]
			self.Associate(
				m = shapeM( self.stimulationIntensities, self.Magnitudes( self.boundsM ), robust=robust, excuses=self.excuses, **self.descriptors ),
			)
		if boundsH is not None:
			boundsH = numpy.asarray( boundsH, dtype=float ).ravel()
			self.boundsH = [ boundsH.min(), boundsH.max() ]
			self.Associate(
				h = shapeH( self.stimulationIntensities, self.Magnitudes( self.boundsH ), robust=robust, excuses=self.excuses, **self.descriptors ),
			)
		return self
	
	def Plot( self, **kwargs ):
		"""
		Assuming you have just performed `self.Fit()`, plot the resulting
		`self.m` and `self.h` together on the same axes (requires the
		third-party package `matplotlib`).
		
		You can hover the mouse pointer over each data-point to see the
		corresponding waveform.
		"""
		self.overlayAxes = None
		self.lines = []
		if self.m: self.m.Plot( **kwargs ); kwargs.update( hold=True )
		if self.h: self.h.Plot( **kwargs )
		return self
	
	@property
	def axes( self ):
		for key in list( self.clients.keys() ):
			attrName, client = self.clients[ key ]
			client = client() # de-reference weak ref
			if client is None: self.clients.pop( key )
			elif getattr( client, 'axes', None ): return client.axes
		return None
		
	def PlotHoverCallback( self, event, indices ):
		if self.waveforms is None: return
		
		parentAxes = self.axes # NB: cannot just use event.inaxes
		if parentAxes is None or not parentAxes.get_visible(): return
		
		from matplotlib.backend_tools import Cursors
		canvas = parentAxes.figure.canvas
		if not canvas.widgetlock.locked():
			canvas.set_cursor( Cursors.POINTER if indices is None else Cursors.SELECT_REGION )
		
		box = parentAxes.get_position()
		try: x, y = parentAxes.transAxes.inverted().transform( [ event.x, event.y ] )
		except: corner = 'NW'
		else:   corner = ( 'N' if y <= 0.5 else 'S' ) + ( 'E' if x <= 0.5 else 'W' )
		smallerBox = box.shrunk( 0.5, 0.5 ).anchored( corner, box )
		overlay = self.overlayAxes
		if overlay is None and indices:
			overlay = self.overlayAxes = parentAxes.figure.add_axes( smallerBox )
			overlay.patch.set( alpha=0.5 )
			overlay.spines['left'].set( color='none' )
			overlay.spines['right'].set( color='none' )
			overlay.spines['top'].set( color='none' )
			overlay.spines['bottom'].set( position='center', alpha=overlay.patch.get_alpha() )
			self.lines = overlay.plot( self.timeBase, self.waveforms )
			overlay.set( ylim=numpy.array( [ -1, 1 ] ) * numpy.abs( self.waveforms ).max() )
			overlay.set( xticks=[], yticks=[] )
			from matplotlib.patches import Rectangle
			if getattr( self, 'boundsM', None ): overlay.add_patch( Rectangle( [ min( self.boundsM ), 0.0 ], width=numpy.diff( self.boundsM ).flat[ 0 ], height=1.0, transform=overlay.get_xaxis_transform(), facecolor='C0', alpha=0.2, zorder=-1 ) )
			if getattr( self, 'boundsH', None ): overlay.add_patch( Rectangle( [ min( self.boundsH ), 0.0 ], width=numpy.diff( self.boundsH ).flat[ 0 ], height=1.0, transform=overlay.get_xaxis_transform(), facecolor='C1', alpha=0.2, zorder=-1 ) )
		if not overlay: return
		for lineIndex, line in enumerate( self.lines ):
			if indices and lineIndex in indices: line.set( linewidth=3, color='m', alpha=0.8, zorder=1 )
			else: line.set( linewidth=1, color='k', alpha=0.5, zorder=0 )
		if indices is None: overlay.set( visible=False )
		#if not indices: overlay.set( visible=False )
		if indices: overlay.set( visible=True )
		if overlay.get_visible():
			updatePosition = abs( overlay.get_position().width / parentAxes.get_position().width - 0.5 ) > 0.1
			x, y = overlay.transAxes.inverted().transform( [ event.x, event.y ] )
			x, y = abs( x - 0.5 ), abs( y - 0.5 )
			if min( x, y ) < 0.55 and max( x, y ) < 0.65: updatePosition = True
			if updatePosition: overlay.set( position=smallerBox )
		return True
	
	def H2M( self, boundsH=None, plot=False ):
		"""
		Experimental method for inferring M-wave bounds given H-wave
		bounds and the assumption of isomorphism (NB: requires prior
		removal of stimulation artifact).
		"""
		if boundsH is None: boundsH = self.boundsH
		boundsH = numpy.asarray( boundsH, dtype=float ).ravel()
		hWaveforms = self.Excerpt( boundsH )
		# TODO: at this point we could do some ICA or something to isolate the H from contaminants
		#       For now, let's just sort the trials in descending order of magnitude and average the first few
		hReordering = numpy.argsort( -numpy.abs( hWaveforms ).mean( axis=0 ) )
		firstOrderedHWaveformToAverage = 2
		numberOfHWaveformsToAverage = 8
		canonicalH = hWaveforms[ :, hReordering[ firstOrderedHWaveformToAverage : firstOrderedHWaveformToAverage + numberOfHWaveformsToAverage ] ].mean( axis=1 )
		numberOfMWaveformsToAverage = 8
		mReordering = numpy.argsort( self.stimulationIntensities )
		fullWaveformAtMMax = self.waveforms[ :, mReordering[ -numberOfMWaveformsToAverage: ] ].mean( axis=1 )
		mStartInSamples = numpy.argmax( numpy.correlate( fullWaveformAtMMax, canonicalH ) )
		boundsM = self.timeBase[ [ mStartInSamples, mStartInSamples + canonicalH.size - 1 ] ]
		if plot:
			mmask = self.Excerpt( boundsM, 'mask' )
			#magnitude = lambda x: numpy.abs( x ).mean()
			magnitude = numpy.ptp
			factor = magnitude( fullWaveformAtMMax[ mmask ] ) / magnitude( canonicalH )
			import matplotlib.pyplot as plt
			axes = plt.gcf() if isinstance( plot, bool ) else plt.figure( plot ) if isinstance( plot, int ) else plot
			if isinstance( axes, plt.Figure ): axes = axes.gca()
			title = axes.get_title()
			axes.cla()
			axes.plot( self.timeBase, self.waveforms, color='C0', alpha=0.3 )
			axes.plot( self.timeBase[ mmask ], canonicalH * factor, color='C1' )
			axes.set_title( title )
		return boundsM, boundsH
