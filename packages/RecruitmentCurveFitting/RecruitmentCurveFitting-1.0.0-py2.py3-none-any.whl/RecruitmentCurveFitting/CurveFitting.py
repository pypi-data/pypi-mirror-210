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
This module provides the `Curve` class, which is a generic wrapper
around `scipy.optimize.curve_fit` that provides object-orientation,
indexing of parameters by name, and the option of fixing parameter
values.

Third-party requirements are:

- `numpy`
- `scipy` (optimization uses `scipy.optimize.curve_fit`)
- `matplotlib` if you want to plot
"""

__all__ = [
	'Parameter',
	'Curve',
	'SavePDF',
]

import sys
import copy
import inspect
import weakref

import numpy; from numpy import nan, inf
# Need scipy.optimize and matplotlib.pyplot too (imported inside relevant methods)

class Parameter( object ):
	"""
	Helper class for `Curve`. Use the `@Parameter.Setup` class decorator
	when defining your `Curve` subclasses.
	"""
	def __init__( self, name, index, min=-inf, max=+inf, initialValue=nan ):
		self.name = name
		self.index = index
		self.initialValue = initialValue
		self.finalValue = None
		self.fixedValue = None
		self.min = min
		self.max = max
	def __repr__( self ):
		s = object.__repr__( self )
		s += ': %s' % ( ', '.join( '%s=%r' % ( k, v ) for k, v in self.__dict__.items() ) )
		return s 
	@property
	def isAtMin( self, value=None, tolerance=1e-10 ):
		return ( self.finalValue if value is None else value ) - tolerance < self.min
	@property
	def isAtMax( self, value=None, tolerance=1e-10 ):
		return ( self.finalValue if value is None else value ) + tolerance > self.max
	@property
	def isFixed( self ):
		return self.fixedValue is not None
	
	def GetFixedValue( self, **kwargs ):
		x = self.fixedValue
		if callable( x ): x = x( **kwargs )
		return x
	
	@staticmethod
	def Setup( curveClass ):
		nameStartIndex = 1 if isinstance( curveClass.__dict__[ 'Evaluate' ], staticmethod ) else 2
		try:    names = inspect.getfullargspec( curveClass.Evaluate ).args[ nameStartIndex: ]
		except: names = inspect.getargspec(     curveClass.Evaluate ).args[ nameStartIndex: ]
		curveClass._PARAMS = []
		for index, name in enumerate( names ):
			while hasattr( curveClass, name ): name += '_'
			p = Parameter( name=name, index=index )
			curveClass._PARAMS.append( p )
			setattr( curveClass, name, property( fget=lambda self, i=index: self._PARAMS[ i ], doc=name + ' parameter' ) )
		return curveClass
	
class Curve( object ):
	"""
	This is an abstract base class. Subclass it, and implement
	your own methods. In the following example, the parameter names
	`m` and `c` are arbitrary and can be renamed/removed/extended.
	The `@Parameter.Setup` class decorator ensures that the subclass
	has `Parameter` attributes whose names match the names of the
	input arguments of `.Evaluate()` (after `x`).
	
	Optimization uses `scipy.optimize.curve_fit()` which by default
	uses `method='trf'` (Trust Region Reflective algorithm) if are
	bounds, and `method='lm'` (Levenberg-Marquardt algorithm) if not
	(but note `method='lm'` is also unsuitable when the number of
	points is less than the number of parameters).
	
	Trivial example::

	    from CurveFitting import Curve, Parameter
	    
	    @Parameter.Setup
	    class MyModel( Curve ):	
	        def Evaluate( self, x, m, c ):  # parameters as named arguments
	            '''Linear fit y = m * x + c'''
	            return m * x + c
	        
	        def Initialize( self, x, y ):
	            return dict( m=1.0, c=0.0 )  # initial parameter values
	        
	        def SetBounds( self ): # optional
	            self.m.min = 0.0   # disallow negative slopes.
	        		
	    z = MyModel(x=[1,2,3], y=[4,7,8])
	    z.Fit()
	    z.Plot(label=str(z.pdict))
	    
	    # And now re-do the fit with a fixed offset
	    z.c.fixedValue = 1.5
	    z.Fit().Plot( data=False, hold=True, label=str(z.pdict) )
	    from matplotlib.pyplot import legend; legend()
	"""

	_PARAMS = []
	def __init__( self, x, y=(), robust=False, fix=None, excuses=None, **descriptors ):
		"""
		Args:
		    robust (bool):
		        set the default mode for `.Fit()`:  soft-L1 loss if `True`,
		        L2 loss otherwise.
		    
		    fix (dict):
		        names and values of parameters to fix.
		    
		    excuses (list, tuple):
		        an optional sequence of strings detailing reasons why
		        this dataset is disqualified from ordinary analysis. If
		        non-empty, curve-fitting will be skipped for this dataset.
		    
		    **descriptors:
		        any further keyword arguments are stored in the
		        `self.descriptors` dictionary to distinguish this dataset
		        from other datasets (experimental conditions, etc).
		"""
		if isinstance( x, Curve ):
			other = x
			self._PARAMS = copy.deepcopy( other._PARAMS ) # includes information from `fix`
			self.fittingException = other.fittingException
			self.x = other.x.copy()
			self.y = other.y.copy()
			self.robust = other.robust
			self.excuses = copy.deepcopy( other.excuses )
			self.descriptors = copy.deepcopy( other.descriptors )
		else:
			self._PARAMS = copy.deepcopy( self._PARAMS ) # take an instance-specific copy of the class-universal list of Parameter instances
			self.fittingException = None
			self.x = numpy.asarray( x ).ravel()
			self.y = numpy.asarray( y ).ravel()
			self.robust = robust
			if not fix: fix = {}
			for name, value in fix.items(): # NB: for some reason this loop was originally in between the "skipping" verbosity (which would abort and return early) and the "fitting" verbosity
				param = getattr( self, name, None )
				if not isinstance( param, Parameter ): raise AttributeError( 'cannot fix %s - no such parameter' % name )
				param.fixedValue = value
			self.excuses = list( excuses ) if excuses else []
			self.descriptors = descriptors
			
			if self.excuses:
				print( '#  %s  - skipping (%s)' % ( self.Describe(), ', '.join( self.excuses ) ) )
			elif self.x.size > 0 and self.y.size > 0:
				print( '#  %s  - fitting %s' % ( self.Describe(), self.__class__.__name__ ) )
				self.SetBounds()
				self.Guess()
				self.Fit()
				

	def __repr__( self ):
		s = object.__repr__( self )
		desc = self.Describe()
		if desc: s += ': %s' % desc
		return s
	
	@property
	def _FREEPARAMS( self ):
		return [ param for param in self._PARAMS if not param.isFixed ]
		
	@property
	def p0( self ): return numpy.array( [ param.initialValue for param in self._FREEPARAMS ] )
	@p0.setter
	def p0( self, values ):
		if isinstance( values, dict ): values = [ values[ param.name ] for param in self._FREEPARAMS ]
		values = numpy.asarray( values ).flat
		if len( values ) != len( self._FREEPARAMS ): raise ValueError( 'mismatched parameter set' )
		for value, param in zip( values, self._FREEPARAMS ): param.initialValue = value
			
	@property
	def paramNames( self ): return [ param.name for param in self._PARAMS ]

	@property
	def p( self ): return numpy.array( [ param.finalValue for param in self._FREEPARAMS ] )
	@p.setter
	def p( self, values ):
		if isinstance( values, dict ): values = [ values[ param.name ] for param in self._FREEPARAMS ]
		values = numpy.asarray( values ).flat
		if len( values ) != len( self._FREEPARAMS ): raise ValueError( 'mismatched parameter set' )
		for value, param in zip( values, self._FREEPARAMS ): param.finalValue = value
	
	@property
	def min( self ): return numpy.array( [ param.min for param in self._FREEPARAMS ] )
	@property
	def max( self ): return numpy.array( [ param.max for param in self._FREEPARAMS ] )

	@property
	def pdict( self ): return self.ResolveParameters( asDict=True )

	def Describe( self, associator='=', delimiter=', ', wrap=None ):
		items = [ '%s%s%r' % ( k, associator, v ) for k, v in self.descriptors.items() if not k.startswith( '_' ) ]
		if not wrap: return delimiter.join( items )
		lines = [ '' ]
		while items:
			item = items.pop( 0 )
			candidate = lines[ -1 ] + item
			if items: candidate += delimiter
			if not lines[ -1 ] or len( candidate ) <= wrap: lines[ -1 ] = candidate
			else: lines.append( item )
		return '\n'.join( lines )
	
	def ResolveParameters( self, freeParamSequence=None, asDict=False ):
		if freeParamSequence is None or len( freeParamSequence ) == 0: freeParamSequence = self.p
		freeParamDict = dict( zip( [ param.name for param in self._FREEPARAMS ], freeParamSequence ) )
		fullParamSequence = [ param.GetFixedValue( **freeParamDict ) if param.isFixed else freeParamDict[ param.name ] for param in self._PARAMS ]
		if not asDict: return fullParamSequence
		fullParamDict = dict( zip( [ param.name for param in self._PARAMS ], fullParamSequence ) )
		return fullParamDict
		
		
	def Forward( self, x, *p ):
		# In the absence of `*p` args, `self.Forward()` uses `self.p`
		# `self.p0` and `self.p` should return only free parameters,
		# and `self.Forward()` should take only free parameters (if any),
		# even though `Evaluate()` takes all.
		return self.Evaluate( x, *self.ResolveParameters( p ) )
		
	def SetBounds( self ):
		pass

	def Guess( self ):
		self.p0 = self.Initialize( self.x, self.y )
		tooSmall = [ param.name for param in self._FREEPARAMS if param.initialValue < param.min ]
		tooBig   = [ param.name for param in self._FREEPARAMS if param.initialValue > param.max ]
		if tooSmall: print( '#    initial value too small: %s' % ', '.join( tooSmall ) )
		if tooBig:   print( '#    initial value too big: %s'   % ', '.join( tooBig   ) )
		for param in self._PARAMS:
			if not param.isFixed: param.initialValue = max( param.min, min( param.max, param.initialValue ) )
		fullParamDict = self.ResolveParameters( self.p0, asDict=True )
		for param in self._PARAMS:
			if param.isFixed: param.initialValue = fullParamDict[ param.name ]
		return self
		
	def Fit( self, p0=None, robust=None ):
		"""
		Uses soft-L1 loss if `robust=True`, L2 loss otherwise.
		"""
		self.fittingException = None
		if robust is not None: self.robust = robust
		if p0 is not None: self.p0 = p0
		p0 = self.p0
		bounds = (
			numpy.array( [ param.min for param in self._FREEPARAMS ] ),
			numpy.array( [ param.max for param in self._FREEPARAMS ] ),
		)
		if bounds[ 0 ].max() == -inf and bounds[ 1 ].min() == +inf: bounds = ( -inf, +inf )
		try:
			import scipy.optimize
			self.p, _ = scipy.optimize.curve_fit(
				self.Forward, self.x, self.y, p0,
				bounds=bounds, method='trf',
				loss='soft_l1' if self.robust else 'linear',
			)
			#By default, scipy would use method='trf' (Trust Region Reflective algorithm) if
			# there are bounds, and method='lm' (Levenberg-Marquardt algorithm) if not (but
			# note method='lm' is also unsuitable when number of points < number of params).
		except:
			self.fittingException = cls, exc, tb = sys.exc_info()
			print( '#    failed - %s: %s' % ( cls.__name__, exc ) )
			for param in self._PARAMS: param.finalValue = nan
		else:
			fullParamDict = self.ResolveParameters( self.p, asDict=True )
			for param in self._PARAMS:
				if param.isFixed: param.finalValue = fullParamDict[ param.name ]
			atMin = [ param.name for param in self._FREEPARAMS if param.isAtMin ]
			atMax = [ param.name for param in self._FREEPARAMS if param.isAtMax ]
			if atMin: print( '#    hit lower bound: %s' % ', '.join( atMin ) )
			if atMax: print( '#    hit upper bound: %s' % ', '.join( atMax ) )
		return self
			
	def Plot( self, data=True, guess=False, fit=True, markX=None, markY=None, title=False, grid=None, xlabel=None, ylabel=None, hold='auto', figure=None, axes=None, **kwargs ):
		import matplotlib.pyplot as plt
		axes = plt.gcf() if axes is None else plt.figure( axes ) if isinstance( axes, int ) else axes
		if isinstance( axes, plt.Figure ): axes = axes.gca()
		
		figure = axes.figure
		self.axes = axes
		xlim = self.x.min(), self.x.max()
		x = numpy.linspace( xlim[ 0 ], xlim[ -1 ], 200 )
		if hold in [ None, 'auto' ]: hold = not data
		if not hold: axes.cla()
		hGuess = hFit = hData = None
		if self.excuses:
			if not hold: axes.set( xticks=[], yticks=[] )
			axes.text( 0.5, 0.5, '\n'.join( self.excuses ), transform=axes.transAxes, ha='center', va='center' )
			data = guess = fit = mark = None
		if guess:
			props = dict(); props.update( kwargs, marker=None, linestyle='--' )
			if fit or data: props.pop( 'label', None )
			hGuess, = h, = axes.plot( x, self.Forward( x, *self.p0 ), **props )
			kwargs.setdefault( 'color', h.get_color() )
		if fit:
			props = dict(); props.update( kwargs, marker=None )
			if self.fittingException:
				m = 0.1
				props.update( linewidth=10, alpha=0.5 )
				h, = axes.plot( [ m, 1-m, nan, 1-m, m ], [ m, 1-m, nan, m, 1-m ], transform=axes.transAxes, **props )
			else:
				hFit, = h, = axes.plot( x, self.Forward( x, *self.p ), **props )
			kwargs.setdefault( 'color', h.get_color() )
			
		self.hData = None
		if data and self.x.size and self.y.size:
			props = dict( marker='o', alpha=0.75 ); props.update( kwargs, linestyle='none' )
			if fit: props.pop( 'label', None )
			hData, = h, = axes.plot( self.x, self.y, **props )
			
			self.hData = hData	
			self._mpl_disconnect()
			wrSelf = weakref.ref( self )
			def hover( event ):
				curve = wrSelf()
				if not curve: return
				if curve.axes not in curve.axes.figure.axes: return curve._mpl_disconnect() # TODO: is there a better way of
				if curve.hData not in curve.axes.lines: return curve._mpl_disconnect()      #       asking "is it still there?"
				#if event.inaxes != curve.axes: return # this lets any overlaid axes block the event
				hit, _ = curve.axes.contains( event )
				if hit:
					hit, indices = curve.hData.contains( event )
					indices = tuple( indices[ 'ind' ] )
				else:
					indices = None
				if getattr( curve, 'highlightedIndices', None ) == indices: return
				curve.highlightedIndices = indices
				if curve.PlotHoverCallback( event, indices ): curve.axes.figure.canvas.draw_idle()
			self.mpl_connect_id = figure.canvas.mpl_connect( 'motion_notify_event', hover )
		
		if markX is not None and not isinstance( markX, ( tuple, list, numpy.ndarray ) ): markX = [ markX ]
		if markY is not None and not isinstance( markY, ( tuple, list, numpy.ndarray ) ): markY = [ markY ]
		maxX, maxY = self.Find( 'max' )
		
		if markX is not None:
			markX = [ maxX if x == 'max' else x  for x in ( markX.flat if isinstance( markX, numpy.ndarray ) else markX ) ]
			markX = numpy.asarray( markX ).ravel().tolist()
			props = dict(); props.update( kwargs, marker=None, linestyle=':' )	
			for x in markX:
				#if not min( xlim ) <= x <= max( xlim ): continue
				axes.plot( [ x, x ], [ 0.0, 1.0 ], transform=axes.get_xaxis_transform(), **props )
		if markY is not None:
			markY = [ maxY if y == 'max' else y  for y in ( markY.flat if isinstance( markY, numpy.ndarray ) else markY ) ]
			markY = numpy.asarray( markY ).ravel().tolist()
			props = dict(); props.update( kwargs, marker=None, linestyle=':' )	
			#ylim = axes.get_ylim()
			for y in markY:
				#if not min( ylim ) <= y <= max( ylim ): continue
				axes.plot( [ 0.0, 1.0 ], [ y, y ], transform=axes.get_yaxis_transform(), **props )
		
		if grid is not None: axes.grid( grid )
		if xlabel is not None: axes.set_xlabel( xlabel )
		if ylabel is not None: axes.set_ylabel( ylabel )
		if title: axes.set_title( title if isinstance( title, str ) else self.Describe( ' ', wrap=45 ), fontsize=7, fontweight='bold' )
		return self
		
	def _mpl_disconnect( self ):	
		axes = getattr( self, 'axes', None )
		connection = getattr( self, 'mpl_connect_id', None )
		if axes is not None and connection is not None:
			try: axes.figure.canvas.mpl_disconnect( connection )
			except: pass
			
	def __del__( self ):
		self._mpl_disconnect()
	
	def PlotHoverCallback( self, event, indices ):
		"""
		Overshadow this in your subclass if you want to respond to
		the mouse hovering over one or more plotted data-points (`indices`
		will be a list of indices to the relevant data-points).
		
		The function should return `True` when you want the matplotlib
		drawing engine to update the figure.
		"""
		pass
		
	def Find( self, objective='max', xLimits=None ):
		if xLimits is None: xmin, xmax = self.x.min(), self.x.max()
		else: xmin, xmax = min( xLimits ), max( xLimits )
		if isinstance( objective, ( float, int ) ):
			targetValue, objective = objective, lambda y: numpy.abs( y - targetValue )
		elif objective == 'min': objective = lambda y: y
		elif objective == 'max': objective = lambda y: -y
		elif not callable( objective ): raise ValueError( 'objective %r is of unrecognized type' % objective )
		for iteration in range( 3 ):
			x = numpy.linspace( xmin, xmax, 1000 )
			y = self.Forward( x )
			f = objective( y )
			try: indexOfYMax = numpy.nanargmin( f )
			except: return nan, nan
			xmin = x[ max( 0, indexOfYMax - 1 ) ]
			xmax = x[ min( x.size - 1, indexOfYMax + 1 ) ]
		return x[ indexOfYMax ], y[ indexOfYMax ]

	@staticmethod
	def Evaluate( x, *params ): raise TypeError( 'cannot use the abstract base class in this way - subclass must define method self.Evaluate(x, ...) with named parameters' )
	@staticmethod
	def Initialize( x, y ): raise TypeError( 'cannot use the abstract base class in this way - subclass must define method self.Initialize(x, y)' )

def SavePDF( filename, figures='all' ):
	import matplotlib.pyplot as plt
	if figures == 'all': figures = plt.get_fignums()
	from matplotlib.backends.backend_pdf import PdfPages
	with PdfPages( filename ) as pdf:
		for figure in figures: pdf.savefig( figure )
		
