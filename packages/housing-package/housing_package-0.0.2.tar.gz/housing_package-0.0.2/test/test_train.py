import unittest
import pathlib as pl


class TestCase(unittest.TestCase):
    def test_linear_regression(self):
        # ...
        path = pl.Path("data/models/linear_regression.pkl")
        self.assertTrue(path.is_file())
        self.assertTrue(path.parent.is_dir())

    def test_randomforest_regression(self):
        # ...
        path = pl.Path("data/models/randomforest_regression.pkl")
        self.assertTrue(path.is_file())
        self.assertTrue(path.parent.is_dir())

    def test_tree_regression(self):
        # ...
        path = pl.Path("data/models/tree_regression.pkl")
        self.assertTrue(path.is_file())
        self.assertTrue(path.parent.is_dir())


if __name__ == "__main__":
    unittest.main(verbosity=2)
