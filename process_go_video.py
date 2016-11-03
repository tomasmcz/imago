#!/usr/bin/env python

"""
This is a script by Nicolas Rochette for analysing this video:
https://www.youtube.com/watch?v=_8piw9YtVmM
"""

import sys, os, math, time, cv2
from PIL import Image
from src import imago, linef, intrsc, gridf_new as gridf, output

debug = False
debug_dir = './tmp'
debug_save_steps = False
skip241 = False # Andrew's sleeve creates a black stone in the bottom left corner in frame 241.

# Arguments.
class Args :
    def __init__ (self) :
        self.video_path = './sibicky206.mp4' # This game starts at 2:50, ends at 1:58:15.
        self.start = self.str_to_secs('2:50')
        self.end = self.str_to_secs('10:00')
        self.step = 1.0
        self.all_boards_path = None #'all_boards'
    def str_to_secs (self, str) :
        return sum([ float(x)*pow(60, i) for i, x in enumerate(reversed( str.split(':') )) ])

# Some defs.
def void(*args) :
    pass

class Logger:
    # For ImaGo functions
    def __init__(self):
        self.t = 0
    def __call__(self, m):
        t_n = time.time()
        if self.t > 0:
            print >>sys.stderr, '%.2f' % (t_n - self.t)
            print >>sys.stderr, m
        self.t = t_n

def retrieve_frame(frame, video) :
    video.set(1, frame)
    success, image_array = video.read()
    image = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB), 'RGB')
    return image

def process_image(image, imago_save_path) :
    logger = Logger() if debug else void
    save_steps = imago.Imsave(imago_save_path).save if debug_save_steps else void

    lines, l1, l2, bounds, hough = linef.find_lines(image, save_steps, logger)
    grid, lines = gridf.find(lines, image.size, l1, l2, bounds, hough, debug, save_steps, logger)
    intersections = intrsc.b_intersects(image, lines, debug, save_steps, logger)
    board = intrsc.board(image, intersections, debug, save_steps, logger)

    board.stones = ''.join(board.stones) # board.stones list to str    
    return board

def video_to_boards(video, start, end, step) :
    all_boards = [] # [ (t, board) ]
    
    t = start - step
    bad_series=0
    while t < end - step + 0.01 :
        t += step
    
        if skip241 and abs(t-241) < 0.01 :
            print >>sys.stderr, 'Skipped the 241th second'
            continue

        # Get the image
        f = int(round(t * v.get(cv2.cv.CV_CAP_PROP_FPS)))
        fid = '%09.2f' % (f / v.get(cv2.cv.CV_CAP_PROP_FPS))
        print >>sys.stderr, fid
        image = retrieve_frame(f, v)
        png_save_path = '%s/%s.png' % (debug_dir, fid)
        if debug:
            image.save(png_save_path)
    
        # Process the image.
        try :
            imago_save_path = '%s/%s.d/' % (debug_dir, fid)
            board = process_image(image, imago_save_path)
        except gridf.GridFittingFailedError :
            print >>sys.stderr, 'Failed to process frame %s' % fid
            continue

        # Save the board
        all_boards.append( (fid, board) )

    return all_boards

def rotate_board(board) :
    # Rotates the board clockwise.
    n = board.size
    r = output.Board(board.size, [ '.' for i in range(n*n) ])
    for i in range(n) :
        for j in range(n) :
            if board.stones[n*i+j] != '.' :
                r.stones[n*j + n-i-1] = board.stones[n*i+j]

    r.stones = ''.join(r.stones)
    return r

class Diff :
    def __init__(self, i, j, old, new) :
        self.i = i
        self.j = j
        self.old = old
        self.new = new
    def __str__(self) :
        return '%d,%d/%s:%s' % (self.i+1, self.j+1, self.old, self.new)
    def apply_to(self, board) :
        new_board = output.Board(board.size, None)
        ij = self.i * board.size + self.j
        new_board.stones = board.stones[:ij] + self.new + board.stones[ij+1:]
        return new_board

