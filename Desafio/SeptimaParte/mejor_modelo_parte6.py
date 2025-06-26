
import sys, time, os, json
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

def binary_spread(n):
        """
        Devuelve lista con los enteros 1..n en orden centro-mitades-cuartos.
        """
        res = []
        def rec(lo, hi):
            if lo > hi:
                return
            mid = (lo + hi) // 2
            res.append(mid)
            rec(lo, mid - 1)
            rec(mid + 1, hi)
        rec(1, n)
        return res

def price_column(a, dual_cov, dual_lb, dual_ub, dual_k,
                 demand, supply, LB, UB):
    O = len(demand)
    I = len(supply[0])
    units_o = [sum(demand[o]) for o in range(O)]

    price_o = []
    for o in range(O):
        rc_part  = units_o[o]
        rc_part -= sum(dual_cov[i]*demand[o][i] for i in range(I))
        rc_part -= units_o[o]*dual_lb
        rc_part -= units_o[o]*dual_ub
        # rc_part -= dual_order[o]
        price_o.append(rc_part)

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
        self.rmp_cache = {}
        self.best_sol  = None
        self.dual_of_k = {}
        self.k_order = binary_spread(self.A)  
        
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
    def _rank_k(self, k_list, best_k):
        """Ordena k_list con la heurística ‘marginal gain / slope’."""
        if best_k is None:
            return k_list
        
        def sort_key(kk):
            dual = self.dual_of_k.get(kk, -1e100)
            return (-dual, abs(kk - best_k))
        
        return sorted(k_list, key=sort_key)

    # RMP(k) inicial ------------------------------
    def _build_rmp(self, k):
        m = Model(f"RMP_k{k}")
        try:
            m.hideOutput()
        except AttributeError:
            m.setParam("display/verblevel", 0)
        m.setMaximize()
        zero  = m.addVar(lb=0, ub=0, name="zero")
        expr0 = 0 * zero    
        # order_cons = {
        #     o: m.addCons(expr0 <= 1, f"order_{o}")   # 0*zero <= 1
        #     for o in range(self.O)
        # }
        cov   = {i: m.addCons(expr0 >= 0,            name=f"cov_{i}")
                 for i in range(self.I)}
        lb    = m.addCons(expr0 >= self.LB,          name="LB")
        ub    = m.addCons(expr0 <= self.UB,          name="UB")
        card  = m.addCons(expr0 == k,                name="card_k")

        cols = {}

        # dummy único (factibiliza Σx=k y LB/UB)
        dummy = m.addVar(vtype="B", obj=-1e6, name="dummy")
        add_coef(m, lb,   dummy, self.LB)
        add_coef(m, ub,   dummy, self.LB)
        add_coef(m, card, dummy, 1)
        cols[("dummy", frozenset())] = dummy

        slack = m.addVar(vtype="B", obj=-1e-3, name="slack")
        add_coef(m, lb,  slack, self.LB)
        add_coef(m, ub,  slack, self.LB)
        cols[("slack", frozenset())] = slack

        for a in range(self.A):
            orders, units = self._greedy_pattern(a)
            if not orders:           
                v = m.addVar(vtype="B", obj=0, name=f"col_{a}_0")
                add_coef(m, card, v, 1)
                cols[(a, frozenset())] = v
                continue

            vname = f"col_{a}_" + "_".join(map(str, orders))
            v = m.addVar(vtype="B", obj=units, name=vname)
            for i in range(self.I):
                q = sum(self.demand[o][i] for o in orders)
                if q: add_coef(m, cov[i], v, q)
            add_coef(m, lb,   v, units)
            add_coef(m, ub,   v, units)
            add_coef(m, card, v, 1)
            # for o in orders:
            #     add_coef(m, order_cons[o], v, 1) 
            cols[(a, frozenset(orders))] = v
        # m.writeProblem(f"rmp_k{k}_init.lp")
        return {"model": m, "cols": cols, "cov": cov,
                "lb": lb, "ub": ub, "card": card}

    def _add_column(self, pack, a, orders, units):
        key = (a, frozenset(orders))
        if key in pack["cols"]:
            return
        m = pack["model"]
        v = m.addVar(vtype="B", obj=units,
                     name=f"col_{a}_" + "_".join(map(str, orders)))
        for i in range(self.I):
            q = sum(self.demand[o][i] for o in orders)
            if q: add_coef(m, pack["cov"][i], v, q)
        add_coef(m, pack["lb"],   v, units)
        add_coef(m, pack["ub"],   v, units)
        add_coef(m, pack["card"], v, 1)
        # for o in orders:  
        #     add_coef(m, pack["order_cons"][o], v, 1)
        pack["cols"][key] = v

    #  RMP(k) con column generation --------------------
    def Opt_cantidadPasillosFija(self, k, tlimit):
        if k not in self.rmp_cache:
            self.rmp_cache[k] = self._build_rmp(k)
        pack = self.rmp_cache[k];  m = pack["model"]

        start = time.time(); rounds = 0
        while True:
            rem = max(0.01, tlimit - (time.time() - start))
            m.setParam("limits/time", rem)
            m.optimize()
            if m.getStatus() != "optimal":
                break

            dual_cov = [get_dual(m, pack["cov"][i]) for i in range(self.I)]
            dual_lb  = get_dual(m, pack["lb"])
            dual_ub  = get_dual(m, pack["ub"])
            dual_k   = get_dual(m, pack["card"])
            # dual_order = [get_dual(m, pack["order_cons"][o]) for o in range(self.O)]
            any_new = False
            for a in range(self.A):
                priced = price_column(a, dual_cov, dual_lb, dual_ub, dual_k,
                                      self.demand, self.supply,
                                      self.LB, self.UB)
                if priced:
                    sel, units, _ = priced
                    m.freeTransform() 
                    self._add_column(pack, a, sel, units)
                    any_new = True
            if not any_new:
                break

            rounds += 1
            if (time.time()-start) >= 0.8*tlimit:
                break
        self._last_model = pack["model"]    
        self.dual_of_k[k] = m.getDualbound()    
        return self._extract(pack)

    def Opt_PasillosFijos(self, pasillos, tlimit):
        """
        Reoptimiza el mejor k fijando exactamente los pasillos =1/0.
        `pasillos` es un set de índices que deben quedar en 1.
        """
        k = len(pasillos)
        #crea un RMP nuevo desde cero
        pack = self._build_rmp(k)              
        m    = pack["model"]

        for a in range(self.A):
            var = pack["cols"].get((a, frozenset()))
            if var is None:
                continue
            if a in pasillos:           
                m.chgVarLb(var, 1)
                m.chgVarUb(var, 1)
            else:
                m.chgVarUb(var, 0)
        m.setParam("limits/time", max(tlimit, 0.1))
        m.optimize()
        self._last_model = pack["model"]
        return self._extract(pack)

    def Opt_ExplorarCantidadPasillos(self, tlimit):
        start = time.time()
        best_val = float("-inf"); best_sol = None
        k_list = self.k_order[:]

        while k_list and (time.time()-start) < tlimit:
            k = k_list.pop(0)
            rem = tlimit - (time.time()-start)
            sol = self.Opt_cantidadPasillosFija(k, rem)

            if sol and sol["obj"] > best_val:
                best_val   = sol["obj"]
                best_sol   = sol
            if k_list:
                best_k = len(best_sol["aisles"]) if best_sol else None
                k_list = self._rank_k(k_list, best_k)

        if best_sol:
            rem = tlimit - (time.time()-start)
            rem = max(rem, 0.1)
            best_sol = self.Opt_PasillosFijos(best_sol["aisles"], rem)

        self.best_sol = best_sol
        return best_sol

    def _extract(self, pack):
        m = pack["model"]
        if m.getStatus() != "optimal":
            return None
        ais, ords = set(), set()
        for v in m.getVars():
            if m.getVal(v) > 0.5 and v.name.startswith("col_"):
                p = v.name.split("_")
                ais.add(int(p[1]))
                ords.update(int(x) for x in p[2:])
        return {"obj": int(m.getObjVal()), "aisles": ais, "orders": ords}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    tlimit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    instance = sys.argv[1]

    solver = Columns(instance)
    tic = time.time()
    best = solver.Opt_ExplorarCantidadPasillos(tlimit)
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