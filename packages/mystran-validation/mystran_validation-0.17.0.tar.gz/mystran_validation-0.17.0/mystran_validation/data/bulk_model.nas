INIT MASTER(S)
NASTRAN SYSTEM(442)=-1,SYSTEM(319)=1
ID BEAM FEA,Femap
SOL SESTATIC
TIME 10000
CEND
  TITLE = Analyse
  SUBTITLE = test
  LABEL = test
  ECHO = NONE
  DISPLACEMENT(PRINT) = ALL
  SPCFORCE(PRINT) = ALL
  OLOAD(PRINT) = ALL
  MPCFORCE(PRINT) = ALL
  GPFORCE(PRINT) = ALL
  FORCE(PRINT,CORNER) = ALL
  STRESS(PRINT,CORNER) = ALL
SUBCASE 1
  SUBTITLE = NASTRAN SPC 1 - NASTRAN SPC 1 - lc1
  SPC = 1
  LOAD = 1
SUBCASE 2
  SUBTITLE = NASTRAN SPC 1 - NASTRAN SPC 1 - lc2
  SPC = 1
  LOAD = 2
BEGIN BULK
$ ***************************************************************************
$   Written by : beamsolver by numeric-GmbH
$   Version    : 2.10.0
$   Date       : 2021-05-16 07:39:48.453845
$ ***************************************************************************
$
PARAM,POST,-1
PARAM,OGEOM,NO
PARAM,AUTOSPC,NO
PARAM,K6ROT,100.
PARAM,GRDPNT,0
PARAM,CHECKOUT,NO
PARAM,PRTGPDT,YES
PARAM,PRTCSTM,YES
PARAM,PRTMGG,YES
PARAM,PRTPG,YES
$PARAM,EXTOUT,DMIGPCH

CORD2C         1       0      0.      0.      0.      0.      0.      1.+FEMAPC1
+FEMAPC1      1.      0.      1.        
CORD2S         2       0      0.      0.      0.      0.      0.      1.+FEMAPC2
+FEMAPC2      1.      0.      1.  
$
$ ### Spc ###
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
SPC1           1     123       1
SPC1           1       3       2
SPC1           1     123       3
SPC1           1       3       4
SPC1           1      12       5
SPC1           1      12       6
SPC1           1      12       7
SPC1           1      12      10
SPC1           1      12      11
SPC1           1      12      12
$ ### Load Combinations ###
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
$ Femap Load Set 1 : NASTRAN SPC 1 - lc1
LOAD           1      1.      1.       3
$ Femap Load Set 2 : NASTRAN SPC 1 - lc2
LOAD           2      1.      1.       4
$ ### FORCES ###
$FOR/MOM     SID       G     CID     F/M      N1      N2      N3
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
FORCE          3      10       0      1.      0.      0.-449.618
FORCE          4      11       0      1.      0.      0.-224.809
FORCE          4      12       0      1.      0.      0.-224.809
MOMENT         4      11       0      1.      0.44253.73      0.
MOMENT         4      12       0      1.      0.44253.73      0.
$ ### GRIDS ###
$GRID         ID      CP      X1      X2      X3      CD      PS    SEID
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
GRID           1       0    100.    -20.-7.87402       0
GRID           2       0    100.     20.-7.87402       0
GRID           3       0    500.  -121.8-7.87402       0
GRID           4       0    500.   121.8-7.87402       0
GRID           5       0    100.      0.      2.       0
GRID           6       0    157.      0.      2.       0
GRID           7       0    500.      0.      2.       0
GRID           8       0    100.      0.-7.87402       0
GRID           9       0    500.      0.-7.87402       0
GRID          10       0    300.      0.      2.       0
GRID          11       0    200.      0.      2.       0
GRID          12       0    400.      0.      2.       0
$ ### MATERIALS ###
$MAT1        MID       E       G      NU     RHO       A    TREF      GE
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
$ Femap Material 1 : Alu
MAT1           1  1.04+73900000..333333336127.29      0.      0.      0.
$ Femap Material 2 : Ti
MAT1           2  1.04+73900000..333333372254.58      0.      0.      0.
$ ### PBEAMS ###
$PBAR        PID     MID       A      I1      I2       J     NSM     ...+       
$+            C1      C2      D1      D2      E1      E2      F1      F2+       
$+            K1      K2     I12
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
$ Femap Property 1 : crossbeam1
PBAR           1       1    101.1.2012555.009233 500000.      0.        +       
+             0.      0.      0.      0.      0.      0.      0.      0.+       
+             0.      0.      0.
$ Femap Property 2 : crossbeam2
PBAR           2       1    120.1.44150660.06274 500000.      0.        +       
+             0.      0.      0.      0.      0.      0.      0.      0.+       
+             0.      0.      0.
$ Femap Property 3 : seattrack
PBAR           3       1    73.16.078349  63.186    2.+7      0.        +       
+             0.      0.      0.      0.      0.      0.      0.      0.+       
+             0.      0.      0.
$ ### PBUSHS ###
$PBUSH       PID       K      K1      K2      K3      K4      K5      K6
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
$ Femap Property 4 : goussets_ref10
PBUSH          4       K1.3133+7142753.7571014.78850.7468850.7468850.746
$ ### CBEAMS ###
$CBAR        EID     PID      GA      GB   X1/G0      X2      X3        +       
$+            PA      PB     W1A     W2A     W3A     W1B     W2B     W3B
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
CBAR           1       1       1       8      1.      0.      0.
CBAR           2       1       3       9      1.      0.      0.
CBAR           3       3       5       6      0.      1.      0.
CBAR           4       3       6      11      0.      1.      0.
CBAR           5       1       8       2      1.      0.      0.
CBAR           6       1       9       4      1.      0.      0.
CBAR           9       3      10      12      0.      1.      0.
CBAR          10       3      11      10      0.      1.      0.
CBAR          11       3      12       7      0.      1.      0.
$ ### CBUSHS ###
$CBUSH       EID     PID      GA      GB   G0/X1      X2      X3     CID+       
$+             S    OCID      S1      S2      S3
$--1---|---2---|---3---|---4---|---5---|---6---|---7---|---8---|---9---|---10--|
CBUSH          7       4       8       5      1.      0.      0.
CBUSH          8       4       9       7      1.      0.      0.
ENDDATA