def compare_boards(board, prev_board) :
    if board.size != prev_board.size :
        raise
    n = board.size

    board90 = rotate_board(board)
    board180 = rotate_board(board90)
    board270 = rotate_board(board180)

    boards = [board, board90, board180, board270]
    diffs = [[], [], [], []] # [diffs, diffs90, diffs180, diffs270] where diffs is [ Diff ]
    
    for r in range(4) :
         b = boards[r]
         d = diffs[r]
         for ij in range(n*n) :
             if b.stones[ij] != prev_board.stones[ij] :
                 d.append( Diff(ij//n, ij%n, prev_board.stones[ij], b.stones[ij]) ) # n.b. prev_board.stones[n*diff.i + diff.j] makes sense
                 if len(d) > len(diffs[0]) :
                     break
    
    n_diffs = [ len(d) for d in diffs ]
    d_min = diffs[ n_diffs.index(min(n_diffs)) ] # n.b. may be ambiguous
    return d_min

def process_boards(all_boards) :
    boards = [] # [ (t, board, last_player) ]
    bad_series = 0
    for fid, board in all_boards:
        bad_series += 1
        if bad_series > 30 :
            print >>sys.stderr, 'I\'m lost'
            break

        # Process the board.
        if not boards :
            print >>sys.stderr, 'First board %s' % fid
            print >>sys.stderr, board
            boards.append( (fid, board, None) )
            bad_series = 0
            continue
    
        expected_player = 'B' if boards[-1][2] in {'W', None} else 'W'
        diffs = compare_boards(board, boards[-1][1])

        if len(diffs) == 0 :
            print >>sys.stderr, 'Discarding identical board %s' % fid
            bad_series = 0
            continue
        
        if len(diffs) > 2 :
            print >>sys.stderr, 'Discarding board %s -- multiple (%d) changes : %s' % (fid, len(diffs), [str(d) for d in diffs])
            continue
        
        if not all([d.old == '.' for d in diffs]) :
            print >>sys.stderr, 'Discarding board %s -- illegal change(s) : %s' % (fid, [str(d) for d in diffs])
            continue
    
        if len(diffs) == 1 and diffs[0].new == expected_player :
            print >>sys.stderr, 'Saving board %s : %s' % (fid, [str(d) for d in diffs])
            boards.append( (fid, board, diffs[0].new) )
            bad_series = 0

        elif len(diffs) == 2 and {diffs[0].new, diffs[1].new} == {'B', 'W'} :
            if diffs[0].new == expected_player :
                first_diff = diffs[0]        
                second_diff = diffs[1]
            else :
                first_diff = diffs[1]
                second_diff = diffs[0]
            print >>sys.stderr, 'Saving two boards for %s: %s' % (fid, [str(first_diff), str(second_diff)])
            first_board = first_diff.apply_to(boards[-1][1])
            second_board = second_diff.apply_to(first_board)
            boards.append( (fid, first_board, first_diff.new) )
            boards.append( (fid, second_board, second_diff.new) )
            bad_series = 0

        else :
            print >>sys.stderr, 'Discarding board %s, wrong-player change(s): %s' % (fid, [str(d) for d in diffs])

    return boards

if __name__ == '__main__' :
    a = Args()

    print >>sys.stderr, a.video_path
    print >>sys.stderr, 'start: %ss, max: %ss, step: %ss, %d total frames' % (a.start, a.end, a.step, (a.end-a.start+0.01)//a.step)

    # Open the video
    v = cv2.VideoCapture(a.video_path)
    os.chdir(os.path.dirname(os.path.abspath(a.video_path)))

    if debug :
       try :
           os.mkdir(debug_dir)
       except OSError :
           pass

    # Read the video, process the frames.
    if a.all_boards_path :
        print >>sys.stderr, 'Loading existing boards...'
        all_boards = []
        for line in open(a.all_boards_path) :
            fields = line.rstrip('\n').split()
            fid = fields[0]
            stones = fields[1]
            n = int(math.sqrt(len(stones)))
            all_boards.append( (fid, output.Board(n, stones)) )
    else :
        print >>sys.stderr, '\nProcessing frames...\n----------'
        all_boards = video_to_boards(v, a.start, a.end, a.step)
        if debug :
            all_boards_f = open('%s/all_boards' % debug_dir, 'w')
            for fid, b in all_boards :
                all_boards_f.write('%s\t%s\n' % (fid, b.stones))

    # Process the boards
    print >>sys.stderr, '\nProcessing boards...\n----------'
    boards = process_boards(all_boards)

    print >>sys.stderr, '\nWriting boards...\n----------'
    for (fid, b, player) in boards:
        print '# %s (%s)' % (fid, player)
        print b

    if debug:
        sys.stdout.flush()
        print >>sys.stderr, '\nAll boards:\n----------\n'
        for (fid, b) in all_boards:
            print >>sys.stderr, '# %s' % fid
            print >>sys.stderr, b
