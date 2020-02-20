import unittest

import numpy as np

from industrialucn.optimization.econstraint import *


class EConstraint(unittest.TestCase):

    def test_cplex(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

        # define parameters
        n = 15  # number of parks
        m = 50  # number of buildings
        rnd = np.random
        rnd.seed(0)
        cpx = rnd.rand(n) * 300  # x coordinate for parks
        cpy = rnd.rand(n) * 100  # y coordinate for parks
        cbx = rnd.rand(m) * 300  # x coordinate for buildings
        cby = rnd.rand(m) * 100  # y coordinate for buildings
        parks = [i for i in range(n)]
        buildings = [j for j in range(m)]
        distance = {(i, j): np.hypot(cbx[i] - cpx[j], cby[i] - cpy[j])
                    for i in buildings for j in parks}

        # define model
        mdl = CplexModel()

        # define variables
        x = mdl.binary_var_dict(parks, name='x')
        y = mdl.binary_var_dict([(i, j) for i in buildings for j in parks], name='y')

        # define objective
        f1 = -mdl.sum(x[i] for i in parks)
        f2 = -mdl.sum(distance[i, j] * y[i, j] for i in buildings for j in parks)
        f3 = -mdl.max(distance[i, j] * y[i, j] for i in buildings for j in parks)
        objectives = [f1, f2, f3]

        # define constraints
        mdl.add_constraints(y[i, j] <= x[j] for i in buildings for j in parks)
        mdl.add_constraints(mdl.sum(y[i, j] for j in parks) >= 1 for i in buildings)

        # run e-constraint
        pareto_frontier = run_econstraint(mdl, objectives, optimizer='cplex')

        # print results
        for v in pareto_frontier:
            print([v.get_value(o) for o in objectives])

    def test_payoff_table_gurobi(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

        # define parameters
        n = 15  # number of parks
        m = 50  # number of buildings
        rnd = np.random
        rnd.seed(0)
        cpx = rnd.rand(n) * 300  # x coordinate for parks
        cpy = rnd.rand(n) * 100  # y coordinate for parks
        cbx = rnd.rand(m) * 300  # x coordinate for buildings
        cby = rnd.rand(m) * 100  # y coordinate for buildings
        parks = [i for i in range(n)]
        buildings = [j for j in range(m)]
        distance = {(i, j): np.hypot(cbx[i] - cpx[j], cby[i] - cpy[j])
                    for i in buildings for j in parks}

        # define model
        mdl = GurobiModel()

        # define variables
        x = mdl.addVars(parks, vtype=GRB.BINARY, name='x')
        y = mdl.addVars([(i, j) for i in buildings for j in parks], vtype=GRB.BINARY, name='y')

        # define objective
        f1 = quicksum(-1 * x[i] for i in parks)
        f2 = quicksum(-1 * distance[i, j] * y[i, j] for i in buildings for j in parks)
        objectives = [f1, f2]

        # define constraints
        mdl.addConstrs(y[i, j] <= x[j] for i in buildings for j in parks)
        mdl.addConstrs(quicksum(y[i, j] for j in parks) >= 1 for i in buildings)

        payoff_table = get_payoff_table_gurobi(mdl, objectives)

        print(payoff_table)

    def test_run_econstraint_gurobi(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

        # define parameters
        n = 15  # number of parks
        m = 50  # number of buildings
        rnd = np.random
        rnd.seed(0)
        cpx = rnd.rand(n) * 300  # x coordinate for parks
        cpy = rnd.rand(n) * 100  # y coordinate for parks
        cbx = rnd.rand(m) * 300  # x coordinate for buildings
        cby = rnd.rand(m) * 100  # y coordinate for buildings
        parks = [i for i in range(n)]
        buildings = [j for j in range(m)]
        distance = {(i, j): np.hypot(cbx[i] - cpx[j], cby[i] - cpy[j])
                    for i in buildings for j in parks}

        # define model
        mdl = GurobiModel()

        # define variables
        x = mdl.addVars(parks, vtype=GRB.BINARY, name='x')
        y = mdl.addVars([(i, j) for i in buildings for j in parks], vtype=GRB.BINARY, name='y')

        # define objective
        f1 = quicksum(-1 * x[i] for i in parks)
        f2 = quicksum(-1 * distance[i, j] * y[i, j] for i in buildings for j in parks)
        objectives = [f1, f2]

        # define constraints
        mdl.addConstrs(y[i, j] <= x[j] for i in buildings for j in parks)
        mdl.addConstrs(quicksum(y[i, j] for j in parks) >= 1 for i in buildings)

        payoff_table = get_payoff_table_gurobi(mdl, objectives)

        solutions = []

        def extract_solution():
            xvals = {i: x[i].x for i in parks}
            yvals = {(i, j): y[i, j].x for i in buildings for j in parks}
            solutions.append((xvals, yvals))

        _run_econstraint_gurobi(mdl, objectives, payoff_table, sol_extractor=extract_solution)

        print (solutions)


if __name__ == '__main__':
    unittest.main()
