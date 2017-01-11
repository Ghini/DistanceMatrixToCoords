# -*- coding: utf-8 -*-
"""/***************************************************************************
 DistanceMatrixToCoords
                                 A QGIS plugin
 Calculate point positions in 2D given a few reference points and a matrix
 of mutual horizontal distances
                             -------------------
        begin                : 2017-01-04
        copyright            : (C) 2017 by Mario Frasca
        email                : mario@anche.no
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.

"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DistanceMatrixToCoords class from file DistanceMatrixToCoords.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ghini_tree_position import DistanceMatrixToCoords
    return DistanceMatrixToCoords(iface)
