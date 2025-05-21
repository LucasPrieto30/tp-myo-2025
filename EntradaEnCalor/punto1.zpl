
# 1.  Datos principales

param Osize  := read "head.dat" as "1n" skip 0 use 1;
param Isize := read "head.dat" as "2n" skip 0 use 1;
param Asize := read "head.dat" as "3n" skip 0 use 1;

set O := {0 ..  Osize-1};
set I := {0 ..  Isize-1};
set A := {0 ..  Asize-1};

# u_oi[o,i]  =  veces que el item i aparece en la bolsa o
param u_oi[O*I] := read "bags.dat"  as "<1n> 2n,3n"  default 0 ;

# u_ai[a,i]  =  veces que el item i aparece en el container a
param u_ai[A*I] := read "conts.dat" as "<1n> 2n,3n"  default 0 ;

# Beneficios
param b_oi[O*I] := 1;
param b_a[A]    := 1;

# 3.  Variables

var x[O] binary;     # 1 si se selecciona la bolsita o
var y[A] binary;     # 1 si se selecciona el container a

# 4.  Objetivo

maximize profit:
      sum <o,i> in O*I: u_oi[o,i] * x[o]     # beneficio por copias en bolsitas
    + sum <a>   in A:     y[a];              # beneficio fijo 1 por container


# 5.  Restricciones

subto one_container :
      sum <a> in A: y[a] == 1;

subto cover_items :
      forall <i> in I :
            sum <a> in A: u_ai[a,i] * y[a] >=
            sum <o> in O: u_oi[o,i] * x[o];