#!/usr/bin/env python3
# ------------------------------------------------------------------
#  Solver – Partes 6 + 7  (Column Generation  +  Branch-and-Price)
# ------------------------------------------------------------------
import sys, time, os, json
from pyscipopt import Model, Pricer, quicksum

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

def binary_spread(n):
    """Orden 1..n = centro-mitades-cuartos (búsqueda «spread»)."""
    res = []
    def rec(lo, hi):
        if lo > hi: return
        mid = (lo+hi)//2
        res.append(mid)
        rec(lo, mid-1); rec(mid+1, hi)
    rec(1, n)
    return res

def price_column(a, dual_cov, dual_lb, dual_ub, dual_k,
                 demand, supply, LB, UB):
    O = len(demand);  I = len(supply[0])
    units_o = [sum(demand[o]) for o in range(O)]

    price_o = []
    for o in range(O):
        rc  =  units_o[o]
        rc -= sum(dual_cov[i]*demand[o][i] for i in range(I))
        rc -= units_o[o]*dual_lb
        rc -= units_o[o]*dual_ub
        price_o.append(rc)

    knap = Model(f"pricing_{a}")
    z = {o: knap.addVar(vtype="B", obj=price_o[o]) for o in range(O)}
    for i in range(I):
        knap.addCons(quicksum(demand[o][i]*z[o] for o in range(O))
                     <= supply[a][i])
    tot = quicksum(units_o[o]*z[o] for o in range(O))
    knap.addCons(tot >= LB);  knap.addCons(tot <= UB)
    try: knap.hideOutput()
    except AttributeError: knap.setParam("display/verblevel", 0)
    knap.optimize()
    if knap.getStatus() != "optimal":
        return None

    rc = knap.getObjVal() - dual_k
    if rc <= 1e-6:
        return None
    sel   = [o for o in z if knap.getVal(z[o]) > .5]
    units = sum(units_o[o] for o in sel)
    return sel, units, rc

