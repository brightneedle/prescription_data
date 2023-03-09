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