# PicoHarp 300 TCSPC .phd file loader

This module was written to be able to read in `.phd` photon time histograms from the PicoHarp software.

The layout of the file is as documented in the [PicoHarp 300 manual](http://ridl.cfd.rit.edu/products/manuals/PicoQuant/PicoHarp%20300%20v2.3/manual/Manual.pdf) in section 8.2.1 (pages 56-58).

Both of these are easy to modify, however the scope of this projec tis limited to our usage case.

The module also loads `.txt` files which are the copy-pasted data from the PicoHarp software. This is primary way our research group has extracted data in the past, so it makes sense to keep the functionality alive.

## Installation

```bash
pip install phdimporter
```

## Usage

The module only uses one `struct` import and contains one class of importance, `TRF`.

```python
from phd import TRF

trf = phd('path/to/file/.phd')
## or
trf = phd('path/to/file/.txt')
```

The most simple way to return the histogram data is to:

```python
x = trf.x # bins in ns
y = trf.y # counts/bin
```

It is possible to pull raw data out from the .phd file since it's all stored in the `TRF` object, however I'm not going to document this as the variables share the same names as in the PicoHarp manual, and are easily seen in phd.py.

## Not Implemented

The importer has been written with a couple of limitations in mind that are based on our usage:

* Assumes only one histogram per file
* Assumes only one PicoHarp device on the machine

The only variable I haven't implemented is the acquisition time, as the computer that we use is not internet connected and the clock is always off, and I'm also not sure how to interpret the `time_t` data type that the variable is stored in.

