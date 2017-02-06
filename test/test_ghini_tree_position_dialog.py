# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from PyQt4.QtGui import QDialogButtonBox, QDialog
from ghini_tree_position_dialog import DistanceMatrixToCoordsDialog
from utilities import get_qgis_app

__author__ = 'mario@anche.no'
__date__ = '2017-01-04'
__copyright__ = 'Copyright 2017, Mario Frasca'

QGIS_APP = get_qgis_app()


class DistanceMatrixToCoordsDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = DistanceMatrixToCoordsDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok_disabled(self):
        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        self.assertEqual(button.isEnabled(), False)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, 0)

    def test_dialog_ok_enabled(self):
        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.setEnabled(True)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        self.assertEqual(button.isEnabled(), True)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

if __name__ == "__main__":
    suite = unittest.makeSuite(DistanceMatrixToCoordsDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
