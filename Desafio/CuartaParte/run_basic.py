from basic import Basic
import sys, json

infile  = sys.argv[1] if len(sys.argv) > 1 else "input_0001.txt"
umbral  = int(sys.argv[2]) if len(sys.argv) > 2 else 10

basic = Basic(infile)
sol = basic.Opt_ExplorarCantidadPasillos(umbral)
if sol:                                      
    sol["aisles"] = list(sol["aisles"])
    sol["orders"] = list(sol["orders"])
print(json.dumps(sol, indent=2))