############################################################################
#  MIP completo – Wave Picking (una ola, pasillos fijos = K)
#  Lee los mismos .dat que usamos en las partes 1-4
############################################################################

# ───────────────────── Sets y parámetros ────────────────────────────────

param Osize  := read "head.dat" as "1n" skip 0 use 1;
param Isize := read "head.dat" as "2n" skip 0 use 1;
param Asize := read "head.dat" as "3n" skip 0 use 1;

set O := {0 .. Osize-1};
set I := {0 .. Isize-1};
set A := {0 .. Asize-1};

param d_oi[O*I] := read "orders.dat"  as "<1n> 2n,3n" default 0;
param s_ai[A*I] := read "aisles.dat" as "<1n> 2n,3n"  default 0;

param LB :=  read "limits.dat" as "1n" skip 0 use 1;
param UB :=  read "limits.dat" as "2n" skip 0 use 1;
param K := read "K.dat" as "1n" skip 0 use 1;


# ───────────────────── Variables ────────────────────────────────────────
var x[A] binary;                     # 1 si el pasillo se incluye
var y[O] binary;                     # 1 si el pedido queda en la ola
var z[A*O] binary;                   # 1 si el pedido se sirve desde a

# ───────────────────── Restricciones ────────────────────────────────────
subto capacity:
      forall <a> in A: forall <i> in I:
          sum <o> in O: d_oi[o,i] * z[a,o]  <=  s_ai[a,i] * x[a];

subto assign:
      forall <o> in O:
          sum <a> in A: z[a,o]  ==  y[o];

subto link:
      forall <a> in A: forall <o> in O:
          z[a,o] <= x[a];

subto wave_size_lb:
      sum <o> in O: sum<i> in I: d_oi[o,i] * y[o]  >=  LB;

subto wave_size_ub:
      sum <o> in O: sum<i> in I: d_oi[o,i] * y[o]  <=  UB;

subto num_aisles:
      sum <a> in A: x[a]  ==  K;

# ───────────────────── Función objetivo ────────────────────────────────
maximize total_units:
      sum <o> in O: sum<i> in I: d_oi[o,i] * y[o];

############################################################################
