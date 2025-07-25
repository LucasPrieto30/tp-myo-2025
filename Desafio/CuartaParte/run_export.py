import os


def read_sizes(inst_path):
    with open(inst_path) as f:
        O, I, A = map(int, f.readline().split())
    return O, A

def write_out_part4(inst_path, sol, out_path):
    """
    sol = {"obj": float, "aisles": set[int], "orders": set[int]}
    """
    O, A = read_sizes(inst_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(f"obj {sol['obj']:.6f}\n")
        # x_a
        for a in range(A):
            val = 1 if a in sol["aisles"] else 0
            f.write(f"x_{a} {val}\n")
        # y_o
        for o in range(O):
            val = 1 if o in sol["orders"] else 0
            f.write(f"y_{o} {val}\n")
    print(f"[OK] escrito {out_path}")

sol = {'obj': 3.5, 'aisles': {2, 23}, 'orders': {10}}

inst = "instance_0004.txt"
out  = "Parte4/OUTPUT/A_instance_0004.out"
write_out_part4(inst, sol, out)