import os
import re
import shutil
from dataclasses import replace
from typing import Iterable

import numpy as np
import pandas as pd
import pytest
import sympy

from pharmpy.internals.fs.cwd import chdir
from pharmpy.model import Assignment
from pharmpy.modeling import (
    add_iiv,
    add_iov,
    add_lag_time,
    add_peripheral_compartment,
    add_pk_iiv,
    create_joint_distribution,
    fix_parameters_to,
    get_initial_conditions,
    get_lag_times,
    get_zero_order_inputs,
    has_first_order_elimination,
    has_linear_odes,
    has_linear_odes_with_real_eigenvalues,
    has_michaelis_menten_elimination,
    has_mixed_mm_fo_elimination,
    has_odes,
    has_zero_order_absorption,
    has_zero_order_elimination,
    remove_iiv,
    remove_iov,
    remove_lag_time,
    set_bolus_absorption,
    set_first_order_absorption,
    set_first_order_elimination,
    set_initial_condition,
    set_michaelis_menten_elimination,
    set_mixed_mm_fo_elimination,
    set_ode_solver,
    set_peripheral_compartments,
    set_seq_zo_fo_absorption,
    set_transit_compartments,
    set_zero_order_absorption,
    set_zero_order_elimination,
    set_zero_order_input,
    split_joint_distribution,
    transform_etas_boxcox,
    transform_etas_john_draper,
    transform_etas_tdist,
    update_initial_individual_estimates,
    update_inits,
)
from pharmpy.modeling.odes import find_clearance_parameters, find_volume_parameters
from pharmpy.tools import read_modelfit_results


def test_set_first_order_elimination(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'pheno.mod')
    correct = model.model_code
    model = set_first_order_elimination(model)
    assert model.model_code == correct
    assert has_first_order_elimination(model)
    model = set_zero_order_elimination(model)
    model = set_first_order_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN1 TRANS2

$PK
CL = THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V

$ERROR
Y=F+F*EPS(1)

