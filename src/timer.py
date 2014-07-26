#!/usr/bin/env python

"""Go timer.

This module defines a UI that combines game clock with automatic game recording.
When player presses the clock, an image of the board is taken. The sequence of
images can later be analysed by Imago to produce a game record in abstract
notation.
"""

import os
import sys
import time
import argparse
import subprocess

import pygame

class Timer:
    """Keeps track of time remaining one player."""
    def __init__(self, main_time, byop, byot):
        self._last = 0
        self._elapsed = 0.
        self._main_t = main_time
        self.byost = "main time"
        self._byop = byop + 1
        self._byot = byot
        self._byo = False

    def get_time(self):
        """Return string representation of remaining time."""
        if self._last > 0: # when running:
            r_time = self._main_t - (time.time() - self._last + self._elapsed)
            if (r_time - int(r_time)) < 0.75:
                sep = ":"
            else:
               sep = " "
        else: # not running:
            if self._byo and self._byop > 0:
                self._elapsed = 0
            r_time = self._main_t - self._elapsed
            sep = ":"
        if r_time < 0:
            self._byo = True
            self._main_t = self._byot
            self._byop -= 1
            if self._byop > 0:
                self._elapsed = 0
                self._last = time.time()
                self.byost = "(" + str(self._byop) + ")"
                return self.get_time()
            else:
                r_time = 0
                self.byost = "lost on time"
        return "{0:0>2}".format(int(r_time / 60)) + sep + "{0:0>2}".format(int(r_time % 60))

    def start(self):
        """Start the clock."""
        self._last = time.time()

    def stop(self):
        """Stop the clock."""
        self._elapsed += time.time() - self._last
        self._last = 0

    def is_running(self):
        """Return True if the clock is running."""
        if self._last > 0:
            return True
        else:
            return False

def main():
    """Parse the arguments and run the clock."""
    # TODO refactor into smaller functions
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-m', type=int, default=10,
                        help="main time in minutes (default is 10)")
    parser.add_argument('-b', type=int, nargs=2, default=[5, 20],
                        help="japanese byoyomi: number of periods, period length in"
                            " seconds (default is 5 periods, 20 seconds)")
    parser.add_argument('-c', '--camera', dest='cam', action='store_true',
                        help="camera on")
    parser.add_argument('-d', type=int, default=0,
                        help="video device id")
    parser.add_argument('-r', type=int, nargs=2, default=[640, 480],
                        help="set camera resolution")
    args = parser.parse_args()


    pygame.init()
    pygame.display.set_mode((600, 130))
    pygame.display.set_caption("Go timer")
    screen = pygame.display.get_surface()

    clock = pygame.time.Clock()

    font = pygame.font.Font(pygame.font.match_font('monospace'), 80)
    font2 = pygame.font.Font(None, 25)

    done = False
    first = True

    main_time = args.m * 60

    timers = (Timer(main_time, args.b[0], args.b[1]), Timer(main_time, args.b[0], args.b[1]))

    if args.cam:
        capture = subprocess.Popen(['python', 'src/capture.py', '-c', '-d', str(args.d), '-r',
                          str(args.r[0]),
                          str(args.r[1])], stdin=subprocess.PIPE)
    last = 0

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if time.time() - last < 0.7:
                    continue
                last = time.time()
                if first:
                    timers[0].start()
                    first = False
                    if args.cam:
                        print >> capture.stdin, "stop"
                        print >> capture.stdin, "take"
                    continue
                if args.cam:
                    print >> capture.stdin, "take"
                for timer in timers:
                    if timer.is_running():
                        timer.stop()
                    else:
                        timer.start()

        screen.fill([0, 0, 0])
        text1 = font.render(timers[0].get_time(), True, [128, 255, 128])
        screen.blit(text1, [10, 10])
        text2 = font.render(timers[1].get_time(), True, [128, 255, 128])
        screen.blit(text2, [300, 10])
        text3 = font2.render(timers[0].byost, True, [128, 255, 128])
        screen.blit(text3, [10, 90])
        text4 = font2.render(timers[1].byost, True, [128, 255, 128])
        screen.blit(text4, [300, 90])
        pygame.display.flip()
        clock.tick(15)

    if args.cam:
        print >> capture.stdin, "exit"

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
