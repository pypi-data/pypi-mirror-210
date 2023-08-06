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
    grid2fp(csv_file=file_location / "un.csv", out_file=file_location / "un.svg")
    assert 1 == 1


def test_random():
    """TODO: Update Testcase description."""
    g = grid2fp(csv_file=file_location / "random.csv",string_color = "pink",
        crossing_color="purple")
    d = g.draw()
    d.save_svg(file_location / "random.svg")
    assert 1 == 1


def test_trefoil():
    g = grid2fp(csv_file=file_location / "trefoil.csv")
    d = g.draw()
    d.save_svg(file_location / "trefoil.svg")
    assert 1 == 1


def test_fig1():
    g = grid2fp(csv_file=file_location / "fig1_from_paper.csv")
    d = g.draw()
    d.save_svg(file_location / "fig1_from_paper.svg")
    assert 1 == 1
