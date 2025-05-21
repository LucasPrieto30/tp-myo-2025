
# 1. Datos
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
param K  :=  read "limits.dat" as "3n" skip 0 use 1;   # |A†| fijado

# 3.  Variables

var x[O] binary;     # 1 si se selecciona la ordenes  o
var y[A] binary;     # 1 si se selecciona el pasillo  a

# 4.  Objetivo

maximize total_units: sum <o,i> in O*I: u_oi[o,i] * x[o];  # max ordenes seleccionadas

# 5.  Restricciones

subto wave_lower:   sum <o,i> in O*I: u_oi[o,i] * x[o] >= LB;
subto wave_upper:   sum <o,i> in O*I: u_oi[o,i] * x[o] <= UB;

subto coverage:
      forall <i> in I:
            sum <a> in A: u_ai[a,i] * y[a] >=
            sum <o> in O: u_oi[o,i] * x[o];

subto aisle_limit:  sum <a> in A: y[a] == K;