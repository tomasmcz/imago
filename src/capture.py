#!/usr/bin/env python

"""Go image capture.

This module defines a UI for capturing images with a (web)camera and imediately
proccessing them with Imago.
"""

import os
import sys
import argparse
import time
from threading import Thread
from Queue import Queue, Empty

import pygame
from pygame.locals import QUIT, KEYDOWN
import Image

from camera import Camera

class Screen:
    """Basic PyGame setup."""
    def __init__(self, res):
        pygame.init()
        pygame.display.set_mode(res)
        pygame.display.set_caption("Go image capture")
        self._screen = pygame.display.get_surface()

    def display_picture(self, im):
        """Display image on PyGame screen."""
        pg_img = pygame.image.frombuffer(im.tostring(), im.size, im.mode)
        self._screen.blit(pg_img, (0,0))
        pygame.display.flip()

class Capture:
    """This object maintains communication between the camera, the PyGame screen
    and Imago."""
    def __init__(self, device, res):
        self.cam = Camera(vid=device, res=res)
        self.screen = Screen(res)

        self.im_number = 0

        self.saving_dir = "./captured/" + time.strftime("%Y-%m-%d %H:%M/")

        if not os.path.isdir(self.saving_dir):
            os.makedirs(self.saving_dir)

    def __del__(self):
        del self.cam

    def live(self, q):
        """Run live preview on the screen."""
        clock = pygame.time.Clock()
        done = False
        while not done: 
            if q:
                try:
                    line = q.get_nowait() # or q.get(timeout=.1)
                except Empty:
                    pass
                else:
                    if line == "stop\n":
                        done = True
                    elif line == "exit\n":
                        sys.exit()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        done = True

            im = self.cam.get_image()
            self.screen.display_picture(im)
            clock.tick(5)

    def auto(self, interval):
        """Take new image every *interval* seconds.""" #TODO or is it milisecs?
        last = 0
        clock = pygame.time.Clock()

        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            if time.time() - last > interval:
                last = time.time()
                self.take()
            clock.tick(15)

    def manual(self):
        """Take images manualy by pressing a key."""
        while True:
            event = pygame.event.wait()
            if event.type == QUIT:
                break
            if event.type != KEYDOWN:
                continue
            self.take()
            
    def take(self):
        """Take a new image from the camera."""
        print "taking pic"
        im = self.cam.get_image()
        self.screen.display_picture(im)
        im.save(self.saving_dir + "{0:0>3}.jpg".format(self.im_number), 'JPEG')
        self.im_number += 1


def main():
    """Parse the argument and setup the UI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--cmd', dest='cmd', action='store_true',
                    help="take commands from stdin")
    parser.add_argument('-d', type=int, default=0,
                        help="video device id")
    parser.add_argument('-a', type=int, default=0,
                        help="take picture automaticaly every A seconds")
    parser.add_argument('-r', type=int, nargs=2, default=[640, 480],
                        help="set camera resolution")
    args = parser.parse_args()

    res=(args.r[0], args.r[1])
    capture = Capture(args.d, res)


    if args.cmd:
        def enqueue_input(queue):
            for line in iter(sys.stdin.readline, b''):
                queue.put(line)

        q = Queue()
        t = Thread(target=enqueue_input, args=(q,))
        t.daemon = True 
        t.start()
        
        capture.live(q)

        clock = pygame.time.Clock()

        while True:
            try:
                line = q.get_nowait() # or q.get(timeout=.1)
            except Empty:
                pass
            else: 
                if line == "take\n":
                    capture.take()
                elif line == "exit\n":
                    break
            clock.tick(10)

    else:
        capture.live(None)
        if args.a > 0:
            capture.auto(args.a)
        else:
            capture.manual()

    del capture
    
if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
