# coding=utf-8
"""

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from numpy.testing import assert_almost_equal
from ghini_tree_position import place_initial_three_points
from ghini_tree_position import most_connected_point, most_connected_3clique
from ghini_tree_position import rigid_transform_points
from ghini_tree_position import distance_between_homonyms
from ghini_tree_position import compute_minimal_distance_transformation
from ghini_tree_position import enumerate_3cliques

__author__ = 'mario@anche.no'
__date__ = '2017-01-18'
__copyright__ = 'Copyright 2017, Mario Frasca'


def compute_from_to_dictionary(from_to):
    ftd = {}
    for k, n in from_to:
        ftd.setdefault(k, {})
        ftd.setdefault(n, {})
        ftd[k][n] = 0
        ftd[n][k] = 0
    return ftd


class TestEnumerate3Cliques(unittest.TestCase):

    def test_enumerate_3cliques_easy(self):
        from_to = [('1', '2'), ('2', '3'), ('3', '1')]
        ftd = compute_from_to_dictionary(from_to)
        expect = [('1', '2', '3')]
        self.assertEquals(list(enumerate_3cliques(ftd)), expect)

    def test_enumerate_3cliques_two(self):
        from_to = [('1', '2'), ('2', '3'), ('3', '1'),
                   ('4', '2'), ('3', '4')]
        ftd = compute_from_to_dictionary(from_to)
        expect = [('1', '2', '3'), ('2', '3', '4')]
        self.assertEquals(list(enumerate_3cliques(ftd)), expect)


class TestMostConnectedPoint(unittest.TestCase):
    def setUp(self):
        """bad example, it's from DistanceMatrixToCoords/issues/5
        """
        self.from_to = [("18", "02"), ("14", "02"), ("14", "21"), ("14", "12"),
                        ("12", "02"), ("12", "21"), ("12", "03"), ("12", "16"),
                        ("16", "21"), ("16", "03"), ("16", "15"), ("16", "07"),
                        ("22", "03"), ("22", "02"), ("22", "10"), ("10", "02"),
                        ("10", "21"), ("10", "03"), ("21", "02"), ("21", "03"),
                        ('12', '18')]

    def test_best_clique(self):
        expect = ('12', '16', '21')
        ftd = compute_from_to_dictionary(self.from_to)
        self.assertEquals(most_connected_3clique(ftd), expect)

    def test_other_best_clique(self):
        self.from_to.extend([("03", "15"), ('02', '16'), ('02', '03'),
                             ('21', '18')])
        ftd = compute_from_to_dictionary(self.from_to)
        expect = ('02', '12', '21')
        self.assertEquals(most_connected_3clique(ftd), expect)

    def test_best_clique_completely_connects_to_most_points(self):
        from_to = [("04", "10"), ("04", "18"), ("04", "19"), ("04", "20"),
                   ("04", "02"), ("10", "18"), ("10", "19"), ("10", "20"),
                   ("10", "02"), ("10", "21"), ("18", "19"), ("18", "20"),
                   ("18", "02"), ("18", "12"), ("12", "14"), ("12", "21"),
                   ("12", "03"), ("12", "16"), ("16", "21"), ("16", "03")]
        ftd = compute_from_to_dictionary(from_to)
        expect = ('04', '10', '18')
        self.assertEquals(most_connected_3clique(ftd), expect)


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
        p = rigid_transform_points(p, x=0, y=0, theta=0)
        self.assertEquals(p['p1']['coordinates'], (1.0, 1.0))
        self.assertEquals(p['p2']['coordinates'], (4.0, 5.0))
        self.assertEquals(p['p3']['coordinates'], (1.0, 5.0))

    def test_rigid_transform_points_only_translate(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        p = rigid_transform_points(p, x=10, y=0, theta=0)
        self.assertEquals(p['p1']['coordinates'], (11.0, 1.0))
        self.assertEquals(p['p2']['coordinates'], (14.0, 5.0))
        self.assertEquals(p['p3']['coordinates'], (11.0, 5.0))
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        p = rigid_transform_points(p, x=0, y=10, theta=0)
        self.assertEquals(p['p1']['coordinates'], (1.0, 11.0))
        self.assertEquals(p['p2']['coordinates'], (4.0, 15.0))
        self.assertEquals(p['p3']['coordinates'], (1.0, 15.0))
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        p = rigid_transform_points(p, x=10, y=10, theta=0)
        self.assertEquals(p['p1']['coordinates'], (11.0, 11.0))
        self.assertEquals(p['p2']['coordinates'], (14.0, 15.0))
        self.assertEquals(p['p3']['coordinates'], (11.0, 15.0))

    def test_rigid_transform_points_rotate_90(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        p = rigid_transform_points(p, x=0, y=0, theta=90)
        assert_almost_equal(p['p1']['coordinates'], (-1.0, 1.0))
        assert_almost_equal(p['p2']['coordinates'], (-5.0, 4.0))
        assert_almost_equal(p['p3']['coordinates'], (-5.0, 1.0))

    def test_rigid_transform_points_rotate_45(self):
        p = {'p1': {'coordinates': (1.0, 0.0)},
             'p2': {'coordinates': (0.0, 1.0)},
             'p3': {'coordinates': (1.0, 1.0)}, }
        p = rigid_transform_points(p, x=0, y=0, theta=45)
        assert_almost_equal(p['p1']['coordinates'], (.70710678, .707106780))
        assert_almost_equal(p['p2']['coordinates'], (-.70710678, .70710678))
        assert_almost_equal(p['p3']['coordinates'], (0, 1.41421356))

    def test_rigid_transform_points_rotate_m90(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        p = rigid_transform_points(p, x=0, y=0, theta=-90)
        assert_almost_equal(p['p1']['coordinates'], (1.0, -1.0))
        assert_almost_equal(p['p2']['coordinates'], (5.0, -4.0))
        assert_almost_equal(p['p3']['coordinates'], (5.0, -1.0))

    def test_rigid_transform_points_move_rotate(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        p = rigid_transform_points(p, x=10, y=10, theta=90)
        assert_almost_equal(p['p1']['coordinates'], (9.0, 11.0))
        assert_almost_equal(p['p2']['coordinates'], (5.0, 14.0))
        assert_almost_equal(p['p3']['coordinates'], (5.0, 11.0))

    def test_rigid_transform_points_leave_input_alone(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        q = rigid_transform_points(p, x=10, y=10, theta=90)
        assert_almost_equal(q['p1']['coordinates'], (9.0, 11.0))
        assert_almost_equal(q['p2']['coordinates'], (5.0, 14.0))
        assert_almost_equal(q['p3']['coordinates'], (5.0, 11.0))
        assert_almost_equal(p['p1']['coordinates'], (1.0, 1.0))
        assert_almost_equal(p['p2']['coordinates'], (4.0, 5.0))
        assert_almost_equal(p['p3']['coordinates'], (1.0, 5.0))


class TestDistanceBetweenHomonyms(unittest.TestCase):

    def test_distance_between_homonyms_zero(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        q = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        distance = distance_between_homonyms(p, q)
        assert_almost_equal(distance, 0.0)

    def test_distance_between_homonyms_nonzero(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        q = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 6.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        distance = distance_between_homonyms(p, q)
        assert_almost_equal(distance, 1.0)
        q = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 6.0)},
             'p3': {'coordinates': (1.0, 4.0)}, }
        distance = distance_between_homonyms(p, q)
        assert_almost_equal(distance, 2.0)
        q = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 7.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        distance = distance_between_homonyms(p, q)
        assert_almost_equal(distance, 4.0)


class TestMinimalDistanceTransformation(unittest.TestCase):

    def test_compute_minimal_distance_transformation_null(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        q = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        x, y, theta = compute_minimal_distance_transformation(p, q)
        assert_almost_equal((x, y, theta), (0.0, 0.0, 0.0))

    def test_compute_minimal_distance_transformation_null(self):
        p = {'p1': {'coordinates': (1.0, 1.0)},
             'p2': {'coordinates': (4.0, 5.0)},
             'p4': {'coordinates': (0.0, 5.0)},
             'p5': {'coordinates': (4.0, 4.0)},
             'p3': {'coordinates': (1.0, 5.0)}, }
        q = {'p1': {'coordinates': (9.0, 11.0)},
             'p2': {'coordinates': (5.0, 14.0)},
             'p4': {'coordinates': (5.0, 10.0)},
             'p5': {'coordinates': (6.0, 14.0)},
             'p3': {'coordinates': (5.0, 11.0)}, }
        x, y, theta = compute_minimal_distance_transformation(p, q)
        assert_almost_equal((x, y, theta), (10.0, 10.0, 90.0), decimal=6)
