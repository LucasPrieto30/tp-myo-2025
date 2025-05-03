#   Genera:
#       head.dat   –  o  i  a
#       bags.dat   –  bolsa   item   cantidad
#       conts.dat  –  cont    item   cantidad
import sys, pathlib

def main(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        tokens = list(map(int, f.read().strip().split()))
    pos = 0
    O, I, A = tokens[pos:pos+3]
    pos += 3

    out_head  = open('head.dat',  'w')
    out_bags  = open('bags.dat',  'w')
    out_conts = open('conts.dat', 'w')

    print(O, I, A, file=out_head)

    # Bolsitas
    for bag in range(O):
        k = tokens[pos]; pos += 1
        for _ in range(k):
            item = tokens[pos]; qty = tokens[pos+1]
            pos += 2
            print(bag, item, qty, file=out_bags)

    # Containers
    for cont in range(A):
        l = tokens[pos]; pos += 1
        for _ in range(l):
            item = tokens[pos]; qty = tokens[pos+1]
            pos += 2
            print(cont, item, qty, file=out_conts)

    # Si hubiera mas datos (como LB UB) se podrian guardar leyendo tokens[pos]..

    for f in (out_head, out_bags, out_conts):
        f.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('pasar el txt como parametro')
        sys.exit(1)
    main(sys.argv[1])
