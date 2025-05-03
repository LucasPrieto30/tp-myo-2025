#!/usr/bin/env python3
# solve_subprob2.py
#
# Punto 2: elegir cualquier subconjunto de contenedores y de bolsitas
# de modo que la oferta total cubra la demanda_por_bolsita total y se maximice:
#   sum_{c in A'} -10 (por ejemplo)           (cada contenedor vale -10)
# + sum_{b in O'} sum_i demanda_por_bolsita[b][i]  (cada ítem en la bolsita vale 1)

from pyscipopt import Model, quicksum

def read_data(filename):
    """Lee input.txt con el formato descrito y devuelve
       cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor."""
    with open(filename, 'r') as f:
        o, i, a = map(int, f.readline().split())
        cant_bolsitas, cant_items, cant_contenedores = o, i, a

        # demanda_por_bolsitaa[b][i] = cantidad del ítem i que pide la bolsita b
        demanda_por_bolsita = [[0]*cant_items for _ in range(cant_bolsitas)]
        for bolsita in range(cant_bolsitas):
            datos = list(map(int, f.readline().split()))
            k = datos[0]
            pares = datos[1:]
            for idx in range(0, 2*k, 2):
                item, cantidad = pares[idx], pares[idx+1]
                demanda_por_bolsita[bolsita][item] = cantidad

        # items_por_contenedor[c][i] = cantidad del ítem i que aporta el contenedor c
        items_por_contenedor = [[0]*cant_items for _ in range(cant_contenedores)]
        for c in range(cant_contenedores):
            datos = list(map(int, f.readline().split()))
            l, pares = datos[0], datos[1:]
            for idx in range(l):
                itm, cantidad = pares[2*idx], pares[2*idx+1]
                items_por_contenedor[c][itm] = cantidad

        # Ignorar los dos enteros finales (LB, UB)
        f.readline()

    return cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor

def solve_point2(cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor):
    """Construye y resuelve el modelo del Punto 2 con PySCIPOpt."""
    model = Model("Subprob2_Many_Containers")

    # Variables binarias
    x = {c: model.addVar(vtype="B", name=f"x[{c}]") for c in range(cant_contenedores)}
    y = {b: model.addVar(vtype="B", name=f"y[{b}]") for b in range(cant_bolsitas)}

    # Restricciones de cobertura para cada ítem i
    for itm in range(cant_items):
        model.addCons(
            quicksum(y[b]*demanda_por_bolsita[b][itm] for b in range(cant_bolsitas))
            <=
            quicksum(x[c]*items_por_contenedor[c][itm] for c in range(cant_contenedores)),
            name=f"Cover_item_{itm}"
        )

    #Beneficios
    bagVal  = {b: sum(demanda_por_bolsita[b])   for b in range(cant_bolsitas)}    # suma de ítems en bolsa b
    contVal = {c: -10                 for c in range(cant_contenedores)} 

    # Función objetivo
    model.setObjective(
        quicksum(y[b]*bagVal[b] for b in range(cant_bolsitas))
      + quicksum(x[c]*contVal[c] for c in range(cant_contenedores)),
      "maximize"
    )

    # Resolver
    model.optimize()

    status = model.getStatus()
    print("Estado:", status)
    if status == "optimal":
        print("Beneficio óptimo:", model.getObjVal())
        conts = [c for c in x if model.getVal(x[c]) > 0.5]
        bags  = [b for b in y if model.getVal(y[b]) > 0.5]
        print("Contenedores elegidos:", conts)
        print("Bolsitas elegidas:   ", bags)
    else:
        print("No se encontró solución óptima.")

if __name__ == "__main__":
    fn = "input_0001.txt"
    cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor = read_data(fn)
    solve_point2(cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor)
