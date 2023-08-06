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

__all__ = [ 'Cite' ]
import os, sys, ast
from . import RecruitmentCurves
__doc__ = RecruitmentCurves.__doc__
__all__ += RecruitmentCurves.__all__
from .RecruitmentCurves import *

__version__ = '1.0.0'

CITATION_INFO = """
If you use this software in your research, your report should cite
the article in which this approach was introduced, as follows:

- McKinnon ML, Hill NJ, Carp JS, Dellenbach B & Thompson AK (2023).
  Automated identification of EMG responses evoked by peripheral
  nerve stimulation: quantitative effects on critical parameters
  of diagnostic and closed-loop therapeutic applications.
  @JOURNAL@ @NUMBER@(@VOLUME@):@PAGES@
  @DOI@
    
The corresponding BibTeX entry is::

    @article{mckinnonhill2023,
        author  = {McKinnon, Michael L. and Hill, N. Jeremy  and  Carp, Jonathan S.  and Dellenbach, Blair and Thompson, Aiko K.},
        title   = {Automated Identification of {EMG} Responses Evoked by Peripheral Nerve Stimulation: Quantitative Effects on Critical Parameters of Diagnostic and Closed-Loop Therapeutic Applications},
        journal = {xxxx},
        volume  = {x},
        number  = {x},
        pages   = {xx-xx},
        month   = {xxx},
        year    = {2023},
        date    = {2023-xx-xx},
        doi     = {xxx/xxxx},
        url     = {https://doi.org/xxx/xxxx},
    }
"""

def Cite( command=None, prefix='', stream=None ):
	"""
=============================================================
This is the RecruitmentCurveFitting package version @VERSION@
by Jeremy Hill, running in Python @PYVERSION@.

@CITATION_INFO@

To acknowledge this message and prevent it from being displayed
every time you import the package::

	from RecruitmentCurveFitting import Cite
	Cite('agree')

To refer back to this information again, simply call `Cite()`.
=============================================================
	"""
	if isinstance( command, str ):
		command = command.lower()
		if command in [ 'on_import' ]:
			if not Preferences().get( 'silent', False ):
				command = None
		elif command in [ 'agree', 'acknowledge', 'ok' ]:
			Preferences( silent=True )
		else:
			raise ValueError( 'unrecognized command option' )
	if command is None:
		if stream is None: stream = sys.stdout
		stream.write( '\n'.join( prefix + line for line in Cite.__doc__.split( '\n' ) ) + '\n' )
		try: stream.flush()
		except: pass
def Preferences( **kwargs ):
	prefsFile = os.path.expanduser( '~/.RecruitmentCurveFitting' )
	try: prefs = ast.literal_eval( open( prefsFile, 'rt' ).read() )
	except: prefs = {}
	if kwargs:
		prefs.update( kwargs )
		prefsText = '{\n' + ''.join( '\t%r : %r,\n' % item for item in prefs.items() ) + '}\n'
		prefs = ast.literal_eval( prefsText )
		open( prefsFile, 'wt' ).write( prefsText )
	return prefs
Cite.__doc__ = Cite.__doc__.rstrip().replace( '@VERSION@', __version__ ).replace( '@PYVERSION@', '%s.%s' % ( sys.version_info.major, sys.version_info.minor ) ).replace( '@CITATION_INFO@', CITATION_INFO.strip() )
Cite( 'on_import', stream=sys.stderr )
