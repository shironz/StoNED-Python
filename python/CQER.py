"""
@Title   : Convex quantile/expectile regression (CQR/CER)
@Author  : Sheng Dai, Timo Kuosmanen
@Mail    : sheng.dai@aalto.fi (S. Dai); timo.kuosmanen@aalto.fi (T. Kuosmanen)  
@Time    : 2020-04-16
"""

# Import of the pyomo module
from pyomo.environ import *


def cqer(y, x, tau, crt, func, pps, tile):
    # crt     = "addi" : Additive composite error term
    #         = "mult" : Multiplicative composite error term
    # func    = "prod" : production frontier
    #         = "cost" : cost frontier
    # pps     = "vrs"  : variable returns to scale production possibility sets (pps)
    #         = "crs"  : constant returns to scale pps
    # tile    = "quantile" : quantile regression
    #         = "expectile": expectile regression

    # number of DMUS
    n = len(y)

    # number of inputs
    if type(x[0]) == int or type(x[0]) == float:
        m = 1
    else:
        m = len(x[0])

    # Creation of a Concrete Model
    model = ConcreteModel()

    # Set
    model.i = Set(initialize=range(n))
    model.j = Set(initialize=range(m))

    # Alias
    model.h = SetOf(model.i)

    # Variables
    model.a = Var(model.i, doc='alpha')
    model.b = Var(model.i, model.j, bounds=(0.0, None), doc='beta')
    model.ep = Var(model.i, doc='error term eplus')
    model.em = Var(model.i, doc='error term eminus')
    model.f = Var(model.i, bounds=(0.0, None), doc='estimated frontier')

    # Additive composite error term
    if crt == "addi":

        # production model
        if func == "prod":

            if tile == "quantile":

                # Objective function
                def objective_rule(model):
                    return tau * sum(model.ep[i] for i in model.i) + (1 - tau) * sum(model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if tile == "expectile":

                # Objective function
                def objective_rule(model):
                    return tau * sum(model.ep[i] * model.ep[i] for i in model.i) + (1 - tau) * sum(
                        model.em[i] * model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if pps == "vrs":

                # Constraints
                def reg_rule(model, i):
                    arow = x[i]
                    return y[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + model.ep[i] - model.em[
                        i]

                model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

                def concav_rule(model, i, h):
                    brow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * brow[j] for j in model.j) <= model.a[h] + sum(
                        model.b[h, j] * brow[j] for j in model.j)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

        # cost model
        if func == "cost":

            if tile == "quantile":

                # Objective function
                def objective_rule(model):
                    return tau * sum(model.ep[i] for i in model.i) + (1 - tau) * sum(model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if tile == "expectile":

                # Objective function
                def objective_rule(model):
                    return tau * sum(model.ep[i] * model.ep[i] for i in model.i) + (1 - tau) * sum(
                        model.em[i] * model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if pps == "vrs":

                # Constraints
                def reg_rule(model, i):
                    arow = x[i]
                    return y[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) + model.ep[i] - model.em[
                        i]

                model.reg = Constraint(model.i, rule=reg_rule, doc='regression')

                def concav_rule(model, i, h):
                    brow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * brow[j] for j in model.j) >= model.a[h] + sum(
                        model.b[h, j] * brow[j] for j in model.j)

                model.concav = Constraint(model.i, model.h, rule=concav_rule, doc='concavity constraint')

    # Multiplicative composite error term
    if crt == "mult":

        # production model
        if func == "prod":

            if tile == "quantile":

                # Objectivr function
                def objective_rule(model):
                    return tau * sum(model.ep[i] for i in model.i) + (1 - tau) * sum(model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if tile == "expectile":

                # Objectivr function
                def objective_rule(model):
                    return tau * sum(model.ep[i] * model.ep[i] for i in model.i) + (1 - tau) * sum(
                        model.em[i] * model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if pps == "vrs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.ep[i] - model.em[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    arow = x[i]
                    return model.f[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                def qconcav_rule(model, i, h):
                    brow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * brow[j] for j in model.j) <= model.a[h] + sum(
                        model.b[h, j] * brow[j] for j in model.j)

                model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

            if pps == "crs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.ep[i] - model.em[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    arow = x[i]
                    return model.f[i] == sum(model.b[i, j] * arow[j] for j in model.j) - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                def qconcav_rule(model, i, h):
                    brow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return sum(model.b[i, j] * brow[j] for j in model.j) <= sum(
                        model.b[h, j] * brow[j] for j in model.j)

                model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

        # cost model
        if func == "cost":

            if tile == "quantile":

                # Objective function
                def objective_rule(model):
                    return tau * sum(model.ep[i] for i in model.i) + (1 - tau) * sum(model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if tile == "expectile":

                # Objective function
                def objective_rule(model):
                    return tau * sum(model.ep[i] * model.ep[i] for i in model.i) + (1 - tau) * sum(
                        model.em[i] * model.em[i] for i in model.i)

                model.objective = Objective(rule=objective_rule, sense=minimize, doc='Define objective function')

            if pps == "vrs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.ep[i] - model.em[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    arow = x[i]
                    return model.f[i] == model.a[i] + sum(model.b[i, j] * arow[j] for j in model.j) - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                def qconcav_rule(model, i, h):
                    brow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return model.a[i] + sum(model.b[i, j] * brow[j] for j in model.j) >= model.a[h] + sum(
                        model.b[h, j] * brow[j] for j in model.j)

                model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

            if pps == "crs":

                # Constraints
                def qreg_rule(model, i):
                    return log(y[i]) == log(model.f[i] + 1) + model.ep[i] - model.em[i]

                model.qreg = Constraint(model.i, rule=qreg_rule, doc='log-transformed regression')

                def qlog_rule(model, i):
                    arow = x[i]
                    return model.f[i] == sum(model.b[i, j] * arow[j] for j in model.j) - 1

                model.qlog = Constraint(model.i, rule=qlog_rule, doc='cost function')

                def qconcav_rule(model, i, h):
                    brow = x[i]
                    if i == h:
                        return Constraint.Skip
                    return sum(model.b[i, j] * brow[j] for j in model.j) >= sum(
                        model.b[h, j] * brow[j] for j in model.j)

                model.qconcav = Constraint(model.i, model.h, rule=qconcav_rule, doc='concavity constraint')

    return model