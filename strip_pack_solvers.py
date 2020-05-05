from helpers import *
from collections import OrderedDict


def BL(strip, piece_set):
    for p in piece_set.pieces:
        placed = False
        r = 0
        while (not placed) and (r < piece_set.total_height):
            for c in range(0, strip.width - p.width + 1):
                if strip.open(r, c):
                    res = strip.try_place(p, r, c, anchor='top_left')
                    if res >= 0:
                        strip.place(p, r, c, anchor='top_left')
                        placed = True
                        break
            r += 1


def BL_WUB(strip, piece_set):
    for p in piece_set.pieces:
        placed = False
        # don't look more than W back
        r = max(0, strip.max_height_occupied - strip.width)
        while (not placed) and (r < piece_set.total_height):
            for c in range(0, strip.width - p.width + 1):
                if strip.open(r, c):
                    res = strip.try_place(p, r, c, anchor='top_left')
                    if res >= 0:
                        strip.place(p, r, c, anchor='top_left')
                        placed = True
                        break
            r += 1


def NFDH(strip, piece_set):
    piece_set = piece_set.sorted(by='height')
    r, c = 0, 0
    next_row = piece_set.pieces[0].height
    for p in piece_set.pieces:
        while not strip.open(r, c):
            c += 1
        res = strip.try_place(p, r, c, anchor='top_left')
        while (res == -1) or (res == -3): # overlapping or too far left
            c += 1
            res = strip.try_place(p, r, c, anchor='top_left')
        if res == -2: # too far right
            c = 0
            r = next_row
            next_row += p.height
            res = strip.try_place(p, r, c, anchor='top_left')
            if res > 0:
                strip.place(p, r, c, anchor='top_left')
        else:
            strip.place(p, r, c, anchor='top_left')
            c += 1 + p.top_right - p.top_left # increment by width of top


def NFDH_slow(strip, piece_set):
    piece_set = piece_set.sorted(by='height')
    r, c = 0, 0
    next_row = piece_set.pieces[0].height
    for p in piece_set.pieces:
        placed = False
        while not placed:
            while not strip.open(r, c):
                c += 1
            res = strip.try_place(p, r, c, anchor='top_left')
            while (res == -1) or (res == -3): # overlapping or too far left
                c += 1
                res = strip.try_place(p, r, c, anchor='top_left')
            if res == -2: # too far right
                c = 0
                r += 1
                res = strip.try_place(p, r, c, anchor='top_left')
                if res > 0:
                    strip.place(p, r, c, anchor='top_left')
                    placed = True
            else:
                strip.place(p, r, c, anchor='top_left')
                placed = True
                c += 1 + p.top_right - p.top_left # increment by width of top


def FFDH(strip, piece_set):
    piece_set = piece_set.sorted(by='height')
    levels = [0, piece_set.pieces[0].height]
    for p in piece_set.pieces:
        placed = False
        l, c = 0, 0
        while (not placed) and (levels[l] < piece_set.total_height):
            r = levels[l]
            while not strip.open(r, c):
                c += 1
            res = strip.try_place(p, r, c, anchor='top_left')
            while (res == -1) or (res == -3): # overlapping or too far left
                c += 1
                res = strip.try_place(p, r, c, anchor='top_left')
            if res == -2: # too far right
                c = 0
                l += 1
                if r == levels[-2]:
                    # if you were on the highest level with a defined
                    # "top shelf", and you're going up - add new top shelf
                    levels.append(levels[-1] + p.height)
            else:
                strip.place(p, r, c, anchor='top_left')
                placed = True


def FFDH_WUB(strip, piece_set):
    piece_set = piece_set.sorted(by='height')
    levels = [0, piece_set.pieces[0].height]
    for p in piece_set.pieces:
        placed = False
        c = 0
        l = max(-12, -len(levels)) # don't look more than 12 levels back
        while (not placed) and (levels[l] < piece_set.total_height):
            r = levels[l]
            while not strip.open(r, c):
                c += 1
            res = strip.try_place(p, r, c, anchor='top_left')
            while (res == -1) or (res == -3): # overlapping or too far left
                c += 1
                res = strip.try_place(p, r, c, anchor='top_left')
            if res == -2: # too far right
                c = 0
                l += 1
                if r == levels[-2]:
                    # if you were on the highest level with a defined
                    # "top shelf", and you're going up - add new top shelf
                    levels.append(levels[-1] + p.height)
            else:
                strip.place(p, r, c, anchor='top_left')
                placed = True


