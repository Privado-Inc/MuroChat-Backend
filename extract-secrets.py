import os
import json

SECRETS_VARIABLE = os.getenv('SECRETS')

if SECRETS_VARIABLE:
    secrets = json.loads(SECRETS_VARIABLE)

    # Iterate over the keys and set environment variables
    with open('.env', 'w') as env_file:
        for key, value in secrets.items():
            env_file.write(f'{key}="{value}"\n')
