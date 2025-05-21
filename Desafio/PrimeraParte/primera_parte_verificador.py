from collections import defaultdict

def load_data():
    # head.dat  ->  O  I  A
    with open("head.dat") as f:
        O, I, A = map(int, f.read().split())

    # orders.dat  ->  o  i  u_oi
    u_oi = defaultdict(int)
    with open("orders.dat") as f:
        for line in f:
            o, i, u = map(int, line.split())
            u_oi[(o, i)] += u

    # aisles.dat  ->  a  i  u_ai
    u_ai = defaultdict(int)
    with open("aisles.dat") as f:
        for line in f:
            a, i, u = map(int, line.split())
            u_ai[(a, i)] += u

    # limits.dat  ->  LB  UB  K
    LB, UB, K = map(int, open("limits.dat").read().split())

    return O, I, A, u_oi, u_ai, LB, UB, K

def check(O_sel, A_sel):
    """
    O_sel = conjunto (set) de órdenes elegidas
    A_sel = conjunto (set) de pasillos elegidos
    Devuelve ("OK") si la selección es factible, o (False,mensaje).
    """
    O, I, A, u_oi, u_ai, LB, UB, K = load_data()

    # 1. tamaño de la wave
    total_units = sum(u_oi[(o, i)] for o in O_sel for i in range(I))
    if total_units < LB or total_units > UB:
        return False, f"Unidades {total_units} fuera de [{LB},{UB}]"

    # 2. número de pasillos
    if len(A_sel) != K:
        return False, f"Nº pasillos = {len(A_sel)} distinto de K = {K}"

    # 3. cobertura de cada ítem
    for i in range(I):
        need = sum(u_oi[(o, i)] for o in O_sel)
        have = sum(u_ai[(a, i)] for a in A_sel)
        if have < need:
            return False, f"Ítem {i}: {have} < {need} (no cubierto)"

    return True, "OK"

# -------------------------------------------------------------------
if __name__ == "__main__":
    # ejemplo tonto: wave vacía y primer K pasillos
    ok, msg = check(O_sel=set(), A_sel=set(range(5)))
    print(msg)
