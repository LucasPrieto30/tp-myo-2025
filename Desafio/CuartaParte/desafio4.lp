\ This file was automatically generated by Zimpl
\ param Osize  := read "head.dat" as "1n" skip 0 use 1;
\ param Isize := read "head.dat" as "2n" skip 0 use 1;
\ param Asize := read "head.dat" as "3n" skip 0 use 1;
\ set O := {0 .. Osize-1};
\ set I := {0 .. Isize-1};
\ set A := {0 .. Asize-1};
\ param u_oi[O*I] := read "orders.dat"  as "<1n> 2n,3n" default 0;
\ param u_ai[A*I] := read "aisles.dat" as "<1n> 2n,3n"  default 0;
\ param LB :=  read "limits.dat" as "1n" skip 0 use 1;
\ param UB :=  read "limits.dat" as "2n" skip 0 use 1;
\ param K := read "K.dat" as "1n" skip 0 use 1;
\ param lb[A] := 0;
\ param ub[A] := 1;
\ param lb[A], ub[A] :=       read "bounds.dat" as "<1n>,2n,3n" default (lb=0, ub=1);
\ var x[A] binary;
\ var y[O] binary;
\ maximize unidades:     sum <o> in O: sum <i> in I: u_oi[o,i] * y[o];
\ subto eq_K:       sum <a> in A: x[a] == K;
\ subto lower: forall <a> in A: x[a] >= lb[a];
\ subto upper : forall <a> in A: x[a] <= ub[a];
\ subto cover_items :       forall <i> in I :             sum <a> in A: u_ai[a,i] * x[a] >=             sum <o> in O: u_oi[o,i]
\  * y[o];
\ subto wave_lb:       sum <o> in O: sum <i> in I: u_oi[o,i] * y[o] >= LB;
\ subto wave_ub:       sum <o> in O: sum <i> in I: u_oi[o,i] * y[o] <= UB;
\Problem name: desafio4.zpl
Maximize
 unidades:  +3 y#0 +4 y#1 +5 y#2 +3 y#3 +3 y#4 +5 y#5
  +4 y#6 +2 y#7 +2 y#8 +4 y#9 +2 y#10 +2 y#11
  +3 y#12 +4 y#13 +8 y#14 +2 y#15 +3 y#16 +3 y#17
  +3 y#18 +4 y#19 +4 y#20 +3 y#21 +4 y#22 +3 y#23
  +3 y#24 +2 y#25 +2 y#26 +2 y#27 +7 y#28 +6 y#29
  +2 y#30 +2 y#31 +6 y#32 +2 y#33 +2 y#34 +5 y#35
  +2 y#36 +5 y#37 +4 y#38 +3 y#39 +5 y#40 +4 y#41
  +3 y#42 +2 y#43 +3 y#44 +2 y#45 +5 y#46 +3 y#47
  +3 y#48 +5 y#49 +3 y#50 +2 y#51 +9 y#52 +15 y#53
  +2 y#54 +3 y#55 +2 y#56 +3 y#57 +4 y#58 +3 y#59
  +7 y#60
