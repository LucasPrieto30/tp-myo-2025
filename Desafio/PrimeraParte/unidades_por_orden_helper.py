#!/usr/bin/env python3
from collections import Counter

def main():
    total_por_orden = Counter()
    with open("orders.dat") as f:
        for line in f:
            o, i, u = map(int, line.split())
            total_por_orden[o] += u
    # Muestra las 20 órdenes con más unidades
    for o, u in total_por_orden.most_common(20):
        print(f"orden {o:3d} : {u} unidades")

if __name__ == "__main__":
    main()
