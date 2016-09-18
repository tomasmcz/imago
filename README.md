# Imago Go Image Recognition

[![Build Status](https://travis-ci.org/tomasmcz/imago.svg?branch=master)](https://travis-ci.org/tomasmcz/imago)
[![Documentation Status](https://readthedocs.org/projects/imago/badge/?version=latest)](http://imago.readthedocs.io/en/latest/?badge=latest)

http://tomasm.cz/imago

There is also an experimantal [Haskell version of Imago](https://github.com/tomasmcz/imago-hs).

## Requirements

- Python 2.7 (including dev)
- PIL >= 3.0
- pygame
- matplotlib (for generating debug images)
- openCV (if you want to use a camera, otherwise not needed)
- for documentation:
    - sphinx
    - sphinx-argparse

## Installation

Run `make` in this directory.

## Usage

Run `./imago image.jpg` to extract game position from image.jpg.
Run `./imago -m image.jpg` to manually select grid position.
Run `./imago image000.jpg image001.jpg image002.jpg ...` to produce a game record from a sequence of images, one for every move. Use `-S` option to select SGF output. 
Run `./imago --help` for help and list of all options.

## Tests

The imago test suite lives in the
[imago-tests](https://github.com/tomasmcz/imago-tests) repository, which is a 
[submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) of this repository.
Run `git submodule init; git submodule update` (or clone this repository with
`git clone --recursive`) to get the test data. 

To run the tests, build imago and run `./runtests` from the root of the
working directory.

The runtests program runs imago on each input image and compares the
output to the expected.  Any discrepancy is a test failure.

Failing tests can be disabled by moving them into a directory named
"skip".  "skip" directories are by default ignored by the runtests
program.  Run `./runtests --all` to include tests marked "skip".

## Contributors

- Tomáš Musil (@tomasmcz)
- Sebastian Kuzminsky (@SebKuzminsky)
