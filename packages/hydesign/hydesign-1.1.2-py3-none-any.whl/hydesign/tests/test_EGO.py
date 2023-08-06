# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 14:43:04 2022

@author: mikf
"""
import numpy as np
# import matplotlib.pyplot as plt
from hydesign.EGO_surrogate_based_optimization import (
    get_sm, LCB, EI, KStd, KB, eval_sm, opt_sm,
    get_candiate_points)
from hydesign.tests.test_files import tfp
import pandas as pd
import pytest
from smt.applications.mixed_integer import (
    MixedIntegerContext,
    FLOAT,
    # ENUM,
    INT,
)
import pickle

def test_get_sm():
    nt = 100
    data = pd.read_csv(tfp + 'test_data.csv', sep=';',nrows=nt)
    x = data[[f'x{int(i + 1)}' for i in range(9)]].values
    y = data['y'].values.reshape(nt, 1)
    return get_sm(x, y)

def save_sm():
    sm = test_get_sm()
    with open(tfp + 'sm.pkl','wb') as f:
         pickle.dump(sm, f)

def load_sm():
    with open(tfp + 'sm.pkl','rb') as f:
        sm = pickle.load(f)
    return sm

sm = load_sm()
fmins = [1, 10, 50, 500, 10000]
point = np.array([10, 1, 0, 142, 2, 10, 0, 0, 1]).reshape((1, 9))

def get_data2(fmin):
    data2 = pd.read_csv(tfp + 'sm_pred_test_data.csv', sep=';').values
    n = fmins.index(fmin)
    a = data2[n * 5: n * 5 + 5, :9]
    b = data2[n * 5: n * 5 + 5, 9]
    return a, b

def generate_data2():
    new_data = np.zeros((25, 10))
    for n, fmin in enumerate(fmins):
        a, b = eval_sm(sm, mixint, npred=5, fmin=fmin)
        new_data[n*5:n*5+5,:9] = a
        new_data[n*5:n*5+5,9] = b.ravel()
    df = pd.DataFrame(new_data, columns=[f'x{i + 1}' for i in range(9)] + ['y'])
    df.to_csv(tfp + 'sm_pred_test_data.csv', sep=';', index=False)

def test_LCB():
    res = LCB(sm, point)
    np.testing.assert_allclose(res, np.array([[-52174.21032693]]))

def test_EI():
    res = EI(sm, point)
    np.testing.assert_allclose(res, np.array([[-5176.64021695]]))

def test_KStd():
    res = KStd(sm, point)
    np.testing.assert_allclose(res, np.array([[19795.76331878]]))

def test_KB():
    res = KB(sm, point)
    np.testing.assert_allclose(res, np.array([[7213.07962942]]))

xtypes = [INT, FLOAT, FLOAT, INT, FLOAT,
          INT, FLOAT, FLOAT, FLOAT]
xlimits = np.array([[4, 22], [0.1, 4.5], [-0.65, 1.75], [8, 270], [1, 4.9],
    [-22, 43], [-10, 9], [-10, 9], [1.1, 1.34]])   
mixint = MixedIntegerContext(xtypes, xlimits)

@pytest.mark.parametrize('fmin', fmins)
def test_eval_sm(fmin):
    a, b = eval_sm(sm, mixint, npred=5, fmin=fmin)
    a_ref, b_ref = get_data2(fmin)
    np.testing.assert_allclose(a, a_ref)
    np.testing.assert_allclose(b.ravel(), b_ref)

def test_get_candidate_points():
    xpred, ypred_LB = eval_sm(sm, mixint, npred=5, fmin=10)
    xnew = get_candiate_points(
    xpred, ypred_LB, 
    n_clusters = 1, 
    quantile = 1e-4) 
    np.testing.assert_allclose(xnew, np.array([[ 1.700e+01,  5.400e-01,  7.000e-02,  2.440e+02,  4.510e+00,
                                                3.600e+01,  7.100e+00, -8.100e+00,  1.268e+00]]))

    
