# coding=utf-8

import unittest
from numpy.testing import assert_almost_equal
from utils import solve_puzzle, get_distances_from_csv
from utils import utm_zone_proj4
from utils import extrapolate_coordinates
from utils import compute_minimal_distance_transformation
from utils import place_initial_three_points
from utils import rigid_transform_points


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
        self.assertTrue(len(points) == 3)
        self.assertTrue('14' in points)
        self.assertTrue('24' in points)
        self.assertTrue('25' in points)
        self.assertEquals(d['14']['24'], 3)
        self.assertEquals(d['24']['14'], 3)
        self.assertEquals(d['14']['25'], 4)
        self.assertEquals(d['25']['14'], 4)
        self.assertEquals(d['24']['25'], 5)
        self.assertEquals(d['25']['24'], 5)

    def test_get_distances_from_csv_with_header(self):
        points = {}
        from StringIO import StringIO
        s = StringIO('f,t,d\n14,24,3\n14,25,4\n24,25,5\n')
        d = get_distances_from_csv(s, points)
        self.assertTrue(len(points) == 3)
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
        self.assertFalse('coordinates' in points['x'])
        self.assertFalse('coordinates' in points['y'])
        self.assertFalse('coordinates' in points['z'])
        self.assertFalse('coordinates' in points['t'])
        extrapolate_coordinates(points, d)
        self.assertEquals(tuple(points['x']['coordinates']), (4.0, 3.0))
        self.assertEquals(tuple(points['y']['coordinates']), (4.0, 6.0))
        self.assertEquals(tuple(points['z']['coordinates']), (4.0, 9.0))
        assert_almost_equal(tuple(points['t']['coordinates']), (2.0, 4.5))


class TestComputeMinimalDistanceTransformation(unittest.TestCase):

    def test_compute_minimal_distance_transformation_2_points(self):
        p = {'A': {'coordinates': (0, 0)},
             'B': {'coordinates': (2, 0)}}
        q = {'A': {'coordinates': (0, 0)},
             'B': {'coordinates': (4, 0)}}
        t = compute_minimal_distance_transformation(p, q)
        assert_almost_equal(t, (1, 0, 0), decimal=6)

    def test_compute_minimal_distance_transformation_345(self):
        p = {'A': {'coordinates': (0, 0)},
             'B': {'coordinates': (4, 0)},
             'C': {'coordinates': (0, 3)},
             'D': {'coordinates': (4, 3)}}
        q = {'A': {'coordinates': (0, 0)},
             'B': {'coordinates': (8, 0)},
             'C': {'coordinates': (0, 6)},
             'D': {'coordinates': (8, 6)}}
        t = compute_minimal_distance_transformation(p, q)
        assert_almost_equal(t, (2, 1.5, 0), decimal=6)

    def test_compute_minimal_distance_transformation_4_points(self):
        p = {'A': {'coordinates': (2, 0)},
             'B': {'coordinates': (1, 0)},
             'C': {'coordinates': (0, 1)},
             'D': {'coordinates': (0, 2)}}
        q = {'A': {'coordinates': (0, 2)},
             'B': {'coordinates': (0, 1)},
             'C': {'coordinates': (-1, 0)},
             'D': {'coordinates': (-2, 0)}}
        t = compute_minimal_distance_transformation(p, q)
        assert_almost_equal(t[:2], (0, 0), decimal=6)
        assert_almost_equal(t[2] / 90, 1.0, decimal=5)

    def test_compute_minimal_distance_transformation_4_points2(self):
        p = {'A': {'coordinates': (2, 0)},
             'B': {'coordinates': (1, 0)},
             'C': {'coordinates': (0, 1)},
             'D': {'coordinates': (0, 2)}}
        q = {'A': {'coordinates': (0, 2.1)},
             'B': {'coordinates': (0, 0.9)},
             'C': {'coordinates': (-0.9, 0)},
             'D': {'coordinates': (-2.1, 0)}}
        t = compute_minimal_distance_transformation(p, q)
        assert_almost_equal(t[:2], (0, 0), decimal=6)
        assert_almost_equal(t[2] / 90, 1.0, decimal=5)


class TestSolvePuzzle(unittest.TestCase):

    def test_solve_puzzle(self):
        points = {
            'A': {'id': 'A'},
            'B': {'id': 'B'},
            'C': {'id': 'C'},
            'D': {'id': 'D'}}
        proj_gps = {'A': {'coordinates': (0.0, 0.0)},
                    'B': {'coordinates': (8.0, 0.0)},
                    'C': {'coordinates': (8.0, 6.0)},
                    'D': {'coordinates': (0.0, 6.0)}, }
        distances_list = [('A', 'B', 4.0),
                          ('A', 'C', 5.0),
                          ('A', 'D', 3.0),
                          ('B', 'C', 3.0),
                          ('B', 'D', 5.0),
                          ('C', 'D', 4.0)]
        distances = {}
        for p, q, d in distances_list:
            distances.setdefault(p, {})
            distances.setdefault(q, {})
            distances[p][q] = distances[q][p] = d
        place_initial_three_points(points, distances, proj_gps)
        extrapolate_coordinates(points, distances)
        t = compute_minimal_distance_transformation(points, proj_gps)
        p = rigid_transform_points(points, *t)
        assert_almost_equal(p['A']['coordinates'], (2, 1.5), decimal=6)
        assert_almost_equal(p['B']['coordinates'], (6, 1.5), decimal=6)
        assert_almost_equal(p['C']['coordinates'], (6, 4.5), decimal=6)
        assert_almost_equal(p['D']['coordinates'], (2, 4.5), decimal=6)
