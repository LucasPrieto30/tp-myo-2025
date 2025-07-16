#!/usr/bin/env python3
"""
Parte 7 – Modelo de competencia
===============================

Branch-and-Price *minimalista*:

  • Semillas greedy densidad-unidades.
  • Pricer que resuelve un knapsack 0-1 por pasillo y añade columnas.
  • Variables binarias  ⇒  SCIP hace branch-and-bound por defecto.
  • Rankear(k) mediante puntuación UCB.
  • Purga de columnas inactivas ≥ PRUNE_HORIZON rondas.
"""

import sys, time, math
from collections import defaultdict
from typing import List, Dict, Tuple, Set

from pyscipopt import Model, Pricer, quicksum, SCIP_RESULT

# ────────────────────────────────────────────────────────────────────
#  Utilidades
# ────────────────────────────────────────────────────────────────────
def add_coef(model: Model, cons, var, coef):
    if hasattr(model, "addCoefLinear"):
        model.addCoefLinear(cons, var, coef)
    else:
        cons.addCoef(var, coef)

def get_dual(model: Model, cons):
    try:
        return (model.getDualsolLinear(cons)
                if hasattr(model, "getDualsolLinear")
                else model.getDual(cons))
    except Exception:
        return 0.0           # restricción eliminada en presolve

# ────────────────────────────────────────────────────────────────────
#  Lectura de instancia
# ────────────────────────────────────────────────────────────────────
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

# ────────────────────────────────────────────────────────────────────
#  Sub-problema de pricing (knapsack 0-1 por pasillo)
# ────────────────────────────────────────────────────────────────────
def price_column(a: int, dual_cov: List[float],
                 dual_lb: float, dual_ub: float,
                 dual_k: float, dual_ord: List[float],
                 demand: List[List[int]], supply: List[List[int]],
                 LB: int, UB: int):
    O = len(demand); I = len(supply[0])
    u_o = [sum(demand[o]) for o in range(O)]

    rc_obj = []
    for o in range(O):
        rc  = u_o[o]
        rc -= sum(dual_cov[i]*demand[o][i] for i in range(I))
        rc -= u_o[o]*(dual_lb + dual_ub)
        rc -= dual_ord[o]
        rc_obj.append(rc)

    knap = Model(f"pricing_{a}")
    z = {o: knap.addVar(vtype="B", obj=rc_obj[o]) for o in range(O)}

    for i in range(I):
        knap.addCons(quicksum(demand[o][i]*z[o] for o in range(O))
                     <= supply[a][i])
    tot = quicksum(u_o[o]*z[o] for o in range(O))
    knap.addCons(tot >= LB)
    knap.addCons(tot <= UB)

    knap.hideOutput()
    knap.optimize()
    if knap.getStatus() != "optimal":
        return None

    red_cost = knap.getObjVal() - dual_k
    if red_cost <= 1e-6:
        return None

    sel = [o for o in z if knap.getVal(z[o]) > 0.5]
    units = sum(u_o[o] for o in sel)
    return sel, units, red_cost

