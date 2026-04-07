# glomerular-segment-matcher

[![PyPI](https://img.shields.io/pypi/v/glomerular-segment-matcher.svg?color=green)](https://pypi.org/project/glomerular-segment-matcher)
[![tests](https://github.com/Ananya-Sundararajan/glomerular-segment-matcher/workflows/tests/badge.svg)](https://github.com/Ananya-Sundararajan/glomerular-segment-matcher/actions)
[![npe2](https://img.shields.io/badge/plugin-npe2-blue?link=https://napari.org/stable/plugins/index.html)](https://napari.org/stable/plugins/index.html)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)

A simple plugin used to manually match segments of same anatomical structure across slices (3D reconstruction).

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template] (None).

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/napari-plugin-template#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## Data Folders Set Up
Create a directory with 2 folders labeled "images" and "masks."
If reconstructed masks are also available, you can also have a 3rd folder in the directory labeled "reconstructed."

This plugin only accepts .tif or .png across all three folders that may be given as input. When dragging and dropping the directory into napari, make sure to open with "Glomerular Segment Matcher."

## Installation

You can install `glomerular-segment-matcher` via [pip]:

```bash
pip install glomerular-segment-matcher
```

If napari is not already installed, you can install `glomerular-segment-matcher` with napari and Qt via:

```bash
pip install "glomerular-segment-matcher[all]"
```


To install latest development version:

```bash
pip install git+https://github.com/Ananya-Sundararajan/glomerular-segment-matcher.git
```



## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"glomerular-segment-matcher" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[file an issue]: https://github.com/Ananya-Sundararajan/glomerular-segment-matcher/issues

[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
