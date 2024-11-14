import asyncio
import random
import string
import time
from typing import Optional, Tuple, Dict
import requests
from colorama import Fore, Style, init
from faker import Faker
from datetime import datetime
from capmonster_python import TurnstileTask
from twocaptcha import TwoCaptcha
from anticaptchaofficial.turnstileproxyless import turnstileProxyless

init(autoreset=True)

def print_banner():
    ascii_art = f"""
    {Fore.CYAN}
         █████╗ ██╗██████╗ ██████╗ ██████╗  ██████╗ ██████╗ 
        ██╔══██╗██║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
        ███████║██║██████╔╝██║  ██║██████╔╝██║   ██║██████╔╝
        ██╔══██║██║██╔══██╗██║  ██║██╔══██╗██║   ██║██╔═══╝ 
        ██║  ██║██║██║  ██║██████╔╝██║  ██║╚██████╔╝██║     
        ╚═╝  ╚═╝╚═╝╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     

        ██╗███╗   ██╗███████╗██╗██████╗ ███████╗██████╗     
        ██║████╗  ██║██╔════╝██║██╔══██╗██╔════╝██╔══██╗    
        ██║██╔██╗ ██║███████╗██║██║  ██║█████╗  ██████╔╝    
        ██║██║╚██╗██║╚════██║██║██║  ██║██╔══╝  ██╔══██╗    
        ██║██║ ╚████║███████║██║██████╔╝███████╗██║  ██║    
        ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝{Fore.RESET}
    """
    print(ascii_art)
    print(f"{Fore.CYAN}{'='*45}")
    print(f"{Fore.YELLOW}       Nodepay Auto Referral Bot")
    print(f"{Fore.YELLOW}       t.me/AirdropInsiderID")
    print(f"{Fore.YELLOW}       do with your own risk")
    print(f"{Fore.CYAN}{'='*45}\n")

def log_step(message: str, type: str = "info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW
    }
    color = colors.get(type, Fore.WHITE)
    prefix = {
        "info": "ℹ",
        "success": "✓",
        "error": "✗",
        "warning": "⚠"
    }
    print(f"{Fore.WHITE}[{timestamp}] {color}{prefix.get(type, '•')} {message}{Style.RESET_ALL}")

class CaptchaConfig:
    WEBSITE_KEY = '0x4AAAAAAAx1CyDNL8zOEPe7'
    WEBSITE_URL = 'https://app.nodepay.ai/login'

class ServiceCapmonster:
    def __init__(self, api_key):
        self.capmonster = TurnstileTask(api_key)

    async def get_captcha_token_async(self):
        task_id = self.capmonster.create_task(
            website_key=CaptchaConfig.WEBSITE_KEY,
            website_url=CaptchaConfig.WEBSITE_URL
        )
        return self.capmonster.join_task_result(task_id).get("token")

class ServiceAnticaptcha:
    def __init__(self, api_key):
        self.api_key = api_key
        self.solver = turnstileProxyless()
        self.solver.set_verbose(0)
        self.solver.set_key(self.api_key)
        self.solver.set_website_url(CaptchaConfig.WEBSITE_URL)    
        self.solver.set_website_key(CaptchaConfig.WEBSITE_KEY)
        self.solver.set_action("login")
    
    async def get_captcha_token_async(self):
        return await asyncio.to_thread(self.solver.solve_and_return_solution)

class Service2Captcha:
    def __init__(self, api_key):
        self.solver = TwoCaptcha(api_key)
    
    async def get_captcha_token_async(self):
        result = await asyncio.to_thread(
            lambda: self.solver.turnstile(
                sitekey=CaptchaConfig.WEBSITE_KEY,
                url=CaptchaConfig.WEBSITE_URL
            )
        )
        return result['code']

class CaptchaServiceFactory:
    @staticmethod
    def create_service(service_name: str, api_key: str):
        if service_name.lower() == "capmonster":
            return ServiceCapmonster(api_key)
        elif service_name.lower() == "anticaptcha":
            return ServiceAnticaptcha(api_key)
        elif service_name.lower() == "2captcha":
            return Service2Captcha(api_key)
        raise ValueError(f"Unknown service: {service_name}")

