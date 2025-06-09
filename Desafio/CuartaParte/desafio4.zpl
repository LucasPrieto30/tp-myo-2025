param Osize  := read "head.dat" as "1n" skip 0 use 1;
param Isize := read "head.dat" as "2n" skip 0 use 1;
param Asize := read "head.dat" as "3n" skip 0 use 1;

set O := {0 .. Osize-1};
set I := {0 .. Isize-1};
set A := {0 .. Asize-1};

param u_oi[O*I] := read "orders.dat"  as "<1n> 2n,3n" default 0;
param u_ai[A*I] := read "aisles.dat" as "<1n> 2n,3n"  default 0;

param LB :=  read "limits.dat" as "1n" skip 0 use 1;
param UB :=  read "limits.dat" as "2n" skip 0 use 1;

param K := read "K.dat" as "1n" skip 0 use 1;

param lb[A] := 0;      # límite inferior (0/1)
param ub[A] := 1;      # límite superior (0/1)

# … lee bounds.dat si existe …
param lb[A], ub[A] :=
      read "bounds.dat" as "<1n>,2n,3n" default (lb=0, ub=1);

###############################################################################
#  Variables
###############################################################################
var x[A] binary;
var y[O] binary;      # 1 si la orden o entra en la wave

###############################################################################
#  Función objetivo
###############################################################################
maximize unidades:
    sum <o> in O: sum <i> in I: u_oi[o,i] * y[o];

###############################################################################
#  Restricciones
###############################################################################
subto eq_K:
      sum <a> in A: x[a] == K;

subto lower: forall <a> in A: x[a] >= lb[a];
subto upper : forall <a> in A: x[a] <= ub[a];

# cobertura de ítems
#subto cover_items[i in I]:
#     sum <o> in O: u_oi[o,i] * y[o] <=
#    sum <a> in A: u_ai[a,i] * x[a];

subto cover_items :
      forall <i> in I :
            sum <a> in A: u_ai[a,i] * x[a] >=
            sum <o> in O: u_oi[o,i] * y[o];


# tamaño de wave
subto wave_lb:
      sum <o> in O: sum <i> in I: u_oi[o,i] * y[o] >= LB;

subto wave_ub:
      sum <o> in O: sum <i> in I: u_oi[o,i] * y[o] <= UB;
