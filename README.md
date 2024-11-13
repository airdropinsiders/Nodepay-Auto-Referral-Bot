# Nodepay Autoreferral v1.0
Automatic referral script for Nodepay Account using captcha solver and proxies.
### Tools and components required
1. Nodepay Account| Register: [https://app.nodepay.ai/register](https://app.nodepay.ai/register?ref=2ef5JE5Tr7XfYUL)
2. Proxies Static Residental | [FREE 10 PREMIUM PROXIES](https://www.webshare.io/?referral_code=gbny3acbph42)
3. Captcha Solvers API keys | [2captcha.com](https://2captcha.com/?from=23248152)
4. VPS or RDP (OPTIONAL)
5. Python version 3.10
# Installation
- Install Python For Windows: [Python](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe)
- For Unix:
```bash
apt install python3 python3-pip -y
```
- Install requirements, Windows:
```bash
pip install -r requirements.txt
```
- Unix:
```bash
pip3 install -r requirements.txt
```
### Run the Bot
- Replace the proxies example in ```proxies.txt``` to your own proxies
#### Run command:
- Windows:
```bash
python main.py
```
- Unix
```bash
python3 main.py
```
- Insert your referral code, example: ``https://app.nodepay.ai/register?ref=XXXXX`` this is your code > ``XXXXX``
- Enter how many referrals you want, more referrals will result in more use of your captcha solver api credits
- Select your captcha solver service (Make sure you have credits, you can topup first)
- Select proxy usage yes or no
- Result account generated will be saved to accounts.txt
# Notes
- Run this bot, and it will update your referrer code to my invite code if you don't have one.
- This bot have delays for sending Reports to Nodepay server to avoid rate limiting.
- You can just run this bot at your own risk, I'm not responsible for any loss or damage caused by this bot. This bot is for educational purposes only.
