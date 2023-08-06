"""
TODO: Update Brief.

TODO: Update Description.

"""
from grid2fp.grid2fp import grid2fp
import os
from pathlib import Path

file_location = Path(os.path.dirname(__file__))


def test_un():
    """TODO: Update Testcase description."""
    g = grid2fp(csv_file=file_location / "un.csv")
    g.draw(file_location / "un.svg")
    assert 1 == 1


def test_random():
    """TODO: Update Testcase description."""
    g = grid2fp(csv_file=file_location / "random.csv")
    g.draw(file_location / "random.svg")
    assert 1 == 1


def test_trefoil():
    g = grid2fp(csv_file=file_location / "trefoil.csv")
    g.draw(file_location / "trefoil.svg")
    assert 1 == 1