# ────────────────────────────────────────────────────────────────────
#  Pricer
# ────────────────────────────────────────────────────────────────────
class WavePricer(Pricer):
    def __init__(self, solver, pack):
        super().__init__()
        self.solver = solver   # referencia al Solver principal
        self.pack   = pack     # dicc. con modelo y restricciones

    # SCIP llamará a esto mientras exista costo reducido negativo
    def pricerredcost(self):
        m       = self.model
        pack    = self.pack
        added   = False

        dual_cov   = [get_dual(m, pack["cov"][i])   for i in range(self.solver.I)]
        dual_lb    = get_dual(m, pack["lb"])
        dual_ub    = get_dual(m, pack["ub"])
        dual_k     = get_dual(m, pack["card"])
        dual_order = [get_dual(m, pack["order"][o]) for o in range(self.solver.O)]

        for a in range(self.solver.A):
            res = price_column(a, dual_cov, dual_lb, dual_ub, dual_k,
                               dual_order,
                               self.solver.demand, self.solver.supply,
                               self.solver.LB, self.solver.UB)
            if not res:
                continue
            orders, units, _ = res
            key = (a, frozenset(orders))
            if key in pack["cols"]:
                continue                      # ya existe

            # ── crear la variable en el nodo actual ─────────────────────────
            name = f"col_{a}_" + "_".join(map(str, orders))
            var  = m.addVar(vtype="B", obj=units, name=name)

            for i in range(self.solver.I):
                q = sum(self.solver.demand[o][i] for o in orders)
                if q:
                    add_coef(m, pack["cov"][i], var, q)
            add_coef(m, pack["lb"]  , var, units)
            add_coef(m, pack["ub"]  , var, units)
            add_coef(m, pack["card"], var, 1)
            for o in orders:
                add_coef(m, pack["order"][o], var, 1)

            m.addPricedVar(var, 1.0)          # coste de columna ya en obj
            pack["cols"][key] = var
            added = True

        return {"result": SCIP_RESULT.SUCCESS if added
                          else SCIP_RESULT.DIDNOTFIND}

    # no usamos branching dinámico → pricerfarkas no necesario
    def pricerfarkas(self):
        return {"result": SCIP_RESULT.DIDNOTRUN}

