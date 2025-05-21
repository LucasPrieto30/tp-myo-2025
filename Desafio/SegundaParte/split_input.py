#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#   Genera:
#       head.dat    –  o  i  a
#       orders.dat  –  order   item   units
#       aisles.dat  –  aisle   item   units
#       limits.dat  –  LB  UB  K   (K se pasa como 2º argumento)
# ---------------------------------------------------------------------------
import sys, pathlib, itertools

def main(fname, K):
    with open(fname, "r", encoding="utf-8") as f:
        tokens = list(map(int, f.read().strip().split()))
    pos = 0

    # cabecera
    O, I, A = tokens[pos:pos+3]
    pos += 3

    head   = open("head.dat",   "w")
    orders = open("orders.dat", "w")
    aisles = open("aisles.dat", "w")

    print(O, I, A, file=head)

    # órdenes (bolsitas)
    for o in range(O):
        k = tokens[pos]; pos += 1
        for _ in range(k):
            item = tokens[pos]
            qty  = tokens[pos + 1]
            pos += 2
            print(o, item, qty, file=orders)

    # pasillos (containers)
    for a in range(A):
        l = tokens[pos]; pos += 1
        for _ in range(l):
            item = tokens[pos]
            qty  = tokens[pos + 1]
            pos += 2
            print(a, item, qty, file=aisles)

    # última línea =  LB  UB
    LB, UB = tokens[pos:pos+2]

    with open("limits.dat", "w") as f_lim:
        print(LB, UB, K, file=f_lim)

    for f in (head, orders, aisles):
        f.close()

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Uso:  python split_input_k.py  input_0001.txt  [K]")
        sys.exit(1)
    input_file = sys.argv[1]
    K_value = int(sys.argv[2]) if len(sys.argv) == 3 else 1   # valor por defecto
    main(input_file, K_value)