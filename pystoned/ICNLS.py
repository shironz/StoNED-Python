"""
@Title   : Isotonic Convex Nonparametric Least Square (ICNLS)
@Author  : Sheng Dai, Timo Kuosmanen
@Mail    : sheng.dai@aalto.fi (S. Dai); timo.kuosmanen@aalto.fi (T. Kuosmanen)  
@Date    : 2020-04-22
"""

# Import of the pyomo module
from pyomo.environ import *


def icnls(y, x, p, cet, fun, rts):
    # cet     = "addi" : Additive composite error term
    #         = "mult" : Multiplicative composite error term
    # fun     = "prod" : production frontier
    #         = "cost" : cost frontier
    # rts     = "vrs"  : variable returns to scale
    #         = "crs"  : constant returns to scale

    # number of DMUS
    n = len(y)

    # number of inputs
    if type(x[0]) == int or type(x[0]) == float:
        m = 1
    else:
        m = len(x[0])

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

        # Additive composite error term
        if cet == "addi":

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if rts == "vrs":

                # Constraints
                def reg_rule(model, i):
                    return y[i] == model.a[i] + model.b[i] * x[i] + model.e[i]

                model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

                # production model
                if fun == "prod":
                    def concav_rule(model, i, h):
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + model.b[i] * x[i]) <= \
                               brow[h] * (model.a[h] + model.b[h] * x[i])

                    model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

                # cost model
                if fun == "cost":

                    def concav_rule(model, i, h):
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + model.b[i] * x[i]) >= \
                               brow[h] * (model.a[h] + model.b[h] * x[i])

                    model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

        # Multiplicative composite error term
        if cet == "mult":

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if rts == "vrs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.e[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    return model.f[i] == model.a[i] + model.b[i] * x[i] - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                # production model
                if fun == "prod":

                    def qconcav_rule(model, i, h):
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + model.b[i] * x[i]) <= \
                               brow[h] * (model.a[h] + model.b[h] * x[i])

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

                # cost model
                if fun == "cost":

                    def qconcav_rule(model, i, h):
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + model.b[i] * x[i]) >= \
                               brow[h] * (model.a[h] + model.b[h] * x[i])

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

            if rts == "crs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.e[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    return model.f[i] == model.b[i] * x[i] - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                # production model
                if fun == "prod":

                    def qconcav_rule(model, i, h):
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.b[i] * x[i]) <= brow[h] * (model.b[h] * x[i])

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

                # cost model
                if fun == "cost":

                    def qconcav_rule(model, i, h):
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.b[i] * x[i]) >= brow[h] * (model.b[h] * x[i])

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

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

        # Additive composite error term
        if cet == "addi":

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if rts == "vrs":

                # Constraints
                def reg_rule(model, i):
                    arow = x[i]
                    return y[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + model.e[i]

                model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

                # production model
                if fun == "prod":
                    def concav_rule(model, i, h):
                        arow = x[i]
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j)) <= brow[h] * \
                               (model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j))

                    model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

                # cost model
                if fun == "cost":

                    def concav_rule(model, i, h):
                        arow = x[i]
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j)) >= brow[h] * \
                               (model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j))

                    model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

        # Multiplicative composite error term
        if cet == "mult":

            # Objective function
            def objective_rule(model):
                return sum(model.e[i] * model.e[i] for i in model.i)

            model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if rts == "vrs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.e[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    arow = x[i]
                    return model.f[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                # production model
                if fun == "prod":

                    def qconcav_rule(model, i, h):
                        arow = x[i]
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j)) <= brow[h] * \
                               (model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j))

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

                # cost model
                if fun == "cost":

                    def qconcav_rule(model, i, h):
                        arow = x[i]
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j)) >= brow[h] * \
                               (model.a[h] + sum(model.b[h, j] * arow[j] for j in model.j))

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

            if rts == "crs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.e[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    arow = x[i]
                    return model.f[i] == sum(model.b[i, j] * arow[j] for j in model.j) - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                # production model
                if fun == "prod":

                    def qconcav_rule(model, i, h):
                        arow = x[i]
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (sum(model.b[i, j] * arow[j] for j in model.j)) <= brow[h] * \
                               (sum(model.b[h, j] * arow[j] for j in model.j))

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

                # cost model
                if fun == "cost":

                    def qconcav_rule(model, i, h):
                        arow = x[i]
                        brow = p[i]
                        if i == h:
                            return Constraint.Skip
                        if brow[h] == 0:
                            return Constraint.Skip
                        return brow[i] * (sum(model.b[i, j] * arow[j] for j in model.j)) >= brow[h] * \
                               (sum(model.b[h, j] * arow[j] for j in model.j))

                    model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

    return model
