#PARA EJECUTAR CORRER   python solve_Afix.py  input_0001.txt  fixed_aisles.dat
#
#  - input_0001.txt  :  (o, i, a, órdenes, pasillos, LB UB)
#  - fixed_aisles.dat:  índices de los pasillos que SÍ se visitan

from pyscipopt import Model, quicksum
import sys

# 1. datos
# ---------------------------------------------------------------------------
def read_data(fname_input, fname_fixed):
    """
    Devuelve:
        cant_bolsitas, cant_items, cant_pasillos,
        demanda_por_bolsita[b][i],
        items_por_pasillo[a][i],
        pasillos_fijos (set),
        LB, UB
    """
    with open(fname_input, "r") as f:
        o, i, a = map(int, f.readline().split())
        cant_bolsitas, cant_items, cant_pasillos = o, i, a

        # demanda_por_bolsita[b][i] = u_oi
        demanda_por_bolsita = [[0] * cant_items for _ in range(cant_bolsitas)]
        for b in range(cant_bolsitas):
            datos = list(map(int, f.readline().split()))
            k, pares = datos[0], datos[1:]
            for idx in range(0, 2 * k, 2):
                item, qty = pares[idx], pares[idx + 1]
                demanda_por_bolsita[b][item] = qty

        # items_por_pasillo[a][i] = u_ai
        items_por_pasillo = [[0] * cant_items for _ in range(cant_pasillos)]
        for a_id in range(cant_pasillos):
            datos = list(map(int, f.readline().split()))
            l, pares = datos[0], datos[1:]
            for idx in range(0, 2 * l, 2):
                item, qty = pares[idx], pares[idx + 1]
                items_por_pasillo[a_id][item] = qty

        # última línea del input: LB  UB
        LB, UB = map(int, f.readline().split())

    # pasillos fijados
    pasillos_fijos = set(map(int, open(fname_fixed).read().split()))

    return (cant_bolsitas, cant_items, cant_pasillos,
            demanda_por_bolsita, items_por_pasillo,
            pasillos_fijos, LB, UB)

# 2. Modelo
# ---------------------------------------------------------------------------
def solve(cant_bolsitas, cant_items, cant_pasillos,
          demanda_por_bolsita, items_por_pasillo,
          pasillos_fijos, LB, UB):

    model = Model("Parte2_Afix")

    # Variables: y[b] = 1 si la orden b entra en la wave
    y = {b: model.addVar(vtype="B", name=f"y_{b}") for b in range(cant_bolsitas)}

    # Unidades totales en la wave
    total_units = quicksum(demanda_por_bolsita[b][i] * y[b]
                           for b in range(cant_bolsitas)
                           for i in range(cant_items))

    # Rango [LB, UB]
    model.addCons(total_units >= LB, name="LB_wave")
    model.addCons(total_units <= UB, name="UB_wave")

    # Cobertura: solo con los pasillos dados
    for i in range(cant_items):
        capacidad_i = sum(items_por_pasillo[a][i] for a in pasillos_fijos)
        model.addCons(
            quicksum(demanda_por_bolsita[b][i] * y[b]
                     for b in range(cant_bolsitas))
            <= capacidad_i,
            name=f"Cover_item_{i}"
        )

    # Objetivo
    model.setObjective(total_units, "maximize")
    model.optimize()

    # resultados
    status = model.getStatus()
    if status == "optimal":
        sel_bags = [b for b in y if model.getVal(y[b]) > 0.5]
        print(f"Unidades óptimas = {int(model.getObjVal())}")
        print("Órdenes elegidas:", sel_bags)
        print("Pasillos fijos:  ", sorted(pasillos_fijos))
    else:
        print("No se halló óptimo. Estado:", status)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    input_file  = sys.argv[1] if len(sys.argv) > 1 else "input_0001.txt"
    fixed_file  = sys.argv[2] if len(sys.argv) > 2 else "fixed_aisles.dat"

    datos = read_data(input_file, fixed_file)
    solve(*datos)
