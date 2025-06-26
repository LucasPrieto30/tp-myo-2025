import configparser, subprocess, os, glob, csv, time, re

def parse_metrics(text: str):
    """
    Extrae las métricas de la línea que imprime solver_columns:

      METRICS inst=instance_0007.txt conss=158 vars=119 vars_rmp=46 dual=68 obj=51 time=12.3
    """
    pat = (r"METRICS\s+inst=(\S+)\s+"
           r"conss=(\d+)\s+vars=(\d+)\s+vars_rmp=(\d+)\s+"
           r"dual=(-?\d+)\s+obj=(\d+|NA)\s+time=([0-9.]+)")
    m = re.search(pat, text)
    if not m:
        raise ValueError("No se encontró línea METRICS en la salida")

    inst       = m.group(1)
    nconss     = int(m.group(2))
    nvars      = int(m.group(3))
    nvars_rmp  = int(m.group(4))
    dual_bd    = int(m.group(5))
    obj        = None if m.group(6) == "NA" else int(m.group(6))
    elapsed    = float(m.group(7))
    return obj, nvars, nconss, nvars_rmp, dual_bd, elapsed, inst

cfg = configparser.ConfigParser()
cfg.read("experimento.cfg")

in_path   = cfg["general"]["inPath"]
th        = int(cfg["general"]["threshold"])

for section in [s for s in cfg if s.startswith("model")]:
    solver   = cfg[section]["path"]
    out_path = cfg[section]["outPath"]
    os.makedirs(out_path, exist_ok=True)

    csv_rows = []
    for inst in sorted(glob.glob(os.path.join(in_path, "instance_*.txt")))[:4]:
        t0 = time.time()
        res = subprocess.run(
            ["python", solver, inst, str(th)],
            capture_output=True, text=True
        )
        elapsed = time.time() - t0
        # ―― guarda el .sol ――
        with open(os.path.join(out_path,
                               os.path.basename(inst).replace(".txt",".sol")),
                  "w") as f:
            f.write(res.stdout)

        # ―― extrae métricas de la última línea impresa por el solver ――
        print(res.stdout)
        obj, nvars, nconss, nvars_rmp, dual, elaps, inst = parse_metrics(res.stdout)
        csv_rows.append([os.path.basename(inst), nconss, nvars,
                         nvars_rmp, dual, obj, elapsed])

    with open(os.path.join(out_path, "summary.csv"), "w", newline="") as f:
        csv.writer(f).writerows([["inst","conss","vars",
                                  "vars_rmp","dual","obj","time"]] +
                                csv_rows)