Subject to
 eq_K_1:
  + x#115 + x#114 + x#113 + x#112 + x#111 + x#110
  + x#109 + x#108 + x#107 + x#106 + x#105 + x#104
  + x#103 + x#102 + x#101 + x#100 + x#99 + x#98
  + x#97 + x#96 + x#95 + x#94 + x#93 + x#92
  + x#91 + x#90 + x#89 + x#88 + x#87 + x#86
  + x#85 + x#84 + x#83 + x#82 + x#81 + x#80
  + x#79 + x#78 + x#77 + x#76 + x#75 + x#74
  + x#73 + x#72 + x#71 + x#70 + x#69 + x#68
  + x#67 + x#66 + x#65 + x#64 + x#63 + x#62
  + x#61 + x#60 + x#59 + x#58 + x#57 + x#56
  + x#55 + x#54 + x#53 + x#52 + x#51 + x#50
  + x#49 + x#48 + x#47 + x#46 + x#45 + x#44
  + x#43 + x#42 + x#41 + x#40 + x#39 + x#38
  + x#37 + x#36 + x#35 + x#34 + x#33 + x#32
  + x#31 + x#30 + x#29 + x#28 + x#27 + x#26
  + x#25 + x#24 + x#23 + x#22 + x#21 + x#20
  + x#19 + x#18 + x#17 + x#16 + x#15 + x#14
  + x#13 + x#12 + x#11 + x#10 + x#9 + x#8
  + x#7 + x#6 + x#5 + x#4 + x#3 + x#2
  + x#1 + x#0 = 7
 lower_1:
  + x#0 >= 0
 lower_2:
  + x#1 >= 0
 lower_3:
  + x#2 >= 0
 lower_4:
  + x#3 >= 0
 lower_5:
  + x#4 >= 0
 lower_6:
  + x#5 >= 0
 lower_7:
  + x#6 >= 0
 lower_8:
  + x#7 >= 0
 lower_9:
  + x#8 >= 0
 lower_10:
  + x#9 >= 0
 lower_11:
  + x#10 >= 0
 lower_12:
  + x#11 >= 0
 lower_13:
  + x#12 >= 0
 lower_14:
  + x#13 >= 0
 lower_15:
  + x#14 >= 0
 lower_16:
  + x#15 >= 0
 lower_17:
  + x#16 >= 0
 lower_18:
  + x#17 >= 0
 lower_19:
  + x#18 >= 0
 lower_20:
  + x#19 >= 0
 lower_21:
  + x#20 >= 0
 lower_22:
  + x#21 >= 0
 lower_23:
  + x#22 >= 0
 lower_24:
  + x#23 >= 0
 lower_25:
  + x#24 >= 0
 lower_26:
  + x#25 >= 0
 lower_27:
  + x#26 >= 0
 lower_28:
  + x#27 >= 0
 lower_29:
  + x#28 >= 0
 lower_30:
  + x#29 >= 0
 lower_31:
  + x#30 >= 0
 lower_32:
  + x#31 >= 0
 lower_33:
  + x#32 >= 0
 lower_34:
  + x#33 >= 0
 lower_35:
  + x#34 >= 0
 lower_36:
  + x#35 >= 0
 lower_37:
  + x#36 >= 0
 lower_38:
  + x#37 >= 0
 lower_39:
  + x#38 >= 0
 lower_40:
  + x#39 >= 0
 lower_41:
  + x#40 >= 0
 lower_42:
  + x#41 >= 0
 lower_43:
  + x#42 >= 0
 lower_44:
  + x#43 >= 0
 lower_45:
  + x#44 >= 0
 lower_46:
  + x#45 >= 0
 lower_47:
  + x#46 >= 0
 lower_48:
  + x#47 >= 0
 lower_49:
  + x#48 >= 0
 lower_50:
  + x#49 >= 0
 lower_51:
  + x#50 >= 0
 lower_52:
  + x#51 >= 0
 lower_53:
  + x#52 >= 0
 lower_54:
  + x#53 >= 0
 lower_55:
  + x#54 >= 0
 lower_56:
  + x#55 >= 0
 lower_57:
  + x#56 >= 0
 lower_58:
  + x#57 >= 0
 lower_59:
  + x#58 >= 0
 lower_60:
  + x#59 >= 0
 lower_61:
  + x#60 >= 0
 lower_62:
  + x#61 >= 0
 lower_63:
  + x#62 >= 0
 lower_64:
  + x#63 >= 0
 lower_65:
  + x#64 >= 0
 lower_66:
  + x#65 >= 0
 lower_67:
  + x#66 >= 0
 lower_68:
  + x#67 >= 0
 lower_69:
  + x#68 >= 0
 lower_70:
  + x#69 >= 0
 lower_71:
  + x#70 >= 0
 lower_72:
  + x#71 >= 0
 lower_73:
  + x#72 >= 0
 lower_74:
  + x#73 >= 0
 lower_75:
  + x#74 >= 0
 lower_76:
  + x#75 >= 0
 lower_77:
  + x#76 >= 0
 lower_78:
  + x#77 >= 0
 lower_79:
  + x#78 >= 0
 lower_80:
  + x#79 >= 0
 lower_81:
  + x#80 >= 0
 lower_82:
  + x#81 >= 0
 lower_83:
  + x#82 >= 0
 lower_84:
  + x#83 >= 0
 lower_85:
  + x#84 >= 0
 lower_86:
  + x#85 >= 0
 lower_87:
  + x#86 >= 0
 lower_88:
  + x#87 >= 0
 lower_89:
  + x#88 >= 0
 lower_90:
  + x#89 >= 0
 lower_91:
  + x#90 >= 0
 lower_92:
  + x#91 >= 0
 lower_93:
  + x#92 >= 0
 lower_94:
  + x#93 >= 0
 lower_95:
  + x#94 >= 0
 lower_96:
  + x#95 >= 0
 lower_97:
  + x#96 >= 0
 lower_98:
  + x#97 >= 0
 lower_99:
  + x#98 >= 0
 lower_100:
  + x#99 >= 0
 lower_101:
  + x#100 >= 0
 lower_102:
  + x#101 >= 0
 lower_103:
  + x#102 >= 0
 lower_104:
  + x#103 >= 0
 lower_105:
  + x#104 >= 0
 lower_106:
  + x#105 >= 0
 lower_107:
  + x#106 >= 0
 lower_108:
  + x#107 >= 0
 lower_109:
  + x#108 >= 0
 lower_110:
  + x#109 >= 0
 lower_111:
  + x#110 >= 0
 lower_112:
  + x#111 >= 0
 lower_113:
  + x#112 >= 0
 lower_114:
  + x#113 >= 0
 lower_115:
  + x#114 >= 0
 lower_116:
  + x#115 >= 0
 upper_1:
  + x#0 <= 1
 upper_2:
  + x#1 <= 1
 upper_3:
  + x#2 <= 1
 upper_4:
  + x#3 <= 1
 upper_5:
  + x#4 <= 1
 upper_6:
  + x#5 <= 1
 upper_7:
  + x#6 <= 1
 upper_8:
  + x#7 <= 1
 upper_9:
  + x#8 <= 1
 upper_10:
  + x#9 <= 1
 upper_11:
  + x#10 <= 1
 upper_12:
  + x#11 <= 1
 upper_13:
  + x#12 <= 1
 upper_14:
  + x#13 <= 1
 upper_15:
  + x#14 <= 1
 upper_16:
  + x#15 <= 1
 upper_17:
  + x#16 <= 1
 upper_18:
  + x#17 <= 1
 upper_19:
  + x#18 <= 1
 upper_20:
  + x#19 <= 1
 upper_21:
  + x#20 <= 1
 upper_22:
  + x#21 <= 1
 upper_23:
  + x#22 <= 1
 upper_24:
  + x#23 <= 1
 upper_25:
  + x#24 <= 1
 upper_26:
  + x#25 <= 1
 upper_27:
  + x#26 <= 1
 upper_28:
  + x#27 <= 1
 upper_29:
  + x#28 <= 1
 upper_30:
  + x#29 <= 1
 upper_31:
  + x#30 <= 1
 upper_32:
  + x#31 <= 1
 upper_33:
  + x#32 <= 1
 upper_34:
  + x#33 <= 1
 upper_35:
  + x#34 <= 1
 upper_36:
  + x#35 <= 1
 upper_37:
  + x#36 <= 1
 upper_38:
  + x#37 <= 1
 upper_39:
  + x#38 <= 1
 upper_40:
  + x#39 <= 1
 upper_41:
  + x#40 <= 1
 upper_42:
  + x#41 <= 1
 upper_43:
  + x#42 <= 1
 upper_44:
  + x#43 <= 1
 upper_45:
  + x#44 <= 1
 upper_46:
  + x#45 <= 1
 upper_47:
  + x#46 <= 1
 upper_48:
  + x#47 <= 1
 upper_49:
  + x#48 <= 1
 upper_50:
  + x#49 <= 1
 upper_51:
  + x#50 <= 1
 upper_52:
  + x#51 <= 1
 upper_53:
  + x#52 <= 1
 upper_54:
  + x#53 <= 1
 upper_55:
  + x#54 <= 1
 upper_56:
  + x#55 <= 1
 upper_57:
  + x#56 <= 1
 upper_58:
  + x#57 <= 1
 upper_59:
  + x#58 <= 1
 upper_60:
  + x#59 <= 1
 upper_61:
  + x#60 <= 1
 upper_62:
  + x#61 <= 1
 upper_63:
  + x#62 <= 1
 upper_64:
  + x#63 <= 1
 upper_65:
  + x#64 <= 1
 upper_66:
  + x#65 <= 1
 upper_67:
  + x#66 <= 1
 upper_68:
  + x#67 <= 1
 upper_69:
  + x#68 <= 1
 upper_70:
  + x#69 <= 1
 upper_71:
  + x#70 <= 1
 upper_72:
  + x#71 <= 1
 upper_73:
  + x#72 <= 1
 upper_74:
  + x#73 <= 1
 upper_75:
  + x#74 <= 1
 upper_76:
  + x#75 <= 1
 upper_77:
  + x#76 <= 1
 upper_78:
  + x#77 <= 1
 upper_79:
  + x#78 <= 1
 upper_80:
  + x#79 <= 1
 upper_81:
  + x#80 <= 1
 upper_82:
  + x#81 <= 1
 upper_83:
  + x#82 <= 1
 upper_84:
  + x#83 <= 1
 upper_85:
  + x#84 <= 1
 upper_86:
  + x#85 <= 1
 upper_87:
  + x#86 <= 1
 upper_88:
  + x#87 <= 1
 upper_89:
  + x#88 <= 1
 upper_90:
  + x#89 <= 1
 upper_91:
  + x#90 <= 1
 upper_92:
  + x#91 <= 1
 upper_93:
  + x#92 <= 1
 upper_94:
  + x#93 <= 1
 upper_95:
  + x#94 <= 1
 upper_96:
  + x#95 <= 1
 upper_97:
  + x#96 <= 1
 upper_98:
  + x#97 <= 1
 upper_99:
  + x#98 <= 1
 upper_100:
  + x#99 <= 1
 upper_101:
  + x#100 <= 1
 upper_102:
  + x#101 <= 1
 upper_103:
  + x#102 <= 1
 upper_104:
  + x#103 <= 1
 upper_105:
  + x#104 <= 1
 upper_106:
  + x#105 <= 1
 upper_107:
  + x#106 <= 1
 upper_108:
  + x#107 <= 1
 upper_109:
  + x#108 <= 1
 upper_110:
  + x#109 <= 1
 upper_111:
  + x#110 <= 1
 upper_112:
  + x#111 <= 1
 upper_113:
  + x#112 <= 1
 upper_114:
  + x#113 <= 1
 upper_115:
  + x#114 <= 1
 upper_116:
  + x#115 <= 1
 cover_items_1:
  -2 y#35 +14 x#99 +5 x#73 +13 x#35 +20 x#6 >= 0
 cover_items_2:
  - y#50 +2 x#3 >= 0
 cover_items_3:
  -2 y#2 +6 x#99 +9 x#64 +27 x#35 +18 x#32 +11 x#25
  +14 x#6 >= 0
 cover_items_4:
  - y#38 +8 x#99 +2 x#64 +35 x#35 +10 x#25 +3 x#6
  >= 0
 cover_items_5:
  - y#35 +13 x#69 +5 x#39 >= 0
 cover_items_6:
  - y#26 + x#97 +2 x#43 +4 x#15 >= 0
 cover_items_7:
  - y#47 +36 x#97 +11 x#43 +24 x#15 >= 0
 cover_items_8:
  -2 y#23 +2 x#97 +2 x#43 >= 0
 cover_items_9:
  -3 y#49 +3 x#87 + x#61 >= 0
 cover_items_10:
  - y#44 - y#12 +5 x#110 +3 x#106 +12 x#104 + x#103
  +25 x#98 +9 x#96 +14 x#88 +4 x#87 +2 x#85 +10 x#82
  +15 x#80 +6 x#62 +9 x#53 + x#51 + x#42 +20 x#41
  +5 x#16 + x#12 >= 0
 cover_items_11:
  - y#34 +3 x#79 >= 0
 cover_items_12:
  -2 y#60 +24 x#97 +27 x#71 +5 x#43 +24 x#15 +3 x#4
  >= 0
 cover_items_13:
  - y#29 + x#97 >= 0
 cover_items_14:
  - y#0 +6 x#83 >= 0
 cover_items_15:
  - y#12 +10 x#88 +2 x#74 >= 0
 cover_items_16:
  - y#48 +2 x#16 >= 0
 cover_items_17:
  -2 y#41 +5 x#97 +5 x#15 >= 0
 cover_items_18:
  - y#57 +14 x#71 >= 0
 cover_items_19:
  - y#45 +25 x#16 >= 0
 cover_items_20:
  - y#52 +12 x#89 >= 0
 cover_items_21:
  - y#1 +9 x#57 >= 0
 cover_items_22:
  - y#2 + x#99 +12 x#64 +8 x#35 +6 x#32 +12 x#25
  +11 x#6 >= 0
 cover_items_23:
  -2 y#18 +34 x#43 >= 0
 cover_items_24:
  - y#47 +26 x#112 +40 x#91 >= 0
 cover_items_25:
  - y#6 +6 x#35 + x#25 +21 x#6 >= 0
 cover_items_26:
  - y#10 +14 x#92 >= 0
 cover_items_27:
  -5 y#14 +5 x#87 >= 0
 cover_items_28:
  -4 y#20 +4 x#105 +7 x#81 +4 x#13 >= 0
 cover_items_29:
  - y#11 + x#97 +29 x#71 + x#43 +72 x#15 >= 0
 cover_items_30:
  -3 y#3 +2 x#83 +2 x#54 + x#4 >= 0
 cover_items_31:
  - y#12 +10 x#104 +2 x#90 + x#80 >= 0
 cover_items_32:
  - y#51 +9 x#113 + x#110 +7 x#108 +9 x#101 +4 x#80
  +10 x#65 +5 x#51 +4 x#41 + x#36 +5 x#28 +7 x#26
  +4 x#19 >= 0
 cover_items_33:
  - y#36 +2 x#33 >= 0
 cover_items_34:
  - y#13 +6 x#101 + x#93 +2 x#59 +3 x#14 +6 x#0
  >= 0
 cover_items_35:
  -2 y#22 +20 x#10 >= 0
 cover_items_36:
  - y#8 +3 x#63 +6 x#49 >= 0
 cover_items_37:
  - y#0 +4 x#101 +4 x#96 +4 x#94 +2 x#90 +6 x#77
  +7 x#47 +5 x#38 +2 x#34 +3 x#30 +2 x#28 +6 x#21
  +4 x#20 + x#12 +3 x#11 +13 x#9 + x#3 +6 x#0
  >= 0
 cover_items_38:
  -3 y#32 +42 x#67 +41 x#60 +19 x#58 +10 x#39 >= 0
 cover_items_39:
  -3 y#38 +2 x#64 + x#32 +3 x#25 + x#6 >= 0
 cover_items_40:
  -2 y#29 +2 x#97 >= 0
 cover_items_41:
  - y#59 +3 x#71 +9 x#43 +30 x#15 >= 0
 cover_items_42:
  - y#15 +5 x#112 +14 x#91 >= 0
 cover_items_43:
  - y#25 + x#82 >= 0
 cover_items_44:
  - y#14 +152 x#99 +227 x#97 + x#32 >= 0
 cover_items_45:
  - y#22 +5 x#38 >= 0
 cover_items_46:
  -2 y#28 +7 x#89 >= 0
 cover_items_47:
  -2 y#48 +53 x#66 >= 0
 cover_items_48:
  - y#35 +12 x#60 +6 x#1 >= 0
 cover_items_49:
  -3 y#40 +9 x#15 >= 0
 cover_items_50:
  - y#40 +22 x#87 +18 x#29 >= 0
 cover_items_51:
  -2 y#28 +8 x#73 +50 x#64 + x#35 +12 x#6 >= 0
 cover_items_52:
  - y#21 +34 x#100 +8 x#94 +18 x#68 +3 x#49 +19 x#47
  +26 x#28 >= 0
 cover_items_53:
  - y#24 +3 x#71 >= 0
 cover_items_54:
  -2 y#39 +5 x#99 +16 x#64 +19 x#25 +12 x#6 >= 0
 cover_items_55:
  - y#52 + x#97 +12 x#71 +2 x#15 +24 x#4 >= 0
 cover_items_56:
  - y#13 +24 x#97 +37 x#71 +102 x#43 +29 x#15 >= 0
 cover_items_57:
  - y#16 +16 x#71 +10 x#43 >= 0
 cover_items_58:
  -4 y#58 + x#28 >= 0
 cover_items_59:
  - y#6 +7 x#43 >= 0
 cover_items_60:
  - y#49 +10 x#39 >= 0
 cover_items_61:
  - y#52 +6 x#89 +12 x#61 >= 0
 cover_items_62:
  -2 y#9 +50 x#9 >= 0
 cover_items_63:
  - y#55 +5 x#71 +30 x#15 >= 0
 cover_items_64:
  - y#54 + x#109 + x#108 +2 x#100 + x#98 +3 x#88
  +3 x#76 +2 x#67 +4 x#63 +2 x#57 +4 x#44 +3 x#28
  +4 x#23 +4 x#17 + x#0 >= 0
 cover_items_65:
  - y#52 + x#89 +6 x#61 >= 0
 cover_items_66:
  -2 y#28 +13 x#32 >= 0
 cover_items_67:
  - y#4 +6 x#112 >= 0
 cover_items_68:
  - y#14 +10 x#53 >= 0
 cover_items_69:
  - y#19 + x#43 + x#15 >= 0
 cover_items_70:
  - y#42 -2 y#24 - y#23 - y#11 +11 x#97 >= 0
 cover_items_71:
  - y#37 +4 x#25 >= 0
 cover_items_72:
  - y#25 + x#82 + x#72 +3 x#63 >= 0
 cover_items_73:
  - y#14 + x#114 +27 x#58 +29 x#19 +21 x#1 >= 0
 cover_items_74:
  - y#52 +6 x#89 +3 x#61 >= 0
 cover_items_75:
  - y#16 +57 x#112 +11 x#91 >= 0
 cover_items_76:
  - y#55 + x#97 +17 x#71 >= 0
 cover_items_77:
  - y#4 +8 x#112 +10 x#91 >= 0
 cover_items_78:
  - y#41 +24 x#97 +5 x#71 >= 0
 cover_items_79:
  - y#47 +70 x#91 >= 0
 cover_items_80:
  - y#35 +7 x#82 +6 x#79 +25 x#63 >= 0
 cover_items_81:
  - y#56 + x#71 +24 x#43 >= 0
 cover_items_82:
  -2 y#5 +16 x#64 +6 x#35 + x#25 >= 0
 cover_items_83:
  - y#30 + x#101 >= 0
 cover_items_84:
  - y#19 +46 x#71 +6 x#15 >= 0
 cover_items_85:
  - y#2 +21 x#99 +2 x#64 >= 0
 cover_items_86:
  - y#40 +45 x#110 +18 x#52 +39 x#33 >= 0
 cover_items_87:
  - y#1 +32 x#82 >= 0
 cover_items_88:
  - y#55 +22 x#97 >= 0
 cover_items_89:
  - y#27 +18 x#103 >= 0
 cover_items_90:
  - y#37 +12 x#99 +5 x#73 + x#64 +12 x#35 +48 x#32
  +12 x#6 >= 0
 cover_items_91:
  -2 y#42 +24 x#97 +12 x#71 +15 x#43 >= 0
 cover_items_92:
  - y#22 +29 x#108 +44 x#104 +10 x#102 + x#78 +23 x#69
  +11 x#67 +28 x#60 +30 x#58 + x#50 +30 x#44 +20 x#39
  +13 x#31 +24 x#29 +24 x#10 >= 0
 cover_items_93:
  - y#26 +4 x#71 +12 x#43 +9 x#15 >= 0
 cover_items_94:
  -12 y#53 +60 x#99 +5 x#64 >= 0
 cover_items_95:
  - y#9 +5 x#9 >= 0
 cover_items_96:
  - y#52 +12 x#89 + x#61 >= 0
 cover_items_97:
  - y#18 +7 x#46 +13 x#32 +9 x#6 >= 0
 cover_items_98:
  - y#1 +6 x#41 >= 0
 cover_items_99:
  - y#52 + x#89 +8 x#61 >= 0
 cover_items_100:
  - y#50 + x#69 +8 x#68 +6 x#40 +5 x#11 >= 0
 cover_items_101:
  - y#44 +9 x#95 +13 x#45 >= 0
 cover_items_102:
  -2 y#21 +25 x#105 +100 x#81 +50 x#13 >= 0
 cover_items_103:
  - y#30 +4 x#10 >= 0
 cover_items_104:
  - y#50 +3 x#70 >= 0
 cover_items_105:
  -2 y#29 +3 x#43 >= 0
 cover_items_106:
  -2 y#6 +20 x#97 +914 x#54 +878 x#15 >= 0
 cover_items_107:
  - y#16 +35 x#71 +70 x#43 +14 x#15 >= 0
 cover_items_108:
  -3 y#53 +18 x#52 >= 0
 cover_items_109:
  - y#27 +4 x#29 +15 x#19 >= 0
 cover_items_110:
  - y#41 +14 x#71 >= 0
 cover_items_111:
  - y#28 +18 x#113 +10 x#103 + x#69 >= 0
 cover_items_112:
  - y#31 +11 x#101 +9 x#40 +23 x#11 +14 x#1 >= 0
 cover_items_113:
  - y#52 + x#89 +5 x#61 >= 0
 cover_items_114:
  -5 y#60 +36 x#71 + x#15 >= 0
 cover_items_115:
  - y#19 +25 x#97 >= 0
 cover_items_116:
  - y#34 +3 x#79 +3 x#62 +7 x#47 >= 0
 cover_items_117:
  - y#39 +14 x#64 +11 x#35 +17 x#6 >= 0
 cover_items_118:
  -3 y#5 +8 x#72 + x#69 +24 x#38 + x#17 +23 x#10
  >= 0
 cover_items_119:
  - y#37 +18 x#25 >= 0
 cover_items_120:
  - y#57 +5 x#71 >= 0
 cover_items_121:
  - y#49 +2 x#81 >= 0
 cover_items_122:
  - y#56 +96 x#35 >= 0
 cover_items_123:
  -3 y#32 +45 x#95 +3 x#92 +23 x#90 +2 x#84 +2 x#75
  +3 x#72 + x#34 +28 x#31 +4 x#2 >= 0
 cover_items_124:
  - y#1 + x#69 +4 x#38 >= 0
 cover_items_125:
  - y#15 +6 x#112 +2 x#91 >= 0
 cover_items_126:
  - y#10 +3 x#98 +3 x#88 +10 x#63 +4 x#33 +4 x#5
  >= 0
 cover_items_127:
  - y#29 + x#43 >= 0
 cover_items_128:
  - y#8 +14 x#112 >= 0
 cover_items_129:
  -3 y#46 +2 x#97 +9 x#43 >= 0
 cover_items_130:
  -2 y#17 +10 x#33 +7 x#23 >= 0
 cover_items_131:
  - y#19 + x#71 +5 x#43 >= 0
 cover_items_132:
  -2 y#59 +11 x#24 >= 0
 cover_items_133:
  - y#17 +9 x#64 + x#35 >= 0
 cover_items_134:
  - y#4 +11 x#91 >= 0
 cover_items_135:
  - y#33 +5 x#71 +2 x#43 >= 0
 cover_items_136:
  - y#0 + x#108 +5 x#55 +6 x#30 +9 x#21 >= 0
 cover_items_137:
  - y#51 +2 x#65 +2 x#17 >= 0
 cover_items_138:
  - y#37 + x#73 +21 x#64 +20 x#35 +30 x#6 >= 0
 cover_items_139:
  - y#37 +2 x#35 + x#25 >= 0
 cover_items_140:
  - y#57 +21 x#97 + x#15 >= 0
 cover_items_141:
  - y#33 +2 x#15 >= 0
 cover_items_142:
  -2 y#46 +26 x#71 >= 0
 cover_items_143:
  - y#2 +18 x#99 +23 x#73 +12 x#64 +10 x#35 +12 x#32
  +4 x#25 +12 x#6 >= 0
 cover_items_144:
  - y#54 +8 x#110 +5 x#88 + x#69 +9 x#12 >= 0
 cover_items_145:
  - y#52 + x#89 +15 x#61 >= 0
 cover_items_146:
  - y#7 + x#115 + x#109 + x#101 + x#90 + x#87
  + x#86 + x#85 + x#80 + x#68 + x#58 + x#57
  + x#50 + x#37 + x#31 + x#22 +2 x#11 + x#8
  + x#3 + x#0 >= 0
 cover_items_147:
  -2 y#13 +16 x#97 + x#15 >= 0
 cover_items_148:
  - y#44 +23 x#114 + x#89 +10 x#78 +5 x#72 +29 x#66
  +7 x#63 + x#42 +70 x#10 +28 x#1 >= 0
 cover_items_149:
  - y#36 +19 x#107 +2 x#83 +20 x#54 + x#4 >= 0
 cover_items_150:
  - y#7 +4 x#115 + x#111 + x#110 + x#106 + x#88
  +2 x#84 + x#79 + x#78 + x#62 + x#58 + x#55
  + x#50 + x#48 + x#42 + x#27 + x#18 + x#12
  + x#7 + x#3 >= 0
 cover_items_151:
  - y#45 +7 x#67 + x#56 +48 x#50 + x#14 + x#12
  >= 0
 cover_items_152:
  - y#43 +6 x#108 + x#92 +8 x#86 +2 x#82 +8 x#78
  + x#58 +4 x#40 +5 x#22 +3 x#17 >= 0
 cover_items_153:
  - y#9 +5 x#9 >= 0
 cover_items_154:
  - y#43 + x#86 +5 x#79 +8 x#72 +8 x#58 +2 x#53
  +4 x#44 +3 x#42 +6 x#33 +5 x#29 >= 0
 cover_items_155:
  - y#31 +3 x#27 >= 0
 wave_lb_1:
  +7 y#60 +3 y#59 +4 y#58 +3 y#57 +2 y#56 +3 y#55
  +2 y#54 +15 y#53 +9 y#52 +2 y#51 +3 y#50 +5 y#49
  +3 y#48 +3 y#47 +5 y#46 +2 y#45 +3 y#44 +2 y#43
  +3 y#42 +4 y#41 +5 y#40 +3 y#39 +4 y#38 +5 y#37
  +2 y#36 +5 y#35 +2 y#34 +2 y#33 +6 y#32 +2 y#31
  +2 y#30 +6 y#29 +7 y#28 +2 y#27 +2 y#26 +2 y#25
  +3 y#24 +3 y#23 +4 y#22 +3 y#21 +4 y#20 +4 y#19
  +3 y#18 +3 y#17 +3 y#16 +2 y#15 +8 y#14 +4 y#13
  +3 y#12 +2 y#11 +2 y#10 +4 y#9 +2 y#8 +2 y#7
  +4 y#6 +5 y#5 +3 y#4 +3 y#3 +5 y#2 +4 y#1
  +3 y#0 >= 30
 wave_ub_1:
  +7 y#60 +3 y#59 +4 y#58 +3 y#57 +2 y#56 +3 y#55
  +2 y#54 +15 y#53 +9 y#52 +2 y#51 +3 y#50 +5 y#49
  +3 y#48 +3 y#47 +5 y#46 +2 y#45 +3 y#44 +2 y#43
  +3 y#42 +4 y#41 +5 y#40 +3 y#39 +4 y#38 +5 y#37
  +2 y#36 +5 y#35 +2 y#34 +2 y#33 +6 y#32 +2 y#31
  +2 y#30 +6 y#29 +7 y#28 +2 y#27 +2 y#26 +2 y#25
  +3 y#24 +3 y#23 +4 y#22 +3 y#21 +4 y#20 +4 y#19
  +3 y#18 +3 y#17 +3 y#16 +2 y#15 +8 y#14 +4 y#13
  +3 y#12 +2 y#11 +2 y#10 +4 y#9 +2 y#8 +2 y#7
  +4 y#6 +5 y#5 +3 y#4 +3 y#3 +5 y#2 +4 y#1
  +3 y#0 <= 68