class ProxyManager:
    def __init__(self, proxy_list: list):
        self.proxies = proxy_list
        self.current_index = -1
        self.total_proxies = len(proxy_list) if proxy_list else 0
        
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        if not self.proxies:
            return None
        
        self.current_index = (self.current_index + 1) % self.total_proxies
        proxy = self.proxies[self.current_index]
        return {"http": proxy, "https": proxy}

class ApiEndpoints:
    BASE_URL = "https://api.nodepay.ai/api"
    
    @classmethod
    def get_url(cls, endpoint: str) -> str:
        return f"{cls.BASE_URL}/{endpoint}"
    
    class Auth:
        REGISTER = "auth/register"
        LOGIN = "auth/login"
        ACTIVATE = "auth/active-account"

class LoginError(Exception):
    pass

class ReferralClient:
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.faker = Faker()
        self.proxy_manager = proxy_manager
        self.current_proxy = None
        self.email = None
        self.password = None
        
    def _generate_credentials(self) -> Tuple[str, str, str]:
        email_domains = ["@gmail.com", "@outlook.com", "@yahoo.com", "@hotmail.com"]
        username = self.faker.user_name()[:15] + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        email = f"{username}{random.choice(email_domains)}"
        password = (
            random.choice(string.ascii_uppercase) +
            ''.join(random.choices(string.digits, k=3)) +
            '@' +
            ''.join(random.choices(string.ascii_lowercase, k=8)) +
            random.choice(string.ascii_uppercase)
        )
        self.email = email
        self.password = password
        return username, email, password

    def _update_proxy(self):
        if self.proxy_manager:
            self.current_proxy = self.proxy_manager.get_next_proxy()
            if self.current_proxy:
                proxy_addr = self.current_proxy['http']
                log_step(f"Using proxy: {proxy_addr}", "info")
    def _get_headers(self, auth_token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://app.nodepay.ai',
            'priority': 'u=1, i',
            'referer': 'https://app.nodepay.ai/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        }
        
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
            headers['origin'] = 'chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm'
            
        return headers 

    async def _make_request(self, method: str, endpoint: str, json_data: dict, auth_token: Optional[str] = None) -> dict:
        self._update_proxy()
        headers = self._get_headers(auth_token)
        url = ApiEndpoints.get_url(endpoint)

        try:
            response = await asyncio.to_thread(
                lambda: requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    proxies=self.current_proxy,
                    timeout=30
                )
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            log_step(f"Request failed: {str(e)}", "error")
            return {"success": False, "msg": str(e)}

    async def login(self, captcha_service) -> str:
        try:
            log_step("Getting captcha token for login...", "info")
            captcha_token = await captcha_service.get_captcha_token_async()
            log_step("Captcha token obtained", "success")

            json_data = {
                'user': self.email,
                'password': self.password,
                'remember_me': True,
                'recaptcha_token': captcha_token
            }

            log_step("Attempting login...", "info")
            response = await self._make_request(
                method='POST',
                endpoint=ApiEndpoints.Auth.LOGIN,
                json_data=json_data
            )

            if not response.get("success"):
                msg = response.get("msg", "Unknown login error")
                log_step(f"Login failed: {msg}", "error")
                raise LoginError(msg)

            access_token = response['data']['token']
            log_step("Login successful", "success")
            return access_token

        except Exception as e:
            log_step(f"Login error: {str(e)}", "error")
            raise

    async def activate_account(self, access_token: str):
        try:
            log_step("Attempting account activation...", "info")
            response = await self._make_request(
                method='POST',
                endpoint=ApiEndpoints.Auth.ACTIVATE,
                json_data={},
                auth_token=access_token
            )

            if response.get("success"):
                log_step(f"Account activation successful: {response.get('msg', 'Success')}", "success")
            else:
                log_step(f"Account activation failed: {response.get('msg', 'Unknown error')}", "error")

            return response

        except Exception as e:
            log_step(f"Activation error: {str(e)}", "error")
            raise
        
    async def process_referral(self, ref_code: str, captcha_service) -> Optional[Dict]:
        try:
            username, email, password = self._generate_credentials()
            log_step(f"Generated credentials for: {email}", "info")
            
            log_step("Getting captcha token...", "info")
            captcha_token = await captcha_service.get_captcha_token_async()
            log_step("Captcha token obtained", "success")
            
            register_data = {
                'email': email,
                'password': password,
                'username': username,
                'referral_code': ref_code,
                'recaptcha_token': captcha_token
            }
            
            log_step("Registering account...", "info")
            register_response = await self._make_request('POST', ApiEndpoints.Auth.REGISTER, register_data)
            
            if register_response.get("success"):
                log_step(f"Registration successful: {register_response.get('msg', 'Success')}", "success")
                
                access_token = await self.login(captcha_service)
                
                activation_response = await self.activate_account(access_token)
                
                return {
                    "username": username,
                    "email": email,
                    "password": password,
                    "referral_code": ref_code,
                    "token": access_token,
                    "activation_status": activation_response.get('success', False),
                    "activation_message": activation_response.get('msg', 'Unknown')
                }
            else:
                log_step(f"Registration failed: {register_response.get('msg', 'Unknown error')}", "error")
                return None

        except Exception as e:
            log_step(f"Error processing referral: {str(e)}", "error")
            return None

async def main():
    print_banner()

    ref_code = input(f"{Fore.GREEN}Enter referral code: {Style.RESET_ALL}")
    num_referrals = int(input(f"{Fore.GREEN}Enter number of referrals: {Style.RESET_ALL}"))
    
    print(f"\n{Fore.YELLOW}Available captcha services:{Style.RESET_ALL}")
    print(f"1. Capmonster")
    print(f"2. Anticaptcha")
    print(f"3. 2Captcha{Style.RESET_ALL}")
    service_choice = input(f"{Fore.GREEN}Choose captcha service (1-3): {Style.RESET_ALL}")
    api_key = input(f"{Fore.GREEN}Enter API key for captcha service: {Style.RESET_ALL}")

    use_proxies = input(f"{Fore.GREEN}Use proxies? (yes/no): {Style.RESET_ALL}").lower() == 'yes'
    proxy_manager = None
    
    if use_proxies:
        try:
            with open('proxies.txt', 'r') as f:
                proxy_list = [line.strip() for line in f if line.strip()]
            proxy_manager = ProxyManager(proxy_list)
            log_step(f"Loaded {len(proxy_list)} proxies", "success")
        except FileNotFoundError:
            log_step("proxies.txt not found. Running without proxies.", "warning")

    service_map = {
        "1": "capmonster",
        "2": "anticaptcha",
        "3": "2captcha"
    }
    
    try:
        captcha_service = CaptchaServiceFactory.create_service(service_map[service_choice], api_key)
        log_step("Captcha service initialized", "success")
    except Exception as e:
        log_step(f"Failed to initialize captcha service: {str(e)}", "error")
        return

    client = ReferralClient(proxy_manager)
    successful_referrals = []
    
    log_step("Starting referral process...", "info")
    
    for i in range(num_referrals):
        print(f"\n{Fore.CYAN}{'='*45}")
        log_step(f"Processing referral {i+1}/{num_referrals}", "info")
        
        result = await client.process_referral(ref_code, captcha_service)
        if result:
            log_step("Account details:", "success")
            print(f"{Fore.CYAN}Username: {Fore.WHITE}{result['username']}")
            print(f"{Fore.CYAN}Email: {Fore.WHITE}{result['email']}")
            print(f"{Fore.CYAN}Password: {Fore.WHITE}{result['password']}")
            print(f"{Fore.CYAN}Referred to: {Fore.WHITE}{result['referral_code']}")
            print(f"{Fore.CYAN}Token: {Fore.WHITE}{result['token']}")
            successful_referrals.append(result)
            
            with open('accounts.txt', 'a') as f:
                f.write(f"Email: {result['email']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write(f"Username: {result['username']}\n")
                f.write(f"Referred to: {result['referral_code']}\n")
                f.write(f"Token: {result['token']}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 50 + "\n")
        
        if i < num_referrals - 1:
            delay = random.uniform(2, 5)
            log_step(f"Waiting {delay:.2f} seconds...", "info")
            time.sleep(delay)

    print(f"\n{Fore.CYAN}{'='*45}")
    log_step("Summary:", "info")
    log_step(f"Total attempted: {num_referrals}", "info")
    log_step(f"Successful: {len(successful_referrals)}", "success")
    print(f"{Fore.CYAN}{'='*45}\n")

if __name__ == "__main__":
    asyncio.run(main())
