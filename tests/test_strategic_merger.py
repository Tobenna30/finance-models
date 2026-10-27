"""EQT / Range: independent controls, cached workbook parity and input changes."""
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import pytest
from openpyxl import load_workbook

P = 'projects.05-strategic-merger.eqt_range.'
engine = importlib.import_module(P+'engine')
assumptions = importlib.import_module(P+'assumptions')
builder = importlib.import_module(P+'build_excel')

def test_history_and_attributable_income():
    r = engine.calculate()
    assert r['ltm']['e_adj'] == pytest.approx(2601.217)
    assert r['ltm']['e_gaap'] == pytest.approx(2711.615)
    assert r['ltm']['r_adj'] == pytest.approx(875.606)
    assert r['ltm']['r_gaap'] == pytest.approx(860.347)
    assert r['ltm']['r_sbc'] == pytest.approx(47.607)
    assert r['r_normal'] == pytest.approx(875.606 - 47.607*.75)

def test_share_exchange_and_dilution_algebra():
    r=engine.calculate()
    assert r['new_shares'] == pytest.approx(236.210*.987)
    assert r['total_shares'] == pytest.approx(629.049+236.210*.987)
    assert r['target_ownership'] == pytest.approx(.270404706,abs=.00001)
    expected = (2601.217+875.606-47.607*.75+(325-100)*.75)/(629.049+236.210*.987)/(2601.217/629.049)-1
    assert r['years'][2]['recurring_accretion'] == pytest.approx(expected)

def test_eps_break_even_is_zero():
    r=engine.calculate()
    z=engine.calculate({'synergy':r['eps_breakeven_synergy']})
    assert z['years'][2]['recurring_accretion'] == pytest.approx(0,abs=1e-12)
    assert engine.calculate({'synergy':r['eps_breakeven_synergy']-1})['years'][2]['recurring_accretion'] < 0

def test_value_break_even_and_premium_in_stock():
    r=engine.calculate()
    assert r['value_surplus'] < 0
    assert engine.calculate({'synergy':r['value_breakeven_synergy']})['value_surplus'] == pytest.approx(0,abs=1e-9)
    assert engine.calculate({'ratio':r['max_value_ratio']})['value_surplus'] == pytest.approx(0,abs=1e-8)
    assert r['finite_surplus'] < r['value_surplus']
    # Independent 100-year discounted cash calculation approximates the perpetuity.
    pv=sum((325*(.5 if y==1 else 1)*.75-300*(.6 if y==1 else .4 if y==2 else 0)*.75)/1.1**y for y in range(1,301))-50
    assert r['net_synergy_pv'] == pytest.approx(pv,abs=1e-8)

def test_costs_cash_and_accounting_bridge():
    r=engine.calculate(); a=assumptions.values()
    assert sum(y['integration'] for y in r['years']) == a['integration']
    assert sum(y['fees'] for y in r['years']) == a['fees']
    for y in r['years']:
        assert y['inclusive_ni'] == pytest.approx(y['recurring_ni']-y['integration']*.75-y['fees'])
        assert y['inclusive_eps']*r['total_shares'] == pytest.approx(y['inclusive_ni'])
    assert r['years'][0]['inclusive_accretion'] < r['years'][2]['recurring_accretion']
    assert r['years'][2]['company_accretion'] > r['years'][2]['recurring_accretion']

def test_scenarios_and_assumption_sensitivity():
    cases=[engine.calculate({'case':i}) for i in (1,2,3)]
    assert cases[0]['years'][2]['recurring_accretion'] < cases[1]['years'][2]['recurring_accretion'] < cases[2]['years'][2]['recurring_accretion']
    assert engine.calculate({'stepup':0})['years'][2]['recurring_accretion'] > cases[1]['years'][2]['recurring_accretion']
    assert engine.calculate({'ratio':1.1})['years'][2]['recurring_accretion'] < cases[1]['years'][2]['recurring_accretion']
    assert engine.calculate({'discount':.12})['value_surplus'] < cases[1]['value_surplus']

