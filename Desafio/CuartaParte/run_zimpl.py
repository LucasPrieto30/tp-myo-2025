#!/usr/bin/env python3
"""
Explora varios K, guarda la mejor ola y reoptimiza con pasillos fijos.
Uso: python run_zimpl.py  limite_total_seg
Requiere que el ejecutable `zimpl` y `scip` estén en el PATH.
"""
import pathlib
pathlib.Path("bounds.dat").touch() 
import subprocess, time, json, os, re, sys

TOTAL = int(sys.argv[1]) if len(sys.argv) > 1 else 30   # seg

import tempfile, os, subprocess, re

# -------------------------------------------------------------------------
def solve_one_K(K, tlim):
    # ---------- 1) escribir K.dat ----------
    open("K.dat", "w").write(f"{K}\n")

    # ---------- 2) compilar modelo ----------
    subprocess.run(["zimpl", "desafio4.zpl"],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL,
                   check=True)

    # ---------- 3) archivo temporal para la SOLUCIÓN ----------
    solfile = tempfile.NamedTemporaryFile(delete=False).name

    # ---------- 4) ejecutar SCIP ----------
    cmd = [
        "scip", "-q",
        "-c",
        f"read desafio4.lp "
        f"set limits time {tlim} "
        f"optimize "
        f"write solution {solfile} "
        f"quit"
    ]
    try:
        subprocess.run(cmd,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       timeout=tlim + 1, check=True)
    except subprocess.TimeoutExpired:
        os.unlink(solfile)
        return {}

    # ---------- 5) parsear el .sol ----------
    obj, ais, ords = None, set(), set()
    with open(solfile) as f:
        for line in f:
            if "objective value" in line:
                obj = int(float(line.split()[-1]))
            elif line.startswith("x#"):
                ais.add(int(line.split("#")[1].split()[0]))
            elif line.startswith("y#"):
                ords.add(int(line.split("#")[1].split()[0]))
    os.unlink(solfile)

    if obj is None:
        return {}
    return {"obj": obj, "aisles": ais, "orders": ords}

def main():
    best = {"obj":-1}
    start = time.time()
    A = int(open("head.dat").read().split()[2])

    for K in range(1, A+1):
        rem = TOTAL - (time.time() - start)
        if rem <= 0: break
        print(f"K={K}  (tiempo restante {rem:.1f}s)")
        sol = solve_one_K(K, rem)
        print("  ↳ devuelto:", sol) 
        if sol and sol["obj"] > best["obj"]:
            best = sol

    # ---- reoptimizar con pasillos fijos ----
    if best["obj"] >= 0:
        print("\nMejor K provisional:", len(best["aisles"]), "obj:", best["obj"])
        # fijar bounds: crear un archivo con varbounds
        with open("bounds.dat", "w") as f:
            for a in range(A):
                if a in best["aisles"]:
                    f.write(f"{a} 1 1\n")   # lb=1, ub=1
                else:
                    f.write(f"{a} 0 0\n")   # lb=ub=0
        # rehacer modelo con bounds.dat incluida
        subprocess.run(["zimpl", "desafio4.zpl", "bounds.dat"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        # optimizar sin límite extra de K
        cmd = ["scip", "-q",
       "-c", "read desafio4.lp optimize display solution quit"]
        out = subprocess.check_output(cmd, text=True)
        print(out) 
        print("\n== JSON resultado ==")
        best["aisles"] = list(best["aisles"])
        best["orders"] = list(best["orders"])
        print(json.dumps(best, indent=2))

if __name__ == "__main__":
    main()
