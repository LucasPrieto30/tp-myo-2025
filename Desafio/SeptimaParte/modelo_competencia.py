#!/usr/bin/env python3
"""
Modelo de competencia (Séptima parte)
------------------------------------
• Column Generation + pequeñas extensiones para competir:
   – Semillas (columnas iniciales) algo mejores.
   – Rankear(k) con política tipo UCB.
   – Purga de columnas inactivas durante ≥ 3 iteraciones.

El archivo es *auto‑contenible*: no depende de ningún otro módulo.
"""

import sys, os, time, math
from collections import defaultdict
from typing import Dict, List, Tuple, Set, FrozenSet, Optional

from pyscipopt import Model, quicksum  # type: ignore

##############################################################################
# utilidades genéricas                                                       #
##############################################################################

def add_coef(model: Model, cons, var, coef):
    """Compatibilidad SCIP 7/8 (PySCIPOpt ≥ 4)."""
    if hasattr(model, "addCoefLinear"):
        model.addCoefLinear(cons, var, coef)
    else:
        cons.addCoef(var, coef)

def get_dual(model: Model, cons):
    """Obtiene el valor dual robusto a presolve."""
    try:
        return model.getDualsolLinear(cons) if hasattr(model, "getDualsolLinear") else model.getDual(cons)
    except Exception:
        return 0.0               # fila eliminada por presolve

##############################################################################
# lectura de instancia                                                       #
##############################################################################

def read_instance(fname: str):
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

##############################################################################
# pricing – knapsack 0‑1                                                     #
##############################################################################

def price_column(a: int, dual_cov: List[float], dual_lb: float, dual_ub: float,
                 dual_k: float, dual_order: List[float],
                 demand: List[List[int]], supply: List[List[int]],
                 LB: int, UB: int, debug: bool=False):
    """Resuelve el sub‑problema para pasillo *a*.
       Devuelve (ordersSel, units, redCost) o None si rc≤0."""
    O = len(demand)
    I = len(supply[0])
    units_o = [sum(demand[o]) for o in range(O)]

    price_o: List[float] = []
    for o in range(O):
        rc  = units_o[o]                              # + u_o
        rc -= sum(dual_cov[i]*demand[o][i] for i in range(I))
        rc -= units_o[o]*dual_lb                     # ‑ λ u_o
        rc -= units_o[o]*dual_ub                     # ‑ μ u_o
        rc -= dual_order[o]
        price_o.append(rc)

    knap = Model(f"pricing_{a}")
    z = {o: knap.addVar(vtype="B", obj=price_o[o]) for o in range(O)}

    for i in range(I):
        knap.addCons(quicksum(demand[o][i]*z[o] for o in range(O)) <= supply[a][i])
    tot = quicksum(units_o[o]*z[o] for o in range(O))
    knap.addCons(tot >= LB)
    knap.addCons(tot <= UB)

    try:
        knap.hideOutput()
    except AttributeError:
        knap.setParam("display/verblevel", 0)

    knap.optimize()
    if knap.getStatus() != "optimal":
        return None

    rc = knap.getObjVal() - dual_k
    if rc <= 1e-6:
        return None

    sel = [o for o in z if knap.getVal(z[o]) > 0.5]
    units = sum(units_o[o] for o in sel)
    if debug:
        print(f"[pricing] a={a:3d} rc={rc:6.2f} units={units:3d} sel={sel}")
    return sel, units, rc

##############################################################################
# clase principal                                                            #
##############################################################################

