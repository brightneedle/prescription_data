import numpy as np
import pandas as pd
import pgeocode as pg
from utils import listdir_nohidden, antibiotics
import os

nomi = pg.Nominatim('gb')

path = 'raw_gp/'

month_folders = listdir_nohidden(path) # path to downloaded data

Address = []
BNF = []
ChemSubstance = []
GP_data = []

codes = ['0501011C0', '0501011F0', '0501011I0', '0501011J0', '0501011K0', '0501011L0', '0501011P0', '0501011P0', '0501011T0', '0501011V0', '0501011W0']

for month in month_folders:
    address = pd.read_csv(path+month+'/Address.csv')
    bnf = pd.read_csv(path+month+'/BNF.csv')
    chem = pd.read_csv(path+month+'/ChemSubstance.csv')

    gp_path = [f for f in os.listdir(path+month) if f.startswith("GPData")][0]
    gp_data = pd.read_csv(path+month+'/'+gp_path, delimiter=',')

    antibiotic_mask = gp_data['BNFCode'].str.startswith(tuple(antibiotics.values()))
    gp_data = gp_data.loc[antibiotic_mask]

    zips = address['Postcode'].apply(lambda x: x[:4]) # get 1st 4 chars of postcode
    geo_query = nomi.query_postal_code(zips.to_numpy()) # lookup coords from postcodes

    # Add coords
    address['lat'] = geo_query['latitude']
    address['long'] = geo_query['longitude']
    
    Address.append(address)
    BNF.append(bnf)
    ChemSubstance.append(chem)
    GP_data.append(gp_data)

    print(gp_path+' done!')

pd.concat(Address, axis=0).drop_duplicates(subset='PracticeId').to_csv('gp_data/AllAddresses_NoDup.csv', index=False)
pd.concat(BNF, axis=0).drop_duplicates().to_csv('gp_data/AllBNF_NoDup.csv', index=False)
pd.concat(ChemSubstance, axis=0).drop_duplicates().to_csv('gp_data/AllChemSubstance_NoDup.csv', index=False)

pd.concat(GP_data, axis=0).sort_values(by='Period').to_csv('gp_data/AllGPData.csv', index=False)