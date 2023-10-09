import io
import solution

prob = solution.FleetProblem(None)

P = """# number of points and distances
P 3
20 30
   40
# requests
R 1
10 1 2 1
# vehicles and # of seats
V 1
4

"""

with io.StringIO(P) as fh:
    prob.load(fh)

print(prob.actions(prob.state))

