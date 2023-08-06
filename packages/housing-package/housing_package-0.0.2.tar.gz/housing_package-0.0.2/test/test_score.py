import unittest
import pathlib as pl


class TestCase(unittest.TestCase):
    def test_score(self):
        # ...
        path = pl.Path("data/models/score.csv")
        self.assertTrue(path.is_file())
        self.assertTrue(path.parent.is_dir())


if __name__ == "__main__":
    unittest.main(verbosity=2)
