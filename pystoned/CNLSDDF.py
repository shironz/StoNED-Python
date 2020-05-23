"""
@Title   : Convex Nonparametric Least Square with multiple Outputs (DDF formulation)
@Author  : Sheng Dai, Timo Kuosmanen
@Mail    : sheng.dai@aalto.fi (S. Dai); timo.kuosmanen@aalto.fi (T. Kuosmanen)
@Date    : 2020-04-25
"""

# Import of the pyomo module
from pyomo.environ import *
from . import directV
import numpy as np


# without undesirable outputs
def cnlsddf(y, x, fun, gx, gy):
    # fun    = "prod" : production frontier
    #         = "cost" : cost frontier

    # number of DMUS
    n = len(y)

    # number of inputs
    if type(x[0]) == int or type(x[0]) == float:
        m = 1
    else:
        m = len(x[0])

    # number of outputs
    if type(y[0]) == int or type(y[0]) == float:
        p = 1
    else:
        p = len(y[0])

    # identity matrix
    id = np.repeat(1, n)
    id = id.tolist()

    # directional vectors
    gx = directV.dv(gx, gy, n, m, p)[0]
    gy = directV.dv(gx, gy, n, m, p)[1]

    # Creation of a Concrete Model
    model = ConcreteModel()

    if m == 1:

        # Set
        model.i = Set(initialize=range(n))

        # Alias
        model.h = SetOf(model.i)

        # Variables
        model.a = Var(model.i, doc='alpha')
        model.b = Var(model.i, bounds=(0.0, None), doc='beta')
        model.e = Var(model.i, doc='residuals')
        model.f = Var(model.i, bounds=(0.0, None), doc='estimated frontier')

        if p == 1:

            # Variables
            model.g = Var(model.i, bounds=(0.0, None), doc='gamma')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                return model.g[i] * y[i] == model.a[i] + model.b[i] * x[i] - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                return model.b[i] * gx[i] + model.g[i] * gy[i] == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "prod":

                def concav_rule(model, i, h):
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[i] - model.g[i] * y[i] <= \
                           model.a[h] + model.b[h] * x[i] - model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[i] - model.g[i] * y[i] >= \
                           model.a[h] + model.b[h] * x[i] - model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

        if p > 1:

            # Set
            model.k = Set(initialize=range(p))

            # Variables
            model.g = Var(model.i, model.k, bounds=(0.0, None), doc='gamma')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                brow = y[i]
                return sum(model.g[i, k] * brow[k] for k in model.k) == \
                       model.a[i] + model.b[i] * x[i] - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                frow = gy[i]
                return model.b[i] * gx[i] + sum(model.g[i, k] * frow[k] for k in model.k) == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "cost":

                def concav_rule(model, i, h):
                    brow = y[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[j] - sum(model.g[i, k] * brow[k] for k in model.k) <= \
                           model.a[h] + model.b[h] * x[i] - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    brow = y[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[i] - sum(model.g[i, k] * brow[k] for k in model.k) >= \
                           model.a[h] + model.b[h] * x[i] - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

    if m > 1:

        # Set
        model.i = Set(initialize=range(n))

        # Alias
        model.h = SetOf(model.i)

        # Variables
        model.a = Var(model.i, doc='alpha')
        model.b = Var(model.i, model.j, bounds=(0.0, None), doc='beta')
        model.e = Var(model.i, doc='residuals')
        model.f = Var(model.i, bounds=(0.0, None), doc='estimated frontier')

        if p == 1:

            # Variables
            model.g = Var(model.i, bounds=(0.0, None), doc='gamma')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                arow = x[i]
                return model.g[i] * y[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                erow = gx[i]
                return sum(model.b[i, j] * erow[j] for j in model.j) + model.g[i] * gy[i] == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "prod":

                def concav_rule(model, i, h):
                    arow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - model.g[i] * y[
                            i] <= model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j) - model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    arow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - model.g[i] * y[
                            i] >= model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j) - model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

        if p > 1:

            # Set
            model.k = Set(initialize=range(p))

            # Variables
            model.g = Var(model.i, model.k, bounds=(0.0, None), doc='gamma')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                arow = x[i]
                brow = y[i]
                return sum(model.g[i, k] * brow[k] for k in model.k) == model.a[i] + sum(
                        model.b[i, j] * arow[j] for j in model.j) - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                erow = gx[i]
                frow = gy[i]
                return sum(model.b[i, j] * erow[j] for j in model.j) + sum(model.g[i, k] * frow[k] for k in model.k) == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "cost":

                def concav_rule(model, i, h):
                    arow = x[i]
                    brow = y[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - \
                           sum(model.g[i, k] * brow[k] for k in model.k) <= model.a[h] + sum(
                            model.b[h, j] * arow[j] for j in model.j) - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    arow = x[i]
                    brow = y[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - \
                            sum(model.g[i, k] * brow[k] for k in model.k) >= model.a[h] + sum(
                            model.b[h, j] * arow[j] for j in model.j) - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

    return model


# with undesirable outputs
def cnlsddfb(y, x, b, fun, gx, gb, gy):
    # fun    = "prod" : production frontier
    #         = "cost" : cost frontier

    # number of DMUS
    n = len(y)

    # number of inputs
    if type(x[0]) == int or type(x[0]) == float:
        m = 1
    else:
        m = len(x[0])

    # number of outputs
    if type(y[0]) == int or type(y[0]) == float:
        p = 1
    else:
        p = len(y[0])

    # number of undesirable outputs
    if type(b[0]) == int or type(b[0]) == float:
        q = 1
    else:
        q = len(b[0])

    # identity matrix
    id = np.repeat(1, n)
    id = id.tolist()

    # directional vectors
    gx = directV.dvb(gx, gb, gy, n, m, q, p)[0]
    gb = directV.dvb(gx, gb, gy, n, m, q, p)[1]
    gy = directV.dvb(gx, gb, gy, n, m, q, p)[2]

    # Creation of a Concrete Model
    model = ConcreteModel()

    if m == 1:

        # Set
        model.i = Set(initialize=range(n))

        # Alias
        model.h = SetOf(model.i)

        # Variables
        model.a = Var(model.i, doc='alpha')
        model.b = Var(model.i, bounds=(0.0, None), doc='beta')
        model.e = Var(model.i, doc='residuals')
        model.f = Var(model.i, bounds=(0.0, None), doc='estimated frontier')

        if q == 1 and p == 1:

            # Variables
            model.g = Var(model.i, bounds=(0.0, None), doc='gamma')
            model.d = Var(model.i, bounds=(0.0, None), doc='delta')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                return model.g[i] * y[i] == model.a[i] + model.b[i] * x[i] + model.d[i] * b[i] - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                return model.b[i] * gx[i] + model.g[i] * gy[i] + model.d[i] * gb[i] == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "prod":

                def concav_rule(model, i, h):
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[i] + model.d[i] * b[i] - model.g[i] * y[i] <= \
                           model.a[h] + model.b[h] * x[i] + model.d[h] * b[i] - model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[i] + model.d[i] * b[i] - model.g[i] * y[i] >= \
                           model.a[h] + model.b[h] * x[i] + model.d[h] * b[i] - model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

        if q > 1 and p > 1:

            # Set
            model.k = Set(initialize=range(p))
            model.l = Set(initialize=range(q))

            # Variables
            model.g = Var(model.i, model.k, bounds=(0.0, None), doc='gamma')
            model.d = Var(model.i, model.l, bounds=(0.0, None), doc='delta')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                brow = y[i]
                crow = b[i]
                return sum(model.g[i, k] * brow[k] for k in model.k) == model.a[i] + model.b[i] * x[i] + \
                       sum(model.d[i, l] * crow[l] for l in model.l) - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                frow = gy[i]
                grow = gb[i]
                return model.b[i] * gx[i] + sum(model.g[i, k] * frow[k] for k in model.k) + \
                       sum(model.d[i, l] * grow[l] for l in model.l) == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "cost":

                def concav_rule(model, i, h):
                    brow = y[i]
                    crow = b[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[i] + sum(model.d[i, l] * crow[l] for l in model.l) - \
                            sum(model.g[i, k] * brow[k] for k in model.k) <= model.a[h] + model.b[h] * x[i] + \
                            sum(model.d[h, l] * crow[l] for l in model.l) - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    brow = y[i]
                    crow = b[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + model.b[i] * x[i] + sum(model.d[i, l] * crow[l] for l in model.l) - \
                            sum(model.g[i, k] * brow[k] for k in model.k) >= model.a[h] + model.b[h] * x[i] + \
                            sum(model.d[h, l] * crow[l] for l in model.l) - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

    if m > 1:

        # Set
        model.i = Set(initialize=range(n))
        model.j = Set(initialize=range(m))

        # Alias
        model.h = SetOf(model.i)

        # Variables
        model.a = Var(model.i, doc='alpha')
        model.b = Var(model.i, model.j, bounds=(0.0, None), doc='beta')
        model.e = Var(model.i, doc='residuals')
        model.f = Var(model.i, bounds=(0.0, None), doc='estimated frontier')

        if q == 1 and p == 1:

            # Variables
            model.g = Var(model.i, bounds=(0.0, None), doc='gamma')
            model.d = Var(model.i, bounds=(0.0, None), doc='delta')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                arow = x[i]
                return model.g[i] * y[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + \
                       model.d[i] * b[i] - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                erow = gx[i]
                return sum(model.b[i, j] * erow[j] for j in model.j) + model.g[i] * gy[i] + model.d[i] * gb[i] == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "prod":

                def concav_rule(model, i, h):
                    arow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + model.d[i] * b[i] - model.g[i] * y[
                           i] <= model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j) + model.d[h] * b[i] - \
                            model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    arow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + model.d[i] * b[i] - model.g[i] * y[
                           i] >= model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j) + model.d[h] * b[i] - \
                            model.g[h] * y[i]

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

        if q > 1 and p > 1:

            # Set
            model.k = Set(initialize=range(p))
            model.l = Set(initialize=range(q))

            # Variables
            model.g = Var(model.i, model.k, bounds=(0.0, None), doc='gamma')
            model.d = Var(model.i, model.l, bounds=(0.0, None), doc='delta')

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            # Constraints
            def reg_rule(model, i):
                arow = x[i]
                brow = y[i]
                crow = b[i]
                return sum(model.g[i, k] * brow[k] for k in model.k) == model.a[i] + sum(
                       model.b[i, j] * arow[j] for j in model.j) + \
                       sum(model.d[i, l] * crow[l] for l in model.l) - model.e[i]

            model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

            def trans_rule(model, i):
                erow = gx[i]
                frow = gy[i]
                grow = gb[i]
                return sum(model.b[i, j] * erow[j] for j in model.j) + sum(model.g[i, k] * frow[k] for k in model.k) + \
                       sum(model.d[i, l] * grow[l] for l in model.l) == id[i]

            model.trans = Constraint(model.i, rule=trans_rule, doc='translation property')

            # production model
            if fun == "cost":

                def concav_rule(model, i, h):
                    arow = x[i]
                    brow = y[i]
                    crow = b[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + sum(
                           model.d[i, l] * crow[l] for l in model.l) - \
                            sum(model.g[i, k] * brow[k] for k in model.k) <= model.a[h] + sum(
                            model.b[h, j] * arow[j] for j in model.j) + \
                            sum(model.d[h, l] * crow[l] for l in model.l) - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

            # cost model
            if fun == "cost":

                def concav_rule(model, i, h):
                    arow = x[i]
                    brow = y[i]
                    crow = b[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + sum(
                           model.d[i, l] * crow[l] for l in model.l) - \
                            sum(model.g[i, k] * brow[k] for k in model.k) >= model.a[h] + sum(
                            model.b[h, j] * arow[j] for j in model.j) + \
                            sum(model.d[h, l] * crow[l] for l in model.l) - sum(model.g[h, k] * brow[k] for k in model.k)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

    return model