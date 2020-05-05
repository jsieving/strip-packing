from random import random, randint, choice, sample
import numpy as np
from scipy.ndimage import convolve
import time
import pickle

def flip(p):
    return random() < p

class Strip:
    def __init__(self, width, height = None):
        self.width = width
        self.height = height if height is not None else width
        self.area_filled = 0
        self.max_height_occupied = 0
        self.array = np.zeros((self.height, self.width), dtype = "int")

    def __repr__(self):
        return stringify(self.array)

    def open(self, row, column):
        if row >= self.height:
            return 1
        if column >= self.width:
            return -1
        if self.array[row, column] == 0:
            return 1
        else:
            return 0

    def try_place(self, piece, r, c, anchor=None):
        if anchor is not None:
            c -= piece.__dict__[anchor]
            if c < 0:
                return -3 # designated for off-edge b/c of anchor
        if r > self.height: # catches math errors when placed off of existing strip - not usually necessary
            return r + piece.height
        c2 = c + piece.width     
        if (c2 > self.width): # piece cannot go off side of fabric
            return -2 # designated for off-the-side
        r2 = min(self.height, r + piece.height) # ignore if it hangs off the end
        cutoff = r2 - r # where to cut off the piece; only look at area overlapping existing strip
        region = self.array[r:r2, c:c2] + piece.array[:cutoff]
        if (region > 1).any(): # check for overlap with previously-placed pieces
            return -1 # designated for overlap
        return r + piece.height # return the max height occupied on the strip

    def place(self, piece, r, c, anchor=None):
        if anchor is not None:
            c -= piece.__dict__[anchor]
            if c < 0:
                raise IndexError('A piece has been placed off the left edge of the strip. Please use try_place to verify placements.')
                return
        r2, c2 = r + piece.height, c + piece.width
        if c2 > self.width:
            raise IndexError('A piece has been placed off the right edge of the strip. Please use try_place to verify placements.')
            return
        if r2 >= self.height: # extend piece if ceiling reached
            extend_height = max(2*piece.height, self.height)
            new_array = np.zeros((extend_height, self.width), dtype='int')
            self.array = np.concatenate([self.array, new_array])

        self.array[r:r2, c:c2] += piece.array
        
        self.height = self.array.shape[0]
        self.area_filled += piece.area
        self.max_height_occupied = max(self.max_height_occupied, r2)


class Piece:
    def __init__(self, height=None, width=None, data=None):
        if data is not None:
            self.array = data.astype('int')
            self.area = self.array.sum()
        elif (height is not None) and (width is not None):
            self.array = np.ones((height, width), dtype = "int")
            self.area = height * width
        
        self.height = self.array.shape[0]
        self.width = self.array.shape[1]
        self.top_left = np.argwhere(self.array[0]==1)[0,0]
        self.top_right = np.argwhere(self.array[0]==1)[-1,0]

    def __repr__(self):
        return stringify(self.array)


class PieceSet:
    def __init__(self, n=None, min_dim=None, max_dim=None, shape=None, pieces=None):
        self.total_area = 0
        self.total_height = 0
        self.min_width = 10e6
        self.max_width = 0

        if pieces is None:
            self.pieces = []
            try:
                self.generate(n, min_dim, max_dim, shape)
            except:
                print("Insufficient or incorrect parameters to generate pieces.")
        else:
            self.pieces = pieces
            for p in self.pieces:
                self.total_area += p.area
                self.total_height += p.height
                self.min_width = min(self.min_width, p.width)
                self.max_width = max(self.max_width, p.width)
            self.length = len(self.pieces)

    def __repr__(self):
        return "PieceSet with %i pieces, max width %i, total area %i." % (self.length, self.max_width, self.total_area)

    def generate(self, n, min_dim, max_dim, shape):
        for i in range(n):
            p = generate_piece(min_dim, max_dim, shape)
            self.pieces.append(p)
            self.total_area += p.area
            self.total_height += p.height
        self.length = len(self.pieces)
        self.min_width = min_dim
        self.max_width = max_dim
        return self.pieces

    def subset(self, start=None, end=None, shuffled=False):
        if start is None:
            start = 0
        if end is None:
            end = self.length
        if shuffled:
            pieces = sample(self.pieces, end-start)
        else:
            pieces = self.pieces[start:end]
        return PieceSet(pieces=pieces)

    def partition(self, attribute, threshold, round_up=False):
        if round_up:
            low = [p for p in self.pieces if p.__dict__[attribute] < threshold]
            high = [p for p in self.pieces if p.__dict__[attribute] >= threshold]
        else:
            low = [p for p in self.pieces if p.__dict__[attribute] <= threshold]
            high = [p for p in self.pieces if p.__dict__[attribute] > threshold]
        return PieceSet(pieces=low), PieceSet(pieces=high)

    def sorted(self, by, ascending=False):
        sorted_pieces = sorted(self.pieces, key=lambda p: p.__dict__[by], reverse=not ascending)
        return PieceSet(pieces=sorted_pieces)

    def save(self, filename_hint="", overwrite=False):
        file_name = "test-sets/%s_%i-pieces_min-%i_max_%i.pcs" % (filename_hint, self.length, self.min_width, self.max_width)
        try:
            f = open(file_name, 'xb')
        except FileExistsError as e:
            if overwrite:
                print("Similar file previously created. Overwriting...")
                f = open(file_name, 'wb')
            else:
                print(e)
                print("Similar file previously created. Specify 'overwrite=True' to overwrite existing file.")
                return
        pickle.dump(self, f)
        print("PieceSet saved as '%s'" % file_name)


