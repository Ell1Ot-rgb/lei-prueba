
import pexpect
import sys

def connect():
    cmd = "ssh -o StrictHostKeyChecking=no -p 9022 root@159.203.164.103"
    print(f"Ejecutando: {cmd}")
    child = pexpect.spawn(cmd, encoding='utf-8', timeout=20)
    
    try:
        index = child.expect(['password:', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print("Enviando contraseña...")
            child.sendline('kali')
            # Wait for any prompt (NetHunter prompt is often 'root@kali' or similar, but we'll use a regex)
            child.expect([r'[#❯]', pexpect.EOF, pexpect.TIMEOUT])
            print("--- CONECTADO A NETHUNTER ---")
            child.sendline('uname -a && id')
            child.expect([r'[#❯]', pexpect.EOF, pexpect.TIMEOUT])
            print(child.before)
            print("--- FIN DE LA SESIÓN ---")
        elif index == 1:
            print("Error: EOF alcanzado prematuramente")
            print(child.before)
        elif index == 2:
            print("Error: Timeout al esperar el prompt de contraseña")
            print(child.before)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        child.close()

if __name__ == "__main__":
    connect()
