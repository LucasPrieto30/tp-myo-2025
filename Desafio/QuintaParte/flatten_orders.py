import sys, pathlib, re
flat = []
with open("orders.dat") as f:
    for line in f:
        nums = list(map(int, re.findall(r"\d+", line)))
        o, k, pairs = nums[0], nums[1], nums[2:]
        for j in range(0, 2*k, 2):
            i, q = pairs[j], pairs[j+1]
            flat.append(f"{o} {i} {q}\n")

pathlib.Path("orders_flat.dat").write_text("".join(flat))
print("Escribí orders_flat.dat con", len(flat), "triples")