# Imago Go Image Recognition

http://tomasm.cz/imago

## Requirements

- Python 2.7 (including dev)
- PIL
- pygame
- openCV (if you want to use a camera, otherwise not needed)
- for documentation:
    - sphinx
    - sphinx-argparse

## Installation

Run `make install` in this directory.

## Usage

Run `./imago image.jpg` to extract game position from image.jpg.
Run `./imago -m image.jpg` to manually select grid position.
Run `./imago image000.jpg image001.jpg image002.jpg ...` to produce a game record from a sequence of images, one for every move. Use `-S` option to select SGF output. 
Run `./imago --help` for help and list of all options.

