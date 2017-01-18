# coding=utf-8
"""

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from ghini_tree_position import place_initial_three_points
from ghini_tree_position import most_connected_point, most_connected_3clique
from ghini_tree_position import rigid_transform_points
from numpy.testing import assert_almost_equal

__author__ = 'mario@anche.no'
__date__ = '2017-01-18'
__copyright__ = 'Copyright 2017, Mario Frasca'


class TestMostConnectedPoint(unittest.TestCase):
    def setUp(self):
        """bad example, it's from DistanceMatrixToCoords/issues/5
        """
        self.from_to = [("04", "10"), ("04", "18"), ("04", "19"), ("19", "10"),
                        ("19", "18"), ("19", "14"), ("18", "10"), ("18", "14"),
                        ("18", "02"), ("14", "02"), ("14", "21"), ("14", "12"),
                        ("12", "02"), ("12", "21"), ("12", "03"), ("12", "16"),
                        ("16", "21"), ("16", "03"), ("16", "15"), ("16", "07"),
                        ("16", "08"), ("08", "07"), ("08", "17"), ("08", "09"),
                        ("08", "05"), ("05", "07"), ("05", "17"), ("05", "09"),
                        ("09", "07"), ("09", "17"), ("07", "17"), ("07", "15"),
                        ("17", "15"), ("17", "06"), ("06", "01"), ("06", "11"),
                        ("06", "15"), ("11", "20"), ("11", "13"), ("11", "01"),
                        ("13", "20"), ("13", "01"), ("13", "22"), ("13", "10"),
                        ("13", "04"), ("01", "15"), ("01", "22"), ("22", "15"),
                        ("22", "03"), ("22", "02"), ("22", "10"), ("10", "02"),
                        ("10", "21"), ("10", "03"), ("21", "02"), ("21", "03"),
                        ("03", "15"), ]
        self.from_to_d = {}
        for k, n in self.from_to:
            self.from_to_d.setdefault(k, {})
            self.from_to_d.setdefault(n, {})
            self.from_to_d[k][n] = 0
            self.from_to_d[n][k] = 0

    def test_best_clique(self):
        expect = ('10', '13', '22')
        self.assertEquals(most_connected_3clique(self.from_to_d, '10'), expect)
        self.assertEquals(most_connected_3clique(self.from_to_d, '13'), expect)
        self.assertEquals(most_connected_3clique(self.from_to_d, '22'), expect)

    def test_other_best_clique(self):
        expect = ('07', '15', '16')
        self.assertEquals(most_connected_3clique(self.from_to_d, '07'), expect)
        self.assertEquals(most_connected_3clique(self.from_to_d, '15'), expect)
        self.assertEquals(most_connected_3clique(self.from_to_d, '16'), expect)

    def test_suboptimal_cliques(self):
        expect = ('11', '13', '20')
        self.assertEquals(most_connected_3clique(self.from_to_d, '20'), expect)
        expect = ('01', '11', '13')
        self.assertEquals(most_connected_3clique(self.from_to_d, '11'), expect)
        expect = ('01', '15', '22')
        self.assertEquals(most_connected_3clique(self.from_to_d, '01'), expect)

    def test_best_clique_from_most_connected_point(self):
        expect = ('10', '13', '22')
        self.assertEquals(most_connected_3clique(self.from_to_d), expect)
        self.assertEquals(most_connected_3clique(self.from_to_d), expect)
        self.assertEquals(most_connected_3clique(self.from_to_d), expect)


class TestInitialTriangle(unittest.TestCase):

    def test_345_right(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (7.0, 0.0)},
                    'p3': {'coordinates': (0.0, 7.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 4.0},
                     'p2': {'p1': 5.0, 'p3': 3.0},
                     'p3': {'p1': 4.0, 'p2': 3.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p2']['coordinates'], (5.0, 0.0))
        assert_almost_equal(points['p3']['coordinates'], (3.2, 2.4))

    def test_345_left(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (7.0, 0.0)},
                    'p3': {'coordinates': (0.0, -7.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 4.0},
                     'p2': {'p1': 5.0, 'p3': 3.0},
                     'p3': {'p1': 4.0, 'p2': 3.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p2']['coordinates'], (5.0, 0.0))
        assert_almost_equal(points['p3']['coordinates'], (3.2, -2.4))

    def test_435_right(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (7.0, 0.0)},
                    'p3': {'coordinates': (0.0, 7.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 3.0},
                     'p2': {'p1': 5.0, 'p3': 4.0},
                     'p3': {'p1': 3.0, 'p2': 4.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p2']['coordinates'], (5.0, 0.0))
        assert_almost_equal(points['p3']['coordinates'], (1.8, 2.4))

    def test_51213_right(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (7.0, 0.0)},
                    'p3': {'coordinates': (0.0, 7.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 12.0},
                     'p2': {'p1': 5.0, 'p3': 13.0},
                     'p3': {'p1': 12.0, 'p2': 13.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p2']['coordinates'], (5.0, 0.0))
        assert_almost_equal(points['p3']['coordinates'], (0, 12))

    def test_51213_left(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (7.0, 0.0)},
                    'p3': {'coordinates': (0.0, -7.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 12.0},
                     'p2': {'p1': 5.0, 'p3': 13.0},
                     'p3': {'p1': 12.0, 'p2': 13.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p2']['coordinates'], (5.0, 0.0))
        assert_almost_equal(points['p3']['coordinates'], (0, -12))

    def test_566_90_right(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (0.0, 7.0)},
                    'p3': {'coordinates': (-7.0, 0.0)}, }
        distances = {'p1': {'p2': 6.0, 'p3': 5.0},
                     'p2': {'p1': 6.0, 'p3': 5.0},
                     'p3': {'p1': 5.0, 'p2': 5.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p2']['coordinates'], (0.0, 6.0))
        assert_almost_equal(points['p3']['coordinates'], (-4, 3))

    def test_566_90_left(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (0.0, 0.0)},
                    'p2': {'coordinates': (0.0, 7.0)},
                    'p3': {'coordinates': (7.0, 0.0)}, }
        distances = {'p1': {'p2': 6.0, 'p3': 5.0},
                     'p2': {'p1': 6.0, 'p3': 5.0},
                     'p3': {'p1': 5.0, 'p2': 5.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p1']['coordinates'], (0.0, 0.0))
        self.assertEquals(points['p2']['coordinates'], (0.0, 6.0))
        assert_almost_equal(points['p3']['coordinates'], (4, 3))

    def test_345_translated(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (1.0, 1.0)},
                    'p2': {'coordinates': (11.0, 1.0)},
                    'p3': {'coordinates': (0.0, 7.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 4.0},
                     'p2': {'p1': 5.0, 'p3': 3.0},
                     'p3': {'p1': 4.0, 'p2': 3.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p1']['coordinates'], (1.0, 1.0))
        self.assertEquals(points['p2']['coordinates'], (6.0, 1.0))
        assert_almost_equal(points['p3']['coordinates'], (4.2, 3.4))

    def test_345_translated_opposite(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (1.0, 1.0)},
                    'p2': {'coordinates': (11.0, 1.0)},
                    'p3': {'coordinates': (7.0, 0.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 4.0},
                     'p2': {'p1': 5.0, 'p3': 3.0},
                     'p3': {'p1': 4.0, 'p2': 3.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p1']['coordinates'], (1.0, 1.0))
        self.assertEquals(points['p2']['coordinates'], (6.0, 1.0))
        assert_almost_equal(points['p3']['coordinates'], (4.2, -1.4))

    def test_345_rototranslated(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (1.0, 1.0)},
                    'p2': {'coordinates': (7.0, 9.0)},
                    'p3': {'coordinates': (7.0, 0.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 3.0},
                     'p2': {'p1': 5.0, 'p3': 4.0},
                     'p3': {'p1': 3.0, 'p2': 4.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p1']['coordinates'], (1.0, 1.0))
        self.assertEquals(points['p2']['coordinates'], (4.0, 5.0))
        assert_almost_equal(points['p3']['coordinates'], (4, 1))

    def test_345_rototranslated_opposite(self):
        points = {
            'p1': {'id': 'p1'},
            'p2': {'id': 'p2'},
            'p3': {'id': 'p3'}}
        proj_gps = {'p1': {'coordinates': (1.0, 1.0)},
                    'p2': {'coordinates': (7.0, 9.0)},
                    'p3': {'coordinates': (0.0, 7.0)}, }
        distances = {'p1': {'p2': 5.0, 'p3': 4.0},
                     'p2': {'p1': 5.0, 'p3': 3.0},
                     'p3': {'p1': 4.0, 'p2': 3.0}, }
        place_initial_three_points(points, distances, proj_gps)
        self.assertEquals(points['p1']['coordinates'], (1.0, 1.0))
        self.assertEquals(points['p2']['coordinates'], (4.0, 5.0))
        assert_almost_equal(points['p3']['coordinates'], (1, 5))


class TestRigidTransformation(unittest.TestCase):

    def test_rigid_transform_points_no_movement(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        rigid_transform_points(p, x=0, y=0, theta=0)
        self.assertEquals(p['p1']['coordinates'], (1.0, 1.0))
        self.assertEquals(p['p2']['coordinates'], (4.0, 5.0))
        self.assertEquals(p['p3']['coordinates'], (1.0, 5.0))

    def test_rigid_transform_points_only_translate(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        rigid_transform_points(p, x=10, y=0, theta=0)
        self.assertEquals(p['p1']['coordinates'], (11.0, 1.0))
        self.assertEquals(p['p2']['coordinates'], (14.0, 5.0))
        self.assertEquals(p['p3']['coordinates'], (11.0, 5.0))
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        rigid_transform_points(p, x=0, y=10, theta=0)
        self.assertEquals(p['p1']['coordinates'], (1.0, 11.0))
        self.assertEquals(p['p2']['coordinates'], (4.0, 15.0))
        self.assertEquals(p['p3']['coordinates'], (1.0, 15.0))
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        rigid_transform_points(p, x=10, y=10, theta=0)
        self.assertEquals(p['p1']['coordinates'], (11.0, 11.0))
        self.assertEquals(p['p2']['coordinates'], (14.0, 15.0))
        self.assertEquals(p['p3']['coordinates'], (11.0, 15.0))
        
    def test_rigid_transform_points_rotate_90(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        rigid_transform_points(p, x=0, y=0, theta=90)
        assert_almost_equal(p['p1']['coordinates'], (-1.0, 1.0))
        assert_almost_equal(p['p2']['coordinates'], (-5.0, 4.0))
        assert_almost_equal(p['p3']['coordinates'], (-5.0, 1.0))
        
    def test_rigid_transform_points_rotate_m90(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        rigid_transform_points(p, x=0, y=0, theta=-90)
        assert_almost_equal(p['p1']['coordinates'], (1.0, -1.0))
        assert_almost_equal(p['p2']['coordinates'], (5.0, -4.0))
        assert_almost_equal(p['p3']['coordinates'], (5.0, -1.0))

    def test_rigid_transform_points_move_rotate(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        rigid_transform_points(p, x=10, y=10, theta=90)
        assert_almost_equal(p['p1']['coordinates'], (9.0, 11.0))
        assert_almost_equal(p['p2']['coordinates'], (5.0, 14.0))
        assert_almost_equal(p['p3']['coordinates'], (5.0, 11.0))