class Solver:

    # purga si variable 0 en las últimas PRUNE_HORIZON iteraciones
    PRUNE_HORIZON = 3
    PRUNE_WARMUP  = 5      # no podar antes de la 5ª ronda  
    def __init__(self, fname: str):
        (self.O, self.I, self.A,
         self.demand, self.supply,
         self.LB, self.UB) = read_instance(fname)
        print("sdfds")
        self.rmp_cache: Dict[int, dict] = {}
        self.k_stats   : Dict[int, dict] = {
            k: {"best": float("-inf"), "trials": 0}
            for k in range(1, self.A+1)
        }
        self.last_seen: Dict[str, int] = defaultdict(int)  # <<–– CAMBIO AQUÍ (key=str)
        self.best_sol  = None

    # ------------------------------------------------------------------
    # semilla greed‑max (pero 2‑fase: primero densidad, luego unidades)
    # ------------------------------------------------------------------
    def _greedy_pattern(self, a: int):
        units_o = [(o, sum(self.demand[o])) for o in range(self.O)]
        # orden por densidad (u/|items|) para usar bien capacidad de pasillo
        dens   = lambda t: t[1] / (sum(1 for q in self.demand[t[0]] if q>0) or 1)
        units_o.sort(key=lambda t: (-dens(t), -t[1]))

        cap = self.supply[a][:]
        sel: List[int] = []
        tot = 0
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

    # ------------------------------------------------------------------
    # RMP(k) inicial
    # ------------------------------------------------------------------
    def _build_rmp(self, k: int):
        m = Model(f"RMP_k{k}")
        try:
            m.hideOutput()
        except AttributeError:
            m.setParam("display/verblevel", 0)
        m.setMaximize()

        zero  = m.addVar(lb=0, ub=0, name="zero")
        expr0 = 0*zero

        order_c = {o: m.addCons(expr0 <= 1, f"order_{o}") for o in range(self.O)}
        cov_c   = {i: m.addCons(expr0 >= 0, f"cov_{i}")    for i in range(self.I)}
        lb_c    = m.addCons(expr0 >= self.LB,  "LB")
        ub_c    = m.addCons(expr0 <= self.UB,  "UB")
        k_c     = m.addCons(expr0 == k,        "card_k")

        cols = {}

        # dummy y slack
        dummy = m.addVar(vtype="B", obj=-1e6, name="dummy")
        add_coef(m, lb_c, dummy, self.LB)
        add_coef(m, ub_c, dummy, self.LB)
        add_coef(m, k_c , dummy, 1)
        cols[("dummy", frozenset())] = dummy

        slack = m.addVar(vtype="B", obj=-1e-3, name="slack")
        add_coef(m, lb_c, slack, self.LB)
        add_coef(m, ub_c, slack, self.LB)
        cols[("slack", frozenset())] = slack

        # una semilla por pasillo
        for a in range(self.A):
            orders, units = self._greedy_pattern(a)
            if not orders:
                v = m.addVar(vtype="B", obj=0, name=f"col_{a}_0")
                add_coef(m, k_c, v, 1)
                cols[(a, frozenset())] = v
                continue
            vname = f"col_{a}_" + "_".join(map(str, orders))
            v = m.addVar(vtype="B", obj=units, name=vname)
            for i in range(self.I):
                q = sum(self.demand[o][i] for o in orders)
                if q:
                    add_coef(m, cov_c[i], v, q)
            add_coef(m, lb_c, v, units)
            add_coef(m, ub_c, v, units)
            add_coef(m, k_c , v, 1)
            for o in orders:
                add_coef(m, order_c[o], v, 1)
            cols[(a, frozenset(orders))] = v

        return {
            "model": m,
            "cols" : cols,
            "cov"  : cov_c,
            "lb"   : lb_c,
            "ub"   : ub_c,
            "card" : k_c,
            "order": order_c,
        }

    # ------------------------------------------------------------------
    def _add_column(self, pack: dict, a: int, orders: List[int], units: int):
        key = (a, frozenset(orders))
        if key in pack["cols"]:
            return
        m = pack["model"]
        v = m.addVar(vtype="B", obj=units, name=f"col_{a}_"+"_".join(map(str,orders)))
        for i in range(self.I):
            q = sum(self.demand[o][i] for o in orders)
            if q:
                add_coef(m, pack["cov"][i], v, q)
        add_coef(m, pack["lb"],   v, units)
        add_coef(m, pack["ub"],   v, units)
        add_coef(m, pack["card"], v, 1)
        for o in orders:
            add_coef(m, pack["order"][o], v, 1)
        pack["cols"][key] = v

    # ------------------------------------------------------------------
    # lógica de purga & timestamp
    # ------------------------------------------------------------------
    def _after_opt(self, pack: dict, current_round: int):
        """
        ▸ Registra cuántas rondas lleva cada columna sin estar en la base
        ▸ Poda las que superen PRUNE_HORIZON, pero solo después de PRUNE_WARMUP
        """
        m: Model = pack["model"]

        # 1) Actualizar contadores -------------------------------------------
        for var in m.getVars():
            if not var.name.startswith("col_"):
                continue                     # no es una columna de patrón

            key = var.name                  # String → hashable
            if m.getVal(var) < 1e-6:        # inactiva en esta ronda
                self.last_seen[key] = self.last_seen.get(key, 0) + 1
            else:                           # utilizada (valor 1)
                self.last_seen[key] = 0

        # 2) Si aún estamos en warm-up, salir sin podar ----------------------
        if current_round < self.PRUNE_WARMUP:
            return

        # 3) Recoger variables que superan el umbral -------------------------
        to_delete = []
        for var in m.getVars():
            key = var.name
            if key.startswith("col_") and self.last_seen.get(key, 0) >= self.PRUNE_HORIZON:
                to_delete.append(var)

        # 4) Purgar en bloque -------------------------------------------------
        if to_delete:
            m.freeTransform()               # una única llamada basta
            for var in to_delete:
                m.delVar(var)
                self.last_seen.pop(var.name, None)   # limpiar contador

    # ------------------------------------------------------------------
    def _solve_lp_for_k(self, k: int, tlim: float, debug: bool=False):
        if k not in self.rmp_cache:
            self.rmp_cache[k] = self._build_rmp(k)
        pack = self.rmp_cache[k]
        m: Model = pack["model"]
        rounds = 0
        start = time.time()
        while True:
            rounds += 1
            rem = max(0.01, tlim - (time.time()-start))
            m.setParam("limits/time", rem)
            m.optimize()
            if m.getStatus() != "optimal":
                break
            self._after_opt(pack, rounds)      # <<– purga

            dual_cov   = [get_dual(m, pack["cov"][i]) for i in range(self.I)]
            dual_lb    = get_dual(m, pack["lb"])
            dual_ub    = get_dual(m, pack["ub"])
            dual_k     = get_dual(m, pack["card"])
            dual_order = [get_dual(m, pack["order"][o]) for o in range(self.O)]

            any_new = False
            for a in range(self.A):
                res = price_column(a, dual_cov, dual_lb, dual_ub, dual_k,
                                   dual_order,
                                   self.demand, self.supply, self.LB, self.UB,
                                   debug=debug)
                if res:
                    sel, units, _ = res
                    m.freeTransform()
                    self._add_column(pack, a, sel, units)
                    any_new = True
            if not any_new:
                break

            if (time.time()-start) >= 0.9*tlim:
                break

        return self._extract(pack)

    # ------------------------------------------------------------------
    def _ucb_score(self, k: int):
        s = self.k_stats[k]
        if s["trials"] == 0:
            return float("inf")
        C = 0.5
        total = sum(t["trials"] for t in self.k_stats.values()) + 1
        return s["best"] + C*math.sqrt(math.log(total)/s["trials"])

    # ------------------------------------------------------------------
    def solve(self, tlim: float):
        start = time.time()
        best_val = float("-inf"); best_sol = None
        k_list = list(range(1, self.A+1))

        while k_list and (time.time()-start) < tlim:
            # selección según ranking/UCB
            k_list.sort(key=self._ucb_score, reverse=True)
            k = k_list.pop(0)
            print(k_list)
            remaining = tlim - (time.time()-start)
            sol = self._solve_lp_for_k(k, remaining)

            st = self.k_stats[k]
            st["trials"] += 1
            if sol:
                st["best"] = max(st["best"], sol["obj"])

            if sol and (best_sol is None or sol["obj"] > best_val or
                         (sol["obj"] == best_val and len(sol["aisles"]) < len(best_sol["aisles"]))):
                best_val = sol["obj"]; best_sol = sol

        self.best_sol = best_sol
        print(best_sol)
        return best_sol

    # ------------------------------------------------------------------
    def _extract(self, pack: dict):
        m: Model = pack["model"]
        if m.getStatus() != "optimal":
            return None
        # si slack/dummy activos ⇒ infactible real
        for v in m.getVars():
            if v.name.startswith(("slack","dummy")) and m.getVal(v) > 1e-6:
                return None

        ais: Set[int] = set(); ords: Set[int] = set()
        for v in m.getVars():
            if v.name.startswith("col_") and m.getVal(v) > 0.5:
                parts = v.name.split("_")
                ais.add(int(parts[1]))
                ords.update(int(x) for x in parts[2:])
        if not ords:
            return None
        units = sum(sum(self.demand[o]) for o in ords)
        if units < self.LB or units > self.UB:
            return None
        k = len(ais) or 1
        return {
            "obj": units/k,
            "units": units,
            "aisles": sorted(ais),
            "orders": sorted(ords),
        }

##############################################################################
# main                                                                       #
##############################################################################

def main(argv: List[str]):
    print("gola")
    if len(argv) < 2:
        print("uso: python modelo_competencia.py <input_file> [tiempo_seg]")
        sys.exit(1)
    inp = argv[1]
    tlim = float(argv[2]) if len(argv) > 2 else 300
    print(tlim)
    solver = Solver(inp)
    print("asa")
    best = solver.solve(tlim)

    print("\n== Mejor ola ==")
    print(best)

if __name__ == "__main__":
    main(sys.argv)
