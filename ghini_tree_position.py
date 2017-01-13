# -*- coding: utf-8 -*-
"""/***************************************************************************
 DistanceMatrixToCoords
 A QGIS plugin
 Calculate point positions in 2D given a few reference points and a matrix
 of mutual horizontal distances
                              -------------------
        begin                : 2017-01-04
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Mario Frasca
        email                : mario@anche.no
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
try:
    from DistanceMatrixToCoords import resources
except ImportError:
    import resources
# Import the code for the dialog
from ghini_tree_position_dialog import DistanceMatrixToCoordsDialog
import os.path

from qgis.core import (
    QgsMapLayerRegistry, QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    QgsFeature, QgsGeometry, QgsPoint)


class DistanceMatrixToCoords:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DistanceMatrixToCoords_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = DistanceMatrixToCoordsDialog()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GhiniTreePositioner')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DistanceMatrixToCoords')
        self.toolbar.setObjectName(u'DistanceMatrixToCoords')
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_input_file)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DistanceMatrixToCoords', message)

    def add_action(self,
                   icon_path,
                   text,
                   callback,
                   enabled_flag=True,
                   add_to_menu=True,
                   add_to_toolbar=True,
                   status_tip=None,
                   whats_this=None,
                   parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/DistanceMatrixToCoords/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'add points from distances'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GhiniTreePositioner'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_input_file(self):
        filename = QFileDialog.getOpenFileName(
            self.dlg, "Select distances file ", "", '*.csv')
        self.dlg.lineEdit.setText(filename)

    def run(self):
        """Run method that performs all the real work"""

        # work only on vector layers (where 0 means points)
        layers = [l for l in self.iface.legendInterface().layers()
                  if l.type() == l.VectorLayer and l.geometryType() == 0]
        self.dlg.comboBox.addItems([l.name() for l in layers])

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            # get reference points from the layer
            layer = layers[self.dlg.comboBox.currentIndex()]
            points = {}
            for feature in layer.getFeatures():
                # TODO target coordinates system should come from layer
                transf = QgsCoordinateTransform(
                    QgsCoordinateReferenceSystem(4326),
                    QgsCoordinateReferenceSystem(3117))
                easting_northing = transf.transform(
                    feature.geometry().asPoint())
                point_id = feature['id']
                points[point_id] = {'id': point_id,
                                    'coordinates': easting_northing}

            # the name of the file comes from the dialog box
            distances = {}
            with open(self.dlg.lineEdit.text()) as f:
                for l in f.readlines():
                    l = l.strip()
                    try:
                        from_id, to_id, distance = l.split(',')[:3]
                        distance = float(distance)
                    except Exception, e:
                        print '»', l, '«', type(e), e
                        continue
                    distances.setdefault(from_id, {})
                    distances.setdefault(to_id, {})
                    distances[from_id][to_id] = distance
                    distances[to_id][from_id] = distance
                    points.setdefault(to_id, {'id': to_id,
                                              "type": "Point"})
                    points.setdefault(from_id, {'id': from_id,
                                                "type": "Point"})

            # inform each point on how many links lead to referenced point
            for n, point in points.items():
                point['prio'] = len(
                    filter(lambda x: 'coordinates' in points[x],
                           distances.get(n, {}).keys()))
                point['computed'] = False

            # remember last attempted point, to avoid deadlocks
            last_attempted_point = None
            # construct priority queue of points for which we still have no
            # coordinates
            heap = Heap([p for p in points.values() if 'coordinates' not in p])

            while heap:
                point = heap.pop()
                # compute coordinates of point
                try:
                    point['coordinates'] = list(
                        find_point_coordinates(points, distances, point['id']))
                except ValueError:
                    point['prio'] = 2
                    if last_attempted_point != point:
                        heap.push(point)
                        last_attempted_point = point
                    continue
                point['computed'] = True

                # inform points connected to point that they have one more
                # referenced neighbour
                for neighbour_id, destinations in distances[
                        point['id']].items():
                    neighbour = points[neighbour_id]
                    if 'heappos' in neighbour:
                        heap.reprioritize(neighbour)

            # remember editable status
            wasEditable = layer.isEditable()
            # force editable if not already editable
            if not wasEditable:
                layer.startEditing()

            # TODO source coordinate reference system should be from active
            # layer
            transf = QgsCoordinateTransform(
                QgsCoordinateReferenceSystem(3117),
                QgsCoordinateReferenceSystem(4326))

            fields = layer.fields()

            featureList = []
            # now add the computed points to the layer
            for p in [p for p in points.values() if p['computed']]:
                x, y = p['coordinates']
                layerPoint = transf.transform(QgsPoint(x, y))
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
            still_missing = [p for p in points.values() if not p.get('coordinates')]
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


class Heap:
    def __init__(self, elems):
        """creates a binary heap from list of dictionaries

        elements in heap are sorted according to their 'prio' value and will
        receive a 'heappos' key, that informs them of their position in the
        heap.

        highest priority values goes to front of array.

        """
        self.heap = list(elems)
        self.heap[0]['heappos'] = 0
        for k in range(1, len(elems)):
            self.heap[k]['heappos'] = k
            self._swim(k)

    def push(self, elem):
        """push new element into heap

        """
        k = len(self.heap)
        elem['heappos'] = k
        self.heap.append(elem)
        self._swim(k)

    def pop(self):
        """pop highest priority from heap

        element with highest priority value is removed from heap.
        """
        k = len(self.heap) - 1
        self._swap(0, k)
        result = self.heap.pop()
        del result['heappos']
        self._sink(0)
        return result

    def reprioritize(self, elem, prio_change=1):
        """change priority of heap element, and let it swim up or sink down

        nothing happens if the priority change is zero

        the priority change default value is the positive unit. you specify
        the object of which the priority has to be altered.

        you can give any value for the desired priority change.

        a negative priority change will sink the object into the heap

        """
        elem['prio'] += prio_change
        if prio_change > 0:
            self._swim(elem['heappos'])
        elif prio_change < 0:
            self._sink(elem['heappos'])

    def __len__(self):
        return self.heap.__len__()

    def priorities(self):
        return [e['prio'] for e in self.heap]

    def _swap(self, i1, i2):
        """this is an internal private function: direct use will break heap
        structure.

        >>> i = Heap([{'prio':1},{'prio':2},{'prio':3}])
        >>> i.priorities()
        [3, 1, 2]
        >>> i._swap(0, 1)
        >>> i.priorities()
        [1, 3, 2]

        """
        self.heap[i1], self.heap[i2] = self.heap[i2], self.heap[i1]
        self.heap[i1]['heappos'], self.heap[i2]['heappos'] = (
            self.heap[i2]['heappos'], self.heap[i1]['heappos'])

    def _sink(self, index):
        """move element down starting at index

        this is an internal private function: do not use directly

        """
        while True:
            maxleafindex = (index + 1) * 2 - 1
            try:
                if self.heap[maxleafindex]['prio'] < self.heap[
                        maxleafindex + 1]['prio']:
                    maxleafindex += 1
            except IndexError:
                pass
            try:
                if self.heap[index]['prio'] < self.heap[
                        maxleafindex]['prio']:
                    self._swap(index, maxleafindex)
                    index = maxleafindex
                else:
                    break
            except IndexError:
                break

    def _swim(self, index):
        """move element up starting at index

        this is an internal private function: do not use directly

        """
        if index == 0:
            return
        parent = int((index + 1) / 2) - 1
        while True:
            if self.heap[index]['prio'] > self.heap[parent]['prio']:
                self._swap(index, parent)
            else:
                break
            index, parent = parent, int((parent + 1) / 2) - 1
            if index == 0:
                break


def find_point_coordinates(points, distances, point_id):
    import numpy as np
    from numpy.core.umath_tests import matrix_multiply

    connected_to = [id for id in sorted(distances[point_id])
                    if points[id].get('coordinates')]
    connected_matrix = np.array([points[id]['coordinates']
                                 for id in connected_to])
    A = connected_matrix[1:, ] - connected_matrix[0, ]
    if almost_parallel(A):
        raise ValueError('Almost singular matrix')
    A = 1.0 * A  # make sure we work with floating point values

    # squared distances vector, beacon_i to first beacon for which we have
    # distances
    D_i1_2 = matrix_multiply(A * A, [[1], [1]])
    # distances of targeted point from used reference points
    dfb_sel = np.array([distances[point_id][ref_id]
                        for ref_id in connected_to])
    r2 = dfb_sel * dfb_sel

    rhs = ((r2[0] - r2[1:]).reshape(D_i1_2.shape) + D_i1_2) / 2.0
    r1, r2, r3, r4 = np.linalg.lstsq(A, rhs.reshape(rhs.shape[:1]))
    return connected_matrix[0, ] + r1


def normalize(v):
    """return the unit vector parallel to v

    if given a null vector, return it verbatim.
    """
    import numpy as np
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def almost_parallel(u, v=None, tolerance=0.085):
    """tell whether two vectors are almost parallel

    Works with two vectors in 2 or 3 dimensions, or on a matrix with 2 rows
    of 2 or 3 columns.  Based on norm of cross product among unit vectors

    """
    import numpy as np
    if v is not None:
        cross_vector = np.cross(normalize(u), normalize(v))
        return np.linalg.norm(cross_vector) < tolerance
    elif u.shape in [(2, 2), (2, 3)]:
        cross_vector = np.cross(normalize(u[0, :]), normalize(u[1, :]))
        return np.linalg.norm(cross_vector) < tolerance
    else:
        return None
