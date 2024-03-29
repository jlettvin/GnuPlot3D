#! /usr/bin/env python

###############################################################################
__date__       = "20130301"
__author__     = "jlettvin"
__maintainer__ = "jlettvin"
__email__      = "jlettvin@gmail.com"
__copyright__  = "Copyright(c) 2013 Jonathan D. Lettvin, All Rights Reserved"
__license__    = "GPLv3"
__status__     = "Production"
__version__    = "0.0.1"

"""
GunuPlot3D.py

Implements a dynamic scientific 3D visualizer class.

Copyright(c) 2013 Jonathan D. Lettvin, All Rights Reserved"

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

See __main__ for an example of use.

TODO: keyboard input requires changing focus back to window of launching app.
"""

import os
import sys
import subprocess as sp

from scipy import *

#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
class GnuPlot3D(dict):
    """
    This class implements the context pattern for running gnuplot as a
    slave process for displaying generic gnuplot data.
    Specializations are implemented for handling particles in 3D.
    """

    #TODO Find a better way of discovering executable rather than fixed.
    command  = { #TODO Fill these in for other OSs
        'Linux': "/usr/local/bin/gnuplot",
               }
    terminal = { #TODO Fill these in for other OSs
        'Linux': "wxt",
               }

    #**************************************************************************
    def __init__(self, **kw):
        """
        Initialize a context with specializations if offered.

        Assert that parameters and values are reasonable.
        """
        platform = os.uname()[0]
        self['gnuplot'] = GnuPlot3D.command .get(platform, "missing")
        self['term'   ] = GnuPlot3D.terminal.get(platform, "missing")
        self['width'  ] = 300   # Equilateral by experiment on linux.
        self['height' ] = 400   # Equilateral by experiment on linux.
        self['xrange' ] = [-1.0, +1.0]
        self['yrange' ] = [-1.0, +1.0]
        self['zrange' ] = [-1.0, +1.0]
        self['persist'] = True
        self.update(kw)
        for INTEGER in ['width', 'height']:
            assert isinstance(self[INTEGER], int)
        for STRING  in ['gnuplot', 'term']:
            instance = self[STRING]
            assert isinstance(instance , str)
            assert instance != "missing"
        for LIST in ['xrange', 'yrange', 'zrange']:
            instance = self[LIST]
            assert isinstance(instance, list)
            assert len(instance) == 2
            lo, hi = instance
            assert isinstance(lo, int) or isinstance(lo, float)
            assert isinstance(hi, int) or isinstance(hi, float)
        for FLAG in ['persist',]:
            assert isinstance(self[FLAG], bool)

    #**************************************************************************
    def __enter__(self):
        """
        Open the pipe to make a context.
        """
        self.pipe = sp.Popen(
                [self['gnuplot'],],
                stdin=sp.PIPE,
                stdout=sp.PIPE,
                stderr=sp.PIPE)
        return self

    #**************************************************************************
    def __exit__(self, aType, aValue, aTraceback):
        """
        Close the pipe to leave the context.
        Avoid killing the window if persistence is desirable.
        """
        if not self['persist']:
            try:
                self.pipe.kill()
            except OSError:
                pass

    #**************************************************************************
    def unitcube(self): # Initialize ranges
        """
        Limit displayed 3D data to within a unit radius cube around (0,0,0).
        """
        for line in [   # Set ranges for all 3 axes (remember the newline).
                "set %s%s\n" % (name, pair)
                for name, pair in
                [(name,str(self[name]).replace(',',':'))
                    for name in ['xrange','yrange','zrange']]]:
            #print line,
            self.send(line)
        for line in [   # Set the terminal type and window size.
                ("set terminal %s size %d,%d\n" %
                    (self['term'], self['width'], self['height']))]:
            self.send(line)

    #**************************************************************************
    def send(self, line):
        """
        Send a command to gnuplot.
        """
        self.pipe.stdin.write(line)

    #**************************************************************************
    def recv(self):
        """
        Recv responses from gnuplot.
        """
        return self.pipe.stdout.read()

    #**************************************************************************
    def points(self, data):
        """
        Send individual 3-tuple coordinates to gnuplot for display.
        Finish with the "e" for end gnuplot requests.
        """
        self.send("splot '-' using 1:2:3 with points lt -1 ps 0.5 pt 7\n")
        for x,y,z in data: self.send("%f %f %f\n" % (x,y,z))
        self.send("e\n")

#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
if __name__ == "__main__":
    """
    test illustrates a single point traversing from one cube corner to another.
    """

    #**************************************************************************
    def test():
        with GnuPlot3D() as gp:
            gp.unitcube()
            for j in range(5):
                print j
                for i in arange(-1.0,+1.0,1e-2):
                    gp.points([(i,i,i)])

    #()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()()
    test()

###############################################################################
# GnuPlot3D.py <EOF>
###############################################################################
