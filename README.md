# Imago Go Image Recognition

[![Build Status](https://travis-ci.org/tomasmcz/imago.svg?branch=master)](https://travis-ci.org/tomasmcz/imago)

http://tomasm.cz/imago

There is also an experimantal [Haskell version of Imago](https://github.com/tomasmcz/imago-hs).

## Requirements

- Python 2.7 (including dev)
- PIL >= 3.0
- pygame
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
