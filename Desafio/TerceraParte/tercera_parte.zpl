
# data
param Osize  := read "head.dat" as "1n" skip 0 use 1;
param Isize := read "head.dat" as "2n" skip 0 use 1;
param Asize := read "head.dat" as "3n" skip 0 use 1;

set O := {0 ..  Osize-1};
set I := {0 ..  Isize-1};
set A := {0 ..  Asize-1};

param u_oi[O*I] := read "orders.dat"  as "<1n> 2n,3n"  default 0 ;

param u_ai[A*I] := read "aisles.dat" as "<1n> 2n,3n"  default 0 ;

param LB :=  read "limits.dat" as "1n" skip 0 use 1;
param UB :=  read "limits.dat" as "2n" skip 0 use 1;

set P := {read "aisle.dat" as "<1n>"};

param v_op[P*O] := read "patrones.dat" as "<1n>,2n,3n" default 0 ; # 1 si el patrón p contiene la orden o
param a_p[P]    := read "aisle.dat"    as "<1n>,2n"; # pasillo asociado al patrón
param U_p[P]    := read "units.dat"    as "<1n>,2n"; # unidades del patrón p

set Afix := { read "fixed_aisles.dat" as "<n+>" };

#   Variables

var x[P] binary;                     # 1 ↔ patrón elegido

#  Objective

maximize total_units: sum <p> in P: U_p[p]*x[p];

#   Restricciones
subto at_most_one_order:
      forall <o> in O:
            sum <p> in P: v_op[p,o]*x[p] <= 1;

subto aisle_once:
      forall <a> in Afix:
            sum <p> in P with a_p[p] == a: x[p] <= 1;
            
subto wave_size_LB:
      sum <p> in P: U_p[p]*x[p] >= LB;
      
subto wave_size_UB:
      sum <p> in P: U_p[p]*x[p] <= UB;
