"""The grid segment file."""


class grid_segment:
    """The grid segment class."""

    def __init__(self, source: tuple = None, sink: tuple = None):
        """Init for the grid_segment object.

        Parameters
        ----------
        source : tuple, optional
            coordinate for the source, by default None
        sink : tuple, optional
            coordinate for the sink, by default None
        """
        self.source = source
        self.sink = sink
