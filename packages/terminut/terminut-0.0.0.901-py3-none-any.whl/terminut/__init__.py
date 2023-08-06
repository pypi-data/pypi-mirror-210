__title__ = 'terminut'
__author__ = 'vast#1337'
__version__ = '0.0.0.901'


from .console import *
from .customs import *


## VERSION CHECKER ##
from requests import get
from os import system; from sys import executable
response = get('https://pypi.org/project/terminut/').text
CURRENT_VERSION = str(response.split('<h1 class="package-header__name">\n        terminut ')[1].split('\n')[0])

if __version__ < CURRENT_VERSION:
    Console.printf(
        f"[TERMINUT] Version Out-of-Date. Please upgrade by using: \"python.exe -m pip install -U terminut\"", 
        mainCol=Fore.RED,
        showTimestamp=False
    )
    system(f'{executable} -m pip install -U veilcord  -q')
## VERSION CHECKER ##
