import numpy as np
import pandas as pd
import pgeocode as pg
import requests as rq
import os
from utils import listdir_nohidden, antibiotics

pd.options.mode.chained_assignment = None

nomi = pg.Nominatim('gb')

path = 'raw_hosp/'

def get_coords(month):
    address = pd.read_csv(path+month+'/Address.csv', 
                        on_bad_lines='skip',
                        header=0,
                        names=['Period','Id','Name','Street','Area','Posttown','County','Postcode'])

    zips = address['Postcode'].to_numpy()
    geo_query1 = nomi.query_postal_code(zips)

    address['lat'] = geo_query1['latitude']
    address['long'] = geo_query1['longitude']

    for idx, row in address.iterrows(): # attempts to scrub coords from area if postcode missing
        if pd.isnull(row['lat']):
            loc = row['Area']
            geo_query2 = nomi.query_location(loc)
            geo_query2 = geo_query2.loc[geo_query2['state_name']=='Wales']
            if len(geo_query2)>0:
                address['lat'][idx] = geo_query2['latitude'].iloc[0]
                address['long'][idx] = geo_query2['longitude'].iloc[0]

    return address

month_folders = listdir_nohidden(path)

Address = []
BNF = []
ChemSubstance = []
GP_data = []

for month in month_folders:
    print('Attempting', month)

    bnf = pd.read_csv(path+month+'/BNF.csv', on_bad_lines='skip')
    chem = pd.read_csv(path+month+'/ChemSubstance.csv', on_bad_lines='skip')

    gp_path = [f for f in os.listdir(path+month) if f.startswith("HospitalData")][0]
    gp_data = pd.read_csv(path+month+'/'+gp_path, on_bad_lines='skip')

    antibiotic_mask = gp_data['BNFCode'].str.startswith(tuple(antibiotics.values()))
    gp_data = gp_data.loc[antibiotic_mask]

    address = get_coords(month)

    Address.append(address)
    BNF.append(bnf)
    ChemSubstance.append(chem)
    GP_data.append(gp_data)

    print('done!')

pd.concat(Address, axis=0).drop_duplicates(subset='Id').to_csv('hosp_data/AllAddresses_NoDup.csv', index=False)
pd.concat(BNF, axis=0).drop_duplicates().to_csv('hosp_data/AllBNF_NoDup.csv', index=False)
pd.concat(ChemSubstance, axis=0).drop_duplicates().to_csv('hosp_data/AllChemSubstance_NoDup.csv', index=False)

pd.concat(GP_data, axis=0).sort_values(by='Period').to_csv('hosp_data/AllHospData.csv', index=False)