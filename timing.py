from helpers import *
import strip_pack_solvers as SP
import time

def time_shape_generation(min_dim, max_dim, n=1000):
    results = {}
    for shape in ['R', 'L', 'C', 'I']:
        start_time = time.clock()
        PieceSet(n, min_dim, max_dim, shape)
        end_time = time.clock()
        total_time = end_time - start_time
        results[shape] = total_time
    return results

def average_shape_area(min_dim, max_dim, n=1000):
    results = {}
    for shape in ['R', 'L', 'C', 'I']:
        piece_set = load_piece_set(shape, n, min_dim, max_dim)
        results[shape] = piece_set.total_area / n
    return results

def test_and_time(n_pieces, piece_set, strip_width, solve_fn, iters):
    total_time = 0 # cumulative time to solve for all iters
    total_ratio = 0 # ratio of area used to total area of pieces

    for i in range(iters):
        s = Strip(strip_width)
        ps = piece_set.subset(end=n_pieces, shuffled=True)
        start_time = time.clock()
        solve_fn(s, ps)
        end_time = time.clock()
        total_time += end_time - start_time
        total_ratio += efficiency(s.width, s.max_height_occupied, ps.total_area) / iters

    return total_time/iters, total_ratio

# ''' For timing piece generation with shape types '''
# print("Total generation time for n = 1000:")
# for i in range(3, 12):
#     min_dim = 1
#     results = time_shape_generation(min_dim, i)
#     print("%i-%i:" % (min_dim, i), "".join(["\t%c: %.4f" % (k, v) for (k, v) in results.items()]))

# ''' For testing piece area difference between shape types '''
# print("Average piece area:")
# for i in range(3, 12):
#     min_dim = 1
#     results = average_shape_area(min_dim, i)
#     print("%i-%i:" % (min_dim, i), "".join(["\t%c: %.4f" % (k, v) for (k, v) in results.items()]))

# ''' For making test data sets '''
# for min_dim in [1, 2, 3]:
#     for max_dim in [6, 8, 10, 12]:
#         for shape in ['R', 'L', 'C', 'I']:
#             ps = PieceSet(1000, min_dim, max_dim, shape)
#             ps.save(shape)

# ''' For looking at the time and efficiency dynamics of a solver with varying input length '''
# for shape in ['R', 'L', 'C', 'I']:
#     print("Time and test (%s):" % shape)
#     ps = load_piece_set(shape, 1000, 2, 6)
#     for n in range(8, 20):
#         avg_time, ratio = test_and_time(n, ps, 12, BL, 100)
#         print("%i:" % n, "\tTime: %.5f\tRatio: %.3f" % (avg_time, ratio))


settings = [('R', 1000, 2, 6, 12), ('C', 1000, 2, 6, 12), ('I', 1000, 2, 6, 12), ('R', 1000, 3, 18, 36), ('C', 1000, 3, 18, 36), ('I', 1000, 3, 18, 36)]

# input("Are you sure you want to run? This will take time and overwrite results.")

''' For testing optimality: fewer input lengths, more iterations '''
for shape, n_pieces, min_dim, max_dim, width in settings:
    file_name = "results/optimality_SFB_%s_max-%i_width-%i_1000-iters.csv" % (shape, max_dim, width)
    f = open(file_name, 'w')
    f.write("Optimality for %s - max size %i - width %i - 1000 iters\n" % (shape, max_dim, width))
    start, end = 8, 21
    f.write("Solver, " + ", ".join([str(i) for i in range(start, end)]) + '\n')
    ps = load_piece_set(shape, n_pieces, min_dim, max_dim)
    for solver_name in ['SpaceFiller_better']: # SP.solver_names:
        f.write(solver_name + ', ')
        for n in range(start, end):
            _, ratio = test_and_time(n, ps, width, SP.__dict__[solver_name], 200)
            f.write("%.4f, " % ratio)
        f.write('\n')
        print("Done with", solver_name)
    f.close()
    print("Done with %s-%i" % (shape, width))

''' For testing run time: fewer iterations, larger range of input lengths '''
for shape, n_pieces, min_dim, max_dim, width in settings:
    file_name = "results/speed_SFB_%s_max-%i_width-%i_100-iters.csv" % (shape, max_dim, width)
    f = open(file_name, 'w')
    f.write("Running time for %s - max size %i - width %i - 100 iters\n" % (shape, max_dim, width))
    start, end, step = 10, 50, 3
    f.write("Solver, " + ", ".join([str(i) for i in range(start, end, step)]) + '\n')
    ps = load_piece_set(shape, n_pieces, min_dim, max_dim)
    for solver_name in ['SpaceFiller_better']: # SP.solver_names:
        f.write(solver_name + ', ')
        for n in range(start, end, step):
            avg_time, _ = test_and_time(n, ps, width, SP.__dict__[solver_name], 100)
            f.write("%.5f, " % avg_time)
        f.write('\n')
        print("Done with", solver_name)
    f.close()
    print("Done with %s-%i" % (shape, width))

# ps = PieceSet(8, 3, 7, 'I')

# print(ps.pieces)

# for solver_name in SP.solver_names:
#     solver = SP.__dict__[solver_name]
#     s = Strip(12)
#     solver(s, ps)
#     print("%s: Total height %i" % (solver_name, s.max_height_occupied))
#     print(s)