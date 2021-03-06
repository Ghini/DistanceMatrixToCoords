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
from PyQt4.QtGui import QFileDialog, QDialogButtonBox

from utils import Heap
from utils import get_distances_from_csv
from utils import utm_zone_proj4
from utils import extrapolate_coordinates
from utils import compute_minimal_distance_transformation
from utils import place_initial_three_points
from utils import rigid_transform_points

from qgis.core import (
    QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    QgsFeature, QgsGeometry, QgsPoint)


class GhiniBaseDialog(QtGui.QDialog):

    def computeOKEnabled(self):
        is_valid_selection = self.key_name_cb.currentIndex() > 0
        is_valid_file = os.path.isfile(self.distances_le.text())
        self.buttonOK.setEnabled(is_valid_file and is_valid_selection)

    def on_change_key_name(self):
        self.key_name = self.key_names[self.key_name_cb.currentIndex()]
        if self.key_name_cb.currentIndex() == 0:
            self.key_name = None
        self.computeOKEnabled()

    def on_file_changed(self):
        self.computeOKEnabled()


class DistanceMatrixToCoordsDialog(
        GhiniBaseDialog,
        uic.loadUiType(os.path.join(
            os.path.dirname(__file__),
            'ghini_tree_position_dialog_base.ui'))[0]):

    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(DistanceMatrixToCoordsDialog, self).__init__(parent)
        self.self = self
        self.iface = iface
        self.setupUi(self)
        self.distances_le.clear()
        self.pushButton.clicked.connect(self.select_input_file)
        try:
            self.layers = [
                l for l in self.iface.legendInterface().layers()
                if l.type() == l.VectorLayer and l.geometryType() == 0]
        except AttributeError:  # happens when testing
            self.layers = []
        self.buttonOK = self.button_box.button(QDialogButtonBox.Ok)
        self.buttonOK.setEnabled(False)
        self.key_names = ['choose-one']
        self.key_name = None

    def on_change_layer(self):
        # construct list of key names
        layer = self.layers[self.comboBox.currentIndex()]
        field_names = [i.name() for i in layer.fields()]

        # changing widget status will invoke on_change_key_name callback,
        # which in turn will alter self.key_name
        key_name = self.key_name

        # recompute key_names from current layer
        self.key_names = ['<choose-one>'] + sorted(field_names)
        self.key_name_cb.clear()
        self.key_name_cb.addItems(self.key_names)

        # check whether previous key_name is still a valid option
        if key_name in self.key_names[1:]:
            self.key_name_cb.setCurrentIndex(self.key_names.index(key_name))
        else:
            self.key_name_cb.setCurrentIndex(0)

        # recompute OK enabled/disabled
        self.computeOKEnabled()

    def run(self, *args, **kwargs):
        """Run method that performs all the real work"""

        # work only on vector layers (where 0 means points)
        self.comboBox.clear()
        self.comboBox.addItems([l.name() for l in self.layers])

        # show the dialog
        self.show()
        # Run the dialog event loop
        result = self.exec_()

        # See if OK was pressed
        if result:
            # layer object containing reference points and acting as target
            layer = self.layers[self.comboBox.currentIndex()]

            # where are we in the world and which UTM system do we use to
            # perform our metric operations?
            layer_to_wgs84 = QgsCoordinateTransform(
                layer.crs(),
                QgsCoordinateReferenceSystem(4326))
            # use WGS84 position of first feature to select local UTM
            f1 = layer.getFeatures().next()
            local_utm = QgsCoordinateReferenceSystem()
            local_utm.createFromProj4(utm_zone_proj4(
                layer_to_wgs84.transform(f1.geometry().asPoint())))
            # define forward and backward transformations
            transf = QgsCoordinateTransform(layer.crs(), local_utm)
            back_transf = QgsCoordinateTransform(local_utm, layer.crs())

            # populate 'points' dict with projected coordinates
            points = {}
            for feature in layer.getFeatures():
                # we work with local utm projection
                easting_northing = transf.transform(
                    feature.geometry().asPoint())
                point_id = feature[self.key_name]
                points[point_id] = {'code': point_id,
                                    'coordinates': easting_northing}

            # get distances from csv file, and compute connectivity to
            # referenced points
            with open(self.distances_le.text()) as f:
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
                feature[self.key_name] = p['code']
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
                "success? %s; features added: %s; impossible to add: %s." % (
                    err, len(ids), len(still_missing)),
                level=QgsMessageBar.INFO)

            # commit changes only if layer was not editable
            if not wasEditable:
                layer.commitChanges()

    def select_input_file(self):
        filename = QFileDialog.getOpenFileName(
            self, "Select distances file ", "", '*.csv')
        self.distances_le.setText(filename)


