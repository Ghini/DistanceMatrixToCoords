# -#- coding: utf-8 -#-
#
# Copyright 2017 Mario Frasca <mario@anche.no>.
#
# This file is part of DistanceMatrixToCoordsDialog
#
# DistanceMatrixToCoordsDialog is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# DistanceMatrixToCoordsDialog is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with DistanceMatrixToCoordsDialog. If not, see
# <http://www.gnu.org/licenses/>.
#
# dialog classes definition, from the Q4 ui sources
#
# the __init__ method in these classes call self.setupUi(self), which sets
# up the user interface from the designer file.  When this is done, you can
# use autoconnect slots, read more about this looking for
# widgets-and-dialogs-with-auto-connect in
# http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html

import os

from PyQt4 import QtGui, uic

from utils import Heap
from utils import get_distances_from_csv
from utils import utm_zone_proj4
from utils import extrapolate_coordinates
from utils import compute_minimal_distance_transformation
from utils import place_initial_three_points
from utils import rigid_transform_points


class DistanceMatrixToCoordsDialog(
        QtGui.QDialog, uic.loadUiType(os.path.join(
            os.path.dirname(__file__),
            'ghini_tree_position_dialog_base.ui'))[0]):
    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(DistanceMatrixToCoordsDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.lineEdit.clear()
        self.pushButton.clicked.connect(self.select_input_file)

    def run(self):
        """Run method that performs all the real work"""

        # work only on vector layers (where 0 means points)
        layers = [l for l in self.iface.legendInterface().layers()
                  if l.type() == l.VectorLayer and l.geometryType() == 0]
        self.comboBox.addItems([l.name() for l in layers])

        # show the dialog
        self.show()
        # Run the dialog event loop
        result = self.exec_()

        # See if OK was pressed
        if result:
            # get reference points from the layer
            layer = layers[self.comboBox.currentIndex()]

            # where are we in the world and which UTM system do we use to
            # perform our metric operations?
            layer_to_wgs84 = QgsCoordinateTransform(
                layer.crs(),
                QgsCoordinateReferenceSystem(4326))
            # use WGS84 position of first feature to select local UTM
            f1 = layer.getFeatures().next()
            local_utm = QgsCoordinateReferenceSystem()
            local_utm.createFromProj4(utm_zone_proj4(
                layer_to_wgs84(f1.geometry().asPoint())))
            # define forward and backward transformations
            transf = QgsCoordinateTransform(layer.crs(), local_utm)
            back_transf = QgsCoordinateTransform(local_utm, layer.crs())

            # populate 'points' dict with projected coordinates
            points = {}
            for feature in layer.getFeatures():
                # we work with local utm projection
                easting_northing = transf.transform(
                    feature.geometry().asPoint())
                point_id = feature['id']
                points[point_id] = {'id': point_id,
                                    'coordinates': easting_northing}

            # get distances from csv file, and compute connectivity to
            # referenced points
            with open(self.lineEdit.text()) as f:
                distances = get_distances_from_csv(f, points)

            # compute missing coordinates
            extrapolate_coordinates(points, distances)

            # remember editable status
            wasEditable = layer.isEditable()
            # force editable if not already editable
            if not wasEditable:
                layer.startEditing()

            fields = layer.fields()

            featureList = []
            # now add the computed points to the layer
            for p in [p for p in points.values() if p['computed']]:
                x, y = p['coordinates']
                layerPoint = back_transf.transform(QgsPoint(x, y))
                feature = QgsFeature(fields)
                feature.setGeometry(QgsGeometry.fromPoint(layerPoint))
                feature['id'] = p['id']
                featureList.append(feature)

            # bulk-add features to data provider associated to layer
            (err, ids) = layer.dataProvider().addFeatures(featureList)
            # set selection to new features - simplifies removing them in
            # case user does not like the results
            layer.setSelectedFeatures([i.id() for i in ids])

            # some feedback about the result
            still_missing = [p for p in points.values()
                             if not p.get('coordinates')]
            # TODO show the user which points we did not compute
            from qgis.gui import QgsMessageBar
            self.iface.messageBar().pushMessage(
                "Info",
                "success? %s; features added: %s; impossible to add: %s" % (
                    err, len(ids), len(still_missing)),
                level=QgsMessageBar.INFO)

            # commit changes only if layer was not editable
            if not wasEditable:
                layer.commitChanges()

    def select_input_file(self):
        filename = QFileDialog.getOpenFileName(
            self.dlg, "Select distances file ", "", '*.csv')
        self.lineEdit.setText(filename)


class GpsAndDistancesToAdjustedGpsDialog(
        QtGui.QDialog, uic.loadUiType(os.path.join(
            os.path.dirname(__file__),
            'ghini_correct_GPS_dialog_base.ui'))[0]):
    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(GpsAndDistancesToAdjustedGpsDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface

    def run(self):
        # show the dialog
        self.show()
        # Run the dialog event loop
        result = self.exec_()