def SpaceFiller(strip, piece_set):
    '''
    make hashmap of free spaces on strip
    sort by row -> column
    for each piece:
        i = 0
        res = try freespaces[i] (if width would fit)
        i += 1
    when placed, remove spaces, add rows to hash
    '''
    free = OrderedDict()
    for r in range(strip.height):
        for c in range(strip.width):
            if strip.open(r, c):
                free[(r, c)] = True

    for p in piece_set.pieces:
        placed = False
        for r, c in free.keys():
            res = strip.try_place(p, r, c, anchor='top_left')
            if res > 0:
                strip.place(p, r, c, anchor = 'top_left')
                placed = True
                for r2 in range(r, r+p.height):
                    for c2 in range(strip.width):
                        if (free.get((r2, c2)) is not None) and (not strip.open(r2, c2)):
                            free.pop((r2, c2))
                        elif strip.open(r2, c2):
                            free[(r2, c2)] = True
                break
            
        if not placed:
            new_row = strip.max_height_occupied # above all placed pieces
            strip.place(p, new_row, 0)
            for r2 in range(new_row, new_row+p.height):
                for c2 in range(strip.width):
                    if strip.open(r2, c2):
                        free[(r2, c2)] = True


def SpaceFiller_WUB(strip, piece_set):
    '''
    make hashmap of free spaces on strip
    sort by row -> column
    for each piece:
        i = 0
        res = try freespaces[i] (if width would fit)
        i += 1
    when placed, remove spaces, add rows to hash
    '''
    free = OrderedDict()
    for r in range(strip.height):
        for c in range(strip.width):
            if strip.open(r, c):
                free[(r, c)] = True

    max_height = 0
    for p in piece_set.pieces:
        placed = False
        for r, c in free.keys():
            if (max_height - r) > (strip.width):
                # don't look more than W back
                continue
            res = strip.try_place(p, r, c, anchor='top_left')
            if res > 0:
                strip.place(p, r, c, anchor = 'top_left')
                max_height = max(max_height, r + p.height)
                placed = True
                for r2 in range(r, r+p.height):
                    for c2 in range(strip.width):
                        if (free.get((r2, c2)) is not None) and (not strip.open(r2, c2)):
                            free.pop((r2, c2))
                        elif strip.open(r2, c2):
                            free[(r2, c2)] = True
                break
            
        if not placed:
            new_row = strip.max_height_occupied # above all placed pieces
            strip.place(p, new_row, 0)
            for r2 in range(new_row, new_row+p.height):
                for c2 in range(strip.width):
                    if strip.open(r2, c2):
                        free[(r2, c2)] = True


def Tetris(strip, piece_set):
    '''
    keep track of leading edge
    test position of each piece one by one, each spot on leading edge: minimize height
    '''
    for p in piece_set.pieces[:]:
        top = max(2, strip.max_height_occupied)
        bottom_row = strip.array[0]
        edge = (np.argmax(strip.array[top:0:-1], axis = 0))
        edge = np.where(edge==0, bottom_row, top-edge+1) # lowest open spot on the top
        min_col = None
        min_height = float('inf')
        while min_col is None:
            for c, r in enumerate(edge):
                res = strip.try_place(p, r, c, anchor='top_left')
                if res > 0:
                    if res < min_height:
                        min_height = res
                        min_col = c
            row = edge[min_col] # if min_col is None, this = edge, but keeps looping
            edge += 1
        strip.place(p, row, min_col, anchor='top_left')

    
def Tetris_flip(strip, piece_set):
    '''
    keep track of leading edge
    test position of each piece one by one, each spot on leading edge: minimize height
    '''
    for p in piece_set.pieces[:]:
        top = max(2, strip.max_height_occupied)
        bottom_row = strip.array[0]
        edge = (np.argmax(strip.array[top:0:-1], axis = 0))
        edge = np.where(edge==0, bottom_row, top-edge+1) # lowest open spot on the top
        min_col = None
        min_height = float('inf')
        best_anchor = None
        while min_col is None:
            for c, r in enumerate(edge):
                for anchor in ['top_left', 'top_right']:
                    res = strip.try_place(p, r, c, anchor=anchor)
                    if res > 0:
                        if res < min_height:
                            min_height = res
                            min_col = c
                            best_anchor = anchor
            row = edge[min_col] # if min_col is None, this = edge, but keeps looping
            edge += 1
        strip.place(p, row, min_col, anchor=best_anchor)


def SpaceFiller_better(strip, piece_set):
    narrow, wide = piece_set.partition('width', strip.width/4)
    if wide.length > 0:
        NFDH(strip, wide)
    if narrow.length > 0:
        narrow = narrow.sorted('height')
        SpaceFiller_WUB(strip, narrow)


solver_names = ["BL", "BL_WUB", "NFDH", "NFDH_slow", "FFDH", "FFDH_WUB", "SpaceFiller", "SpaceFiller_WUB", "Tetris", "Tetris_flip", "SpaceFiller_better"]

if __name__ == "__main__":
    strip = Strip(12)

    ps = PieceSet(10, 2, 8, 'R')
    print(ps.pieces)
    SpaceFiller_better(strip, ps)
    print(strip)