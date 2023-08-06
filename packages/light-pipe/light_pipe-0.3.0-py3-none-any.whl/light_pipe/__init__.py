__author__ = "Richard Correro (richard@richardcorrero.com)"


from .data import *
from .parallelizer import *
from .transformer import *

__doc__ = """
# [Light-Pipe](https://github.com/rcorrero/light-pipe)

---

## Overview

[Light-Pipe](https://www.light-pipe.io/) is an extensible, light-weight Python framework for data pipelines that scale. It provides a set of intuitive abstractions designed to decouple pipeline implementation from the operations they perform. It is designed to scale effortlessly, being built from the ground-up to support concurrency in all its forms, and it has zero non-standard dependencies. It's also super fast and efficient, used to perform critical geospatial data processing tasks [at least an order of magnitude faster than existing systems](https://github.com/rcorrero/light-pipe/blob/depth_first/data/plots/test_geo_tiling.png).

Light-Pipe is released under a [BSD-3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

## More Information

- [GitHub](https://github.com/rcorrero/light-pipe)

- [Documentation](https://www.light-pipe.io/)

---

Copyright 2020-2023 [Richard Correro](https://www.richardcorrero.com/).
"""
