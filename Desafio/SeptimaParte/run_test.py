import configparser, subprocess, os, glob, csv, time, re, math

def parse_metrics(text: str):
    pat = (r"METRICS\s+inst=(\S+)\s+"
        r"conss=(\d+)\s+vars=(\d+)\s+vars_rmp=(\d+)\s+"
        r"obj=([0-9]+(?:\.[0-9]+)?|NA)\s+time=([0-9]+(?:\.[0-9]+)?|NA)")
    m = re.search(pat, text)
    if not m:
        raise ValueError("No se encontró línea METRICS en la salida")

    inst       = m.group(1)
    nconss     = int(m.group(2))
    nvars      = int(m.group(3))
    nvars_rmp  = int(m.group(4))
    obj        = None if m.group(5) == "NA" else float(m.group(5))
    elapsed    = float(m.group(6))
    return obj, nvars, nconss, nvars_rmp, elapsed, inst

cfg = configparser.ConfigParser()
cfg.read("experimento.cfg")

in_path   = cfg["general"]["inPath"]
total_budget = float(cfg["general"]["threshold"]) # tiempo TOTAL por modelo 

for section in [s for s in cfg if s.startswith("model")]:
    solver   = cfg[section]["path"]
    out_path = cfg[section]["outPath"]
    os.makedirs(out_path, exist_ok=True)

    csv_rows = []
    inst_files = sorted(glob.glob(os.path.join(in_path, "*instance_*.txt")))[:4]

    model_start = time.time()

    for idx, inst in enumerate(inst_files):
        elapsed_global = time.time() - model_start
        remaining = total_budget - elapsed_global
        if remaining <= 0:
            print(f"*** Sin presupuesto restante para {solver}. "
                  f"Se omiten instancias restantes.")
            break

        
        inst_budget = max(1.0, remaining)

        print(f"\n>>> {os.path.basename(solver)} "
              f"inst={os.path.basename(inst)} "
              f"tlim={inst_budget:.1f}s (quedan {remaining:.1f}s)")

        t0 = time.time()
        inst_budget_int = max(1, math.ceil(remaining))

        res = subprocess.run(
            ["python", solver, inst, str(inst_budget_int)],
            capture_output=True, text=True
        )
        elapsed = time.time() - t0

        with open(os.path.join(
                  out_path,
                  os.path.basename(inst).replace(".txt",".sol")), "w") as f:
            f.write(res.stdout)

        try:
            print(res.stdout)
            obj, nvars, nconss, nvars_rmp, elaps_line, inst_name = parse_metrics(res.stdout)
        except ValueError as e:
            obj = nvars = nconss = nvars_rmp = dual = "NA"
            inst_name = os.path.basename(inst)
            print("   [WARN]", e)

        csv_rows.append([inst_name, nconss, nvars,
                         nvars_rmp, obj, f"{elapsed:.1f}"])

    with open(os.path.join(out_path, "summary.csv"), "w", newline="") as f:
        csv.writer(f).writerows(
            [["inst","conss","vars","vars_rmp","obj","time"]] + csv_rows
        )