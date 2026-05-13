import pandas as pd

FILE = 'gabriel-ex2_ppg_by_creditor_class.xlsx'

KEY = ['country_code', 'year', 'income_group']

# Cargar sheets
bil   = pd.read_excel(FILE, sheet_name='Bilateral')
mlat  = pd.read_excel(FILE, sheet_name='Multilateral')
bonds = pd.read_excel(FILE, sheet_name='Bonds')
banks = pd.read_excel(FILE, sheet_name='Commercial Banks')
opriv = pd.read_excel(FILE, sheet_name='Other Private')
imf   = pd.read_excel(FILE, sheet_name='IMF Credit')
total = pd.read_excel(FILE, sheet_name='Total PPG')

# Merge
df = (total
      .merge(bil  [KEY + ['DT.DOD.BLAT.CD_total','DT.DOD.BLAT.CD_pc','DT.DOD.BLAT.CD_nonpc']], on=KEY, how='left')
      .merge(mlat [KEY + ['DT.DOD.MLAT.CD_total']], on=KEY, how='left')
      .merge(bonds[KEY + ['bonds_value']],           on=KEY, how='left')
      .merge(banks[KEY + ['commbanks_value']],        on=KEY, how='left')
      .merge(opriv[KEY + ['otherprivate_value']],     on=KEY, how='left')
      .merge(imf  [KEY + ['imf_value']],              on=KEY, how='left')
).fillna(0)

# Denominador
df['total'] = df['total_ppg_value'] + df['imf_value']

# Categorías con opción A para bilateral pre-2006
df['official_covered'] = df.apply(
    lambda r: r['DT.DOD.BLAT.CD_pc']    if r['year'] >= 2006 else r['DT.DOD.BLAT.CD_total'], axis=1)
df['official_outside'] = df.apply(
    lambda r: r['DT.DOD.BLAT.CD_nonpc'] if r['year'] >= 2006 else 0, axis=1)

df['banks_covered']  = df.apply(
    lambda r: r['commbanks_value'] if r['year'] >= 1976 else 0, axis=1)
df['bonds_covered']  = df.apply(
    lambda r: r['bonds_value']     if r['year'] >= 2003 else 0, axis=1)

df['private_outside'] = (
    df['otherprivate_value']
    + df.apply(lambda r: r['commbanks_value'] if r['year'] < 1976 else 0, axis=1)
    + df.apply(lambda r: r['bonds_value']     if r['year'] < 2003 else 0, axis=1)
)
df['multilateral_outside'] = df['DT.DOD.MLAT.CD_total'] + df['imf_value']

# Convertir a %
cats = ['official_covered','banks_covered','bonds_covered',
        'official_outside','private_outside','multilateral_outside']
for c in cats:
    df[c + '_pct'] = df[c] / df['total'] * 100

# Median por año — LICs
lic = df[df['income_group'] == 'LIC']
annual = lic.groupby('year')[[c + '_pct' for c in cats]].median().reset_index()

# Renombrar columnas para Excel
annual.columns = ['Year',
                  'Official covered (Paris Club/CF)',
                  'Private banks covered (London Club)',
                  'Bond debt covered (CACs)',
                  'Official outside framework',
                  'Private outside framework',
                  'Multilateral/IMF outside']

annual.to_excel('resolution_mechanisms_chart_data.xlsx', index=False)
print('Listo:', annual.shape)
print(annual.head())