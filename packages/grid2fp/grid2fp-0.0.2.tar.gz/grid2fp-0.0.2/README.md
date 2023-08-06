# grid2fp

A tool to eat grid diagrams and generate its front projections.

## Disclaimer
The tool is lightly tested. I would expect bugs and strange behavior. If you find something make an issue.

## Installation

Install with pip:

```
pip install grid2fp
```

## Usage

### CLI
Doesn't exist.
## Scripting


```python
from grid2fp import grid2fp
import drawsvg as draw



csv_path = "path"
svg_path = "path"

diagram = [["x","","o"],["","",""],["o","","x"]]


# Option 1

g = grid2fp(csv_file=csv_path)
d = g.draw()
d.save_svg(svg_path)

# Option 2
grid2fp(csv_file=csv_path, out_file=svg_path)

# Option 3

g = grid2fp(diagram=diagram)
d = g.draw()
d.save_svg(svg_path)

# Option 4

g = grid2fp(csv_file=csv_path)
d = g.draw()
# make some changes to d with drawsvg
d.save_svg(svg_path)

```

## ToDo
- [ ] CLI interface
- [ ] fit canvas to drawing better.
- [ ] set string color
- [ ] ???
