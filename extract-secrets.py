import os
import json

secrets = json.loads(os.getenv('SECRETS'))

# Iterate over the keys and set environment variables
with open('.env', 'w') as env_file:
    for key, value in secrets.items():
        env_file.write(f'{key}="{value}"\n')
