import os
import cProfile
import pstats

from solution import FleetProblem

if __name__=="__main__":
    prob = FleetProblem()
    
    for i in range(0,9):    
        filename = f"ex{i}.dat"

        file_path = os.path.join('tests', filename)
        with open(file_path) as fh:
            prob.load(fh)

        sol = 0
        cProfile.run('sol = prob.solve()', 'output.prof')
        p = pstats.Stats('output.prof')
        if i == 9:
            p.sort_stats('cumulative').print_stats(20)
        print(f"Solution for {filename}:")
        #print(sol)
        print(prob.cost(sol))