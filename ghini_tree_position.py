# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DistanceMatrixToCoords
 A QGIS plugin
 Calculate point positions in 2D given a few reference points and a matrix of mutual horizontal distances
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
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from ghini_tree_position_dialog import DistanceMatrixToCoordsDialog
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


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


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GhiniTreePositioner')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DistanceMatrixToCoords')
        self.toolbar.setObjectName(u'DistanceMatrixToCoords')

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


    def add_action(
        self,
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

        # Create the dialog (after translation) and keep reference
        self.dlg = DistanceMatrixToCoordsDialog()

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


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            ## these values should come from the layer
            points = {
                '13': {'id': '13', 'type': 'Point', 'coordinates': [690514,720254]},
                '14': {'id': '14', 'type': 'Point', 'coordinates': [690514,720408]},
                '15': {'id': '15', 'type': 'Point', 'coordinates': [690514,720562]},
                '22': {'id': '22', 'type': 'Point', 'coordinates': [690360,720100]},
                '32': {'id': '32', 'type': 'Point', 'coordinates': [690206,720100]},
                '42': {'id': '42', 'type': 'Point', 'coordinates': [690052,720100]},
                '51': {'id': '51', 'type': 'Point', 'coordinates': [689898,719946]},
                '55': {'id': '55', 'type': 'Point', 'coordinates': [689898,720562]},
            }

            ## these values should come from the input files
            distances = {
                '14': {'24': 154, '25': 217.788888605},
                '22': {'23': 154, '13': 217.788888605, '33': 217.788888605},
                '23': {'33': 154, '24': 154, '14': 217.788888605, '34': 217.788888605},
                '24': {'34': 154, '25': 154, '15': 217.788888605, '35': 217.788888605},
                '25': {'35': 154, '15': 154,},
                '32': {'33': 154, '23': 217.788888605, '43': 217.788888605},
                '33': {'43': 154, '34': 154, '24': 217.788888605, '44': 217.788888605},
                '34': {'44': 154, '35': 154, '25': 217.788888605, '45': 217.788888605},
                '42': {'43': 154, '33': 217.788888605, '53': 217.788888605},
                '43': {'53': 154, '44': 154, '34': 217.788888605, '54': 217.788888605},
                '44': {'54': 154, '45': 154, '35': 217.788888605, '53': 217.788888605, '55': 217.788888605},
                '53': {'55': 308, },
                '54': {'53': 154, },
                '55': {'45': 154, '54': 154, '43': 344.354468535, '34': 344.354468535, },
            }

            ## fill in points from distances
            for k1, v in distances.items():
                points.setdefault(k1, {'id': k1, "type": "Point"})
                for k2 in v:
                    points.setdefault(k2, {'id': k2, "type": "Point"})

            ## fill-back-links in distances
            for n1, destinations in distances.items():
                for n2, distance in destinations.items():
                    distances.setdefault(n2, {})
                    if distances[n2].get(n1, distance) != distance:
                        print 'overwriting %s-%s (%s) with %s' % (n2, n1, distances[n2][n1], distance)
                    distances[n2][n1] = distance

            ## inform each point on how many links lead to referenced point
            for n, point in points.items():
                point['prio'] = 0
                point['computed'] = False
                for reachable in distances.get(n, {}):
                    if 'coordinates' in points[reachable]:
                        point['prio'] += 1

            ## construct priority queue of points for which we still have no coordinates
            heap = Heap([p for p in points.values() if 'coordinates' not in p])

            while heap:
                point = heap.pop()
                ## compute coordinates of point
                point['coordinates'] = list(find_point_coordinates(points, distances, point['id']))
                point['computed'] = True

                ## inform points connected to point that they have one more referenced neighbour
                ## TODO - we should not add points that are aligned with those already connected
                for neighbour_id, destinations in distances[point['id']].items():
                    neighbour = points[neighbour_id]
                    if 'heappos' in neighbour:
                        heap.reprioritize(neighbour)

            ## layer name should be from active layer
            layer = QgsMapLayerRegistry.instance().mapLayers()['beacons20170101115312666']
            layer.startEditing()

            ## source coordinate reference system should be from active layer
            transf = QgsCoordinateTransform(QgsCoordinateReferenceSystem(3117), QgsCoordinateReferenceSystem(4326))

            featureList = []
            ## now add the computed points to the layer
            for (x, y) in [p['coordinates'] for p in points.values() if p['computed']]:
                feature = QgsFeature()
                layerPoint = transf.transform(QgsPoint(x, y))
                feature.setGeometry(QgsGeometry.fromPoint(layerPoint))
                featureList.append(feature)

            layer.dataProvider().addFeatures(featureList)
            layer.commitChanges()


class Heap:
    def __init__(self, elems):
        """creates a binary heap from list of dictionaries

        elements in heap are sorted according to their 'prio' value and will
        receive a 'heappos' key, that informs them of their position in the
        heap.

        highest priority values goes to front of array.

        >>> i = Heap([{'prio':1},{'prio':2},{'prio':3}])
        >>> i.priorities()
        [3, 1, 2]
        >>> i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5}])
        >>> i.priorities()
        [5, 4, 2, 1, 3]
        >>> i = Heap([{'prio':1},{'prio':3},{'prio':2},{'prio':4},{'prio':5}])
        >>> i.priorities()
        [5, 4, 2, 1, 3]
        >>> i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7}])
        >>> i.priorities()
        [7, 4, 5, 1, 3, 2]

        """
        self.heap = list(elems)
        self.heap[0]['heappos'] = 0
        for k in range(1, len(elems)):
            self.heap[k]['heappos'] = k
            self._swim(k)

    def push(self, elem):
        """push new element into heap

        >>> i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7}])
        >>> i.push({'prio': 8})
        >>> i.pop()
        {'prio': 8}
        >>> i.push({'prio': 6})
        >>> i.pop()
        {'prio': 7}
        >>> i.pop()
        {'prio': 6}

        """
        k = len(self.heap)
        elem['heappos'] = k
        self.heap.append(elem)
        self._swim(k)

    def pop(self):
        """pop highest priority from heap

        element with highest priority value is removed from heap.

        >>> i = Heap([{'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7}])
        >>> i.pop()
        {'prio': 7}
        >>> i.pop()
        {'prio': 5}
        >>> i.pop()
        {'prio': 4}
        >>> i.pop()
        {'prio': 3}
        >>> i.pop()
        {'prio': 2}
        >>> i.pop()
        {'prio': 1}
        >>> len(i.priorities())
        0

        >>> a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        >>> i = Heap([f, e, b, c, d, a])
        >>> i.priorities()
        [7, 5, 2, 3, 4, 1]
        >>> i.pop()
        {'prio': 7}
        >>> i.priorities()
        [5, 4, 2, 3, 1]
        >>> i.pop()
        {'prio': 5}
        >>> i.priorities()
        [4, 3, 2, 1]
        """
        k = len(self.heap) - 1
        self._swap(0, k)
        result = self.heap.pop()
        del result['heappos']
        self._sink(0)
        return result

    def reprioritize(self, elem, prio_change=1):
        """change priority of heap element, and let it swim up or sink down

        >>> a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        >>> i = Heap([a, b, c, d, e, f])

        nothing happens if the priority change is zero
        >>> i.priorities()
        [7, 4, 5, 1, 3, 2]
        >>> i.reprioritize(a, 0)
        >>> i.priorities()
        [7, 4, 5, 1, 3, 2]

        the priority change default value is the positive unit. you specify
        the object of which the priority has to be altered.
        >>> a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        >>> i = Heap([a, b, c, d, e, f])
        >>> i.priorities()
        [7, 4, 5, 1, 3, 2]
        >>> i.reprioritize(a)
        >>> i.priorities()
        [7, 4, 5, 2, 3, 2]
        >>> i.reprioritize(a)
        >>> i.priorities()
        [7, 4, 5, 3, 3, 2]
        >>> i.reprioritize(a)
        >>> i.priorities()
        [7, 4, 5, 4, 3, 2]
        >>> i.reprioritize(a)
        >>> i.priorities()
        [7, 5, 5, 4, 3, 2]
        >>> a
        {'heappos': 1, 'prio': 5}

        you can give any value for the desired priority change.
        >>> a, b, c, d, e, f = ({'prio':1},{'prio':2},{'prio':3},{'prio':4},{'prio':5},{'prio':7})
        >>> i = Heap([a, b, c, d, e, f])
        >>> i.priorities()
        [7, 4, 5, 1, 3, 2]
        >>> i.reprioritize(c, 8)
        >>> i.priorities()
        [11, 7, 5, 1, 4, 2]
        >>> i.reprioritize(e, 15)
        >>> i.priorities()
        [20, 7, 11, 1, 4, 2]

        a negative priority change will sink the object into the heap
        >>> i.reprioritize(e, -20)
        >>> i.priorities()
        [11, 7, 2, 1, 4, 0]
        >>> i.reprioritize(c, -12)
        >>> i.priorities()
        [7, 4, 2, 1, -1, 0]

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
        """

        this is an internal private function: direct use will break heap structure.

        >>> i = Heap([{'prio':1},{'prio':2},{'prio':3}])
        >>> i.priorities()
        [3, 1, 2]
        >>> i._swap(0, 1)
        >>> i.priorities()
        [1, 3, 2]

        """
        self.heap[i1], self.heap[i2]= self.heap[i2], self.heap[i1]
        self.heap[i1]['heappos'], self.heap[i2]['heappos'] = (
            self.heap[i2]['heappos'], self.heap[i1]['heappos'])

    def _sink(self, index):
        """move element down starting at index

        this is an internal private function: do not use directly

        """
        while True:
            maxleafindex = (index+1)*2-1
            try:
                if self.heap[maxleafindex]['prio'] < self.heap[maxleafindex+1]['prio']:
                    maxleafindex += 1
            except IndexError:
                pass
            try:
                if self.heap[index]['prio'] < self.heap[maxleafindex]['prio']:
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

    connected_to = [id for id in sorted(distances[point_id]) if points[id].get('coordinates')]
    connected_matrix = np.array([points[id]['coordinates'] for id in connected_to])
    A = connected_matrix[1:,] - connected_matrix[0,]
    A = 1.0 * A  # make sure we work with floating point values

    ## squared distances vector, beacon_i to first beacon for which we have distances
    D_i1_2 = matrix_multiply(A*A, [[1],[1]])
    ## distances of targeted point from used reference points
    dfb_sel = np.array([distances[point_id][ref_id] for ref_id in connected_to])
    r2 = dfb_sel * dfb_sel

    rhs = ((r2[0] - r2[1:]).reshape(D_i1_2.shape) + D_i1_2) / 2.0
    r1, r2, r3, r4 = np.linalg.lstsq(A, rhs.reshape(rhs.shape[:1]))
    return connected_matrix[0,] + r1
