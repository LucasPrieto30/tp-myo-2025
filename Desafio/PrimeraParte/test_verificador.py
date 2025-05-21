from primera_parte_verificador import check

feasible_orders  = {2, 6, 11, 19, 23, 24, 26, 29, 37, 38, 39, 41, 42, 46, 55, 57, 60}  # ordenes
feasible_aisles  = {25, 43, 64, 71 ,97}	      # pasillos   (|A_sel| = 5)

print(check(feasible_orders, feasible_aisles))

O_sel = {2, 6, 11, 19, 23, 24, 26, 29, 37, 38, 39, 41, 42, 46, 55, 57, 60}  
A_sel = {11, 23, 64}    # solo 3 pasillos  (K = 5)

print(check(O_sel, A_sel))


O_sel = {2, 39}    
A_sel = {25, 43, 64, 71 ,97}	

print(check(O_sel, A_sel))