# coding=utf-8

import unittest
from numpy.testing import assert_almost_equal
from ghini_tree_position import solve_puzzle, get_distances_from_csv
from ghini_tree_position import utm_zone_proj4
from ghini_tree_position import extrapolate_coordinates


class TestUTMChoice(unittest.TestCase):

    def test_utm_zone_proj4_europe(self):
        # Naples
        ex = '+proj=utm +ellps=WGS84 +datum=WGS84 +units=m +no_defs +zone=33'
        self.assertEquals(utm_zone_proj4((14, 41)), ex)
        # Netherlands
        ex = '+proj=utm +ellps=WGS84 +datum=WGS84 +units=m +no_defs +zone=31'
        self.assertEquals(utm_zone_proj4((5, 52)), ex)
        # Małopolska
        ex = '+proj=utm +ellps=WGS84 +datum=WGS84 +units=m +no_defs +zone=34'
        self.assertEquals(utm_zone_proj4((20, 50)), ex)

    def test_utm_zone_proj4_morocco(self):
        # مراكش
        ex = '+proj=utm +ellps=WGS84 +datum=WGS84 +units=m +no_defs +zone=29'
        self.assertEquals(utm_zone_proj4((-8, 31)), ex)
        # فاس
        ex = '+proj=utm +ellps=WGS84 +datum=WGS84 +units=m +no_defs +zone=30'
        self.assertEquals(utm_zone_proj4((-5, 34)), ex)

    def test_utm_zone_proj4_colombia_venezuela_ecuador_panama(self):
        # Quito
        ex = '+no_defs +zone=17 +south'
        self.assertTrue(utm_zone_proj4((-78.5, -0.2)).endswith(ex))
        # Cartagena
        ex = '+no_defs +zone=18'
        self.assertTrue(utm_zone_proj4((-75, 10)).endswith(ex))
        # David
        ex = '+no_defs +zone=17'
        self.assertTrue(utm_zone_proj4((-82.4, 8.5)).endswith(ex))
        # Iquitos
        ex = '+no_defs +zone=18 +south'
        self.assertTrue(utm_zone_proj4((-73, -3.7)).endswith(ex))


class TestGetDistancesFromCsv(unittest.TestCase):

    def test_get_distances_from_csv(self):
        points = {}
        from StringIO import StringIO
        s = StringIO('14,24,3\n14,25,4\n24,25,5\n')
        d = get_distances_from_csv(s, points)
        self.assertTrue('14' in points)
        self.assertTrue('24' in points)
        self.assertTrue('25' in points)
        self.assertEquals(d['14']['24'], 3)
        self.assertEquals(d['24']['14'], 3)
        self.assertEquals(d['14']['25'], 4)
        self.assertEquals(d['25']['14'], 4)
        self.assertEquals(d['24']['25'], 5)
        self.assertEquals(d['25']['24'], 5)

    def test_get_distances_from_csv_adding(self):
        points = {'15': {'coordinates': (0, 0)}}
        from StringIO import StringIO
        s = StringIO('14,15,3\n')
        d = get_distances_from_csv(s, points)
        self.assertTrue('14' in points)
        self.assertTrue('15' in points)
        self.assertFalse('coordinates' in points['14'])
        self.assertTrue('coordinates' in points['15'])
        self.assertEquals(d['14']['15'], 3)
        self.assertEquals(d['15']['14'], 3)

    def test_get_distances_connectivity_zero(self):
        points = {}
        from StringIO import StringIO
        s = StringIO('14,24,3\n14,25,4\n24,25,5\n')
        d = get_distances_from_csv(s, points)
        self.assertEquals(points['14']['prio'], 0)
        self.assertEquals(points['24']['prio'], 0)
        self.assertEquals(points['25']['prio'], 0)

    def test_get_distances_connectivity_three(self):
        points = {'15': {'coordinates': (0, 0)},
                  '16': {'coordinates': (0, 0)},
                  '17': {'coordinates': (0, 0)}}
        from StringIO import StringIO
        s = StringIO('14,15,3\n14,16,3\n14,17,3\n15,16,3\n')
        d = get_distances_from_csv(s, points)
        self.assertEquals(points['14']['prio'], 3)
        self.assertEquals(points['15']['prio'], 1)
        self.assertEquals(points['17']['prio'], 0)

    def test_get_distances_connectivity_one(self):
        points = {'15': {'coordinates': (0, 0)}}
        from StringIO import StringIO
        s = StringIO('14,15,3\n')
        d = get_distances_from_csv(s, points)
        self.assertEquals(points['14']['prio'], 1)
        self.assertEquals(points['15']['prio'], 0)


class TestExtrapolateCoordinates(unittest.TestCase):

    def test_extrapolate_coordinates_one(self):
        points = {'0': {'coordinates': (0, 0)},
                  'A': {'coordinates': (4, 0)},
                  'B': {'coordinates': (0, 3)}}
        from StringIO import StringIO
        s = StringIO('x,0,5\nx,A,3\nx,B,4\n')
        d = get_distances_from_csv(s, points)
        extrapolate_coordinates(points, d)
        self.assertEquals(tuple(points['x']['coordinates']), (4.0, 3.0))
        self.assertEquals(points['x']['computed'], True)

    def test_extrapolate_coordinates_two(self):
        points = {'0': {'coordinates': (4, 0)},
                  'A': {'coordinates': (0, 0)},
                  'B': {'coordinates': (0, 3)},
                  'C': {'coordinates': (0, 6)},
                  'D': {'coordinates': (0, 9)}}
        from StringIO import StringIO
        s = StringIO('x,0,3\nx,A,5\nx,B,4\n'
                     'y,x,3\ny,B,5\ny,C,4\n'
                     'z,y,3\nz,C,5\nz,D,4\n'
                     't,x,2.5\nt,B,2.5\nt,y,2.5\n')
        d = get_distances_from_csv(s, points)
        extrapolate_coordinates(points, d)
        self.assertEquals(tuple(points['x']['coordinates']), (4.0, 3.0))
        self.assertEquals(tuple(points['y']['coordinates']), (4.0, 6.0))
        self.assertEquals(tuple(points['z']['coordinates']), (4.0, 9.0))
        assert_almost_equal(tuple(points['t']['coordinates']), (2.0, 4.5))


class TestSolvePuzzle(unittest.TestCase):

    def test_solve_puzzle(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'},
            'p4': {'id': 'p4'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (4.0, 0.0)},
                    'p3': {'coordinates': (4.0, 3.0)},
                    'p4': {'coordinates': (0.0, 3.0)}, }
        distances_list = [('p1', 'p2', 4.0),
                          ('p1', 'p3', 5.0),
                          ('p1', 'p4', 3.0),
                          ('p2', 'p3', 3.0),
                          ('p2', 'p4', 5.0),
                          ('p1', 'p4', 4.0)]
        distances = {}
        for p, q, d in distances_list:
            distances.setdefault(p, {})
            distances.setdefault(q, {})
            distances[p][q] = distances[q][p] = d
        solution = solve_puzzle(points, distances, proj_gps)
