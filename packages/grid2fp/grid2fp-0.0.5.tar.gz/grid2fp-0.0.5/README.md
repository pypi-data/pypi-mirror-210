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

g = grid2fp(csv_file=csv_path,draw_crossings=False)
d = g.draw()
d.save_svg(svg_path)

# Option 2
grid2fp(csv_file=csv_path, out_file=svg_path)

# Option 3

g = grid2fp(diagram=diagram)
d = g.draw()
d.save_svg(svg_path)

# Option 4

g = grid2fp(csv_file=csv_path,string_color = "pink", crossing_color="purple")
d = g.draw()
# make some changes to d with drawsvg
d.save_svg(svg_path)

```
# Sample images

x|o| | |
-|-|-|-|
 |x|o|
 | |x|o|
o| | |x|

![random](https://github.com/Joecstarr/grid2fp/assets/52646388/0e22c161-359d-4bb1-a10a-51011e7eefac)

o| | |x| |
-|-|-|-|-|
 | |x| |o|
 |x| |o| |
x| |o| | |
 |o| | |x|

![trefoil](https://github.com/Joecstarr/grid2fp/assets/52646388/f4b49ff9-9630-4ccf-b1e8-f4d9a50013d8)

x| |o|
-|-|-|
 | | |
o| |x|

![un](https://github.com/Joecstarr/grid2fp/assets/52646388/3a080da3-f5aa-4b23-b4b2-a917140cd95a)

 | |o| | |x| |
-|-|-|-|-|-|-|
 | | | |o| |x|
 |x| | | |o| |
o| |x| | | | |
 | | |x| | |o|
 |o| | |x| | |
x| | |o| | | |

![fig1_from_paper](https://github.com/Joecstarr/grid2fp/assets/52646388/d349f4c2-bb07-4e6d-9f29-a69ae518a832)

## ToDo
- [ ] CLI interface
- [x] fit canvas to drawing better.(still not perfect)
- [x] set string color
- [ ] ???
