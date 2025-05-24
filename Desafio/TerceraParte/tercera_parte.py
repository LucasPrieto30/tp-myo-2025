
from pyscipopt import Model, quicksum
from itertools import combinations
import sys, collections

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
        print(LB)
    return O, I, A, demand, supply, LB, UB

def cabe_todas(ordenes, pasillo, demand, supply, I):
    """True si el pasillo cubre la suma de demandas del subconjunto."""
    for i in range(I):
        if sum(demand[o][i] for o in ordenes) > supply[pasillo][i]:
            return False
    return True

def unidades(ordenes, demand):
    return sum(sum(demand[o]) for o in ordenes)

class ColumnGenerationMaster:
    def __init__(self, O, I, demand, pasillos_fijos, LB, UB):
        self.O, self.I   = O, I
        self.demand      = demand
        self.Afix        = pasillos_fijos
        self.LB, self.UB = LB, UB

        self.model = Model("RMP")
        # ------------------------------------------------------------------
        # variable "zero" con dominio [0,0] para generar LinExpr 0*zero
        zero = self.model.addVar(lb=0.0, ub=0.0, name="zero")

        slack = self.model.addVar(lb=0.0, name="slack_dummy")

        self.order_cons = {o: self.model.addCons(slack <= 1, f"order_{o}") for o in range(O)}
        self.aisle_cons = {a: self.model.addCons(slack <= 1, f"aisle_{a}") for a in pasillos_fijos}

        self.size_lb = self.model.addCons(zero * 0 >= LB, "LB")
        self.size_ub = self.model.addCons(zero * 0 <= UB, "UB")

        # tablas de patrones y variables
        self.patterns = {}
        self.x_vars   = {}

    # -----------------------------------------------------------------------
    def add_pattern(self, patt):
        """
        patt debe contener:
            id, ordenes, aisle, unidades
        y, opcionalmente,  obj  (coeficiente en la función objetivo).
        """
        pid = patt['id']
        if pid in self.x_vars:
            return

        # --- coeficiente objetivo ------------------------------------------------
        obj_coeff = patt.get('obj', patt['unidades'])

        # --- crea la variable ----------------------------------------------------
        var = self.model.addVar(vtype="B",
                                obj=obj_coeff,        
                                name=f"x_{pid}")

        self.x_vars[pid]   = var
        self.patterns[pid] = patt

        # --- coeficientes en restricciones de órdenes ---------------------------
        for o in patt['ordenes']:
            self.model.addCoefLinear(self.order_cons[o], var, 1.0)

        # --- coeficiente en restricción del pasillo -----------------------------
        a = patt['aisle']
        if a is not None and a in self.aisle_cons:
            self.model.addCoefLinear(self.aisle_cons[a], var, 1.0)

        # --- filas de tamaño de wave --------------------------------------------
        self.model.addCoefLinear(self.size_lb, var, patt['unidades'])
        self.model.addCoefLinear(self.size_ub, var, patt['unidades'])


def column_generation(input_txt, fixed_file):
    O,I,A,demand,supply,LB,UB = read_base_data(input_txt)
    pasillos_fijos = set(map(int, open(fixed_file).read().split()))

    cg = ColumnGenerationMaster(O,I,demand,pasillos_fijos,LB,UB)

    pid = 1
    for a in pasillos_fijos:
        for o in range(O):
            if cabe_todas([o], a, demand, supply, I):
                cg.add_pattern({'id': f"p{pid}",
                                'ordenes': {o},
                                'aisle':   a,
                                'unidades': unidades([o], demand)})
                pid += 1
                break

    cg.add_pattern({
        'id'      : 'dummy',
        'ordenes' : set(),
        'aisle'   : None,
        'unidades': 0,        # no aporta unidades → no afecta LB/UB
        'obj'     : -1e6      # penalización en el objetivo
    })

    
    MAX_R = 3        
    EPS   = 1e-6
    iteracion = 0

    while True:
        iteracion += 1
        cg.model.optimize()

        if cg.model.getStatus() != "optimal":
            print("RMP no óptimo:", cg.model.getStatus()); break

        dual_order = {o: cg.model.getDualsolLinear(cg.order_cons[o])
                      for o in cg.order_cons}
        dual_aisle = {a: cg.model.getDualsolLinear(cg.aisle_cons[a])
                      for a in cg.aisle_cons}
        dlb = cg.model.getDualsolLinear(cg.size_lb)
        dub = cg.model.getDualsolLinear(cg.size_ub)

        nuevas = 0

        for a in pasillos_fijos:
            mejor_delta = -1e20
            mejor_subset = None

            candidatos = [o for o in range(O)
                          if cabe_todas([o], a, demand, supply, I)]

            for r in range(1, min(MAX_R, len(candidatos))+1):
                for subset in combinations(candidatos, r):
                    if not cabe_todas(subset, a, demand, supply, I):
                        continue
                    U = unidades(subset, demand)
                    rc = U - sum(dual_order[o] for o in subset) - dual_aisle.get(a,0)
                    rc -= U * (dlb - dub)
                    if rc > mejor_delta + EPS:
                        mejor_delta = rc
                        mejor_subset = subset

            if mejor_delta > EPS:
                pid += 1
                cg.add_pattern({'id': f"p{pid}",
                                'ordenes': set(mejor_subset),
                                'aisle':   a,
                                'unidades': unidades(mejor_subset, demand)})
                nuevas += 1

        if nuevas == 0:
            break   # optimal
        # loop continúa: RMP se reoptimizará con las nuevas columnas

    # -------- resultado final ---------------------------------------------
    print("\n===  ÓPTIMO  =======================================")
    print("Unidades =", int(cg.model.getObjVal()))
    elegidas = [pid for pid,var in cg.x_vars.items()
                if cg.model.getVal(var) > 0.5 and pid != 'dummy']
    ordenes = sorted({o for pid in elegidas for o in cg.patterns[pid]['ordenes']})
    print("Órdenes  :", ordenes)
    print("Patrones :", elegidas)
    print("Pasillos :", sorted(pasillos_fijos))

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    in_file  = sys.argv[1] if len(sys.argv) > 1 else "input_0001.txt"
    ais_file = sys.argv[2] if len(sys.argv) > 2 else "fixed_aisles.dat"
    column_generation(in_file, ais_file)
