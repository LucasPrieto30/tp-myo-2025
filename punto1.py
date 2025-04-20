#!/usr/bin/env python3
# solve_subprob1.py

from pyscipopt import Model, quicksum

def read_data(filename):
    """
    Lee el input con formato:
      línea 1:    o i a
      siguientes o líneas: k (item cantidad)*k   (demanda_por_bolsitaa de cada bolsita)
      siguientes a líneas: l (item cantidad)*l   (oferta de cada contenedor)
      última línea: 2 enteros (ignorados)
    Devuelve: cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor
    - demanda_por_bolsita[b][i] = cantidad del ítem i en bolsita b
    - items_por_contenedor[c][i] = cantidad del ítem i en contenedor c
    """
    with open(filename, 'r') as f:
        o, i, a = map(int, f.readline().split())

        cant_bolsitas, cant_items, cant_contenedores = o, i, a

        # matriz que guarda para cada bolsita b y cada ítem i, cuántas unidades pide
        demanda_por_bolsita = [[0] * cant_items for _ in range(cant_bolsitas)]
        for bolsita in range(cant_bolsitas):
            datos = list(map(int, f.readline().split()))
            k = datos[0]
            pares = datos[1:]
            for idx in range(0, 2*k, 2):
                item, cantidad = pares[idx], pares[idx+1]
                demanda_por_bolsita[bolsita][item] = cantidad

        items_por_contenedor = [[0]*cant_items for _ in range(cant_contenedores)]
        for contenedor in range(cant_contenedores):
            datos = list(map(int, f.readline().split()))
            l = datos[0]
            pares = datos[1:]
            for idx in range(0, 2*l, 2):
                item, cantidad = pares[idx], pares[idx+1]
                items_por_contenedor[contenedor][item] = cantidad
        _ = f.readline()

    return cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor

def solve(cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor):
    model = Model("Punto1")

    # Variables binarias (si se elige el contenedor o la bolsita 1 sino 0)
    x = {c: model.addVar(vtype="B", name=f"x_{c}") for c in range(cant_contenedores)} 
    y = {b: model.addVar(vtype="B", name=f"y_{b}") for b in range(cant_bolsitas)}
    print(y)
    
    # Restricción: exactamente un contenedor
    model.addCons(quicksum(x[c] for c in x) == 1, name="unicoContenedor")

    # Cobertura por ítem
    for item in range(cant_items):
        model.addCons(
            quicksum(y[b] * demanda_por_bolsita[b][item] for b in range(cant_bolsitas))
            <=
            quicksum(x[c] * items_por_contenedor[c][item] for c in range(cant_contenedores)),
            name=f"Cover_item_{item}"
        )
    # Beneficios (cada ítem vale 1)
    bagVal = {b: sum(demanda_por_bolsita[b]) for b in range(cant_bolsitas)} 

    #contVal = {c: sum(items_por_contenedor[c]) for c in range(cant_contenedores)} #cada contenedor vale 1 o vale lo que sumen sus items?
    contVal = { c: 1 for c in range(cant_contenedores) }
    # Objetivo
    model.setObjective(
        quicksum(y[b] * bagVal[b] for b in range(cant_bolsitas))
      + quicksum(x[c] * contVal[c] for c in range(cant_contenedores)),
      "maximize"
    )

    # Resolver
    model.optimize()

    # Resultado
    if model.getStatus() == "optimal":
        print(f"Beneficio óptimo = {model.getObjVal():.0f}")
        sel_cont = [c for c in x if model.getVal(x[c]) > 0.5]
        sel_bags = [b for b in y if model.getVal(y[b]) > 0.5]
        print("Contenedor elegido:", sel_cont[0])
        print("Bolsitas seleccionadas:", sel_bags)
    else:
        print("No se encontró solución óptima. Estado:", model.getStatus())

if __name__ == "__main__":
    input_file = "input_0001.txt"
    cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor = read_data(input_file)
    solve(cant_bolsitas, cant_items, cant_contenedores, demanda_por_bolsita, items_por_contenedor)
