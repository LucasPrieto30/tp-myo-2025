#!/usr/bin/env python3
"""
Parte 5 - Column Generation puro (patrones pasillo-pedidos)
-----------------------------------------------------------
Resuelve el “wave picking” con:
  • RMP(k)  - columnas = (pasillo, subconjunto de órdenes)
  • subproblema de pricing 0-1 knapsack por pasillo
"""

import sys, time, math
from pyscipopt import Model, quicksum

def add_coef(model, cons, var, coef):
    if hasattr(model, "addCoefLinear"):
        model.addCoefLinear(cons, var, coef)
    else:
        cons.addCoef(var, coef)

def get_dual(model, cons):
    try:
        return (model.getDualsolLinear(cons)
                if hasattr(model, "getDualsolLinear")
                else model.getDual(cons))
    except Exception:
        return 0.0

def read_instance(fname):
    with open(fname) as f:
        O, I, A = map(int, f.readline().split())
        demand = [[0]*I for _ in range(O)]
        for o in range(O):
            k, *pairs = map(int, f.readline().split())
            for j in range(0, 2*k, 2):
                i, q = pairs[j], pairs[j+1]
                demand[o][i] = q
        supply = [[0]*I for _ in range(A)]
        for a in range(A):
            l, *pairs = map(int, f.readline().split())
            for j in range(0, 2*l, 2):
                i, q = pairs[j], pairs[j+1]
                supply[a][i] = q
        LB, UB = map(int, f.readline().split())
    return O, I, A, demand, supply, LB, UB


# pricing: knapsack 0-1
def price_column(a, dual_cov, dual_lb, dual_ub, dual_k, dual_order, 
                 demand, supply, LB, UB):
    O = len(demand)
    I = len(supply[0])
    units_o = [sum(demand[o]) for o in range(O)] #u_o

    price_o = []
    for o in range(O):
        rc_part  = units_o[o] # + u_o
        rc_part -= sum(dual_cov[i]*demand[o][i] for i in range(I)) #  -π_i d_oi
        rc_part -= units_o[o]*dual_lb #  -λ u_o
        rc_part -= units_o[o]*dual_ub #  -μ u_o
        rc_part -= dual_order[o]
        price_o.append(rc_part)
    CAP = 1e+09
    for o in range(O):
        if not math.isfinite(price_o[o]):
            price_o[o] = CAP if price_o[o] > 0 else -CAP
        elif price_o[o] >  CAP:
            price_o[o] =  CAP
        elif price_o[o] < -CAP:
            price_o[o] = -CAP

    knap = Model(f"pricing_{a}")
    z = {o: knap.addVar(vtype="B", obj=price_o[o]) for o in range(O)}

    for i in range(I):
        knap.addCons(quicksum(demand[o][i] * z[o] for o in range(O))
                     <= supply[a][i])
    tot = quicksum(units_o[o] * z[o] for o in range(O))
    knap.addCons(tot >= LB)
    knap.addCons(tot <= UB)

    try: knap.hideOutput()
    except AttributeError: knap.setParam("display/verblevel", 0)

    knap.optimize()
    if knap.getStatus() != "optimal":
        return None

    rc = knap.getObjVal() - dual_k
    if rc <= 1e-6:
        return None
    sel   = [o for o in z if knap.getVal(z[o]) > 0.5]
    units = sum(units_o[o] for o in sel)
    print(f"------------------------------------[pricing] a={a:3d}  rc={rc:6.2f}  units={units:3d}  sel={sel}------------------------------------", flush=True)
    return sel, units, rc

