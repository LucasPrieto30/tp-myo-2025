#Parte 6 · Mejora 1
from columns import Columns, price_column, add_coef, get_dual
from pyscipopt import Model, quicksum

import sys, time, os, json, math
from pyscipopt import Model, quicksum
class ColumnsInit(Columns):

    def _best_knapsack(self, a, banned):
        """
        el objetivo maximiza la suma de
        densidades dens_o^a en lugar de las unidades u_o.
        """
        O, I = self.O, self.I
        units_o = [sum(self.demand[o]) for o in range(O)]

        # ---- densidad por pedido y pasillo ----
        dens = [0.0]*O
        for o in range(O):
            cap_use = 0.0
            for i in range(I):
                if self.demand[o][i] and self.supply[a][i]:
                    cap_use += self.demand[o][i]/self.supply[a][i]
            dens[o] = units_o[o]/cap_use if cap_use > 0 else 0.0

        knap = Model(f"knap_init_{a}")
        z = {}
        for o in range(O):
            if o in banned or dens[o] == 0:
                continue
            z[o] = knap.addVar(vtype="B", obj=dens[o], name=f"z{o}")

        for i in range(I):
            knap.addCons(
                quicksum(self.demand[o][i]*z[o] for o in z) <= self.supply[a][i]
            )
        tot = quicksum(units_o[o]*z[o] for o in z)
        knap.addCons(tot >= self.LB)
        knap.addCons(tot <= self.UB)

        knap.setMaximize()
        knap.hideOutput()
        knap.optimize()

        if knap.getStatus() != "optimal" or knap.getObjVal() < 1e-6:
            return [], 0

        sel   = [o for o in z if knap.getVal(z[o]) > 0.5]
        units = sum(units_o[o] for o in sel)
        return sel, units

    def _initial_patterns(self, a):
        """
        Devuelve varios patrones candidatos para el pasillo a
        usando el pequeño knapsack de arriba.

        ─ Empieza sin ordenes prohibidas
        ─ Agrega la mejor ola encontrada
        ─ Banea sus ordenes y busca una segunda ola, etc.
        ─ Corte cuando no quede inventario o supere time-limit interno
        """
        patterns = []
        banned = set()
        for _ in range(3):
            orders, units = self._best_knapsack(a, banned)
            if not orders:
                break
            patterns.append((orders, units))
            banned.update(orders)
        return patterns

    def _build_rmp(self, k):
        m = Model(f"RMP_k{k}")
        try: m.hideOutput()
        except AttributeError: m.setParam("display/verblevel", 0)
        m.setMaximize()

        zero  = m.addVar(lb=0, ub=0, name="zero")
        expr0 = 0 * zero
        order_cons = {o: m.addCons(expr0 <= 1, f"order_{o}") for o in range(self.O)}
        cov   = {i: m.addCons(expr0 >= 0, name=f"cov_{i}")    for i in range(self.I)}
        lb    = m.addCons(expr0 >= self.LB, name="LB")
        ub    = m.addCons(expr0 <= self.UB, name="UB")
        card  = m.addCons(expr0 == k,      name="card_k")

        cols = {}

        # dummy y slack
        dummy = m.addVar(vtype="B", obj=-1e6, name="dummy")
        add_coef(m, lb,   dummy, self.LB)
        add_coef(m, ub,   dummy, self.LB)
        add_coef(m, card, dummy, 1)
        cols[("dummy", frozenset())] = dummy

        slack = m.addVar(vtype="B", obj=-1e-3, name="slack")
        add_coef(m, lb,  slack, self.LB)
        add_coef(m, ub,  slack, self.LB)
        cols[("slack", frozenset())] = slack

        # para cada pasillo generamos varios columnas semilla
        for a in range(self.A):
            for orders, units in self._initial_patterns(a):
                vname = "col_" + str(a) + "_" + "_".join(map(str, orders))
                v = m.addVar(vtype="B", obj=units, name=vname)
                for i in range(self.I):
                    q = sum(self.demand[o][i] for o in orders)
                    if q: add_coef(m, cov[i], v, q)
                add_coef(m, lb,   v, units)
                add_coef(m, ub,   v, units)
                add_coef(m, card, v, 1)
                for o in orders:
                    add_coef(m, order_cons[o], v, 1)
                cols[(a, frozenset(orders))] = v

            if (a, frozenset()) not in cols:
                v = m.addVar(vtype="B", obj=0, name=f"col_{a}_0")
                add_coef(m, card, v, 1)
                cols[(a, frozenset())] = v

        return {"model": m, "cols": cols, "cov": cov,
                "lb": lb, "ub": ub, "card": card, "order_cons": order_cons}
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    umbral = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    instance = sys.argv[1]

    solver = Columns(instance)
    tic = time.time()
    best = solver.Opt_ExplorarCantidadPasillos(umbral)
    elapsed  = time.time() - tic
    if len(sys.argv) > 3: 
        out_file = sys.argv[3]
        with open(out_file, "w") as f:
            json.dump(best, f)
    m = solver._last_model
    total_c  = m.getNConss()
    total_v  = m.getNVars()
    rmp_v    = sum(1 for v in m.getVars() if v.vtype() == "B")
    dual_bd  = m.getDualbound()

    print(f"METRICS inst={os.path.basename(instance)} "
        f"conss={total_c} vars={total_v} vars_rmp={rmp_v} "
        f"dual={int(dual_bd)} obj={best['obj'] if best else 'NA'} "
        f"time={elapsed:.1f}")