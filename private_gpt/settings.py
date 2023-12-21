import os
from dotenv import load_dotenv

load_dotenv()

IS_PROD = os.getenv('IS_PROD')
if IS_PROD and IS_PROD.lower() == 'true':
    is_prod = True
else:
    is_prod = False
if is_prod:
    from .settings_configuration.prod import *
else:
    from .settings_configuration.qa import *
