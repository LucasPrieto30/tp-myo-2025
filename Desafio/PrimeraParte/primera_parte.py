#!/usr/bin/env python3
# --------  DESAFÍO(|A†|)  -------------------------------

#PARA EJECUTAR CORRER python .\primera_parte.py .\input_0001.txt 5 (O cualquier valor k)
from pyscipopt import Model, quicksum
import sys

# --------------------------------------------------------------------
# 1. Lectura del input
# --------------------------------------------------------------------
def read_data(fname):
    with open(fname, "r") as f:
        o, i, a = map(int, f.readline().split())
        O, I, A = o, i, a

        demand = [[0]*I for _ in range(O)]        # u_oi
        for b in range(O):
            line = list(map(int, f.readline().split()))
            k, pairs = line[0], line[1:]
            for idx in range(0, 2*k, 2):
                item, qty = pairs[idx], pairs[idx+1]
                demand[b][item] = qty

        supply = [[0]*I for _ in range(A)]        # u_ai
        for a_id in range(A):
            line = list(map(int, f.readline().split()))
            l, pairs = line[0], line[1:]
            for idx in range(0, 2*l, 2):
                item, qty = pairs[idx], pairs[idx+1]
                supply[a_id][item] = qty

        # última línea:  LB  UB
        LB, UB = map(int, f.readline().split())

    return O, I, A, demand, supply, LB, UB

# --------------------------------------------------------------------
# 2. Solución
# --------------------------------------------------------------------
def solve(O, I, A, demand, supply, LB, UB, K):
    m = Model("Desafio_K")

    # Variables
    y = {b: m.addVar(vtype="B", name=f"y_{b}") for b in range(O)}  # órdenes
    x = {a: m.addVar(vtype="B", name=f"x_{a}") for a in range(A)}  # pasillos

    # Copias totales en las órdenes elegidas
    total_units = quicksum( demand[b][i] * y[b]
                            for b in range(O)
                            for i in range(I) )

    # Límites
    m.addCons(total_units >= LB, name="LB_wave")
    m.addCons(total_units <= UB, name="UB_wave")

    # Cobertura por ítem
    for i in range(I):
        m.addCons(
            quicksum( supply[a][i] * x[a] for a in range(A) ) >=
            quicksum( demand[b][i]  * y[b] for b in range(O) ),
            name=f"cover_item_{i}"
        )

    # 2.3. Exactamente K pasillos
    m.addCons( quicksum(x[a] for a in range(A)) == K , name="K_aisles")

    # Objetivo
    m.setObjective(total_units, sense="maximize")

    # Resolver
    m.optimize()

    # Reporte
    status = m.getStatus()
    if status == "optimal":
        sel_orders   = [b for b in y if m.getVal(y[b]) > 0.5]
        sel_aisles   = [a for a in x if m.getVal(x[a]) > 0.5]
        print(f"Óptimo = {m.getObjVal():.0f} unidades")
        print(f"Aisles elegidos ({len(sel_aisles)}): {sel_aisles}")
        print(f"Órdenes elegidas ({len(sel_orders)}): {sel_orders}")
    else:
        print("Estado:", status)

# --------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) not in (2,3):
        print("uso: python split_input.py  input_0001.txt  [K]")
        sys.exit(1)

    in_file = sys.argv[1]
    K_val   = int(sys.argv[2]) if len(sys.argv)==3 else 1   # valor por defecto

    O,I,A,demand,supply,LB,UB = read_data(in_file)
    if not (1 <= K_val <= A):
        print(f"K debe estar entre 1 y {A}.  Valor recibido: {K_val}")
        sys.exit(1)

    solve(O,I,A,demand,supply,LB,UB,K_val)
