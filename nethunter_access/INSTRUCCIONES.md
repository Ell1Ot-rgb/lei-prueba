# Guía de Acceso Remoto a NetHunter

Para conectarte a tu terminal NetHunter desde cualquier servidor externo:

## 1. Requisitos
- Tener este archivo de clave (`id_ed25519_nethunter`) en el servidor remoto.
- Asegurarte de que el túnel reverso esté activo en NetHunter (ejecutando `ssh -fN -R 9022:localhost:8022 mi-droplet`).

## 2. Comando de Conexión
Ejecuta el siguiente comando desde el servidor externo:
```bash
ssh -i id_ed25519_nethunter -p 9022 root@159.203.164.103
```

## 3. Acceso por Contraseña (Alternativo)
Si no tienes la llave a mano, puedes usar:
```bash
ssh -p 9022 root@159.203.164.103
```
Luego introduce la contraseña: `kali`

## 4. Notas de Seguridad
Asegúrate de dar permisos correctos a la llave en el servidor destino:
`chmod 600 id_ed25519_nethunter`
