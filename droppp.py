import requests
import imaplib
import time
from pyuseragents import random as random_useragent
from colorama import Fore, init
init()


def get_mails():
    mails = {}

    with open("mails.txt", "r") as file:
        for i in file.readlines():
            e, p = i.split(":")[0], i.split(":")[1]
            mails[e] = p.replace("\n", "")

    return mails


def get_proxy():
    with open("proxy.txt", "r") as file:
        proxies = file.readlines()

    return proxies


def check(mail, user_agent, proxies):
    headers = {
        'authority': 'api.droppp.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://droppp.io',
        'referer': 'https://droppp.io/',
        'user-agent': user_agent,
    }

    data = {
        'email': mail,
    }

    response = requests.post('https://api.droppp.io/v1/user/email/check', headers=headers, data=data, proxies=proxies)
    if "This website is using a security service" in response.text:
        time.sleep(5)
        response = requests.post('https://api.droppp.io/v1/user/email/check', headers=headers, data=data,
                                 proxies=proxies)
    elif "The owner of this website (api.droppp.io) has banned your IP address" in response.text:
        return "remove"

    response = response.json()
    try:
        is_registered = response["registered"]
    except KeyError:
        print(Fore.BLUE, f"[ERROR {mail}]", Fore.RED, response["errors"], proxies, Fore.RESET)
        if response["errors"] == {'generic': 'Too many requests'}:
            is_registered = "proxies"
        else:
            is_registered = "continue"
    return is_registered


def create_account(mail, password, user_agent, proxies):
    headers = {
        'authority': 'api.droppp.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://droppp.io',
        'referer': 'https://droppp.io/',
        'user-agent': user_agent
    }

    data = {
        'email': mail,
        'password': password,
    }

    response = requests.post('https://api.droppp.io/v1/user/add', headers=headers, data=data, proxies=proxies).json()
    try:
        token = response["token"]['access_token']
    except KeyError:
        if response["errors"] == {'generic': 'Too many requests'}:
            token = "proxies"

    return token


def send_code(mail, token, user_agent, proxies):
    headers = {
        'authority': 'api.droppp.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {token}',
        # 'content-length': '0',
        'origin': 'https://droppp.io',
        'referer': 'https://droppp.io/',
        'user-agent': user_agent,
    }

    response = requests.post('https://api.droppp.io/v1/user/email/verify/send', headers=headers, proxies=proxies)
    print(Fore.BLUE, f"[{mail}]", Fore.GREEN, "Code sent:", response.text, Fore.RESET)


def get_code_from_rambler(login, password):
    mail = imaplib.IMAP4_SSL('imap.rambler.ru')
    mail.login(login, password)
    mail.list()
    mail.select("inbox")
    result, data = mail.search(None, "ALL")
    ids = data[0]
    id_list = ids.split()
    latest_email_id = id_list[-1]
    result, data = mail.fetch(latest_email_id, '(RFC822)')
    result, data = mail.uid('search', None, "ALL")
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
    mail = raw_email.decode('UTF-8')
    el = mail.split()
    index_of_code = el.index("#F0F0F3;border-radius=")+2
    code = el[index_of_code][6:12]

    return code


def enter_code(code, token, user_agent, proxies, mail):
    headers = {
        'authority': 'api.droppp.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {token}',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://droppp.io',
        'referer': 'https://droppp.io/',
        'user-agent': user_agent,
    }

    data = {
        'code': code,
    }

    response = requests.post('https://api.droppp.io/v1/user/email/verify/set', headers=headers, data=data, proxies=proxies)

    print(Fore.BLUE, f"[{mail}]", Fore.GREEN, "Registration done", Fore.RESET)


mails = get_mails()
proxy = get_proxy()


def main():
    print(Fore.BLUE, " Telegram:", Fore.GREEN, "@FarmerFrog\n",
          Fore.BLUE, "Chat:", Fore.GREEN, "@FarmerFrogChat\n",
          Fore.BLUE, "Creator:", Fore.GREEN, "@deer_fern")
    i = 0

    for mail, password in mails.items():
        while True:
            i += 1
            try:
                tmp = proxy[i].replace('\n', '')
                proxies = {"http": f"http://{tmp}", "https": f"http://{tmp}"}
            except IndexError:
                i = 0
                tmp = proxy[i].replace('\n', '')
                proxies = {"http": f"http://{tmp}", "https": f"http://{tmp}"}
            user_agent = random_useragent()
            is_registered = check(mail, user_agent, proxies)
            if is_registered == True or is_registered == False:
                break
            elif is_registered == "proxies":
                i += 1
                continue
            elif is_registered == "continue":
                break
            elif is_registered == "remove":
                print(Fore.BLUE, "[INFO] Broken proxy removed", Fore.RESET)
                proxy.remove(proxy[i])
                i += 1
        if is_registered == "continue":
            continue
        if not is_registered:
            token = create_account(mail, password, user_agent, proxies)
            if token == "proxies":
                i += 1
                continue
        else:
            print(Fore.BLUE, f"[{mail}]", Fore.GREEN, "Mail already registered", Fore.RESET)
            continue

        send_code(mail, token, user_agent, proxies)
        time.sleep(10)
        try:
            code = get_code_from_rambler(mail, password)
        except:
            print(Fore.RED, "[ERROR] Something wrong with email", Fore.RESET)
        try:
            enter_code(code, token, user_agent, proxies, mail)
        except:
            print(Fore.RED, "Missed code", Fore.RESET)
        if not is_registered:
            with open("registered accounts.txt", "a") as file:
                file.write(f"{mail}:{password}:{token}\n")
        i += 1
        time.sleep(10)


if __name__ == "__main__":
    main()
