
I'm interested in exploring and evaluating approximate solutions to the strip packing problem, particularly when applied to irregular shapes. The strip packing problem is an NP-hard problem where you try to place 2-dimensional rectangles on a larger, fixed-width rectangle while minimizing the height of the region occupied. There are a few approximate algorithms, all of which can only be shown to produce solutions at least 3/2 of the optimal height. I'm not going to try to invent a new algorithm for this, but I'm interested in how existing algorithms perform when applied to irregularly-shaped objects. My project will probably look like this:

- Create a general program for testing strip packing algorithms (create strip, generate cases, pack, evaluate and time)

- Pick ~2 approximation algorithms and implement them in code (may need to adapt for irregular shapes)

- Test algorithms on rectangular vs. irregular shapes, see if either performs better or worse with irregularity

- (Possibly) see if improvement can be achieved by increasing problem size but solving it in chunks (and for example, giving leftover space to next chunk)

I'll represent both rectangles and irregular shapes in terms of an occupancy grid, so detecting overlap won't be too crazy. And when I talk about evaluating performance, I'll be measuring the average time or approximation ratio for solutions under certain parameters, not mathematically finding an upper limit.
