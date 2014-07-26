#!/usr/bin/env python

"""Go image recognition."""

import sys
import os
import argparse
import pickle

try:
    from PIL import Image, ImageDraw
except ImportError, msg:
    print >> sys.stderr, msg
    sys.exit(1)

import linef
import intrsc
import gridf3 as gridf
import output

def argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', metavar='file', nargs='+',
                        help="image to analyse")
    parser.add_argument('-w', type=int, default=640,
                    help="scale image to the specified width before analysis")
    parser.add_argument('-m', '--manual', dest='manual_mode',
                        action='store_true',
                        help="manual grid selection")
    parser.add_argument('-d', '--debug', dest='show_all',
                        action='store_true',
                        help="show every step of the computation")
    parser.add_argument('-s', '--save', dest='saving', action='store_true',
                        help="save images instead of displaying them")
    parser.add_argument('-c', '--cache', dest='l_cache', action='store_true',
                        help="use cached lines")
    parser.add_argument('-S', '--sgf', dest='sgf_output', action='store_true',
                        help="output in SGF")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help="report progress")
    return parser
 

# TODO factor this into smaller functions
def main():
    """Main function of the program."""
    
    parser = argument_parser()
    args = parser.parse_args()

    show_all = args.show_all
    verbose = args.verbose

    try:
        image = Image.open(args.files[0])
    except IOError, msg:
        print >> sys.stderr, msg
        return 1
    if image.mode == 'P':
        image = image.convert('RGB')
    
    if image.size[0] > args.w:
        image = image.resize((args.w, int((float(args.w)/image.size[0]) *
                              image.size[1])), Image.ANTIALIAS)

    if not show_all:
        def nothing(a, b):
            pass
        do_something = nothing
    elif args.saving:
        do_something = Imsave("saved/" + args.files[0][:-4] + "_" +
                               str(image.size[0]) + "/").save
    else:
        import im_debug
        do_something = im_debug.show

    if verbose:
        import time
        class Logger:
            def __init__(self):
                self.t = 0

            def __call__(self, m):
                t_n = time.time()
                if self.t > 0:
                    print >> sys.stderr, "\t" + str(t_n - self.t)
                print >> sys.stderr, m
                self.t = t_n
        logger = Logger()

    else:
        def logger(m):
            pass
        
    if args.manual_mode:
        import manual
        try:
            lines = manual.find_lines(image)
        except manual.UserQuitError:
            #TODO ask user to try again
            return 1
    else:
        if args.l_cache:
            filename = ("saved/cache/" + args.files[0][:-4] + "_" +
                       str(image.size[0]))
            cache_dir = "/".join(filename.split('/')[:-1])
            if os.path.exists(filename):
                lines, l1, l2, bounds, hough = pickle.load(open(filename))
                print >> sys.stderr, "using cached results"
            else:
                lines, l1, l2, bounds, hough = linef.find_lines(image, do_something, logger)
                if not os.path.isdir(cache_dir):
                    os.makedirs(cache_dir)
                d_file = open(filename, 'wb')
                pickle.dump((lines, l1, l2, bounds, hough), d_file)
                d_file.close()
        else:
            lines, l1, l2, bounds, hough = linef.find_lines(image, do_something, logger)
            #d_file = open('lines09.pickle', 'wb')
            #pickle.dump(lines, d_file)
            #d_file.close() #TODO delete this


        grid, lines = gridf.find(lines, image.size, l1, l2, bounds, hough,
                                 show_all, do_something, logger)
        if show_all:
            im_g = image.copy()
            draw = ImageDraw.Draw(im_g)
            for l in grid[0] + grid[1]:
                draw.line(l, fill=(64, 255, 64), width=1)
            do_something(im_g, "grid", name="grid")

    intersections = intrsc.b_intersects(image, lines, show_all, do_something, logger)
    board = intrsc.board(image, intersections, show_all, do_something, logger)

    logger("finished")

    # TODO! refactor this mess:
    if len(args.files) == 1:

        if args.sgf_output:
            print board.asSGFsetPos()
        else:
            print board
    
    else:
        game = output.Game(19, board) #TODO size parameter
        for f in args.files[1:]:
            try:
                image = Image.open(f)
            except IOError, msg:
                print >> sys.stderr, msg
                continue
            if verbose:
                print >> sys.stderr, "Opening", f
            if image.mode == 'P':
                image = image.convert('RGB')
            if image.size[0] > args.w:
                image = image.resize((args.w, int((float(args.w)/image.size[0]) *
                              image.size[1])), Image.ANTIALIAS)
            board = intrsc.board(image, intersections, show_all, do_something, logger)
            if args.sgf_output:
                game.addMove(board)
            else:
                print board

        if args.sgf_output:
            print game.asSGF()

    return 0

class Imsave():
    def __init__(self, saving_dir):
        self.saving_dir = saving_dir
        self.saving_num = 0

    def save(self, image, title='', name=None):
        im_format = ('.png', 'PNG')
        if name:
            filename = self.saving_dir + name + im_format[0]
        else:
            filename = self.saving_dir + "{0:0>3}".format(self.saving_num) + im_format[0]
            self.saving_num += 1
        if not os.path.isdir(self.saving_dir):
            os.makedirs(self.saving_dir)
        image.save(filename, im_format[1])

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt: #TODO does this work?
        print >> sys.stderr, "Interrupted."
        sys.exit(1)
