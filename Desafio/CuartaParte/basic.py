from pyscipopt import Model, quicksum
import time, math, sys
from itertools import combinations

def read_base_data(input_txt):
    with open(input_txt) as f:
        O, I, A = map(int, f.readline().split())
        demand = [[0]*I for _ in range(O)]
        for b in range(O):
            k, *pairs = map(int, f.readline().split())
            for idx in range(0, 2*k, 2):
                item, qty = pairs[idx], pairs[idx+1]
                demand[b][item] = qty
        supply = [[0]*I for _ in range(A)]
        for a in range(A):
            l, *pairs = map(int, f.readline().split())
            for idx in range(0, 2*l, 2):
                item, qty = pairs[idx], pairs[idx+1]
                supply[a][item] = qty
        LB, UB = map(int, f.readline().split())
    return O, I, A, demand, supply, LB, UB


class Basic:
    def __init__(self, input_txt):
        self.O, self.I, self.A, self.demand, self.supply, self.LB, self.UB = read_base_data(input_txt)
        self.base_model, self.x, self.y, self.con_K = self._build_master()
        self.best_aisles = set()
        self.best_sol    = None

    # ---------- construcción ------------------------------------------------
    def _build_master(self):
        m = Model("Desafio_full")
        # x_a  (pasillo)    y_o (orden)
        x = {a: m.addVar(vtype="B", name=f"x_{a}") for a in range(self.A)}
        y = {o: m.addVar(vtype="B", name=f"y_{o}") for o in range(self.O)}

        # one container-type constraint: Σ x_a == K  -> RHS cambiará
        con_K = m.addCons(quicksum(x.values()) == 1, name="EqK")  # se cambia RHS
        # cobertura
        for i in range(self.I):
            m.addCons(quicksum(self.demand[o][i]*y[o] for o in y) <=
                      quicksum(self.supply[a][i]*x[a] for a in x))
        # tamaño de wave
        total_units = quicksum(self.demand[o][i]*y[o] for o in y for i in range(self.I))
        m.addCons(total_units >= self.LB, name="LB")
        m.addCons(total_units <= self.UB, name="UB")
        m.setObjective(total_units, "maximize")
        return m, x, y, con_K

    # ---------- auxiliares --------------------------------------------------
    def _model_for_K(self, K):
        """
        Devuelve un modelo con RHS(K) sin crear todo de nuevo si la versión
        de PySCIPOpt lo permite; de lo contrario crea uno nuevo.
        """
        try:                           # SCIP ≥ 7  / PySCIPOpt ≥ 4.3
            clone = self.base_model.copyOrig()
            # recupera el constraint con el mismo nombre
            con_K = clone.getCons("EqK")
            clone.chgRhs(con_K, K)
            return clone
        except AttributeError:
            # fallback → construimos un modelo nuevo
            clone, _, _, con_K = self._build_master()
            clone.chgRhs(con_K, K)
            return clone
    # ------------- extract -------------------------------------------------
    def _extract(self, model):
        if model.getStatus() != "optimal":
            return None
        aisles = {int(v.name.split("_")[1]) for v in model.getVars()
                  if v.name.startswith("x_") and model.getVal(v) > 0.5}
        orders = {int(v.name.split("_")[1]) for v in model.getVars()
                  if v.name.startswith("y_") and model.getVal(v) > 0.5}
        return {"obj": int(model.getObjVal()), "aisles": aisles, "orders": orders}

    # ------------------------------------------------------------------------
    def Opt_cantidadPasillosFija(self, k, umbral):
        model = self._model_for_K(k)
        model.setParam("limits/time", umbral)
        model.optimize()
        return self._extract(model)

    def Opt_PasillosFijos(self, umbral):
        if not self.best_aisles:
            raise RuntimeError("Primero ejecuta Opt_ExplorarCantidadPasillos")

        k = len(self.best_aisles)
        m  = self._model_for_K(k)

        # ---- construir diccionario índice→variable ------------------------
        xvars = {int(v.name.split("_")[1]): v
                 for v in m.getVars() if v.name.startswith("x_")}

        # ---- fijar los pasillos elegidos ----------------------------------
        for a, var in xvars.items():
            if a in self.best_aisles:
                m.chgVarLb(var, 1.0)
                m.chgVarUb(var, 1.0)
            else:
                m.chgVarUb(var, 0.0)

        m.setParam("limits/time", umbral)
        m.optimize()
        sol = self._extract(m)
        if sol:
            self.best_sol = sol
        return sol
    
    def Opt_ExplorarCantidadPasillos(self, umbral):
        start = time.time()
        remaining = lambda: umbral - (time.time() - start)

        # priming loop: k = 1 .. A   (parar si no queda tiempo)
        best_val = -1
        for k in range(1, self.A+1):
            if remaining() <= 0: break
            sol = self.Opt_cantidadPasillosFija(k, remaining())
            if sol and sol["obj"] > best_val:
                best_val, self.best_aisles, self.best_sol = sol["obj"], sol["aisles"], sol

        # exploitation: fija esos pasillos y optimiza otra vez
        if remaining() > 0:
            self.Opt_PasillosFijos(remaining())

        return self.best_sol

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso:  python basic.py  input_0001.txt")
        sys.exit(1)

    basic = Basic(sys.argv[1])

    print(">>> Opt_ExplorarCantidadPasillos  (umbral = 10 s)")
    best = basic.Opt_ExplorarCantidadPasillos(10)
    print(best)

    print("\n>>> Opt_cantidadPasillosFija(k=3, umbral=5 s)")
    print(basic.Opt_cantidadPasillosFija(3, 5))

    print("\n>>> Opt_PasillosFijos(umbral=5 s)  sobre la mejor selección previa")
    print(basic.Opt_PasillosFijos(5))