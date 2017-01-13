import unittest

from ghini_tree_position import almost_parallel, normalize


class UtilsTest(unittest.TestCase):
    def test_normalize_null(self):
        null_vector = (0, 0, 0)
        self.assertEquals(normalize(null_vector), null_vector)

    def test_normalize_not_null(self):
        vector = (0, 3, 4)
        expected = (0, 0.6, 0.8)
        self.assertFalse(any(normalize(vector) - expected))

    def test_almost_parallel_vectors_not(self):
        u, v = [1, 0, 0], [0, 1, 0]
        self.assertFalse(almost_parallel(u, v))

    def test_almost_parallel_matrix_not(self):
        import numpy as np
        A = np.array([[1, 0, 0], [0, 1, 0]])
        self.assertFalse(almost_parallel(A))

    def test_almost_parallel_vectors_precisely(self):
        import numpy as np
        A = np.array([[1, 1, 0], [2, 2, 0]])
        self.assertTrue(almost_parallel(A))

    def test_almost_parallel_matrix_almost(self):
        import numpy as np
        A = np.array([[1, 0, 0], [1999, 1, -1]])
        self.assertTrue(almost_parallel(A))

    def test_almost_parallel_vectors_precisely(self):
        u, v = [1, 1, 0], [2, 2, 0]
        self.assertTrue(almost_parallel(u, v))

    def test_almost_parallel_vectors_almost(self):
        u, v = [1, 0, 0], [1999, 1, -1]
        self.assertTrue(almost_parallel(u, v))