def test_invalid_inputs_visible():
    for bad in ({'case':4},{'eqt_shares':0},{'life':0},{'tax':1},{'ratio':-1},{'cost1':1.2}):
        with pytest.raises(ValueError):engine.calculate(bad)

def assert_workbook(wb, result):
    for cell,key in {'D6':'offer_price','D7':'equity_consideration','D8':'premium_pct','D9':'premium','D11':'gross_synergy_pv','D12':'cost_pv','D13':'net_synergy_pv','D14':'value_surplus','D15':'value_breakeven_synergy','D16':'max_value_ratio','D18':'finite_surplus'}.items():
        assert wb['Value'][cell].value == pytest.approx(result[key],abs=1e-8)
    for cell,key in {'D6':('ltm','e_adj'),'D9':('r_normal',),'D11':('new_shares',),'D12':('total_shares',),'D13':('target_ownership',),'D14':('eqt_eps',),'D15':('annual_da',),'D16':('no_synergy_accretion',),'D17':('eps_breakeven_synergy',)}.items():
        expected=result
        for k in key:expected=expected[k]
        assert wb['Merger'][cell].value == pytest.approx(expected,abs=1e-9)
    for col,y in zip('DEF',result['years']):
        for row,key in {22:'synergy',23:'integration',24:'fees',25:'recurring_ni',26:'recurring_eps',27:'recurring_accretion',28:'inclusive_ni',29:'inclusive_eps',30:'inclusive_accretion',31:'company_eps',32:'company_accretion',33:'gaap_lens_eps',34:'gaap_lens_accretion'}.items():
            assert wb['Merger'][f'{col}{row}'].value == pytest.approx(y[key],abs=1e-8)

def test_cached_workbook_engine_parity():
    wb=load_workbook(builder.OUT,data_only=True)
    assert_workbook(wb,engine.calculate())
    assert wb['Value']['D21'].value == pytest.approx(0,abs=1e-8)
    assert wb['Value']['D23'].value == pytest.approx(0,abs=1e-8)
    for sheet in wb:
        for row in sheet:
            assert all(c.data_type!='e' for c in row)
    # Base sensitivity at announced ratio, USD325m must tie to the live build.
    assert wb['Sensitivity']['G8'].value == pytest.approx(wb['Merger']['F27'].value)

def test_live_formulas_and_source_register():
    wb=load_workbook(builder.OUT,data_only=False)
    for row in range(21,35):
        assert all(wb['Merger'][f'{c}{row}'].data_type=='f' for c in 'DEF')
    assert 'CHOOSE' in wb['Inputs'][f'D{builder.ACTIVE}'].value
    assert len(wb['Inputs'].data_validations.dataValidation)==1
    for key, row in assumptions.INPUTS.items():
        assert row[2] in ('S','A','D') and row[4]
        assert wb['Inputs'][f'D{builder.I[key]}'].value==row[1]
    saved=json.loads((assumptions.ROOT/'outputs/results.json').read_text())
    assert saved['base']['value_surplus'] == pytest.approx(engine.calculate()['value_surplus'])

@pytest.mark.parametrize('overrides',[{'case':1},{'case':3},{'ratio':1.05,'synergy':250,'stepup':0}])
def test_native_recalculation_after_edit(overrides):
    soffice=os.environ.get('SOFFICE') or shutil.which('soffice')
    if not soffice:pytest.skip('LibreOffice unavailable; cached parity still required')
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp); out=tmp/'out';out.mkdir()
        wb=load_workbook(builder.OUT)
        for key,value in overrides.items():wb['Inputs'][f'D{builder.I[key]}']=value
        path=tmp/'changed.xlsx';wb.save(path)
        subprocess.run([soffice,f'-env:UserInstallation={ (tmp/"profile").as_uri() }','--headless','--convert-to','xlsx:Calc MS Excel 2007 XML','--outdir',str(out),str(path)],check=True,capture_output=True,timeout=120)
        assert_workbook(load_workbook(out/path.name,data_only=True),engine.calculate(overrides))
