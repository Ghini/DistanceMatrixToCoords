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


def most_connected_3clique(distances):
    """find the 3clique from which to reach the largest set of points

    this is not really implemented, we need an initial guess for this to
    work. given that, we just perform a complete search.

    """
    cliques = enumerate_3cliques(distances)
    reachable_from_clique = {}
    for a, b, c in cliques:
        reachable_from_clique[(a, b, c)] = set(
            distances[a]).intersection(distances[b]).intersection(distances[c])
    dummy, result, = max((len(v), k) for k, v in reachable_from_clique.items())
    return tuple(sorted(result))


def enumerate_3cliques(distances):
    """enumerate cliques with 3 elements
    """

    nodes = set(distances.keys())
    nodes = reduce(lambda x, y: x.union(y.keys()), distances.values(), nodes)
    nodes = sorted(nodes)
    while nodes:
        a = nodes.pop(0)
        inner = list(nodes)
        while inner:
            b = inner.pop(0)
            if b not in distances[a]:
                continue
            for c in set(inner).intersection(
                    distances[a]).intersection(distances[b]):
                yield (a, b, c)


def place_initial_three_points(points, distances, gps):
    """compute coordinates of three points, compatible with the data

    points (dict)
    distances (dict) defines mutual distances between pairs of points.
    positions (dict) is the measured gps positions, affected by errors.

    """
    P1, P2, P3 = most_connected_3clique(distances)
    points[P1]['coordinates'] = gps[P1]['coordinates']
    # keep direction P1-P2 according to gps, but respect distance
    import numpy as np
    # unit vector P1->P2
    u12 = normalize(np.array(gps[P2]['coordinates']) -
                    np.array(gps[P1]['coordinates']))
    # rotation matrix: x-axis to P1->P2
    R = np.array([[u12[0], -u12[1]], [u12[1], u12[0]]])
    d12 = distances[P1][P2]
    points[P2]['coordinates'] = tuple(d12 * u12 + gps[P1]['coordinates'])
    sqd12 = distances[P1][P2] * distances[P1][P2]
    sqd13 = distances[P1][P3] * distances[P1][P3]
    sqd23 = distances[P2][P3] * distances[P2][P3]
    Cx = (sqd12 + sqd13 - sqd23) / 2 / d12
    from math import sqrt
    Cy = sqrt(sqd13 - Cx * Cx)
    #
    # now crudely decide about handedness
    u13 = normalize(np.array(gps[P3]['coordinates']) -
                    np.array(gps[P1]['coordinates']))
    cross_vector_gps = np.cross(u12, u13)
    if cross_vector_gps > 0:
        v13 = R.dot([Cx, Cy])
    else:
        v13 = R.dot([Cx, -Cy])
    # now rotate as of v12
    points[P3]['coordinates'] = tuple(v13 + gps[P1]['coordinates'])
    #
    # and compute connectivity to these three points for all others
    for p in points.values():
        p.setdefault('prio', 0)
    for p in [P1, P2, P3]:
        for q in distances[p]:
            points[q]['prio'] += 1


def rigid_transform_points(points, x, y, theta):
    """transform 'coordinates' of points by displacement and rotation

    """
    import numpy as np
    from math import cos, sin, pi
    theta = theta / 180.0 * pi
    R = np.array([[cos(theta), -sin(theta), x],
                  [sin(theta), cos(theta), y]])
    result = {}
    for k, p in points.items():
        result[k] = dict(p)
        pt = np.array(tuple(p['coordinates'])[:2] + (1, ))
        result[k]['coordinates'] = tuple(R.dot(pt))
    return result


def distance_between_homonyms(p, q):
    """compute sum of square distances
    """
    import numpy as np
    result = 0.0
    for idp in set(p).union(set(q)):
        result += ((np.array(p[idp]['coordinates']) -
                    np.array(q[idp]['coordinates'])) ** 2).sum()
    return result


def compute_minimal_distance_transformation(p, q):
    """computes the x, y, theta rigid transformation that minimizes the SSD

    the rigid transformation applied to the frame 'p' that approximates it
    to the points 'q'

    """

    def target(x):
        return distance_between_homonyms(rigid_transform_points(p, *x), q)

    import numpy as np
    import scipy.optimize
    optres = scipy.optimize.minimize(target, (0, 0, 0), method='Powell')
    return optres.x


def utm_zone_proj4(pt):
    import math
    lon, lat = pt
    wkt = '+proj=utm +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
    zone_number = int(math.floor((lon + 180) % 360 / 6) + 1)
    wkt += " +zone=%s" % zone_number
    if lat < 0:
        wkt += ' +south'
    return wkt


def solve_puzzle(points, distances, proj_gps):
    place_initial_three_points(points, distances, proj_gps)
    extrapolate_coordinates(points, distances)
    t = compute_minimal_distance_transformation(points, proj_gps)
    return rigid_transform_points(points, *t)


def extrapolate_coordinates(points, distances):
    """compute missing coordinates respecting distances and given points

    navigate distances graph, keep selecting most connected point, to
    compute its coordinates given enough distances from enough referenced
    points.

    """
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
        for neighbour_id, destinations in distances[point['id']].items():
            neighbour = points[neighbour_id]
            if 'heappos' in neighbour:
                heap.reprioritize(neighbour)


def get_distances_from_csv(stream, points):
    distances = {}
    for l in stream.readlines():
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
        point['prio'] = len(filter(lambda x: 'coordinates' in points[x],
                                   distances.get(n, {}).keys()))
        point['computed'] = False
    return distances