$THETA  (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; TVV
$OMEGA  0.0309626 ; IIV_CL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct
    model = set_michaelis_menten_elimination(model)
    model = set_first_order_elimination(model)
    assert model.model_code == correct
    model = set_mixed_mm_fo_elimination(model)
    model = set_first_order_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN1 TRANS2

$PK
CL = THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V

$ERROR
Y=F+F*EPS(1)

$THETA  (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; TVV
$OMEGA  0.0309626 ; IIV_CL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_set_zero_order_elimination(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'pheno.mod')
    assert not has_zero_order_elimination(model)
    model = set_zero_order_elimination(model)
    assert has_zero_order_elimination(model)
    assert not has_michaelis_menten_elimination(model)
    assert not has_first_order_elimination(model)
    assert not has_mixed_mm_fo_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN13 TOL=9

$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
KM = THETA(3)
CLMM = THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V

$DES
DADT(1) = -A(1)*CLMM*KM/(V*(A(1)/V + KM))
$ERROR
Y=F+F*EPS(1)

$THETA  (0,0.00469307) ; POP_CLMM
$THETA (0,1.00916) ; TVV
$THETA  (0,0.067,1358.0) FIX ; POP_KM
$OMEGA  0.0309626 ; IIV_CLMM
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct
    model = set_zero_order_elimination(model)
    assert model.model_code == correct
    model = set_michaelis_menten_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN13 TOL=9

$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
KM = THETA(3)
CLMM = THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V

$DES
DADT(1) = -A(1)*CLMM*KM/(V*(A(1)/V + KM))
$ERROR
Y=F+F*EPS(1)

$THETA  (0,0.00469307) ; POP_CLMM
$THETA (0,1.00916) ; TVV
$THETA  (0,0.067,1358.0) ; POP_KM
$OMEGA  0.0309626 ; IIV_CLMM
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct
    model = load_model_for_test(testdata / 'nonmem' / 'pheno.mod')
    model = set_mixed_mm_fo_elimination(model)
    model = set_zero_order_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN13 TOL=9

$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$ABBR REPLACE ETA_2=ETA(1)
$PK
CLMM = THETA(3)
KM = THETA(2)
V = THETA(1)*EXP(ETA_2)
S1=V

$DES
DADT(1) = -A(1)*CLMM*KM/(V*(A(1)/V + KM))
$ERROR
Y=F+F*EPS(1)

$THETA (0,1.00916) ; TVV
$THETA  (0,135.8,1358.0) FIX ; POP_KM
$THETA  (0,0.002346535) ; POP_CLMM
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_set_michaelis_menten_elimination(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'pheno.mod')
    assert not has_michaelis_menten_elimination(model)
    model = set_michaelis_menten_elimination(model)
    assert has_michaelis_menten_elimination(model)
    assert not has_zero_order_elimination(model)
    assert not has_first_order_elimination(model)
    assert not has_mixed_mm_fo_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN13 TOL=9

$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
KM = THETA(3)
CLMM = THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V

$DES
DADT(1) = -A(1)*CLMM*KM/(V*(A(1)/V + KM))
$ERROR
Y=F+F*EPS(1)

$THETA  (0,0.00469307) ; POP_CLMM
$THETA (0,1.00916) ; TVV
$THETA  (0,135.8,1358.0) ; POP_KM
$OMEGA  0.0309626 ; IIV_CLMM
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct
    model = set_michaelis_menten_elimination(model)
    assert model.model_code == correct

    model = set_zero_order_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN13 TOL=9

$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
KM = THETA(3)
CLMM = THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V

$DES
DADT(1) = -A(1)*CLMM*KM/(V*(A(1)/V + KM))
$ERROR
Y=F+F*EPS(1)

$THETA  (0,0.00469307) ; POP_CLMM
$THETA (0,1.00916) ; TVV
$THETA  (0,135.8,1358.0) FIX ; POP_KM
$OMEGA  0.0309626 ; IIV_CLMM
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_fo_mm_eta(create_model_for_test):
    code = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS2
$PK
CL = THETA(1)*EXP(ETA(1))
V = THETA(2)*EXP(ETA(2))
S1=V
$ERROR
Y=F+F*EPS(1)
$THETA  (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$OMEGA 0.25  ; IIV_CL
$OMEGA 0.5  ; IIV_V
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    model = create_model_for_test(code, dataset='pheno')
    model = set_michaelis_menten_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN13 TOL=9
$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
KM = THETA(3)
CLMM = THETA(1)*EXP(ETA(1))
V = THETA(2)*EXP(ETA(2))
S1=V
$DES
DADT(1) = -A(1)*CLMM*KM/(V*(A(1)/V + KM))
$ERROR
Y=F+F*EPS(1)
$THETA  (0,0.00469307) ; POP_CLMM
$THETA (0,1.00916) ; POP_V
$THETA  (0,135.8,1358.0) ; POP_KM
$OMEGA  0.25 ; IIV_CLMM
$OMEGA 0.5  ; IIV_V
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_set_michaelis_menten_elimination_from_k(create_model_for_test):
    code = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS1
$PK
K=THETA(1)*EXP(ETA(1))
$ERROR
Y=F+F*EPS(1)
$THETA (0,0.00469307) ; TVCL
$OMEGA 0.0309626  ; IVCL
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    model = create_model_for_test(code, dataset='pheno')
    model = set_michaelis_menten_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN13 TOL=9
$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
DUMMYETA = ETA(1)
CLMM = THETA(3)
VC = THETA(2)
KM = THETA(1)
$DES
DADT(1) = -A(1)*CLMM*KM/(VC*(A(1)/VC + KM))
$ERROR
Y=F+F*EPS(1)
$THETA  (0,135.8,1358.0) ; POP_KM
$THETA  (0,0.1) ; POP_VC
$THETA  (0,0.00469307) ; POP_CLMM
$OMEGA  0 FIX ; DUMMYOMEGA
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_combined_mm_fo_elimination(create_model_for_test):
    code = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS2
$PK
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V
$ERROR
Y=F+F*EPS(1)
$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$OMEGA 0.0309626  ; IVCL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    model = create_model_for_test(code, dataset='pheno')
    assert not has_mixed_mm_fo_elimination(model)
    model = set_mixed_mm_fo_elimination(model)
    assert has_mixed_mm_fo_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN13 TOL=9
$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
CLMM = THETA(4)
KM = THETA(3)
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V
$DES
DADT(1) = -A(1)*(CL + CLMM*KM/(A(1)/V + KM))/V
$ERROR
Y=F+F*EPS(1)
$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$THETA  (0,135.8,1358.0) ; POP_KM
$THETA  (0,0.002346535) ; POP_CLMM
$OMEGA 0.0309626  ; IVCL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct
    model = set_mixed_mm_fo_elimination(model)
    assert model.model_code == correct
    model = set_michaelis_menten_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN13 TOL=9
$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$ABBR REPLACE ETA_2=ETA(1)
$PK
CLMM = THETA(3)
KM = THETA(2)
V = THETA(1)*EXP(ETA_2)
S1=V
$DES
DADT(1) = -A(1)*CLMM*KM/(V*(A(1)/V + KM))
$ERROR
Y=F+F*EPS(1)
$THETA (0,1.00916) ; TVV
$THETA  (0,135.8,1358.0) ; POP_KM
$THETA  (0,0.002346535) ; POP_CLMM
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_combined_mm_fo_elimination_from_k(create_model_for_test):
    code = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS1
$PK
K=THETA(1)*EXP(ETA(1))
$ERROR
Y=F+F*EPS(1)
$THETA (0,0.00469307) ; TVCL
$OMEGA 0.0309626  ; IVCL
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    model = create_model_for_test(code, dataset='pheno')
    model = set_mixed_mm_fo_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN13 TOL=9
$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
DUMMYETA = ETA(1)
CLMM = THETA(4)
VC = THETA(3)
CL = THETA(2)
KM = THETA(1)
$DES
DADT(1) = -A(1)*(CL + CLMM*KM/(A(1)/VC + KM))/VC
$ERROR
Y=F+F*EPS(1)
$THETA  (0,135.8,1358.0) ; POP_KM
$THETA  (0,0.002346535) ; POP_CL
$THETA  (0,0.1) ; POP_VC
$THETA  (0,0.002346535) ; POP_CLMM
$OMEGA  0 FIX ; DUMMYOMEGA
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct

    model = create_model_for_test(code, dataset='pheno')
    model = set_zero_order_elimination(model)
    model = set_mixed_mm_fo_elimination(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN13 TOL=9
$MODEL COMPARTMENT=(CENTRAL DEFDOSE)
$PK
CL = THETA(4)
DUMMYETA = ETA(1)
CLMM = THETA(3)
VC = THETA(2)
KM = THETA(1)
$DES
DADT(1) = A(1)*(-CL/VC - CLMM*KM/(VC*(A(1)/VC + KM)))
$ERROR
Y=F+F*EPS(1)
$THETA  (0,0.067,1358.0) ; POP_KM
$THETA  (0,0.1) ; POP_VC
$THETA  (0,0.00469307) ; POP_CLMM
$THETA  (0,0.1) ; POP_CL
$OMEGA  0 FIX ; DUMMYOMEGA
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_transit_compartments(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    model = set_transit_compartments(model, 0)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 0
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_2transits.mod')
    model = set_transit_compartments(model, 1)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 1
    correct = (
        """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN5 TRANS1
$MODEL COMPARTMENT=(TRANS1 DEFDOSE) COMPARTMENT=(DEPOT) COMPARTMENT=(CENTRAL) """
        + """COMPARTMENT=(PERIPHERAL)
$PK
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
K23 = THETA(6)
K30 = CL/V
K34 = THETA(4)
K43 = THETA(5)
K12=THETA(7)
S3 = V

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,10)
$THETA (0,10)
$THETA (1,10)
$THETA (1,10)
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
"""
    )
    assert model.model_code == correct
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_2transits.mod')
    model = set_transit_compartments(model, 4)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 4
    correct = (
        '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN5 TRANS1
$MODEL COMPARTMENT=(TRANS1 DEFDOSE) COMPARTMENT=(TRANS2) COMPARTMENT=(TRANSIT3) '''
        + '''COMPARTMENT=(TRANSIT4) COMPARTMENT=(DEPOT) COMPARTMENT=(CENTRAL) COMPARTMENT=(PERIPHERAL)
$PK
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
K56 = THETA(6)
K34 = THETA(7)
K45 = THETA(7)
K60 = CL/V
K67 = THETA(4)
K76 = THETA(5)
K12=THETA(7)
K23=THETA(7)
S6 = V

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,10)
$THETA (0,10)
$THETA (1,10)
$THETA (1,10)
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    )
    assert model.model_code == correct
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod')
    model = set_transit_compartments(model, 1)

    assert not re.search(r'K *= *', model.model_code)
    assert re.search('K30 = CL/V', model.model_code)


def test_transits_absfo(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod')
    model = set_transit_compartments(model, 0, keep_depot=False)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 0
    assert len(model.statements.ode_system) == 1

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_2transits.mod')
    model = set_transit_compartments(model, 1, keep_depot=False)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 0
    assert len(model.statements.ode_system) == 3
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN4 TRANS1
$PK
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
K20 = CL/V
K23 = THETA(4)
K32 = THETA(5)
K12 = THETA(6)
S2 = V
KA = K12

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,10)
$THETA (0,10)
$THETA (1,10)
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
"""
    assert model.model_code == correct

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_2transits.mod')
    model = set_transit_compartments(model, 4, keep_depot=False)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 4
    correct = (
        '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN5 TRANS1
$MODEL COMPARTMENT=(TRANS1 DEFDOSE) COMPARTMENT=(TRANS2) COMPARTMENT=(TRANSIT3) '''
        + '''COMPARTMENT=(TRANSIT4) COMPARTMENT=(CENTRAL) COMPARTMENT=(PERIPHERAL)
$PK
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
K34 = THETA(6)
K45 = THETA(6)
K50 = CL/V
K56 = THETA(4)
K65 = THETA(5)
K12 = THETA(6)
K23 = THETA(6)
S5 = V

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,10)
$THETA (0,10)
$THETA (1,10)
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    )
    assert model.model_code == correct
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod')
    model = set_transit_compartments(model, 1, keep_depot=False)

    assert not re.search(r'K *= *', model.model_code)
    assert re.search('KA = 1/MDT', model.model_code)


def test_transit_compartments_added_mdt(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan5_nodepot.mod')
    model = set_transit_compartments(model, 2)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 2
    correct = (
        """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN5 TRANS1
$MODEL COMPARTMENT=(TRANSIT1 DEFDOSE) COMPARTMENT=(TRANSIT2) COMPARTMENT=(CENTRAL) """
        + """COMPARTMENT=(PERIPHERAL)
$PK
MDT = THETA(6)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
K12 = 2/MDT
K23 = 2/MDT
K30 = CL/V
K34 = THETA(4)
K43 = THETA(5)
S3 = V

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,10)
$THETA (0,10)
$THETA  (0,0.5) ; POP_MDT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
"""
    )
    assert model.model_code == correct


def test_transit_compartments_change_advan(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    model = set_transit_compartments(model, 3)
    transits = model.statements.ode_system.find_transit_compartments(model.statements)
    assert len(transits) == 3
    correct = (
        """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN5 TRANS1

$MODEL COMPARTMENT=(TRANSIT1 DEFDOSE) COMPARTMENT=(TRANSIT2) COMPARTMENT=(TRANSIT3) """
        + """COMPARTMENT=(CENTRAL)
$PK
MDT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S4 = V
K12 = 3/MDT
K23 = 3/MDT
K34 = 3/MDT
K40 = CL/V

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,0.5) ; POP_MDT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
"""
    )
    assert model.model_code == correct


def test_transit_compartments_change_number(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'pheno.mod')
    model = set_transit_compartments(model, 3)
    model = set_transit_compartments(model, 2)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN5 TRANS1

$MODEL COMPARTMENT=(TRANSIT1 DEFDOSE) COMPARTMENT=(TRANSIT2) COMPARTMENT=(CENTRAL)
$PK
MDT = THETA(3)
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S3 = V
K12 = 2/MDT
K23 = 2/MDT
K30 = CL/V

$ERROR
Y=F+F*EPS(1)

$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$THETA  (0,0.5) ; POP_MDT
$OMEGA 0.0309626  ; IVCL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct

    model = load_model_for_test(testdata / 'nonmem' / 'pheno.mod')
    model = set_transit_compartments(model, 2)
    model = set_transit_compartments(model, 3)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN5 TRANS1

$MODEL COMPARTMENT=(TRANSIT1 DEFDOSE) COMPARTMENT=(TRANSIT2) COMPARTMENT=(TRANSIT3) COMPARTMENT=(CENTRAL)
$PK
MDT = THETA(3)
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S4 = V
K12 = 3/MDT
K23 = 3/MDT
K34 = 3/MDT
K40 = CL/V

$ERROR
Y=F+F*EPS(1)

$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$THETA  (0,0.5) ; POP_MDT
$OMEGA 0.0309626  ; IVCL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""  # noqa: E501
    assert model.model_code == correct


def test_transits_non_linear_elim_with_update(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_transit_compartments(model, 3)
    model = set_zero_order_elimination(model)
    assert 'VC1 =' not in model.model_code
    assert 'CLMM = THETA(1)*EXP(ETA(1))' in model.model_code
    assert 'CL =' not in model.model_code

    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_transit_compartments(model, 3)
    model = set_michaelis_menten_elimination(model)
    assert 'VC1 =' not in model.model_code
    assert 'CLMM = THETA(1)*EXP(ETA(1))' in model.model_code
    assert 'CL =' not in model.model_code

    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_transit_compartments(model, 3)
    model = set_mixed_mm_fo_elimination(model)
    assert 'VC1 =' not in model.model_code
    assert 'CLMM = THETA(6)' in model.model_code
    assert 'CL = THETA(1) * EXP(ETA(1))' in model.model_code


def test_lag_time(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    before = model.model_code
    model = add_lag_time(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS2

$PK
MDT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S1=V
ALAG1 = MDT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,0.5) ; POP_MDT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct

    model = remove_lag_time(model)
    assert model.model_code == before


def test_add_lag_time_updated_dose(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    model = add_lag_time(model)
    model = set_first_order_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN2 TRANS2

$PK
MAT = THETA(5)
MDT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S2 = V
ALAG1 = MDT
KA = 1/MAT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,0.5) ; POP_MDT
$THETA  (0,2.0) ; POP_MAT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct

    model = set_zero_order_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA DUMMYPATH IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2 RATE
$SUBROUTINE ADVAN1 TRANS2

$PK
MAT = THETA(5)
MDT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S1 = V
ALAG1 = MDT
D1 = 2*MAT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,0.5) ; POP_MDT
$THETA  (0,2.0) ; POP_MAT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct


def test_nested_transit_peripherals(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_transit_compartments(model, 1)
    model = set_michaelis_menten_elimination(model)
    model = set_peripheral_compartments(model, 1)
    model = set_peripheral_compartments(model, 2)


def test_add_depot(create_model_for_test):
    code = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS2

$PK
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))

$ERROR
CONC = A(1)/V
Y = CONC + CONC*EPS(1)

$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$OMEGA 0.0309626  ; IVCL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    model = create_model_for_test(code, dataset='pheno')
    model = set_first_order_absorption(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN2 TRANS2

$PK
MAT = THETA(3)
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
KA = 1/MAT

$ERROR
CONC = A(2)/V
Y = CONC + CONC*EPS(1)

$THETA (0,0.00469307) ; TVCL
$THETA (0,1.00916) ; TVV
$THETA  (0,2.0) ; POP_MAT
$OMEGA 0.0309626  ; IVCL
$OMEGA 0.031128  ; IVV
$SIGMA 0.013241

$ESTIMATION METHOD=1 INTERACTION
"""
    assert model.model_code == correct


def test_absorption_rate(load_model_for_test, testdata, tmp_path):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    advan1_before = model.model_code
    model = set_bolus_absorption(model)
    assert advan1_before == model.model_code

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod')
    model = set_bolus_absorption(model)
    assert model.model_code == advan1_before

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan3.mod')
    advan3_before = model.model_code
    model = set_bolus_absorption(model)
    assert model.model_code == advan3_before

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan4.mod')
    model = set_bolus_absorption(model)
    assert model.model_code == advan3_before

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan11.mod')
    advan11_before = model.model_code
    model = set_bolus_absorption(model)
    assert model.model_code == advan11_before

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan12.mod')
    model = set_bolus_absorption(model)
    assert model.model_code == advan11_before

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan5_nodepot.mod')
    advan5_nodepot_before = model.model_code
    model = set_bolus_absorption(model)
    assert model.model_code == advan5_nodepot_before

    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan5_depot.mod')
    model = set_bolus_absorption(model)
    correct = """$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN3 TRANS1
$PK
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
K = CL/V
K12 = THETA(4)
K21 = THETA(5)
S1 = V

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,10)
$THETA (0,10)
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
"""
    assert model.model_code == correct

    # 0-order to 0-order
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1_zero_order.mod')
    advan1_zero_order_before = model.model_code
    model = set_zero_order_absorption(model)
    assert model.model_code == advan1_zero_order_before

    # 0-order to Bolus
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1_zero_order.mod')
    model = set_bolus_absorption(model)
    assert model.model_code.split('\n')[2:] == advan1_before.split('\n')[2:]

    # 1st order to 1st order
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod')
    advan2_before = model.model_code
    model = set_first_order_absorption(model)
    assert model.model_code == advan2_before

    # 0-order to 1st order
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1_zero_order.mod')
    model = set_first_order_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA DUMMYPATH IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN2 TRANS2

$PK
MAT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S2 = V
KA = 1/MAT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,2.0) ; POP_MAT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct

    # Bolus to 1st order
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    model = set_first_order_absorption(model)
    assert model.model_code.split('\n')[2:] == correct.split('\n')[2:]

    # Bolus to 0-order
    datadir = testdata / 'nonmem' / 'modeling'
    (tmp_path / 'abs').mkdir()
    shutil.copy(datadir / 'pheno_advan1.mod', tmp_path / 'abs')
    shutil.copy(datadir / 'pheno_advan2.mod', tmp_path / 'abs')
    shutil.copy(datadir.parent / 'pheno.dta', tmp_path)
    model = load_model_for_test(tmp_path / 'abs' / 'pheno_advan1.mod')
    model = set_zero_order_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA DUMMYPATH IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2 RATE
$SUBROUTINE ADVAN1 TRANS2

$PK
MAT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S1=V
D1 = 2*MAT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,2.0) ; POP_MAT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct

    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA DUMMYPATH IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2 RATE