class GpsAndDistancesToAdjustedGpsDialog(
        GhiniBaseDialog,
        uic.loadUiType(os.path.join(
            os.path.dirname(__file__),
            'ghini_correct_GPS_dialog_base.ui'))[0]):

    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(GpsAndDistancesToAdjustedGpsDialog, self).__init__(parent)
        self.self = self
        self.setupUi(self)
        self.iface = iface
        self.distances_le.clear()
        self.pushButton.clicked.connect(self.select_input_file)
        self.key_names = ['choose-one']
        self.key_name = None
        # work only on vector layers (where 0 means points)
        self.layers = [l for l in self.iface.legendInterface().layers()
                       if l.type() == l.VectorLayer and l.geometryType() == 0]
        self.buttonOK = self.button_box.buttons()[0]
        self.buttonOK.setEnabled(False)

    def on_change_layer(self):
        # construct list of key names
        gps_points_layer = self.layers[self.gps_points_cb.currentIndex()]
        target_layer = self.layers[self.target_layer_cb.currentIndex()]
        gps_points_field_names = [i.name() for i in gps_points_layer.fields()]
        target_field_names = [i.name() for i in target_layer.fields()]
        self.key_names = ['<choose-one>'] + sorted(set(gps_points_field_names)
                                                   .union(target_field_names))

        self.key_name_cb.clear()
        self.key_name_cb.addItems(self.key_names)
        self.on_change_key_name()
        key_name = self.key_name
        if key_name in self.key_names[1:]:
            self.key_name_cb.setCurrentIndex(self.key_names.index(key_name))
        else:
            self.key_name_cb.setCurrentIndex(0)
            self.key_name = None
        self.computeOKEnabled()

    def select_input_file(self):
        filename = QFileDialog.getOpenFileName(
            self, "Select distances file ", "", '*.csv')
        self.distances_le.setText(filename)

    def run(self, *args, **kwargs):
        # prepare the dialog box with data from the project

        self.gps_points_cb.clear()
        self.gps_points_cb.addItems([l.name() for l in self.layers])
        self.target_layer_cb.clear()
        self.target_layer_cb.addItems([l.name() for l in self.layers])

        # show the dialog
        self.show()
        # Run the dialog event loop
        result = self.exec_()
        # See if OK was pressed
        if result:
            # which layers are we working on?
            gps_points_layer = self.layers[self.gps_points_cb.currentIndex()]
            target_layer = self.layers[self.target_layer_cb.currentIndex()]

            # where are we in the world and which UTM system do we use to
            # perform our metric operations?
            layer_to_wgs84 = QgsCoordinateTransform(
                gps_points_layer.crs(),
                QgsCoordinateReferenceSystem(4326))
            # use WGS84 position of first feature to select local UTM
            f1 = gps_points_layer.getFeatures().next()
            local_utm = QgsCoordinateReferenceSystem()
            local_utm.createFromProj4(utm_zone_proj4(
                layer_to_wgs84.transform(f1.geometry().asPoint())))
            # define forward and backward transformations
            transf = QgsCoordinateTransform(gps_points_layer.crs(), local_utm)
            back_transf = QgsCoordinateTransform(local_utm, target_layer.crs())

            # 'gps_points' projected coordinates
            gps_points = {}
            for feature in gps_points_layer.getFeatures():
                # we work with local utm projection
                easting_northing = transf.transform(
                    feature.geometry().asPoint())
                point_id = feature[self.key_name]
                gps_points[point_id] = {'code': point_id,
                                        'coordinates': easting_northing}

            # computed_points is our goal
            computed_points = {}
            # get distances from csv file, and initialize connectivity to 0
            with open(self.distances_le.text()) as f:
                distances = get_distances_from_csv(f, computed_points)

            place_initial_three_points(computed_points, distances, gps_points)
            extrapolate_coordinates(computed_points, distances)
            t = compute_minimal_distance_transformation(computed_points,
                                                        gps_points)
            pts = rigid_transform_points(computed_points, *t)

            # the two layers have the same set of fields, including 'code'
            fields = target_layer.fields()

            features = []
            for key, pt in pts.items():
                new_pt = QgsFeature(fields)
                new_pt['code'] = key
                computed_pos = back_transf.transform(*pt['coordinates'])
                new_pt.setGeometry(QgsGeometry.fromPoint(computed_pos))
                features.append(new_pt)

            wasEditable = target_layer.isEditable()
            if not wasEditable:
                target_layer.startEditing()

            # bulk-add features to data provider associated to layer
            (err, ids) = target_layer.dataProvider().addFeatures(features)

            # set selection to new features - simplifies removing them in
            # case user does not like the results
            target_layer.setSelectedFeatures([i.id() for i in ids])

            if not wasEditable:
                target_layer.commitChanges()

            from qgis.gui import QgsMessageBar
            self.iface.messageBar().pushMessage(
                "Info",
                "success? %s; features added: %s." % (err, len(ids)),
                level=QgsMessageBar.INFO)
