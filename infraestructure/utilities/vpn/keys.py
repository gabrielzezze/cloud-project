import os
import subprocess

class Keys():
    def __init__(self):
        self.GEN_KEYS_SCRIPT_PATH = os.path.join(
            os.path.dirname(__file__), 
            '../../scripts/vpn/gen_keys.sh'
        )
        self.public_key = None
        self.private_key = None

    def __call__(self):
        result = subprocess.run([self.GEN_KEYS_SCRIPT_PATH], stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8')
        keys = result.split('~')
        self.private_key = keys[0]
        self.public_key = keys[1]

