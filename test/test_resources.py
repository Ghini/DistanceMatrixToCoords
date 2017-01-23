# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest

from PyQt4.QtGui import QIcon

__author__ = 'mario@anche.no'
__date__ = '2017-01-04'
__copyright__ = 'Copyright 2017, Mario Frasca'


class DistanceMatrixToCoordsDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icons_png(self):
        """Test our icons work."""
        path = ':/plugins/DistanceMatrixToCoords/ghini-24.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())
        path = ':/plugins/DistanceMatrixToCoords/gpsadjust.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())
        path = ':/plugins/DistanceMatrixToCoords/ptsadd.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())
