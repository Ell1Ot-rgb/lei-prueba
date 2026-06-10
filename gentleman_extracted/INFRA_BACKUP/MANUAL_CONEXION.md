# 🛡️ Manual de Conexión - Gentleman Stack

Este paquete contiene las llaves críticas e instrucciones para acceder a tu infraestructura.

## 1. Servidor Azure (La Bóveda)
- **IP:** 20.125.88.188
- **Usuario:** azureuser
- **Llave:** asd_key_0203.pem
- **Comando:** `ssh -i asd_key_0203.pem azureuser@20.125.88.188`

## 2. Servidor AWS (El Cerebro - Enrutado)
- **IP Interna:** 100.107.109.128
- **Usuario:** ec2-user
- **Llave:** aws_ssh.pem
- **Acceso:** Se requiere saltar desde Azure.
- **Comando Directo:** `ssh -i asd_key_0203.pem azureuser@20.125.88.188 -t "ssh -i aws_ssh.pem ec2-user@100.107.109.128"`

## 3. Servidor DigitalOcean (Automatización)
- **IP:** 159.203.164.103
- **Usuario:** root
- **Llave:** id_ed25519 (OpenSSH)
- **Comando:** `ssh -i id_ed25519 root@159.203.164.103`

---
⚠️ **SEGURIDAD:** No compartas este archivo. Si pierdes estas llaves, perderás el acceso administrativo a tus servidores.
