import unittest
import pandas as pd


def check_null(data):
    return data.isnull().values.any()


train = pd.read_csv("data/train/train.csv")

test = pd.read_csv("data/test/test.csv")

train_labels = pd.read_csv("data/train/train_labels.csv")

test_labels = pd.read_csv("data/test/test_labels.csv")


class MyTest(unittest.TestCase):
    def test_train(self):
        self.assertEqual(check_null(train), False)

    def test_test(self):
        self.assertEqual(check_null(test), False)

    def test_strat_train(self):
        self.assertEqual(check_null(train_labels), False)

    def test_strat_test(self):
        self.assertEqual(check_null(test_labels), False)


if __name__ == "__main__":
    unittest.main()
