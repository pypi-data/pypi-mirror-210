import pandas as pd
import importlib
import unittest

pkg_list = pd.read_csv("test/installed_packages_list.csv")

pkg_not_installed = []


def installation_check(package):
    is_present = importlib.util.find_spec(package.split("==")[0])
    if is_present is None:
        return True
    else:
        return False


for package in pkg_list["0"]:
    if installation_check(package) == True:
        pkg_not_installed.append(package)


class TestCase(unittest.TestCase):
    def test_installation(self):
        self.assertTrue(len(pkg_not_installed) == 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
