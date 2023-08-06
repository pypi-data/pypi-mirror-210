import os


def pytest_configure():
    os.environ["KLU_ENV"] = "dev"


def pytest_unconfigure():
    del os.environ["KLU_ENV"]