# ────────────────────────────────────────────────────────────────────
#  Solver principal
# ────────────────────────────────────────────────────────────────────
class Solver:
    PRUNE_HORIZON = 3
    PRUNE_WARMUP  = 5

    def __init__(self, fname: str):
        (self.O, self.I, self.A,
         self.demand, self.supply,
         self.LB, self.UB) = read_instance(fname)

        self.rmp_cache : Dict[int, dict] = {}
        self.last_seen : Dict[str,int]   = defaultdict(int)
        self.k_stats   : Dict[int,dict]  = {k:{"best":-1e18,"trials":0}
                                            for k in range(1,self.A+1)}

    # ---------------------------------------------------------------
    def _greedy_pattern(self, a: int) -> Tuple[List[int], int]:
        units = [(o, sum(self.demand[o])) for o in range(self.O)]
        dens  = lambda t: t[1] / (sum(1 for q in self.demand[t[0]] if q>0) or 1)
        units.sort(key=lambda t: (-dens(t), -t[1]))

        cap = self.supply[a][:]; sel=[]; tot=0
        for o,u in units:
            if tot+u>self.UB: continue
            if all(self.demand[o][i]<=cap[i] for i in range(self.I)):
                sel.append(o); tot+=u
                for i in range(self.I): cap[i]-=self.demand[o][i]
            if tot==self.UB: break
        return sel, tot

    # ---------------------------------------------------------------
    def _build_master(self, k:int):
        m = Model(f"RMP_k{k}"); m.hideOutput(); m.setMaximize()
        zero = m.addVar(lb=0,ub=0,name="zero"); expr0 = 0*zero

        order = {o:m.addCons(expr0<=1,f"ord_{o}") for o in range(self.O)}
        cov   = {i:m.addCons(expr0>=0,f"cov_{i}") for i in range(self.I)}
        lb    = m.addCons(expr0>=self.LB,"LB")
        ub    = m.addCons(expr0<=self.UB,"UB")
        card  = m.addCons(expr0==k, "card_k")

        cols={}

        # dummy y slack
        d = m.addVar(vtype="B",obj=-1e6,name="dummy")
        for cons in (lb,ub): add_coef(m,cons,d,self.LB)
        add_coef(m,card,d,1); cols[("dummy",frozenset())]=d

        s = m.addVar(vtype="B",obj=-1e-3,name="slack")
        for cons in (lb,ub): add_coef(m,cons,s,self.LB)
        cols[("slack",frozenset())]=s

        for a in range(self.A):
            orders,units = self._greedy_pattern(a)
            if not orders:
                v=m.addVar(vtype="B",obj=0,name=f"col_{a}_0")
                add_coef(m,card,v,1); cols[(a,frozenset())]=v; continue
            name=f"col_{a}_"+"_".join(map(str,orders))
            v=m.addVar(vtype="B",obj=units,name=name)
            for i in range(self.I):
                q=sum(self.demand[o][i] for o in orders)
                if q: add_coef(m,cov[i],v,q)
            for cons in (lb,ub): add_coef(m,cons,v,units)
            add_coef(m,card,v,1)
            for o in orders: add_coef(m,order[o],v,1)
            cols[(a,frozenset(orders))]=v

        pack={"model":m,"cov":cov,"lb":lb,"ub":ub,"card":card,"order":order,"cols":cols}
        pricer=WavePricer(self,pack)
        m.includePricer(pricer,"WavePricer","",1,False)

        return pack

    # ---------------------------------------------------------------
    def _purge(self, pack, round_):
        if round_<self.PRUNE_WARMUP: return
        m=pack["model"]; gone=[]
        for v in m.getVars():
            if not v.name.startswith("col_"): continue
            key=v.name
            if m.getVal(v)<1e-6: self.last_seen[key]+=1
            else: self.last_seen[key]=0
            if self.last_seen[key]>=self.PRUNE_HORIZON: gone.append(v)
        if gone:
            m.freeTransform()
            for v in gone:
                m.delVar(v); self.last_seen.pop(v.name,None)

    # ---------------------------------------------------------------
    def solve_for_k(self,k:int,tlim:float):
        pack=self.rmp_cache.setdefault(k,self._build_master(k))
        m=pack["model"]; start=time.time(); rounds=0
        while True:
            rounds+=1
            m.setParam("limits/time",max(0.01,tlim-(time.time()-start)))
            ncols_before = len(pack["cols"])
            m.optimize()
            if m.getStatus()!="optimal": break
            self._purge(pack,rounds)
            ncols_after = len(pack["cols"])
            if ncols_after == ncols_before:          #  ⇐  nada nuevo → convergió
                break
            # SCIP ya llamó al pricer; si no añadió nada, corte
            if time.time()-start>0.9*tlim: break
        return self._extract(pack)

    # ---------------------------------------------------------------
    # pura línea para def
    def _ucb(self, k):
        s=self.k_stats[k]
        if s["trials"]==0: return float("inf")
        C=0.5; tot=sum(d["trials"] for d in self.k_stats.values())+1
        return s["best"]+C*math.sqrt(math.log(tot)/s["trials"])

    # ---------------------------------------------------------------
    def solve(self,tlimit:float):
        start=time.time(); best=None; best_val=-1e18
        k_list=list(range(1,self.A+1))
        while k_list and time.time()-start<tlimit:
            k_list.sort(key=self._ucb,reverse=True)
            k=k_list.pop(0)
            remaining=tlimit-(time.time()-start)
            sol=self.solve_for_k(k,remaining)
            st=self.k_stats[k]; st["trials"]+=1
            if sol: st["best"]=max(st["best"],sol["obj"])
            if sol and sol["obj"]>best_val:
                best_val=sol["obj"]; best=sol
        return best

    # ---------------------------------------------------------------
    def _extract(self,pack):
        m=pack["model"]
        if m.getStatus()!="optimal": return None
        for v in m.getVars():
            if v.name.startswith(("dummy","slack")) and m.getVal(v)>1e-6:
                return None
        ais=set(); ords=set()
        for v in m.getVars():
            if v.name.startswith("col_") and m.getVal(v)>0.5:
                parts=v.name.split("_"); ais.add(int(parts[1]))
                ords.update(int(x) for x in parts[2:])
        if not ords: return None
        units=sum(sum(self.demand[o]) for o in ords)
        if units<self.LB or units>self.UB: return None
        return {"obj":units/len(ais),"units":units,
                "aisles":sorted(ais),"orders":sorted(ords)}

# ────────────────────────────────────────────────────────────────────
#  Main
# ────────────────────────────────────────────────────────────────────
def main(argv):
    if len(argv)<2:
        print("Uso: python modelo_competencia.py instancia.txt [tiempo_seg]")
        sys.exit(1)
    inst = argv[1]
    tlim = float(argv[2]) if len(argv)>2 else 300
    solver=Solver(inst)
    best = solver.solve(tlim)
    print("\n== Mejor ola ==")
    print(best)

if __name__=="__main__":
    main(sys.argv)
