#!/usr/bin/env python3
import argparse, glob, os, time
from pathlib import Path

# === CAMBIA ESTO si tu solver de la parte 5 tiene otro nombre/clase/método ===
from columns import Columns   # <--- cambia el módulo si es otro archivo

def solve_one(inst_path: str, tlim: float):
    solver = Columns(inst_path)     # <--- cambia la clase si no es Columns
    sol = solver.Opt_ExplorarCantidadPasillos(tlim)  # <--- cambia si tu método difiere
    return sol

def write_out_part5(inst_path: str, sol: dict, out_dir: str):
    """
    Escribe:
      - obj
      - todas las x_j (columnas) como 0/1 (redondeadas a 0/1)
      - (opcional) dumps con info adicional en comentarios
    """
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, Path(inst_path).stem + ".out")
    with open(out_path, "w") as f:
        if sol is None:
            f.write("obj NA\n")
            return

        f.write(f"obj {sol['obj']:.6f}\n")

        # Exportar columnas x_j
        if "columns" in sol:
            for j, col in enumerate(sol["columns"]):
                xval = 1 if col["x"] > 0.5 else 0
                f.write(f"x_{j} {xval}\n")
                # línea informativa (comentario) para humanos:
                f.write(f"# x_{j} = 1  -> {col['name']}  a={col['a']}  orders={col['orders']}  units={col['units']}\n")
        else:
            # Si no devolviste columns, al menos dejá un aviso
            f.write("# WARNING: no 'columns' in solution dict; patch _extract.\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("indir", help="Carpeta con las instancias .txt")
    ap.add_argument("outdir", help="Carpeta donde escribir los .out")
    ap.add_argument("--tlim", type=float, default=300, help="Tiempo límite por instancia (s)")
    args = ap.parse_args()

    insts = sorted(glob.glob(os.path.join(args.indir, "*.txt")))
    print(f"[INFO] Encontradas: {len(insts)} instancias")

    for inst in insts:
        print(f"[Parte5] Resolviendo {inst} ...")
        tic = time.time()
        sol = solve_one(inst, args.tlim)
        toc = time.time()
        print(f"   -> obj={sol['obj']:.6f}  (time={toc-tic:.1f}s)" if sol else "   -> sin solución")
        write_out_part5(inst, sol, args.outdir)

if __name__ == "__main__":
    main()