def generate_piece(min_dim, max_dim, shape):
    if shape == 'R':
        height = randint(min_dim, max_dim)
        width = randint(min_dim, max_dim)
        return Piece(height, width)
    elif shape == 'L':
        height = randint(min_dim, max_dim)
        width = randint(min_dim, max_dim)
        array = np.ones((height, width), dtype="int")
        cut_height = randint(0, height//2)
        cut_width = randint(0, width//2)
        top = choice([0, height-cut_height])
        left = choice([0, width-cut_width])
        bottom = top + cut_height
        right = left + cut_width
        array[top:bottom, left:right] = 0
        return Piece(data=array)
    elif shape == 'C':
        height = randint(min_dim, max_dim)
        width = randint(min_dim, max_dim)
        array = np.ones((height, width), dtype="int")
        for i in range(4):
            cut_height = randint(0, height//2)
            cut_width = randint(0, width//2)
            top = (i % 2) * (height-cut_height)
            left = (i // 2) * (width-cut_width)
            bottom = top + cut_height
            right = left + cut_width
            array[top:bottom, left:right] = 0
        while (array[0, :] == 0).all():
            array = array[1:]
        while (array[-1, :] == 0).all():
            array = array[:-1]
        while (array[:, 0] == 0).all():
            array = array[:, 1:]
        while (array[:, -1] == 0).all():
            array = array[:, :-1]
        return Piece(data=array)
    elif shape == 'I':
        kernel = np.asarray([[0, .4, 0],
                             [.4, 1, .4],
                             [0, .4, 0]])
        array = np.zeros((max_dim, max_dim), dtype = "float")
        array[max_dim//2, max_dim//2] = 1
        iters = max_dim//2
        i = 0
        while (i < iters) or (array.sum() < min_dim**2):
            i += 1
            array = convolve(array, kernel, mode="constant", cval=0)
            for r in range(max_dim):
                for c in range(max_dim):
                    array[r, c] = flip(array[r, c])
        while (array[0, :] == 0).all():
            array = array[1:]
        while (array[-1, :] == 0).all():
            array = array[:-1]
        while (array[:, 0] == 0).all():
            array = array[:, 1:]
        while (array[:, -1] == 0).all():
            array = array[:, :-1]
        return Piece(data=array)
    else:
        print("Invalid shape specification. Please specify:\n'R' = rectangular, 'L' = L-shaped, 'C' = cutouts, 'I' = irregular.")    

def load_piece_set(filename_hint, n, min_dim, max_dim):
    file_name = "test-sets/%s_%i-pieces_min-%i_max_%i.pcs" % (filename_hint, n, min_dim, max_dim)
    try:
        f = open(file_name, 'rb')
    except FileNotFoundError as e:
        print(e)
        print("Attempting to generate and save requested set....")
        ps = PieceSet(n, min_dim, max_dim, filename_hint)
        ps.save(filename_hint)
        return ps
    ps = pickle.load(f)
    # print("Loaded " + str(ps))
    return ps
    

def efficiency(strip_width, total_height, total_area):
    return total_height * strip_width / total_area

def stringify(array):
    height = array.shape[0]
    width = array.shape[1]
    s = '\n+' + '-'*2* width + '-+\n'
    for r in range(height):
        s += '|'
        for c in range(width):
            if array[r, c] == 0:
                s += '  '
            else:
                s += ' #'
        s += ' |\n'
    s += '+' + '-'*2* width + '-+\n'
    return s

if __name__ == "__main__":
    pass
    p = generate_piece(3, 5, 'I')
    print(p.__dict__['top_left'])