$SUBROUTINE ADVAN1 TRANS2

$PK
MAT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S1=V
D1 = 2*MAT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,2.0) ; POP_MAT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''

    # 1st to 0-order
    model = load_model_for_test(tmp_path / 'abs' / 'pheno_advan2.mod')
    model = set_zero_order_absorption(model)
    assert model.model_code == correct


def test_seq_to_FO(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2_seq.mod')
    model = set_first_order_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA DUMMYPATH IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN2 TRANS2

$PK
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S2=V
KA = THETA(4)

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307)
$THETA (0,1.00916)
$THETA (-.99,.1)
$THETA (0,0.1)
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct


def test_lagtime_then_zoabs(load_example_model_for_test):
    model = load_example_model_for_test("pheno")
    model = set_first_order_absorption(model)
    model = add_lag_time(model)
    model = set_zero_order_absorption(model)
    assert get_lag_times(model) == {'CENTRAL': sympy.Symbol('ALAG1')}


def test_seq_to_ZO(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2_seq.mod')
    model = set_zero_order_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno_zero_order.csv IGNORE=@
$INPUT ID TIME AMT RATE WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS2

$PK
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S1 = V
D1 = THETA(4)

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307)
$THETA (0,1.00916)
$THETA (-.99,.1)
$THETA (0,0.1)
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct


def test_bolus_to_seq(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1.mod')
    model = set_seq_zo_fo_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA DUMMYPATH IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2 RATE
$SUBROUTINE ADVAN2 TRANS2

$PK
MDT = THETA(5)
MAT = THETA(4)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S2 = V
KA = 1/MAT
D1 = 2*MDT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA  (0,2.0) ; POP_MAT
$THETA  (0,0.5) ; POP_MDT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct


def test_ZO_to_seq(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan1_zero_order.mod')
    model = set_seq_zo_fo_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno_zero_order.csv IGNORE=@
$INPUT ID TIME AMT RATE WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN2 TRANS2

$PK
MAT = THETA(5)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S2 = V
D1 = THETA(4)
KA = 1/MAT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,0.1)
$THETA  (0,2.0) ; POP_MAT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct


def test_FO_to_seq(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'modeling' / 'pheno_advan2.mod')
    model = set_seq_zo_fo_absorption(model)
    correct = '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA DUMMYPATH IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2 RATE
$SUBROUTINE ADVAN2 TRANS2

$PK
MDT = THETA(5)
IF(AMT.GT.0) BTIME=TIME
TAD=TIME-BTIME
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
IF(APGR.LT.5) TVV=TVV*(1+THETA(3))
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S1=V
KA=THETA(4)
D1 = 2*MDT

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; POP_CL
$THETA (0,1.00916) ; POP_V
$THETA (-.99,.1)
$THETA (0,0.1) ; POP_KA
$THETA  (0,0.5) ; POP_MDT
$OMEGA DIAGONAL(2)
 0.0309626  ;       IVCL
 0.031128  ;        IVV

$SIGMA 1e-7
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE UNCONDITIONAL
$TABLE ID TIME DV AMT WGT APGR IPRED PRED RES TAD CWRES NPDE NOAPPEND
       NOPRINT ONEHEADER FILE=sdtab1
'''
    assert model.model_code == correct


def test_absorption_keep_mat(load_model_for_test, testdata):
    # FO to ZO (start model with MAT-eta)
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_zero_order_absorption(model)
    assert 'MAT = THETA(3) * EXP(ETA(3))' in model.model_code
    assert 'KA =' not in model.model_code
    assert 'D1 =' in model.model_code

    # FO to seq-ZO-FO
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_seq_zo_fo_absorption(model)
    assert 'MAT = THETA(3) * EXP(ETA(3))' in model.model_code
    assert 'KA =' in model.model_code
    assert 'D1 =' in model.model_code

    # ZO to seq-ZO-FO
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_zero_order_absorption(model)
    model = set_seq_zo_fo_absorption(model)
    assert 'MAT = THETA(3) * EXP(ETA(3))' in model.model_code
    assert 'KA =' in model.model_code
    assert 'D1 =' in model.model_code
    assert 'MAT1' not in model.model_code

    # ZO to FO
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_zero_order_absorption(model)
    model = set_first_order_absorption(model)
    assert 'MAT = THETA(3) * EXP(ETA(3))' in model.model_code
    assert 'KA =' in model.model_code
    assert 'D1 =' not in model.model_code

    # Transit without keeping depot
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_transit_compartments(model, 3, keep_depot=False)
    assert 'MDT = THETA(3)*EXP(ETA(3))' in model.model_code


def test_has_zero_order_absorption(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    assert not has_zero_order_absorption(model)
    model = set_zero_order_absorption(model)
    assert has_zero_order_absorption(model)


def test_lag_on_nl_elim(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_zero_order_elimination(model)
    model = add_lag_time(model)
    assert 'ALAG' in model.model_code


def test_zo_abs_on_nl_elim(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem' / 'models' / 'mox2.mod')
    model = set_zero_order_elimination(model)
    model = set_zero_order_absorption(model)
    assert 'RATE' in model.model_code
    assert 'D1 =' in model.model_code
    assert 'CONC = A(1)/VC' in model.model_code
    assert 'DADT(1) = -A(1)*' in model.model_code


@pytest.mark.parametrize(
    'etas, etab, buf_new',
    [
        (
            ['ETA_1'],
            'ETAB1 = (EXP(ETA(1))**THETA(4) - 1)/THETA(4)',
            'CL = TVCL*EXP(ETAB1)\nV=TVV*EXP(ETA(2))',
        ),
        (
            ['ETA_1', 'ETA_2'],
            'ETAB1 = (EXP(ETA(1))**THETA(4) - 1)/THETA(4)\n'
            'ETAB2 = (EXP(ETA(2))**THETA(5) - 1)/THETA(5)',
            'CL = TVCL*EXP(ETAB1)\nV = TVV*EXP(ETAB2)',
        ),
        (
            None,
            'ETAB1 = (EXP(ETA(1))**THETA(4) - 1)/THETA(4)\n'
            'ETAB2 = (EXP(ETA(2))**THETA(5) - 1)/THETA(5)',
            'CL = TVCL*EXP(ETAB1)\nV = TVV*EXP(ETAB2)',
        ),
        (
            'ETA_1',
            'ETAB1 = (EXP(ETA(1))**THETA(4) - 1)/THETA(4)',
            'CL = TVCL*EXP(ETAB1)\nV=TVV*EXP(ETA(2))',
        ),
    ],
)
def test_transform_etas_boxcox(load_model_for_test, pheno_path, etas, etab, buf_new):
    model = load_model_for_test(pheno_path)

    model = transform_etas_boxcox(model, etas)

    rec_ref = (
        f'$PK\n'
        f'{etab}\n'
        f'IF(AMT.GT.0) BTIME=TIME\n'
        f'TAD=TIME-BTIME\n'
        f'TVCL=THETA(1)*WGT\n'
        f'TVV=THETA(2)*WGT\n'
        f'IF(APGR.LT.5) TVV=TVV*(1+THETA(3))\n'
        f'{buf_new}\n'
        f'S1=V\n\n'
    )

    assert str(model.internals.control_stream.get_pred_pk_record()) == rec_ref
    assert model.parameters['lambda1'].init == 0.01


def test_transform_etas_tdist(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)

    model = transform_etas_tdist(model, ['ETA_1'])

    symbol = 'ETAT1'

    eta = 'ETA(1)'
    theta = 'THETA(4)'

    num_1 = f'{eta}**2 + 1'
    denom_1 = f'4*{theta}'

    num_2 = f'5*{eta}**4 + 16*{eta}**2 + 3'
    denom_2 = f'96*{theta}**2'

    num_3 = f'3*{eta}**6 + 17*{eta}**2 + 19*{eta}**4 - 15'
    denom_3 = f'384*{theta}**3'

    expression = (
        f'ETA(1)*(({num_1})/({denom_1}) + ({num_2})/({denom_2}) + ({num_3})/({denom_3}) + 1)'
    )

    rec_ref = (
        f'$PK\n'
        f'{symbol} = {expression}\n'
        f'IF(AMT.GT.0) BTIME=TIME\n'
        f'TAD=TIME-BTIME\n'
        f'TVCL=THETA(1)*WGT\n'
        f'TVV=THETA(2)*WGT\n'
        f'IF(APGR.LT.5) TVV=TVV*(1+THETA(3))\n'
        f'CL = TVCL*EXP(ETAT1)\n'
        f'V=TVV*EXP(ETA(2))\n'
        f'S1=V\n\n'
    )

    assert str(model.internals.control_stream.get_pred_pk_record()) == rec_ref
    assert model.parameters['df1'].init == 80


@pytest.mark.parametrize(
    'etas, etad, buf_new',
    [
        (
            ['ETA_1'],
            'ETAD1 = ((ABS(ETA(1)) + 1)**THETA(4) - 1)*ABS(ETA(1))/(ETA(1)*THETA(4))',
            'CL = TVCL*EXP(ETAD1)\nV=TVV*EXP(ETA(2))',
        ),
        (
            'ETA_1',
            'ETAD1 = ((ABS(ETA(1)) + 1)**THETA(4) - 1)*ABS(ETA(1))/(ETA(1)*THETA(4))',
            'CL = TVCL*EXP(ETAD1)\nV=TVV*EXP(ETA(2))',
        ),
    ],
)
def test_transform_etas_john_draper(load_model_for_test, pheno_path, etas, etad, buf_new):
    model = load_model_for_test(pheno_path)

    model = transform_etas_john_draper(model, etas)

    rec_ref = (
        f'$PK\n'
        f'{etad}\n'
        f'IF(AMT.GT.0) BTIME=TIME\n'
        f'TAD=TIME-BTIME\n'
        f'TVCL=THETA(1)*WGT\n'
        f'TVV=THETA(2)*WGT\n'
        f'IF(APGR.LT.5) TVV=TVV*(1+THETA(3))\n'
        f'{buf_new}\n'
        f'S1=V\n\n'
    )

    assert str(model.internals.control_stream.get_pred_pk_record()) == rec_ref


@pytest.mark.parametrize(
    'parameter, expression, operation, eta_name, buf_new, no_of_omega_recs',
    [
        ('S1', 'exp', '+', None, 'V=TVV*EXP(ETA(2))\nS1 = V + EXP(ETA_S1)', 2),
        ('S1', 'exp', '*', None, 'V=TVV*EXP(ETA(2))\nS1 = V*EXP(ETA_S1)', 2),
        ('V', 'exp', '+', None, 'V = TVV*EXP(ETA(2)) + EXP(ETA_V)\nS1=V', 2),
        ('S1', 'add', None, None, 'V=TVV*EXP(ETA(2))\nS1 = V + ETA_S1', 2),
        ('S1', 'prop', None, None, 'V=TVV*EXP(ETA(2))\nS1 = ETA_S1*V', 2),
        ('S1', 'log', None, None, 'V=TVV*EXP(ETA(2))\nS1 = V*EXP(ETA_S1)/(EXP(ETA_S1) + 1)', 2),
        ('S1', 'eta_new', '+', None, 'V=TVV*EXP(ETA(2))\nS1 = V + ETA_S1', 2),
        ('S1', 'eta_new**2', '+', None, 'V=TVV*EXP(ETA(2))\nS1 = V + ETA_S1**2', 2),
        ('S1', 'exp', '+', 'ETA(3)', 'V=TVV*EXP(ETA(2))\nS1 = V + EXP(ETA(3))', 2),
        (
            ['V', 'S1'],
            'exp',
            '+',
            None,
            'V = TVV*EXP(ETA(2)) + EXP(ETA_V)\nS1 = V + EXP(ETA_S1)',
            3,
        ),
        (
            ['V', 'S1'],
            'exp',
            '+',
            ['new_eta1', 'new_eta2'],
            'V = TVV*EXP(ETA(2)) + EXP(NEW_ETA1)\nS1 = V + EXP(NEW_ETA2)',
            3,
        ),
    ],
)
def test_add_iiv(
    load_model_for_test,
    pheno_path,
    parameter,
    expression,
    operation,
    eta_name,
    buf_new,
    no_of_omega_recs,
):
    model = load_model_for_test(pheno_path)

    model = add_iiv(
        model,
        list_of_parameters=parameter,
        expression=expression,
        operation=operation,
        eta_names=eta_name,
    )

    etas = model.random_variables.etas.names

    assert eta_name is None or set(eta_name).intersection(etas) or eta_name in etas

    rec_ref = (
        f'$PK\n'
        f'IF(AMT.GT.0) BTIME=TIME\n'
        f'TAD=TIME-BTIME\n'
        f'TVCL=THETA(1)*WGT\n'
        f'TVV=THETA(2)*WGT\n'
        f'IF(APGR.LT.5) TVV=TVV*(1+THETA(3))\n'
        f'CL=TVCL*EXP(ETA(1))\n'
        f'{buf_new}\n\n'
    )

    assert str(model.internals.control_stream.get_pred_pk_record()) == rec_ref

    omega_rec = model.internals.control_stream.get_records('OMEGA')

    assert len(omega_rec) == no_of_omega_recs
    assert '$OMEGA  0.09 ; IIV_' in str(omega_rec[-1])


def test_add_iiv_missing_param(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    with pytest.raises(ValueError):
        add_iiv(model, 'non_existing_param', 'add')


@pytest.mark.parametrize(
    'etas, abbr_ref, omega_ref',
    [
        (
            ['ETA_CL', 'ETA_V'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA BLOCK(2)\n'
            '0.0309626\t; IVCL\n'
            '0.0031045\t; IIV_CL_IIV_V\n'
            '0.031128\t; IVV\n'
            '$OMEGA 0.1\n'
            '$OMEGA BLOCK(2)\n'
            '0.0309626\n'
            '0.0005 0.031128\n',
        ),
        (
            ['ETA_CL', 'ETA_S1'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_S1=ETA(2)\n'
            '$ABBR REPLACE ETA_V=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA BLOCK(2)\n'
            '0.0309626\t; IVCL\n'
            '0.0055644\t; IIV_CL_IIV_S1\n'
            '0.1\t; OMEGA_3_3\n'
            '$OMEGA 0.031128  ; IVV\n'
            '$OMEGA BLOCK(2)\n'
            '0.0309626\n'
            '0.0005 0.031128\n',
        ),
        (
            ['ETA_V', 'ETA_S1'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA 0.0309626  ; IVCL\n'
            '$OMEGA BLOCK(2)\n'
            '0.031128\t; IVV\n'
            '0.0055792\t; IIV_V_IIV_S1\n'
            '0.1\n'
            '$OMEGA BLOCK(2)\n'
            '0.0309626\n'
            '0.0005 0.031128\n',
        ),
        (
            ['ETA_CL', 'ETA_V', 'ETA_MAT'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_MAT=ETA(3)\n'
            '$ABBR REPLACE ETA_S1=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA BLOCK(3)\n'
            '0.0309626\t; IVCL\n'
            '0.0031045\t; IIV_CL_IIV_V\n'
            '0.031128\t; IVV\n'
            '0.0030963\t; IIV_CL_IIV_MAT\n'
            '0.0031045\t; IIV_V_IIV_MAT\n'
            '0.0309626\t; OMEGA_4_4\n'
            '$OMEGA 0.1\n'
            '$OMEGA  0.031128\n',
        ),
        (
            ['ETA_V', 'ETA_S1', 'ETA_MAT'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA 0.0309626  ; IVCL\n'
            '$OMEGA BLOCK(3)\n'
            '0.031128\t; IVV\n'
            '0.0055792\t; IIV_V_IIV_S1\n'
            '0.1\n'
            '0.0031045\t; IIV_V_IIV_MAT\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '$OMEGA  0.031128\n',
        ),
        (
            ['ETA_S1', 'ETA_MAT', 'ETA_Q'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA DIAGONAL(2)\n'
            '0.0309626  ; IVCL\n'
            '0.031128  ; IVV\n'
            '$OMEGA BLOCK(3)\n'
            '0.1\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '0.0055792\t; IIV_S1_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
        (
            None,
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA BLOCK(5)\n'
            '0.0309626\t; IVCL\n'
            '0.0031045\t; IIV_CL_IIV_V\n'
            '0.031128\t; IVV\n'
            '0.0055644\t; IIV_CL_IIV_S1\n'
            '0.0055792\t; IIV_V_IIV_S1\n'
            '0.1\n'
            '0.0030963\t; IIV_CL_IIV_MAT\n'
            '0.0031045\t; IIV_V_IIV_MAT\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '0.0031045\t; IIV_CL_IIV_Q\n'
            '0.0031128\t; IIV_V_IIV_Q\n'
            '0.0055792\t; IIV_S1_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
    ],
)
def test_create_joint_distribution_plain(load_model_for_test, testdata, etas, abbr_ref, omega_ref):
    model_start = load_model_for_test(testdata / 'nonmem/pheno_block.mod')

    model = create_joint_distribution(model_start, etas, individual_estimates=None)

    rec_abbr = ''.join(
        str(rec) for rec in model.internals.control_stream.get_records('ABBREVIATED')
    )
    assert rec_abbr == abbr_ref

    rec_pk = str(model.internals.control_stream.get_pred_pk_record())
    pk_ref = str(model_start.internals.control_stream.get_pred_pk_record())
    assert rec_pk == pk_ref

    rec_omega = ''.join(str(rec) for rec in model.internals.control_stream.get_records('OMEGA'))
    assert rec_omega == omega_ref


@pytest.mark.parametrize(
    'etas, abbr_ref, omega_ref',
    [
        (
            (['ETA_CL', 'ETA_V'], ['ETA_CL', 'ETA_S1']),
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_S1=ETA(2)\n'
            '$ABBR REPLACE ETA_V=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA BLOCK(2)\n'
            '0.0309626\t; IVCL\n'
            '0.0055644\t; IIV_CL_IIV_S1\n'
            '0.1\t; OMEGA_3_3\n'
            '$OMEGA  0.031128 ; IVV\n'
            '$OMEGA BLOCK(2)\n'
            '0.0309626\n'
            '0.0005 0.031128\n',
        ),
        (
            (None, ['ETA_CL', 'ETA_V']),
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA BLOCK(2)\n'
            '0.0309626\t; IVCL\n'
            '0.0031045\t; IIV_CL_IIV_V\n'
            '0.031128\t; IVV\n'
            '$OMEGA BLOCK(3)\n'
            '0.1\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '0.0055792\t; IIV_S1_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
        (
            (['ETA_CL', 'ETA_V'], None),
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA BLOCK(5)\n'
            '0.0309626\t; IVCL\n'
            '0.0031045\t; IIV_CL_IIV_V\n'
            '0.031128\t; IVV\n'
            '0.0055644\t; IIV_CL_IIV_S1\n'
            '0.0055792\t; IIV_V_IIV_S1\n'
            '0.1\n'
            '0.0030963\t; IIV_CL_IIV_MAT\n'
            '0.0031045\t; IIV_V_IIV_MAT\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '0.0031045\t; IIV_CL_IIV_Q\n'
            '0.0031128\t; IIV_V_IIV_Q\n'
            '0.0055792\t; IIV_S1_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
    ],
)
def test_create_joint_distribution_nested(load_model_for_test, testdata, etas, abbr_ref, omega_ref):
    model_start = load_model_for_test(testdata / 'nonmem/pheno_block.mod')

    model = create_joint_distribution(model_start, etas[0], individual_estimates=None)
    model = create_joint_distribution(model, etas[1], individual_estimates=None)

    rec_abbr = ''.join(
        str(rec) for rec in model.internals.control_stream.get_records('ABBREVIATED')
    )
    assert rec_abbr == abbr_ref

    rec_pk = str(model.internals.control_stream.get_pred_pk_record())
    pk_ref = str(model_start.internals.control_stream.get_pred_pk_record())
    assert rec_pk == pk_ref

    rec_omega = ''.join(str(rec) for rec in model.internals.control_stream.get_records('OMEGA'))

    assert rec_omega == omega_ref


@pytest.mark.parametrize(
    'etas, abbr_ref, omega_ref',
    [
        (
            ['ETA_CL'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA  0.0309626 ; IVCL\n'
            '$OMEGA BLOCK(4)\n'
            '0.031128\t; IVV\n'
            '0.0055792\t; IIV_V_IIV_S1\n'
            '0.1\n'
            '0.0031045\t; IIV_V_IIV_MAT\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '0.0031128\t; IIV_V_IIV_Q\n'
            '0.0055792\t; IIV_S1_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
        (
            ['ETA_CL', 'ETA_V'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA  0.0309626 ; IVCL\n'
            '$OMEGA  0.031128 ; IVV\n'
            '$OMEGA BLOCK(3)\n'
            '0.1\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '0.0055792\t; IIV_S1_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
        (
            ['ETA_CL', 'ETA_S1'],
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_S1=ETA(2)\n'
            '$ABBR REPLACE ETA_V=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA  0.0309626 ; IVCL\n'
            '$OMEGA  0.1 ; OMEGA_3_3\n'
            '$OMEGA BLOCK(3)\n'
            '0.031128\t; IVV\n'
            '0.0031045\t; IIV_V_IIV_MAT\n'
            '0.0309626\n'
            '0.0031128\t; IIV_V_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
        (
            None,
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA  0.0309626 ; IVCL\n'
            '$OMEGA  0.031128 ; IVV\n'
            '$OMEGA  0.1\n'
            '$OMEGA  0.0309626\n'
            '$OMEGA  0.031128\n',
        ),
        (
            'ETA_CL',
            '$ABBR REPLACE ETA_CL=ETA(1)\n'
            '$ABBR REPLACE ETA_V=ETA(2)\n'
            '$ABBR REPLACE ETA_S1=ETA(3)\n'
            '$ABBR REPLACE ETA_MAT=ETA(4)\n'
            '$ABBR REPLACE ETA_Q=ETA(5)\n',
            '$OMEGA  0.0309626 ; IVCL\n'
            '$OMEGA BLOCK(4)\n'
            '0.031128\t; IVV\n'
            '0.0055792\t; IIV_V_IIV_S1\n'
            '0.1\n'
            '0.0031045\t; IIV_V_IIV_MAT\n'
            '0.0055644\t; IIV_S1_IIV_MAT\n'
            '0.0309626\n'
            '0.0031128\t; IIV_V_IIV_Q\n'
            '0.0055792\t; IIV_S1_IIV_Q\n'
            '0.0005\n'
            '0.031128\n',
        ),
    ],
)
def test_split_joint_distribution(load_model_for_test, testdata, etas, abbr_ref, omega_ref):
    model_start = load_model_for_test(testdata / 'nonmem/pheno_block.mod')
    model = create_joint_distribution(model_start)

    model = split_joint_distribution(model, etas)

    rec_abbr = ''.join(
        str(rec) for rec in model.internals.control_stream.get_records('ABBREVIATED')
    )
    assert rec_abbr == abbr_ref

    rec_pk = str(model.internals.control_stream.get_pred_pk_record())
    pk_ref = str(model_start.internals.control_stream.get_pred_pk_record())
    assert rec_pk == pk_ref

    rec_omega = ''.join(str(rec) for rec in model.internals.control_stream.get_records('OMEGA'))

    assert rec_omega == omega_ref


@pytest.mark.parametrize(
    'etas, pk_ref, omega_ref',
    [
        (
            ['ETA_CL'],
            '$PK\n'
            'CL = THETA(1)\n'
            'V=THETA(2)*EXP(ETA_V)\n'
            'S1=V+ETA_S1\n'
            'MAT=THETA(3)*EXP(ETA_MAT)\n'
            'Q=THETA(4)*EXP(ETA_Q)\n\n',
            '$OMEGA 0.031128  ; IVV\n'
            '$OMEGA 0.1\n'
            '$OMEGA BLOCK(2)\n'
            '0.0309626\n'
            '0.0005 0.031128\n',
        ),
        (
            ['ETA_CL', 'ETA_V'],
            '$PK\n'
            'CL = THETA(1)\n'
            'V = THETA(2)\n'
            'S1=V+ETA_S1\n'
            'MAT=THETA(3)*EXP(ETA_MAT)\n'
            'Q=THETA(4)*EXP(ETA_Q)\n\n',
            '$OMEGA 0.1\n' '$OMEGA BLOCK(2)\n' '0.0309626\n' '0.0005 0.031128\n',
        ),
        (
            ['ETA_CL', 'ETA_MAT'],
            '$PK\n'
            'CL = THETA(1)\n'
            'V=THETA(2)*EXP(ETA_V)\n'
            'S1=V+ETA_S1\n'
            'MAT = THETA(3)\n'
            'Q=THETA(4)*EXP(ETA_Q)\n\n',
            '$OMEGA 0.031128  ; IVV\n' '$OMEGA 0.1\n' '$OMEGA  0.031128 ; OMEGA_5_5\n',
        ),
        (
            ['ETA_MAT', 'ETA_Q'],
            '$PK\n'
            'CL=THETA(1)*EXP(ETA_CL)\n'
            'V=THETA(2)*EXP(ETA_V)\n'
            'S1=V+ETA_S1\n'
            'MAT = THETA(3)\n'
            'Q = THETA(4)\n\n',
            '$OMEGA DIAGONAL(2)\n' '0.0309626  ; IVCL\n' '0.031128  ; IVV\n' '$OMEGA 0.1\n',
        ),
        (
            None,
            '$PK\n'
            'DUMMYETA = ETA(1)\n'
            'CL = THETA(1)\n'
            'V = THETA(2)\n'
            'S1 = V\n'
            'MAT = THETA(3)\n'
            'Q = THETA(4)\n\n',
            '$OMEGA  0 FIX ; DUMMYOMEGA\n',
        ),
        (
            ['CL'],
            '$PK\n'
            'CL = THETA(1)\n'
            'V=THETA(2)*EXP(ETA_V)\n'
            'S1=V+ETA_S1\n'
            'MAT=THETA(3)*EXP(ETA_MAT)\n'
            'Q=THETA(4)*EXP(ETA_Q)\n\n',
            '$OMEGA 0.031128  ; IVV\n'
            '$OMEGA 0.1\n'
            '$OMEGA BLOCK(2)\n'
            '0.0309626\n'
            '0.0005 0.031128\n',
        ),
        (
            'ETA_CL',
            '$PK\n'
            'CL = THETA(1)\n'
            'V=THETA(2)*EXP(ETA_V)\n'
            'S1=V+ETA_S1\n'
            'MAT=THETA(3)*EXP(ETA_MAT)\n'
            'Q=THETA(4)*EXP(ETA_Q)\n\n',
            '$OMEGA 0.031128  ; IVV\n'
            '$OMEGA 0.1\n'
            '$OMEGA BLOCK(2)\n'
            '0.0309626\n'
            '0.0005 0.031128\n',
        ),
    ],
)
def test_remove_iiv(load_model_for_test, testdata, etas, pk_ref, omega_ref):
    model = load_model_for_test(testdata / 'nonmem/pheno_block.mod')
    model = remove_iiv(model, etas)

    assert str(model.internals.control_stream.get_pred_pk_record()) == pk_ref

    rec_omega = ''.join(str(rec) for rec in model.internals.control_stream.get_records('OMEGA'))

    assert rec_omega == omega_ref


def test_remove_iov(create_model_for_test, load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem/pheno_block.mod')

    model_str = model.model_code
    model_with_iov = model_str.replace(
        '$OMEGA DIAGONAL(2)\n' '0.0309626  ; IVCL\n' '0.031128  ; IVV',
        '$OMEGA BLOCK(1)\n0.1\n$OMEGA BLOCK(1) SAME\n',
    )

    model = create_model_for_test(model_with_iov)

    model = remove_iov(model)

    assert (
        str(model.internals.control_stream.get_pred_pk_record()) == '$PK\n'
        'CL = THETA(1)\n'
        'V = THETA(2)\n'
        'S1=V+ETA_S1\n'
        'MAT=THETA(3)*EXP(ETA_MAT)\n'
        'Q=THETA(4)*EXP(ETA_Q)\n\n'
    )
    rec_omega = ''.join(str(rec) for rec in model.internals.control_stream.get_records('OMEGA'))

    assert rec_omega == '$OMEGA 0.1\n' '$OMEGA BLOCK(2)\n' '0.0309626\n' '0.0005 0.031128\n'


def test_remove_iov_no_iovs(load_model_for_test, testdata):
    model = load_model_for_test(testdata / 'nonmem/pheno_block.mod')

    with pytest.warns(UserWarning):
        remove_iov(model)


def test_remove_iov_github_issues_538_and_561_1(load_model_for_test, testdata):
    m = load_model_for_test(testdata / 'nonmem' / 'models' / 'fviii6.mod')

    m = remove_iov(m)

    assert not m.random_variables.iov


def test_remove_iov_github_issues_538_and_561_2(load_model_for_test, testdata):
    m = load_model_for_test(testdata / 'nonmem' / 'models' / 'fviii6.mod')

    m = remove_iov(m, 'ETA_4')

    assert set(m.random_variables.iov.names) == {
        'ETA_12',
        'ETA_13',
        'ETA_14',
        'ETA_15',
        'ETA_16',
        'ETA_17',
        'ETA_18',
        'ETA_19',
    }


def test_remove_iov_diagonal(create_model_for_test):
    model = create_model_for_test(
        '''$PROBLEM PHENOBARB SIMPLE MODEL
$DATA pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV FA1 FA2
$SUBROUTINE ADVAN1 TRANS1
$PK
K=THETA(1)*EXP(ETA(1))+ETA(2)+ETA(3)+ETA(4)+ETA(5)+ETA(6)+ETA(7)
$ERROR
Y=F+F*EPS(1)
$THETA 0.1
$OMEGA DIAGONAL(2)
0.015
0.02
$OMEGA BLOCK(1)
0.6
$OMEGA BLOCK(1) SAME
$OMEGA 0.1
$OMEGA BLOCK(1)
0.01
$OMEGA BLOCK(1) SAME
$SIGMA 0.013241
$ESTIMATION METHOD=1 INTERACTION
'''
    )

    model = remove_iov(model)

    assert (
        '''$OMEGA DIAGONAL(2)
0.015
0.02
$OMEGA 0.1'''
        in model.model_code
    )


@pytest.mark.parametrize(
    ('distribution', 'occ', 'to_remove', 'cases', 'rest', 'abbr_ref'),
    (
        (
            'disjoint',
            'VISI',
            None,
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_2 = 0\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_3 = 0\n',
            (),
            '',
        ),
        (
            'joint',
            'VISI',
            None,
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_2 = 0\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_3 = 0\n',
            (),
            '',
        ),
        (
            'disjoint',
            'VISI',
            'ETA_IOV_1_1',
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3) IOV_2 = ETA_IOV_2_1\n'
            'IF (VISI.EQ.8) IOV_2 = ETA_IOV_2_2\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3) IOV_3 = ETA_IOV_3_1\n'
            'IF (VISI.EQ.8) IOV_3 = ETA_IOV_3_2\n',
            ('ETA_IOV_2_1', 'ETA_IOV_2_2', 'ETA_IOV_3_1', 'ETA_IOV_3_2'),
            '$ABBR REPLACE ETA_IOV_2_1=ETA(4)\n'
            '$ABBR REPLACE ETA_IOV_2_2=ETA(5)\n'
            '$ABBR REPLACE ETA_IOV_3_1=ETA(6)\n'
            '$ABBR REPLACE ETA_IOV_3_2=ETA(7)\n',
        ),
        (
            'joint',
            'VISI',
            'ETA_IOV_1_1',
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3) IOV_2 = ETA_IOV_2_1\n'
            'IF (VISI.EQ.8) IOV_2 = ETA_IOV_2_2\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3) IOV_3 = ETA_IOV_3_1\n'
            'IF (VISI.EQ.8) IOV_3 = ETA_IOV_3_2\n',
            ('ETA_IOV_2_1', 'ETA_IOV_2_2', 'ETA_IOV_3_1', 'ETA_IOV_3_2'),
            '$ABBR REPLACE ETA_IOV_2_1=ETA(4)\n'
            '$ABBR REPLACE ETA_IOV_3_1=ETA(5)\n'
            '$ABBR REPLACE ETA_IOV_2_2=ETA(6)\n'
            '$ABBR REPLACE ETA_IOV_3_2=ETA(7)\n',
        ),
        (
            'disjoint',
            'VISI',
            ['ETA_IOV_1_1', 'ETA_IOV_1_2'],
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3) IOV_2 = ETA_IOV_2_1\n'
            'IF (VISI.EQ.8) IOV_2 = ETA_IOV_2_2\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3) IOV_3 = ETA_IOV_3_1\n'
            'IF (VISI.EQ.8) IOV_3 = ETA_IOV_3_2\n',
            ('ETA_IOV_2_1', 'ETA_IOV_2_2', 'ETA_IOV_3_1', 'ETA_IOV_3_2'),
            '$ABBR REPLACE ETA_IOV_2_1=ETA(4)\n'
            '$ABBR REPLACE ETA_IOV_2_2=ETA(5)\n'
            '$ABBR REPLACE ETA_IOV_3_1=ETA(6)\n'
            '$ABBR REPLACE ETA_IOV_3_2=ETA(7)\n',
        ),
        (
            'joint',
            'VISI',
            ['ETA_IOV_1_1', 'ETA_IOV_1_2'],
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3) IOV_2 = ETA_IOV_2_1\n'
            'IF (VISI.EQ.8) IOV_2 = ETA_IOV_2_2\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3) IOV_3 = ETA_IOV_3_1\n'
            'IF (VISI.EQ.8) IOV_3 = ETA_IOV_3_2\n',
            ('ETA_IOV_2_1', 'ETA_IOV_2_2', 'ETA_IOV_3_1', 'ETA_IOV_3_2'),
            '$ABBR REPLACE ETA_IOV_2_1=ETA(4)\n'
            '$ABBR REPLACE ETA_IOV_3_1=ETA(5)\n'
            '$ABBR REPLACE ETA_IOV_2_2=ETA(6)\n'
            '$ABBR REPLACE ETA_IOV_3_2=ETA(7)\n',
        ),
        (
            'disjoint',
            'VISI',
            ['ETA_IOV_1_1', 'ETA_IOV_1_2', 'ETA_IOV_2_1'],
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_2 = 0\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3) IOV_3 = ETA_IOV_3_1\n'
            'IF (VISI.EQ.8) IOV_3 = ETA_IOV_3_2\n',
            ('ETA_IOV_3_1', 'ETA_IOV_3_2'),
            '$ABBR REPLACE ETA_IOV_3_1=ETA(4)\n' '$ABBR REPLACE ETA_IOV_3_2=ETA(5)\n',
        ),
        (
            'joint',
            'VISI',
            ['ETA_IOV_1_1', 'ETA_IOV_1_2', 'ETA_IOV_2_1'],
            'IOV_1 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_1 = 0\n'
            'IOV_2 = 0\n'
            'IF (VISI.EQ.3.OR.VISI.EQ.8) IOV_2 = 0\n'
            'IOV_3 = 0\n'
            'IF (VISI.EQ.3) IOV_3 = ETA_IOV_3_1\n'
            'IF (VISI.EQ.8) IOV_3 = ETA_IOV_3_2\n',
            ('ETA_IOV_3_1', 'ETA_IOV_3_2'),
            '$ABBR REPLACE ETA_IOV_3_1=ETA(4)\n' '$ABBR REPLACE ETA_IOV_3_2=ETA(5)\n',
        ),
    ),
    ids=repr,
)
def test_remove_iov_with_options(
    tmp_path, load_model_for_test, testdata, distribution, occ, to_remove, cases, rest, abbr_ref
):
    with chdir(tmp_path):
        shutil.copy2(testdata / 'nonmem' / 'models' / 'mox2.mod', tmp_path)
        shutil.copy2(testdata / 'nonmem' / 'models' / 'mox_simulated_normal.csv', tmp_path)
        model = load_model_for_test('mox2.mod')
        model = model.replace(
            datainfo=model.datainfo.replace(path=tmp_path / 'mox_simulated_normal.csv')
        )

        start_model = add_iov(model, occ=occ, distribution=distribution)

        model_with_some_iovs_removed = remove_iov(start_model, to_remove=to_remove)

        assert cases in model_with_some_iovs_removed.model_code
        assert set(model_with_some_iovs_removed.random_variables.iov.names) == set(rest)

        rec_abbr = ''.join(
            str(rec)
            for rec in model_with_some_iovs_removed.internals.control_stream.get_records(
                'ABBREVIATED'
            )
        )
        assert rec_abbr == abbr_ref


@pytest.mark.parametrize(
    'etas_file, force, file_exists',
    [('', False, False), ('', True, True), ('$ETAS FILE=run1.phi', False, True)],
)
def test_update_inits(load_model_for_test, testdata, etas_file, force, file_exists, tmp_path):
    shutil.copy(testdata / 'nonmem/pheno.mod', tmp_path / 'run1.mod')
    shutil.copy(testdata / 'nonmem/pheno.phi', tmp_path / 'run1.phi')
    shutil.copy(testdata / 'nonmem/pheno.ext', tmp_path / 'run1.ext')
    shutil.copy(testdata / 'nonmem/pheno.dta', tmp_path / 'pheno.dta')

    with chdir(tmp_path):
        with open('run1.mod', 'a') as f:
            f.write(etas_file)

        model = load_model_for_test('run1.mod')
        res = read_modelfit_results('run1.mod')
        model = update_initial_individual_estimates(model, res.individual_estimates, force=force)
        model = model.write_files()

        assert ('$ETAS FILE=run1_input.phi' in model.model_code) is file_exists
        assert (os.path.isfile('run1_input.phi')) is file_exists


def test_update_inits_move_est(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    res = read_modelfit_results(pheno_path)

    model = create_joint_distribution(model, individual_estimates=res.individual_estimates)
    model = add_iiv(model, 'S1', 'add')

    param_est = res.parameter_estimates.copy()
    param_est['IIV_CL_IIV_V'] = 0.0285  # Correlation > 0.99
    param_est['IIV_S1'] = 0.0005

    model = update_inits(model, param_est, move_est_close_to_bounds=True)

    assert model.parameters['IVCL'].init == param_est['IVCL']
    assert model.parameters['IIV_S1'].init == 0.01
    assert round(model.parameters['IIV_CL_IIV_V'].init, 6) == 0.025757


def test_update_inits_zero_fix(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    d = {name: 0 for name in model.random_variables.iiv.parameter_names}
    model = fix_parameters_to(model, d)
    res = read_modelfit_results(pheno_path)
    param_est = res.parameter_estimates.drop(index=['IVCL'])
    model = update_inits(model, param_est)
    assert model.parameters['IVCL'].init == 0
    assert model.parameters['IVCL'].fix

    model = load_model_for_test(pheno_path)
    d = {name: 0 for name in model.random_variables.iiv.parameter_names}
    model = fix_parameters_to(model, d)
    param_est = res.parameter_estimates.drop(index=['IVCL'])
    model = update_inits(model, param_est, move_est_close_to_bounds=True)
    assert model.parameters['IVCL'].init == 0
    assert model.parameters['IVCL'].fix


def test_update_inits_no_res(load_model_for_test, testdata, tmp_path):
    shutil.copy(testdata / 'nonmem/pheno.mod', tmp_path / 'run1.mod')
    shutil.copy(testdata / 'nonmem/pheno.dta', tmp_path / 'pheno.dta')

    with chdir(tmp_path):
        shutil.copy(testdata / 'nonmem/pheno.ext', tmp_path / 'run1.ext')
        shutil.copy(testdata / 'nonmem/pheno.lst', tmp_path / 'run1.lst')

        model = load_model_for_test('run1.mod')
        res = read_modelfit_results('run1.mod')

        modelfit_results = replace(
            res,
            parameter_estimates=pd.Series(
                np.nan, name='estimates', index=list(model.parameters.nonfixed.inits.keys())
            ),
        )

        with pytest.raises(ValueError):
            update_inits(model, modelfit_results.parameter_estimates)


def test_nested_update_source(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    res = read_modelfit_results(pheno_path)

    model = create_joint_distribution(model, individual_estimates=res.individual_estimates)
    model = model.update_source()

    assert 'IIV_CL_IIV_V' in model.model_code

    model = load_model_for_test(pheno_path)

    model = remove_iiv(model, 'CL')

    model = model.update_source()

    assert '0.031128' in model.model_code
    assert '0.0309626' not in model.model_code

    model = load_model_for_test(pheno_path)

    model = remove_iiv(model, 'V')

    model = model.update_source()

    assert '0.0309626' in model.model_code
    assert '0.031128' not in model.model_code


@pytest.mark.parametrize(
    'path, occ, etas, eta_names, pk_start_ref, pk_end_ref, omega_ref, distribution',
    [
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['ETA_1'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'disjoint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            'ETA_1',
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'disjoint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            'ETA_1',
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'joint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['CL', 'ETA_1'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'joint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['ETA_1', 'CL'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'joint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            [['CL', 'ETA_1']],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'explicit',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            [['ETA_1', 'CL']],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'explicit',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            None,
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'IOV_2 = 0\n'
            'IF (FA1.EQ.0) IOV_2 = ETA_IOV_2_1\n'
            'IF (FA1.EQ.1) IOV_2 = ETA_IOV_2_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n'
            'ETAI2 = IOV_2 + ETA(2)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V = TVV*EXP(ETAI2)\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n'
            '0.00309626 ; OMEGA_IOV_1\n'
            '$OMEGA  BLOCK(1) SAME\n'
            '$OMEGA  BLOCK(1)\n'
            '0.0031128 ; OMEGA_IOV_2\n'
            '$OMEGA  BLOCK(1) SAME\n',
            'disjoint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            None,
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'IOV_2 = 0\n'
            'IF (FA1.EQ.0) IOV_2 = ETA_IOV_2_1\n'
            'IF (FA1.EQ.1) IOV_2 = ETA_IOV_2_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n'
            'ETAI2 = IOV_2 + ETA(2)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V = TVV*EXP(ETAI2)\n' 'S1=V\n',
            '$OMEGA BLOCK(2)\n'
            '0.00309626\t; OMEGA_IOV_1\n'
            '0.001\t; OMEGA_IOV_1_2\n'
            '0.0031128\t; OMEGA_IOV_2\n'
            '$OMEGA BLOCK(2) SAME\n',
            'joint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            None,
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'IOV_2 = 0\n'
            'IF (FA1.EQ.0) IOV_2 = ETA_IOV_2_1\n'
            'IF (FA1.EQ.1) IOV_2 = ETA_IOV_2_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n'
            'ETAI2 = IOV_2 + ETA(2)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V = TVV*EXP(ETAI2)\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n'
            '0.00309626 ; OMEGA_IOV_1\n'
            '$OMEGA  BLOCK(1) SAME\n'
            '$OMEGA  BLOCK(1)\n'
            '0.0031128 ; OMEGA_IOV_2\n'
            '$OMEGA  BLOCK(1) SAME\n',
            'same-as-iiv',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['ETA_2'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(2)\n',
            'CL=TVCL*EXP(ETA(1))\n' 'V = TVV*EXP(ETAI1)\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.0031128 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'same-as-iiv',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['CL'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'disjoint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['CL', 'ETA_2'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'IOV_2 = 0\n'
            'IF (FA1.EQ.0) IOV_2 = ETA_IOV_2_1\n'
            'IF (FA1.EQ.1) IOV_2 = ETA_IOV_2_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n'
            'ETAI2 = IOV_2 + ETA(2)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V = TVV*EXP(ETAI2)\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n'
            '0.00309626 ; OMEGA_IOV_1\n'
            '$OMEGA  BLOCK(1) SAME\n'
            '$OMEGA  BLOCK(1)\n'
            '0.0031128 ; OMEGA_IOV_2\n'
            '$OMEGA  BLOCK(1) SAME\n',
            'disjoint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['CL', 'ETA_2'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'IOV_2 = 0\n'
            'IF (FA1.EQ.0) IOV_2 = ETA_IOV_2_1\n'
            'IF (FA1.EQ.1) IOV_2 = ETA_IOV_2_2\n'
            'ETAI1 = IOV_1 + ETA(1)\n'
            'ETAI2 = IOV_2 + ETA(2)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V = TVV*EXP(ETAI2)\n' 'S1=V\n',
            '$OMEGA BLOCK(2)\n'
            '0.00309626\t; OMEGA_IOV_1\n'
            '0.001\t; OMEGA_IOV_1_2\n'
            '0.0031128\t; OMEGA_IOV_2\n'
            '$OMEGA BLOCK(2) SAME\n',
            'joint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['ETA_1'],
            ['ETA_3', 'ETA_4'],
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA(3)\n'
            'IF (FA1.EQ.1) IOV_1 = ETA(4)\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'disjoint',
        ),
        (
            'nonmem/pheno_real.mod',
            'FA1',
            ['ETA_1'],
            ['ETA_3', 'ETA_4'],
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA(3)\n'
            'IF (FA1.EQ.1) IOV_1 = ETA(4)\n'
            'ETAI1 = IOV_1 + ETA(1)\n',
            'CL = TVCL*EXP(ETAI1)\n' 'V=TVV*EXP(ETA(2))\n' 'S1=V\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'joint',
        ),
        (
            'nonmem/pheno_block.mod',
            'FA1',
            ['ETA_CL'],
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'ETAI1 = IOV_1 + ETA_CL\n',
            'CL = THETA(1)*EXP(ETAI1)\n'
            'V=THETA(2)*EXP(ETA_V)\n'
            'S1=V+ETA_S1\n'
            'MAT=THETA(3)*EXP(ETA_MAT)\n'
            'Q=THETA(4)*EXP(ETA_Q)\n',
            '$OMEGA  BLOCK(1)\n' '0.00309626 ; OMEGA_IOV_1\n' '$OMEGA  BLOCK(1) SAME\n',
            'disjoint',
        ),
        (
            'nonmem/pheno_block.mod',
            'FA1',
            None,
            None,
            'IOV_1 = 0\n'
            'IF (FA1.EQ.0) IOV_1 = ETA_IOV_1_1\n'
            'IF (FA1.EQ.1) IOV_1 = ETA_IOV_1_2\n'
            'IOV_2 = 0\n'
            'IF (FA1.EQ.0) IOV_2 = ETA_IOV_2_1\n'
            'IF (FA1.EQ.1) IOV_2 = ETA_IOV_2_2\n'
            'IOV_3 = 0\n'
            'IF (FA1.EQ.0) IOV_3 = ETA_IOV_3_1\n'
            'IF (FA1.EQ.1) IOV_3 = ETA_IOV_3_2\n'
            'IOV_4 = 0\n'
            'IF (FA1.EQ.0) IOV_4 = ETA_IOV_4_1\n'
            'IF (FA1.EQ.1) IOV_4 = ETA_IOV_4_2\n'
            'IOV_5 = 0\n'
            'IF (FA1.EQ.0) IOV_5 = ETA_IOV_5_1\n'
            'IF (FA1.EQ.1) IOV_5 = ETA_IOV_5_2\n'
            'ETAI1 = IOV_1 + ETA_CL\n'
            'ETAI2 = IOV_2 + ETA_V\n'
            'ETAI3 = IOV_3 + ETA_S1\n'
            'ETAI4 = IOV_4 + ETA_MAT\n'
            'ETAI5 = IOV_5 + ETA_Q\n',
            'CL = THETA(1)*EXP(ETAI1)\n'
            'V = THETA(2)*EXP(ETAI2)\n'
            'S1 = ETAI3 + V\n'
            'MAT = THETA(3)*EXP(ETAI4)\n'
            'Q = THETA(4)*EXP(ETAI5)\n',
            '$OMEGA  BLOCK(1)\n'
            '0.00309626 ; OMEGA_IOV_1\n'
            '$OMEGA  BLOCK(1) SAME\n'
            '$OMEGA  BLOCK(1)\n'
            '0.0031128 ; OMEGA_IOV_2\n'
            '$OMEGA  BLOCK(1) SAME\n'
            '$OMEGA  BLOCK(1)\n'
            '0.010000000000000002 ; OMEGA_IOV_3\n'
            '$OMEGA  BLOCK(1) SAME\n'
            '$OMEGA BLOCK(2)\n'
            '0.00309626\t; OMEGA_IOV_4\n'
            '5E-05\t; OMEGA_IOV_4_5\n'
            '0.0031128\t; OMEGA_IOV_5\n'
            '$OMEGA BLOCK(2) SAME\n',
            'same-as-iiv',
        ),
    ],
)
def test_add_iov(
    load_model_for_test,
    testdata,
    path,
    occ,
    etas,
    eta_names,
    pk_start_ref,
    pk_end_ref,
    omega_ref,
    distribution,
):
    model = load_model_for_test(testdata / path)
    model = add_iov(model, occ, etas, eta_names, distribution=distribution)

    model_etas = set(model.random_variables.etas.names)
    assert eta_names is None or model_etas.issuperset(eta_names)

    pk_rec = str(model.internals.control_stream.get_pred_pk_record())

    expected_pk_rec_start = f'$PK\n{pk_start_ref}'
    expected_pk_rec_end = f'{pk_end_ref}\n'

    assert pk_rec[: len(expected_pk_rec_start)] == expected_pk_rec_start
    assert pk_rec[-len(expected_pk_rec_end) :] == expected_pk_rec_end

    rec_omega = ''.join(str(rec) for rec in model.internals.control_stream.get_records('OMEGA'))

    assert rec_omega[-len(omega_ref) :] == omega_ref

    if eta_names:
        assert len(model.internals.control_stream.get_records('ABBREVIATED')) == 0
    else:
        assert len(model.internals.control_stream.get_records('ABBREVIATED')) > 0


def test_add_iov_compose(load_model_for_test, pheno_path):
    model1 = load_model_for_test(pheno_path)
    model1 = add_iov(model1, 'FA1', ['ETA_1', 'ETA_2'])

    model2 = load_model_for_test(pheno_path)
    model2 = add_iov(model2, 'FA1', 'ETA_1')
    model2 = add_iov(model2, 'FA1', 'ETA_2')

    assert set(model1.random_variables.etas.names) == set(model2.random_variables.etas.names)
    # FIXME find better way to assert models are equivalent
    assert sorted(str(model1.internals.control_stream.get_pred_pk_record()).split('\n')) == sorted(
        str(model2.internals.control_stream.get_pred_pk_record()).split('\n')
    )

    rec_omega_1 = list(str(rec) for rec in model1.internals.control_stream.get_records('OMEGA'))
    rec_omega_2 = list(str(rec) for rec in model2.internals.control_stream.get_records('OMEGA'))

    assert rec_omega_1 == rec_omega_2


def test_add_iov_only_one_level(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    df = model.dataset.copy()
    df['FA1'] = 1
    model = model.replace(dataset=df)

    with pytest.raises(ValueError, match='Only one value in FA1 column.'):
        add_iov(model, 'FA1', ['ETA_1'])


@pytest.mark.parametrize(
    'occ, params, new_eta_names, distribution, error, message',
    (
        (
            'FA1',
            ['ETA_1', 'CL'],
            None,
            'disjoint',
            ValueError,
            'ETA_1 was given twice.',
        ),
        (
            'FA1',
            ['CL', 'ETA_1'],
            None,
            'disjoint',
            ValueError,
            'ETA_1 was given twice.',
        ),
        (
            'FA1',
            [['ETA_1'], ['CL']],
            None,
            'explicit',
            ValueError,
            'ETA_1 was given twice.',
        ),
        (
            'FA1',
            [['CL'], ['ETA_1']],
            None,
            'explicit',
            ValueError,
            'ETA_1 was given twice.',
        ),
        (
            'FA1',
            ['ETA_1'],
            None,
            'abracadabra',
            ValueError,
            '"abracadabra" is not a valid value for distribution',
        ),
        (
            'FA1',
            ['ETA_1'],
            None,
            'explicit',
            ValueError,
            'distribution == "explicit" requires parameters to be given as lists of lists',
        ),
        (
            'FA1',
            [['ETA_2'], 'ETA_1'],
            None,
            'explicit',
            ValueError,
            'distribution == "explicit" requires parameters to be given as lists of lists',
        ),
        (
            'FA1',
            [['ETA_1']],
            None,
            'joint',
            ValueError,
            'distribution != "explicit" requires parameters to be given as lists of strings',
        ),
        (
            'FA1',
            [['ETA_1'], [2, 'ETA_2']],
            None,
            'explicit',
            ValueError,
            'not all parameters are string',
        ),
        (
            'FA1',
            [['ETA_1', 'ETA_2']],
            ['A', 'B', 'C', 'D', 'E'],
            'explicit',
            ValueError,
            'Number of given eta names is incorrect, need 4 names.',
        ),
    ),
)
def test_add_iov_raises(
    load_model_for_test, pheno_path, occ, params, new_eta_names, distribution, error, message
):
    model = load_model_for_test(pheno_path)
    with pytest.raises(error, match=re.escape(message)):
        add_iov(model, occ, params, eta_names=new_eta_names, distribution=distribution)


def test_set_ode_solver(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    assert model.estimation_steps[0].solver is None
    assert 'ADVAN1' in model.model_code
    assert '$MODEL' not in model.model_code

    model = load_model_for_test(pheno_path)
    model = set_michaelis_menten_elimination(model)
    model = set_ode_solver(model, 'LSODA')
    assert model.estimation_steps[0].solver == 'LSODA'
    assert 'ADVAN13' in model.model_code
    assert '$MODEL' in model.model_code

    model = load_model_for_test(pheno_path)
    model = set_zero_order_elimination(model)
    assert 'ADVAN13' in model.model_code
    assert '$MODEL' in model.model_code
    model = set_ode_solver(model, 'LSODA')
    model = set_michaelis_menten_elimination(model)
    assert model.estimation_steps[0].solver == 'LSODA'
    assert 'ADVAN13' in model.model_code
    assert '$MODEL' in model.model_code
    model = set_ode_solver(model, 'DVERK')
    assert model.estimation_steps[0].solver == 'DVERK'
    assert 'ADVAN6' in model.model_code
    assert '$MODEL' in model.model_code


def test_add_pk_iiv_1(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    model = set_zero_order_elimination(model)
    model = add_pk_iiv(model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA_1', 'ETA_2', 'ETA_KM'}
    model = add_peripheral_compartment(model)
    model = add_pk_iiv(model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA_1', 'ETA_2', 'ETA_KM', 'ETA_VP1', 'ETA_QP1'}


def test_add_pk_iiv_2(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    model = set_zero_order_elimination(model)
    model = add_peripheral_compartment(model)
    model = add_pk_iiv(model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA_1', 'ETA_2', 'ETA_KM', 'ETA_VP1', 'ETA_QP1'}


def test_add_pk_iiv_nested_params(load_model_for_test, pheno_path):
    model = load_model_for_test(pheno_path)
    model = set_transit_compartments(model, 3)
    model = add_pk_iiv(model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA_1', 'ETA_2', 'ETA_MDT'}

    model = load_model_for_test(pheno_path)
    model = set_first_order_absorption(model)
    model = add_pk_iiv(model)
    iivs = set(model.random_variables.iiv.names)
    assert iivs == {'ETA_1', 'ETA_2', 'ETA_MAT'}

    model = load_model_for_test(pheno_path)
    model = set_transit_compartments(model, 3)
    model = add_pk_iiv(model, initial_estimate=0.01)
    assert model.parameters['IIV_MDT'].init == 0.01


def test_mm_then_periph(pheno):
    model = set_michaelis_menten_elimination(pheno)
    model = add_peripheral_compartment(model)
    odes = model.statements.ode_system
    central = odes.central_compartment
    periph = odes.peripheral_compartments[0]
    assert odes.get_flow(central, periph) == sympy.Symbol('QP1') / sympy.Symbol('V')
    assert odes.get_flow(periph, central) == sympy.Symbol('QP1') / sympy.Symbol('VP1')
    model = add_peripheral_compartment(model)
    odes = model.statements.ode_system
    newperiph = odes.peripheral_compartments[1]
    central = odes.central_compartment
    assert odes.get_flow(central, newperiph) == sympy.Symbol('QP2') / sympy.Symbol('V')
    assert odes.get_flow(newperiph, central) == sympy.Symbol('QP2') / sympy.Symbol('VP2')


def _symbols(names: Iterable[str]):
    return list(map(sympy.Symbol, names))


def test_find_clearance_parameters(pheno):
    cl_origin = find_clearance_parameters(pheno)
    assert cl_origin == _symbols(['CL'])

    model = add_peripheral_compartment(pheno)
    cl_p1 = find_clearance_parameters(model)
    assert cl_p1 == _symbols(['CL', 'QP1'])

    model = add_peripheral_compartment(model)
    cl_p2 = find_clearance_parameters(model)
    assert cl_p2 == _symbols(['CL', 'QP1', 'QP2'])


def test_find_clearance_parameters_github_issues_1053_and_1062(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    model = set_michaelis_menten_elimination(model)
    assert find_clearance_parameters(model) == _symbols(['CLMM'])


def test_find_clearance_parameters_github_issues_1044_and_1053(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    model = set_transit_compartments(model, 10)
    assert find_clearance_parameters(model) == _symbols(['CL'])


def test_find_clearance_parameters_github_issues_1053_and_1062_bis(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    model = add_peripheral_compartment(model)
    model = add_peripheral_compartment(model)
    model = set_michaelis_menten_elimination(model)
    assert find_clearance_parameters(model) == _symbols(['CLMM', 'QP1', 'QP2'])


def test_find_volume_parameters(pheno):
    v_origin = find_volume_parameters(pheno)
    assert v_origin == _symbols(['V'])

    model = add_peripheral_compartment(pheno)
    v_p1 = find_volume_parameters(model)
    assert v_p1 == _symbols(['V1', 'VP1'])

    model = add_peripheral_compartment(model)
    v_p2 = find_volume_parameters(model)
    assert v_p2 == _symbols(['V1', 'VP1', 'VP2'])


def test_find_volume_parameters_github_issues_1053_and_1062(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    model = set_michaelis_menten_elimination(model)
    assert find_volume_parameters(model) == _symbols(['V'])


def test_find_volume_parameters_github_issues_1044_and_1053(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    model = set_transit_compartments(model, 10)
    assert find_volume_parameters(model) == _symbols(['V'])


def test_find_volume_parameters_github_issues_1053_and_1062_bis(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    model = add_peripheral_compartment(model)
    model = add_peripheral_compartment(model)
    model = set_michaelis_menten_elimination(model)
    assert find_volume_parameters(model) == _symbols(['V1', 'VP1', 'VP2'])


def test_has_odes(load_example_model_for_test, datadir, load_model_for_test):
    model = load_example_model_for_test('pheno')
    assert has_odes(model)
    path = datadir / 'minimal.mod'
    model = load_model_for_test(path)
    assert not has_odes(model)


def test_has_linear_odes(load_example_model_for_test, datadir, load_model_for_test):
    model = load_example_model_for_test('pheno')
    assert has_linear_odes(model)
    model = set_michaelis_menten_elimination(model)
    assert not has_linear_odes(model)
    path = datadir / 'minimal.mod'
    model = load_model_for_test(path)
    assert not has_linear_odes(model)


def test_has_linear_odes_with_real_eigenvalues(
    load_example_model_for_test, datadir, load_model_for_test
):
    model = load_example_model_for_test('pheno')
    assert has_linear_odes_with_real_eigenvalues(model)
    model = set_michaelis_menten_elimination(model)
    assert not has_linear_odes_with_real_eigenvalues(model)
    path = datadir / 'minimal.mod'
    model = load_model_for_test(path)
    assert not has_linear_odes_with_real_eigenvalues(model)


def test_get_initial_conditions(load_example_model_for_test, load_model_for_test, datadir):
    model = load_example_model_for_test('pheno')
    assert get_initial_conditions(model) == {sympy.Function('A_CENTRAL')(0): sympy.Integer(0)}
    ic = Assignment(sympy.Function('A_CENTRAL')(0), sympy.Integer(23))
    statements = (
        model.statements.before_odes
        + ic
        + model.statements.ode_system
        + model.statements.after_odes
    )
    mod2 = model.replace(statements=statements)
    assert get_initial_conditions(mod2) == {sympy.Function('A_CENTRAL')(0): sympy.Integer(23)}
    path = datadir / 'minimal.mod'
    model = load_model_for_test(path)
    assert get_initial_conditions(model) == {}


def test_set_intial_conditions(load_example_model_for_test):
    model = load_example_model_for_test("pheno")
    model = set_initial_condition(model, "CENTRAL", 10)
    assert len(model.statements) == 16
    ic = Assignment(sympy.Function('A_CENTRAL')(0), sympy.Integer(10))
    assert model.statements.before_odes[-1] == ic
    assert get_initial_conditions(model) == {sympy.Function('A_CENTRAL')(0): sympy.Integer(10)}
    model = set_initial_condition(model, "CENTRAL", 23)
    assert len(model.statements) == 16
    ic = Assignment(sympy.Function('A_CENTRAL')(0), sympy.Integer(23))
    assert model.statements.before_odes[-1] == ic
    model = set_initial_condition(model, "CENTRAL", 0)
    assert len(model.statements) == 15


def test_get_zero_order_inputs(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    zo = get_zero_order_inputs(model)
    assert zo == sympy.Matrix([[0]])


def test_set_zero_order_input(load_example_model_for_test):
    model = load_example_model_for_test('pheno')
    model = set_zero_order_input(model, "CENTRAL", 10)
    zo = get_zero_order_inputs(model)
    assert zo == sympy.Matrix([[10]])
