#!/usr/bin/env python3
"""
make_patterns.py  –  genera los .dat de patrones para la parte 3 estática

Lee:
    input_0001.txt        (formato original)
    fixed_aisles.dat      (una línea con los pasillos fijados)

Crea:
    patrones.dat   –   id  orden  1
    aisle.dat      –   id  pasillo
    units.dat      –   id  unidades

Cada patrón  =  subconjunto de ≤ MAX_R órdenes que CABEN por inventario
                en el pasillo fijado, hasta MAX_PAT_PER_AISLE patrones
                distintos por cada pasillo.

Ajusta los parámetros al comienzo según tu caso.
"""
from itertools import combinations
import sys, pathlib

# ---------------------------  Parámetros tunables  --------------------------
MAX_R              = 3     # nº máx. de órdenes por patrón
MAX_PAT_PER_AISLE  = 15     # para limitar la salida (evitar explosión)
MAX_UNITS          = None     # p. ej. 68, o None para no limitar

INPUT_FILE        = "input_0001.txt"
FIXED_AISLES_FILE = "fixed_aisles.dat"

# ---------------------------------------------------------------------------

def load_base():
    with open(INPUT_FILE) as f:
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

        # última línea = LB  UB (no las usamos aquí)
    aisles_fix = list(map(int, open(FIXED_AISLES_FILE).read().split()))
    return O, I, demand, supply, aisles_fix

def cabe_todas(ordenes, pasillo, demand, supply, I):
    """True si el pasillo tiene unidades suficientes para TODAS las órdenes."""
    for i in range(I):
        need = sum(demand[o][i] for o in ordenes)
        if need > supply[pasillo][i]:
            return False
    return True

def unidades(ordenes, demand):
    return sum(sum(demand[o]) for o in ordenes)

def main():
    O, I, demand, supply, aisles_fix = load_base()

    pat_id = 1
    pat_lines, aisle_lines, unit_lines = [], [], []

    for a in aisles_fix:
        patrones_generados = 0

        # lista de órdenes que caben individualmente en el pasillo
        candidatas = [o for o in range(O) if cabe_todas([o], a, demand, supply, I)]

        # prueba todos los tamaños 1..MAX_R (orden lexicográfica)
        for r in range(1, MAX_R+1):
            if patrones_generados >= MAX_PAT_PER_AISLE:
                break
            for subset in combinations(candidatas, r):
                if patrones_generados >= MAX_PAT_PER_AISLE:
                    break
                if not cabe_todas(subset, a, demand, supply, I):
                    continue

                U = unidades(subset, demand)
                if MAX_UNITS is not None and U > MAX_UNITS:
                    continue  # patrón demasiado grande para el rango UB opcional

                pid_str = str(pat_id)
                for o in subset:
                    pat_lines.append(f"{pid_str} {o} 1\n")
                aisle_lines.append(f"{pid_str} {a}\n")
                unit_lines.append(f"{pid_str} {U}\n")

                pat_id += 1
                patrones_generados += 1

    # ESCRIBIR los archivos .dat ------------------------------------------------
    with open("patrones.dat", "w") as f:
        f.writelines(pat_lines)
    with open("aisle.dat", "w") as f:
        f.writelines(aisle_lines)
    with open("units.dat", "w") as f:
        f.writelines(unit_lines)

    print(f"Total patrones generados: {pat_id-1}")

if __name__ == "__main__":
    main()
