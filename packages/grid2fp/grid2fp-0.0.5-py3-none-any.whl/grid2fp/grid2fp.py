"""The grid2fp file.

The class takes a grid diagram to a picture of the front project for a
Legendrian knot.

"""
import drawsvg as draw
import math
import csv
from grid2fp.grid_segment import grid_segment


class grid2fp:
    """The grid2fp class."""

    def __init__(
        self,
        csv_file=None,
        diagram=None,
        eccentricity=0.9,
        scale=10,
        out_file=None,
        draw_crossings=True,
        string_color="black",
        crossing_color="white",
    ) -> None:
        """Init for the grid2fp object.

        Parameters
        ----------
        csv_file : str, optional
            The location of grid diagram as csv, by default None
        diagram : array, optional
            A grid diagram, by default None
        eccentricity : float, optional
            How far away to place the
            Bézier controls, by default 0.9
        out_file : str
            The output file, by default None
        """
        self.diagram = []
        if csv_file is None and diagram is None:
            raise Exception("You need a csv file or a diagram")

        if csv_file:
            with open(csv_file) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    self.diagram.append(row)

        if diagram:
            self.diagram = diagram
        self.eccentricity = eccentricity
        self.draw_crossings = draw_crossings
        self.string_color = string_color
        self.crossing_color = crossing_color
        self.scale = scale
        self.segments = []
        self.__get_segments()
        if out_file:
            d = self.draw()
            d.save_svg(out_file)

    def __rotate(self, x, y):
        """Do a 45 degree rotation of the point.

        Parameters
        ----------
        x : int
            the x coord
        y : int
            the y coord

        Returns
        -------
        tuple
            rotated cord as tuple
        """
        r = 1 / math.sqrt(2)
        return (-x * r - y * r) * self.scale, (-x * r + y * r) * self.scale

    def __get_segments(self):
        """Parse the grid for segments."""
        self.segments.extend(self.__get_segments_horizontal())
        self.segments.extend(self.__get_segments_vertical())

    def __get_segments_horizontal(self):
        """Parse the grid for horizontal segments.

        Returns
        -------
        grid_segment
            The segment.
        """
        segments = []
        for i, row in enumerate(self.diagram):
            seg = None
            for j, c in enumerate(row):
                if c.strip() != "":
                    if seg is None:
                        seg = grid_segment()
                    if c.strip().lower() == "x":
                        seg.sink = (j, i)
                    if c.strip().lower() == "o":
                        seg.source = (j, i)
            if seg is not None:
                segments.append(seg)
        return segments

    def __get_segments_vertical(self):
        """Parse the grid for vertical segments.

        Returns
        -------
        grid_segment
            The segment.
        """
        segments = []
        for j, c in enumerate(self.diagram[0]):
            seg = None
            for i, row in enumerate(self.diagram):
                if row[j].strip() != "":
                    if seg is None:
                        seg = grid_segment()
                    if row[j].strip().lower() == "x":
                        seg.source = (j, i)
                    if row[j].strip().lower() == "o":
                        seg.sink = (j, i)
            if seg is not None:
                segments.append(seg)
        return segments

    def __draw_segment(self, step):
        """Draws a segment of the front projection as a Bézier curve.

        Parameters
        ----------
        step : grid_segment
            The segment to draw.

        Returns
        -------
        Group
            The svg path segments contained in a group.
        """
        x, y = self.__rotate(step.source[0], step.source[1])
        x2, y2 = self.__rotate(step.sink[0], step.sink[1])
        delta_x = x2 - x
        x_ctr1 = x + (self.eccentricity * delta_x)
        x_ctr2 = x2 - (self.eccentricity * delta_x)
        g = draw.Group()
        if self.draw_crossings:
            p = draw.Path(
                stroke_width=0.2 * self.scale,
                stroke=self.crossing_color,
            )
            p.M(x, y)
            p.C(x_ctr1, y, x_ctr2, y2, x2, y2)
            g.append(p)
        p = draw.Path()
        p.M(x, y)
        p.C(x_ctr1, y, x_ctr2, y2, x2, y2)
        g.append(p)

        return g

    def draw(self, pixel_scale=2):
        """Draws the front projection of the given grid as an SVG.

        Parameters
        ----------
        pixel_scale : int, optional
            The scaling for pixel features, by default 2
        scale : int
            The scale factor for the file

        Returns
        -------
        Drawing
            The svg for the grid diagram.

        """
        try:
            d = draw.Drawing(
                self.scale * math.sqrt(2) * len(self.diagram[0]),
                self.scale * math.sqrt(2) * len(self.diagram[0]),
                origin=(0, 0),
                id_prefix="d",
            )
            g = draw.Group(
                stroke_width=0.1 * self.scale,
                stroke=self.string_color,
                fill="none",
                transform=f"translate({self.scale* math.sqrt(2)*len(self.diagram[0])},{self.scale* math.sqrt(2)*len(self.diagram[0])/2})",
            )
            for step in self.segments:
                p = self.__draw_segment(step)
                g.append(p)
            d.append(g)

            d.set_pixel_scale(pixel_scale)
            return d
        except Exception as err:
            print(
                f"Unexpected {err=}, {type(err)=}, this is probably because the grid diagram is broken in some way."
            )
