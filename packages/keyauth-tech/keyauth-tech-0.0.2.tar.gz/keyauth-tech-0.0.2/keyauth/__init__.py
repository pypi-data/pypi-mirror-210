import subprocess
import requests
import platform
from colorama import Fore, init

init(autoreset=True)  # Automatically reset colorama color styles after they're printed

class KeyAuth:

    def __init__(self, app_id, base_url="https://api.keyauth.tech/api/v1"):
        self.app_id = app_id
        self.auth_url = f"{base_url}/auth/{app_id}"
        self.license_url = f"{base_url}/license"

    def get_hwid(self):
        system = platform.system()
        if system == 'Darwin':
            cmd = ['system_profiler', 'SPHardwareDataType']
            output = subprocess.check_output(cmd).decode()
            for line in output.split('\n'):
                if 'Hardware UUID' in line:
                    uuid = line.split(':')[-1].strip()
                    break
        elif system == 'Windows':
            cmd = ['wmic', 'csproduct', 'get', 'uuid']
            output = subprocess.check_output(cmd).decode()
            for line in output.split('\n'):
                if line.strip() != 'UUID':
                    uuid = line.strip()
                    break
        else:
            uuid = None
        return str(uuid)

    def authenticate(self):
        data = {"hwid": self.get_hwid()}
        response = requests.post(self.auth_url, json=data, timeout=100)
        json_response = response.json()
        if json_response.get('message') == 'Login Success' and json_response.get('status') == 'success':
            print(f"{Fore.GREEN}[+] Successfully authenticated!{Fore.RESET}")
            return True
        else:
            print(f"{Fore.RED}[!] HWID: {self.get_hwid()} is not authenticated!{Fore.RESET}")
            key = input(f"{Fore.RED}License Key: {Fore.RESET}")
            key_payload = {'license_key': key, 'hwid': self.get_hwid()}
            headers = {'x-app-id': self.app_id}

            key_response = requests.post(self.license_url, json=key_payload, headers=headers, timeout=100)
            license_response = key_response.json()
            if license_response.get('message') == 'License key is valid. HWID added.' and license_response.get('status') == 'success':
                print(f"{Fore.GREEN}[+] Successfully authenticated!{Fore.RESET}")
                return True
            else:
                print(f"{Fore.RED}[!] Invalid License Key!{Fore.RESET}")
                return False