class Columns:
    def __init__(self, fname):
        (self.O, self.I, self.A,
         self.demand, self.supply,
         self.LB, self.UB) = read_instance(fname)

        self.rmp_cache, self.best_sol = {}, None
        self.dual_of_k   = {}
        self.k_order     = binary_spread(self.A)

    def _greedy_pattern(self, a):
        units = [(o, sum(self.demand[o])) for o in range(self.O)]
        units.sort(key=lambda t: -t[1])
        cap = self.supply[a][:]; sel, tot = [], 0
        for o,u in units:
            if tot+u>self.UB: continue
            if all(self.demand[o][i] <= cap[i] for i in range(self.I)):
                sel.append(o); tot += u
                for i in range(self.I):
                    cap[i] -= self.demand[o][i]
            if tot == self.UB: break
        return sel, tot

    def _build_rmp(self, k):
        if k in self.rmp_cache:
            return self.rmp_cache[k]

        m = Model(f"RMP_k{k}"); m.setMaximize()
        try: m.hideOutput()
        except AttributeError: m.setParam("display/verblevel",0)

        zero = m.addVar(lb=0, ub=0, name="zero")
        expr0 = 0*zero
        cov  = {i:m.addCons(expr0>=0,  name=f"cov_{i}") for i in range(self.I)}
        lb   = m.addCons(expr0>=self.LB, name="LB")
        ub   = m.addCons(expr0<=self.UB, name="UB")
        card = m.addCons(expr0==k,       name="card_k")
        cols = {}

        dummy = m.addVar(vtype="B", obj=-1e6, name="dummy")
        add_coef(m, lb, dummy, self.LB); add_coef(m, ub, dummy, self.LB)
        add_coef(m, card, dummy, 1); cols[("dummy",frozenset())] = dummy

        slack = m.addVar(vtype="B", obj=-1e-3, name="slack")
        add_coef(m, lb, slack, self.LB); add_coef(m, ub, slack, self.LB)
        cols[("slack",frozenset())] = slack

        for a in range(self.A):
            orders, units = self._greedy_pattern(a)
            vname = (f"col_{a}_0" if not orders
                     else f"col_{a}_"+"_".join(map(str,orders)))
            v = m.addVar(vtype="B", obj=units, name=vname)
            add_coef(m, card, v, 1)
            if orders:
                for i in range(self.I):
                    q = sum(self.demand[o][i] for o in orders)
                    if q: add_coef(m, cov[i], v, q)
                add_coef(m, lb, v, units); add_coef(m, ub, v, units)
            cols[(a, frozenset(orders))] = v

        pack = {"model":m,"cols":cols,"cov":cov,"lb":lb,"ub":ub,"card":card}
        self.rmp_cache[k] = pack
        return pack

    def _add_column(self, pack, a, orders, units):
        key = (a, frozenset(orders))
        if key in pack["cols"]: return
        m = pack["model"]
        if m.getStage() >= 2:
            m.freeTransform()
        v = m.addVar(vtype="B", obj=units,
                     name=f"col_{a}_"+"_".join(map(str,orders)))
        for i in range(self.I):
            q = sum(self.demand[o][i] for o in orders)
            if q: add_coef(m, pack["cov"][i], v, q)
        add_coef(m, pack["lb"], v, units)
        add_coef(m, pack["ub"], v, units)
        add_coef(m, pack["card"], v, 1)
        pack["cols"][key] = v

    def Opt_cantidadPasillosFija(self, k, tlim):
        pack = self._build_rmp(k); m = pack["model"]
        t0 = time.time()
        while time.time()-t0 < tlim:
            m.optimize()
            if m.getStatus()!="optimal": break
            dual_cov = [get_dual(m, pack["cov"][i]) for i in range(self.I)]
            dual_lb  = get_dual(m, pack["lb"])
            dual_ub  = get_dual(m, pack["ub"])
            dual_k   = get_dual(m, pack["card"])
            added=False
            for a in range(self.A):
                pat = price_column(a, dual_cov, dual_lb, dual_ub, dual_k,
                                   self.demand, self.supply,
                                   self.LB, self.UB)
                if pat:
                    sel, units,_ = pat
                    m.freeTransform()
                    self._add_column(pack, a, sel, units); added=True
            if not added: break
        self.dual_of_k[k] = m.getDualbound()
        return self._extract(pack)

    def _rank_k(self,klist,bestk):
        if bestk is None: return klist
        return sorted(klist,key=lambda kk:(-self.dual_of_k.get(kk,-1e100),
                                           abs(kk-bestk)))

    def Opt_ExplorarCantidadPasillos(self, tlim):
        t0=time.time(); best=None; bestval=-1
        klist=self.k_order[:]
        while klist and time.time()-t0<tlim:
            k=klist.pop(0)
            sol=self.Opt_cantidadPasillosFija(k,0.25*tlim)
            if sol and sol["obj"]>bestval:
                best,bestval=sol,sol["obj"]
            if best: klist=self._rank_k(klist,len(best["aisles"]))
        self.best_sol = best
        return best

    def _extract(self, pack):
        m=pack["model"]
        if m.getStatus()!="optimal": return None
        ais,ords=set(),set()
        for v in m.getVars():
            if m.getVal(v)>0.5 and v.name.startswith("col_"):
                p=v.name.split("_"); ais.add(int(p[1]))
                ords.update(int(x) for x in p[2:])
        return {"obj":int(m.getObjVal()),"aisles":ais,"orders":ords}

    # RAMIFICAR + PRICER  (PARTE 7) 
    class SimplePricer(Pricer):
        def __init__(self, colgen, pack):
            super().__init__()
            self.colgen = colgen     # objeto Columns
            self.pack   = pack       # RMP del nodo raíz

        def pricerredcost(self):
            col = self.colgen
            m   = self.model  # modelo SCIP interno
            pack = self.pack

            cov_tr = [m.getTransformedCons(pack["cov"][i])
                      for i in range(col.I)]
            dual_cov = [m.getDualsolLinear(c) for c in cov_tr]
            dual_lb  = m.getDualsolLinear(m.getTransformedCons(pack["lb"]))
            dual_ub  = m.getDualsolLinear(m.getTransformedCons(pack["ub"]))
            dual_k   = m.getDualsolLinear(m.getTransformedCons(pack["card"]))

            # intenta generar al menos una columna con RC>0
            anynew=False
            for a in range(col.A):
                pat = price_column(a, dual_cov, dual_lb, dual_ub, dual_k,
                                   col.demand, col.supply,
                                   col.LB, col.UB)
                if pat:
                    sel, units, _ = pat
                    col._add_column(pack, a, sel, units)
                    anynew=True
            return {"result": "success" if anynew else "didnotrun"}

    def branch_and_price(self, warm_time, bnp_time):
        """
        warm_time  : segundos para CG clásico (root «caliente»)
        bnp_time   : segundos para que SCIP ramifique con pricer.
        """
        warm_sol = self.Opt_ExplorarCantidadPasillos(warm_time)

        # nodo raíz = k = |mejores pasillos|
        k0 = len(warm_sol["aisles"]) if warm_sol else (self.A+1)//2
        pack = self._build_rmp(k0); self._active_pack = pack
        m = pack["model"]

        prc = self.SimplePricer(self, pack)
        m.includePricer(prc, "simple", "Wave pricer", priority=0, delay=False)
        m.setParam("limits/time", max(bnp_time,0.1))
        try: m.hideOutput()
        except AttributeError: m.setParam("display/verblevel", 0)
        m.optimize()

        self.best_sol = self._extract(pack)
        self._last_model = m
        return self.best_sol

def solve_instance(fname, tlimit=600):
    col = Columns(fname)
    warm = 0.3*tlimit;  resto = tlimit-warm
    best = col.branch_and_price(warm, resto)

    m = col._last_model
    return (best,
            m.getNConss(), m.getNVars(),
            sum(1 for v in m.getVars() if v.vtype()=="B"),
            m.getDualbound())

if __name__=="__main__":
    if len(sys.argv)<2:
        print("uso: python competencia.py input.txt [segundos]")
        sys.exit(1)
    instance = sys.argv[1]
    tlim = int(sys.argv[2]) if len(sys.argv)>2 else 600

    tic = time.time()
    best,c,v,rmp_v,dual = solve_instance(instance, tlim)
    elapsed = time.time()-tic

    print(f"\nMETRICS inst={os.path.basename(instance)} "
          f"conss={c} vars={v} vars_rmp={rmp_v} "
          f"dual={int(dual)} obj={best['obj'] if best else 'NA'} "
          f"time={elapsed:.1f}s")