class Columns:
    def __init__(self, fname):
        (self.O, self.I, self.A,
         self.demand, self.supply,
         self.LB, self.UB) = read_instance(fname)
        self.rmp_cache = {} # un modelo por valor de k
        self.best_sol  = None

    # ---------------- patrón greed max por pasillo -------------------------
    def _greedy_pattern(self, a):
        units_o = [(o, sum(self.demand[o])) for o in range(self.O)]
        units_o.sort(key=lambda t: -t[1])
        cap = self.supply[a][:]
        sel, tot = [], 0
        for o, u in units_o:
            if tot + u > self.UB:
                continue
            if all(self.demand[o][i] <= cap[i] for i in range(self.I)):
                sel.append(o); tot += u
                for i in range(self.I):
                    cap[i] -= self.demand[o][i]
            if tot == self.UB:
                break
        return sel, tot

    def _build_rmp(self, k):
        m = Model(f"RMP_k{k}")
        m.setMaximize()
        zero  = m.addVar(lb=0, ub=0, name="zero")
        expr0 = 0 * zero    
        order_cons = {
            o: m.addCons(expr0 <= 1, f"order_{o}")
            for o in range(self.O)
        }
        cov   = {i: m.addCons(expr0 >= 0,            name=f"cov_{i}")
                 for i in range(self.I)}
        lb    = m.addCons(expr0 >= self.LB,          name="LB")
        ub    = m.addCons(expr0 <= self.UB,          name="UB")
        card  = m.addCons(expr0 == k,                name="card_k")

        cols = {}

        dummy = m.addVar(vtype="C", lb=0, ub=1, obj=-1e6, name="dummy")
        add_coef(m, lb,   dummy, self.LB)
        add_coef(m, ub,   dummy, self.LB)
        add_coef(m, card, dummy, 1)
        cols[("dummy", frozenset())] = dummy

        slack = m.addVar(vtype="C", lb=0, ub=1, obj=-1e-3, name="slack")
        add_coef(m, lb,  slack, self.LB)
        add_coef(m, ub,  slack, self.LB)
        cols[("slack", frozenset())] = slack

        for a in range(self.A):
            orders, units = self._greedy_pattern(a)
            if not orders:
                v = m.addVar(vtype="C", lb=0, ub=1, obj=0, name=f"col_{a}_0")
                add_coef(m, card, v, 1)
                cols[(a, frozenset())] = v
                continue

            vname = f"col_{a}_" + "_".join(map(str, orders))
            v = m.addVar(vtype="C", lb=0, ub=1, obj=units, name=vname)
            for i in range(self.I):
                q = sum(self.demand[o][i] for o in orders)
                if q: add_coef(m, cov[i], v, q)
            add_coef(m, lb,   v, units)
            add_coef(m, ub,   v, units)
            add_coef(m, card, v, 1)
            for o in orders:
                add_coef(m, order_cons[o], v, 1) 
            cols[(a, frozenset(orders))] = v
        return {"model": m, "cols": cols, "cov": cov,
                "lb": lb, "ub": ub, "card": card,  "order_cons": order_cons}



    def _solve_integer(self, pack, time_left):
            """
            Convierte todas las columnas actuales en binarias y resuelve
            el problema entero sin volver a llamar al pricing.
            """
            m = pack["model"]
            m.freeTransform() # vuelve al modelo 'original'
            for v in m.getVars():
                if v.name.startswith("col_"):
                    m.chgVarType(v, "B")
                    
            m.setParam("limits/time", max(time_left, 0.1))
            m.optimize()

    def _add_column(self, pack, a, orders, units):
        key = (a, frozenset(orders))
        if key in pack["cols"]:
            return
        m = pack["model"]
        v = m.addVar(vtype="C", lb=0, ub=1, obj=units,
                     name=f"col_{a}_" + "_".join(map(str, orders)))
        for i in range(self.I):
            q = sum(self.demand[o][i] for o in orders)
            if q: add_coef(m, pack["cov"][i], v, q)
        add_coef(m, pack["lb"],   v, units)
        add_coef(m, pack["ub"],   v, units)
        add_coef(m, pack["card"], v, 1)
        for o in orders:
            add_coef(m, pack["order_cons"][o], v, 1)
        pack["cols"][key] = v

    def Opt_cantidadPasillosFija(self, k, umbral, final_exact=False):
        if k not in self.rmp_cache:
            self.rmp_cache[k] = self._build_rmp(k)
        pack = self.rmp_cache[k];  m = pack["model"]

        start = time.time(); rounds = 0
        while True:
            rem = max(0.01, umbral - (time.time() - start))
            m.setParam("limits/time", rem)
            m.optimize()
            if m.getStatus() != "optimal":
                break

            dual_cov = [get_dual(m, pack["cov"][i]) for i in range(self.I)]
            dual_lb  = get_dual(m, pack["lb"])
            dual_ub  = get_dual(m, pack["ub"])
            dual_k   = get_dual(m, pack["card"])
            dual_order = [get_dual(m, pack["order_cons"][o]) for o in range(self.O)]
            any_new = False
            for a in range(self.A):
                priced = price_column(a, dual_cov, dual_lb, dual_ub, dual_k, dual_order,
                                      self.demand, self.supply,
                                      self.LB, self.UB)
                if priced:
                    sel, units, _ = priced
                    m.freeTransform() 
                    self._add_column(pack, a, sel, units)
                    any_new = True
            if not any_new:
                m.freeTransform()
                for v in m.getVars(): m.chgVarType(v, "B") 
                m.optimize()
                break
              

            rounds += 1
            if (time.time()-start) >= 0.8*umbral:
                break

        restante = umbral - (time.time() - start)
        self._solve_integer(pack, restante)
        debug_wave = self._extract_incl_slack(pack)
        print(">> Ola con slack antes de fijar pasillos:", debug_wave)
        return self._extract(pack)

    def Opt_PasillosFijos(self, pasillos, umbral):
        """
        Reoptimiza el mejor k fijando exactamente los pasillos =1/0.
        `pasillos` es un set de índices que deben quedar en 1.
        """
        k = len(pasillos)
        pack = self._build_rmp(k)
        m    = pack["model"]
        
        for v in m.getVars():
            if v.name.startswith(("slack", "dummy")):
                m.chgVarUb(v, 0.0)

        for a in range(self.A):
            var = pack["cols"].get((a, frozenset()))
            if var is None:
                continue
            if a in pasillos:
                m.chgVarLb(var, 1)
                m.chgVarUb(var, 1)
            else:
                m.chgVarUb(var, 0)
        m.setParam("limits/time", max(umbral, 0.1))
        m.optimize()
        return self._extract(pack)

    def Opt_ExplorarCantidadPasillos(self, umbral):
        start = time.time()
        best_val = float("-inf"); best_sol = None
        k_list = list(range(1, self.A+1))

        while k_list and (time.time()-start) < umbral:
            k = k_list.pop(0)
            rem = umbral - (time.time()-start)
            sol = self.Opt_cantidadPasillosFija(k, rem, True)

            if sol and (best_sol is None or sol["obj"] > best_val or
                         (sol["obj"] == best_val and
                          len(sol["aisles"]) < len(best_sol["aisles"]))):
                best_val = sol["obj"]; best_sol = sol

            if best_sol:
                k_list = self._rankear(k_list, best_sol["aisles"])

        if best_sol:
            rem = umbral - (time.time()-start)
            rem = max(rem, 0.1)
            best_sol = self.Opt_PasillosFijos(best_sol["aisles"], rem)

        self.best_sol = best_sol
        return best_sol

    def _rankear(self, k_list, best_aisles):
        """Ordena k_list según lo ‘prometedor’ que es cada k."""
        return sorted(k_list, key=lambda kk: abs(kk - len(best_aisles)))

    def _extract_incl_slack(self, pack):
        """Igual que _extract pero permite slack/dummy (para debug)."""
        m = pack["model"]
        if m.getStatus() != "optimal":
            return None

        ais, ords = set(), set()
        for v in m.getVars():
            if v.name.startswith("col_") and m.getVal(v) > 0.5:
                p = v.name.split("_")
                ais.add(int(p[1]))
                ords.update(int(x) for x in p[2:])

        if not ords:
            return None

        units = sum(sum(self.demand[o]) for o in ords)
        k     = len(ais) or 1
        prod  = units / k

        return {"obj": prod, "units": units, "aisles": ais, "orders": ords}

    def _extract(self, pack):
        """Devuelve la ola sólo si está libre de slack/dummy."""
        m = pack["model"]
        if m.getStatus() != "optimal":
            return None

        #Si slack o dummy están activos, rechazamos la solución
        for v in m.getVars():
            if v.name.startswith(("slack", "dummy")) and m.getVal(v) > 1e-6:
                return None # solución infactible

        ais, ords = set(), set()
        for v in m.getVars():
            if m.getVal(v) > 0.5 and v.name.startswith("col_"):
                p = v.name.split("_")
                ais.add(int(p[1]))
                ords.update(int(x) for x in p[2:])

        if not ords:
            return None
        
        units = sum(sum(self.demand[o]) for o in ords)
        if units < self.LB or units > self.UB:
            return None
        k     = len(ais) or 1
        prod  = units / k

        return {
            "obj":     prod,
            "units":   units,
            "aisles":  ais,
            "orders":  ords,
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python columns_part5.py input_0001.txt [tiempo_seg]")
        sys.exit(1)

    umbral = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    instance = sys.argv[1]

    solver = Columns(instance)
    best = solver.Opt_ExplorarCantidadPasillos(umbral)
    print("\n== Mejor ola ==")
    print(best)
