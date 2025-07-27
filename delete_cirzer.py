import shutil
import os

if os.path.exists('C:/Users/hp/OneDrive/Documents/python/CirZer'):
    shutil.rmtree('C:/Users/hp/OneDrive/Documents/python/CirZer')
    print('Project directory deleted successfully.')
else:
    print('Project directory does not exist.')
