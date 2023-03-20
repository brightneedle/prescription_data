import os

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

antibiotics = {'penicillins'        : '050101',
                'macrolides'        : '050105',
                'tetracyclines'     : '050103',
                'cephalosporins'    : '050102',
                'aminoglycosides'   : '050104'}

def assign_types(data):
    data['type'] = -1
    for type, code in antibiotics.items():
        mask = data['BNFCode'].str.startswith(code)
        data['type'].mask(mask, type, inplace=True)

    data = data.loc[data['type']!=-1]

    return data