Bounds
 0 <= x#0 <= 1
 0 <= x#1 <= 1
 0 <= x#2 <= 1
 0 <= x#3 <= 1
 0 <= x#4 <= 1
 0 <= x#5 <= 1
 0 <= x#6 <= 1
 0 <= x#7 <= 1
 0 <= x#8 <= 1
 0 <= x#9 <= 1
 0 <= x#10 <= 1
 0 <= x#11 <= 1
 0 <= x#12 <= 1
 0 <= x#13 <= 1
 0 <= x#14 <= 1
 0 <= x#15 <= 1
 0 <= x#16 <= 1
 0 <= x#17 <= 1
 0 <= x#18 <= 1
 0 <= x#19 <= 1
 0 <= x#20 <= 1
 0 <= x#21 <= 1
 0 <= x#22 <= 1
 0 <= x#23 <= 1
 0 <= x#24 <= 1
 0 <= x#25 <= 1
 0 <= x#26 <= 1
 0 <= x#27 <= 1
 0 <= x#28 <= 1
 0 <= x#29 <= 1
 0 <= x#30 <= 1
 0 <= x#31 <= 1
 0 <= x#32 <= 1
 0 <= x#33 <= 1
 0 <= x#34 <= 1
 0 <= x#35 <= 1
 0 <= x#36 <= 1
 0 <= x#37 <= 1
 0 <= x#38 <= 1
 0 <= x#39 <= 1
 0 <= x#40 <= 1
 0 <= x#41 <= 1
 0 <= x#42 <= 1
 0 <= x#43 <= 1
 0 <= x#44 <= 1
 0 <= x#45 <= 1
 0 <= x#46 <= 1
 0 <= x#47 <= 1
 0 <= x#48 <= 1
 0 <= x#49 <= 1
 0 <= x#50 <= 1
 0 <= x#51 <= 1
 0 <= x#52 <= 1
 0 <= x#53 <= 1
 0 <= x#54 <= 1
 0 <= x#55 <= 1
 0 <= x#56 <= 1
 0 <= x#57 <= 1
 0 <= x#58 <= 1
 0 <= x#59 <= 1
 0 <= x#60 <= 1
 0 <= x#61 <= 1
 0 <= x#62 <= 1
 0 <= x#63 <= 1
 0 <= x#64 <= 1
 0 <= x#65 <= 1
 0 <= x#66 <= 1
 0 <= x#67 <= 1
 0 <= x#68 <= 1
 0 <= x#69 <= 1
 0 <= x#70 <= 1
 0 <= x#71 <= 1
 0 <= x#72 <= 1
 0 <= x#73 <= 1
 0 <= x#74 <= 1
 0 <= x#75 <= 1
 0 <= x#76 <= 1
 0 <= x#77 <= 1
 0 <= x#78 <= 1
 0 <= x#79 <= 1
 0 <= x#80 <= 1
 0 <= x#81 <= 1
 0 <= x#82 <= 1
 0 <= x#83 <= 1
 0 <= x#84 <= 1
 0 <= x#85 <= 1
 0 <= x#86 <= 1
 0 <= x#87 <= 1
 0 <= x#88 <= 1
 0 <= x#89 <= 1
 0 <= x#90 <= 1
 0 <= x#91 <= 1
 0 <= x#92 <= 1
 0 <= x#93 <= 1
 0 <= x#94 <= 1
 0 <= x#95 <= 1
 0 <= x#96 <= 1
 0 <= x#97 <= 1
 0 <= x#98 <= 1
 0 <= x#99 <= 1
 0 <= x#100 <= 1
 0 <= x#101 <= 1
 0 <= x#102 <= 1
 0 <= x#103 <= 1
 0 <= x#104 <= 1
 0 <= x#105 <= 1
 0 <= x#106 <= 1
 0 <= x#107 <= 1
 0 <= x#108 <= 1
 0 <= x#109 <= 1
 0 <= x#110 <= 1
 0 <= x#111 <= 1
 0 <= x#112 <= 1
 0 <= x#113 <= 1
 0 <= x#114 <= 1
 0 <= x#115 <= 1
 0 <= y#0 <= 1
 0 <= y#1 <= 1
 0 <= y#2 <= 1
 0 <= y#3 <= 1
 0 <= y#4 <= 1
 0 <= y#5 <= 1
 0 <= y#6 <= 1
 0 <= y#7 <= 1
 0 <= y#8 <= 1
 0 <= y#9 <= 1
 0 <= y#10 <= 1
 0 <= y#11 <= 1
 0 <= y#12 <= 1
 0 <= y#13 <= 1
 0 <= y#14 <= 1
 0 <= y#15 <= 1
 0 <= y#16 <= 1
 0 <= y#17 <= 1
 0 <= y#18 <= 1
 0 <= y#19 <= 1
 0 <= y#20 <= 1
 0 <= y#21 <= 1
 0 <= y#22 <= 1
 0 <= y#23 <= 1
 0 <= y#24 <= 1
 0 <= y#25 <= 1
 0 <= y#26 <= 1
 0 <= y#27 <= 1
 0 <= y#28 <= 1
 0 <= y#29 <= 1
 0 <= y#30 <= 1
 0 <= y#31 <= 1
 0 <= y#32 <= 1
 0 <= y#33 <= 1
 0 <= y#34 <= 1
 0 <= y#35 <= 1
 0 <= y#36 <= 1
 0 <= y#37 <= 1
 0 <= y#38 <= 1
 0 <= y#39 <= 1
 0 <= y#40 <= 1
 0 <= y#41 <= 1
 0 <= y#42 <= 1
 0 <= y#43 <= 1
 0 <= y#44 <= 1
 0 <= y#45 <= 1
 0 <= y#46 <= 1
 0 <= y#47 <= 1
 0 <= y#48 <= 1
 0 <= y#49 <= 1
 0 <= y#50 <= 1
 0 <= y#51 <= 1
 0 <= y#52 <= 1
 0 <= y#53 <= 1
 0 <= y#54 <= 1
 0 <= y#55 <= 1
 0 <= y#56 <= 1
 0 <= y#57 <= 1
 0 <= y#58 <= 1
 0 <= y#59 <= 1
 0 <= y#60 <= 1
