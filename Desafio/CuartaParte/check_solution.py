#!/usr/bin/env python3
import sys, json, collections

def read_instance(txtfile):
    with open(txtfile) as f:
        O, I, A = map(int, f.readline().split())
        demand  = [[0]*I for _ in range(O)]
        for b in range(O):
            k, *pairs = map(int, f.readline().split())
            for idx in range(0, 2*k, 2):
                i, q = pairs[idx], pairs[idx+1]
                demand[b][i] = q
        supply  = [[0]*I for _ in range(A)]
        for a in range(A):
            l, *pairs = map(int, f.readline().split())
            for idx in range(0, 2*l, 2):
                i, q = pairs[idx], pairs[idx+1]
                supply[a][i] = q
        LB, UB = map(int, f.readline().split())
    return demand, supply, LB, UB

def check(solution, demand, supply, LB, UB):
    O_sel = set(solution["orders"])
    A_sel = set(solution["aisles"])

    # 1) total unidades
    total = sum(sum(demand[o]) for o in O_sel)
    if not LB <= total <= UB:
        return False, f"unidades {total} fuera de [{LB},{UB}]"

    # 2) cobertura
    I = len(supply[0])
    for i in range(I):
        dem_i = sum(demand[o][i] for o in O_sel)
        sup_i = sum(supply[a][i] for a in A_sel)
        if dem_i > sup_i:
            return False, f"ítem {i}: demanda {dem_i} > oferta {sup_i}"
    return True, f"OK ( {total} unidades, UB = {UB} )"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("uso: python check_wave.py input_0001.txt resultado.json")
        sys.exit(1)

    demand, supply, LB, UB = read_instance(sys.argv[1])
    solution = json.load(open(sys.argv[2]))
    ok, msg = check(solution, demand, supply, LB, UB)
    print(msg if ok else "❌", msg)