General
 x#0
 x#1
 x#2
 x#3
 x#4
 x#5
 x#6
 x#7
 x#8
 x#9
 x#10
 x#11
 x#12
 x#13
 x#14
 x#15
 x#16
 x#17
 x#18
 x#19
 x#20
 x#21
 x#22
 x#23
 x#24
 x#25
 x#26
 x#27
 x#28
 x#29
 x#30
 x#31
 x#32
 x#33
 x#34
 x#35
 x#36
 x#37
 x#38
 x#39
 x#40
 x#41
 x#42
 x#43
 x#44
 x#45
 x#46
 x#47
 x#48
 x#49
 x#50
 x#51
 x#52
 x#53
 x#54
 x#55
 x#56
 x#57
 x#58
 x#59
 x#60
 x#61
 x#62
 x#63
 x#64
 x#65
 x#66
 x#67
 x#68
 x#69
 x#70
 x#71
 x#72
 x#73
 x#74
 x#75
 x#76
 x#77
 x#78
 x#79
 x#80
 x#81
 x#82
 x#83
 x#84
 x#85
 x#86
 x#87
 x#88
 x#89
 x#90
 x#91
 x#92
 x#93
 x#94
 x#95
 x#96
 x#97
 x#98
 x#99
 x#100
 x#101
 x#102
 x#103
 x#104
 x#105
 x#106
 x#107
 x#108
 x#109
 x#110
 x#111
 x#112
 x#113
 x#114
 x#115
 y#0
 y#1
 y#2
 y#3
 y#4
 y#5
 y#6
 y#7
 y#8
 y#9
 y#10
 y#11
 y#12
 y#13
 y#14
 y#15
 y#16
 y#17
 y#18
 y#19
 y#20
 y#21
 y#22
 y#23
 y#24
 y#25
 y#26
 y#27
 y#28
 y#29
 y#30
 y#31
 y#32
 y#33
 y#34
 y#35
 y#36
 y#37
 y#38
 y#39
 y#40
 y#41
 y#42
 y#43
 y#44
 y#45
 y#46
 y#47
 y#48
 y#49
 y#50
 y#51
 y#52
 y#53
 y#54
 y#55
 y#56
 y#57
 y#58
 y#59
 y#60
End
