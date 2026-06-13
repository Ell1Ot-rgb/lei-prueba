# Arquitectura Zero Trust: Integración de Cloudflare Tunnels

Este documento detalla paso a paso la implementación de túneles seguros para aislar el servidor de DigitalOcean del internet abierto, y conectar tu entorno local de n8n exclusivamente a través de la infraestructura perimetral encriptada de Cloudflare.

---

## 🏗️ 1. Visión General de la Arquitectura
Pasaremos de un modelo de "Puerto Abierto" a un modelo "Zero Trust".
El contenedor de Cloudflare dentro de tu servidor creará una conexión de salida hacia la red global de Cloudflare. n8n hará las solicitudes a Cloudflare (a través de tu dominio con HTTPS), y Cloudflare las reenviará a tu contenedor interno. Los puertos 8000 y 7474 desaparecerán de internet.

### Contenedores y Servicios Involucrados
1. **`lightrag_server` (Puerto 8000 interno):** Recibe comandos de ingesta y consulta de Graphiti.
2. **`neo4j_lightrag` (Puerto 7474 interno):** Recibe las consultas analíticas de Cypher.
3. **`cloudflared` (NUEVO):** Contenedor que funcionará como el puente seguro (Túnel). Se conectará a la misma red interna de Docker (`sistema_vivo_rag_network`) para alcanzar los otros servicios sin exponerlos al host.

---

## 🚀 2. Guía de Implementación Paso a Paso

### Paso 1: Creación del Túnel en la Nube
1. Inicia sesión en tu cuenta de **Cloudflare**.
2. Dirígete a **Zero Trust** -> **Networks** -> **Tunnels**.
3. Haz clic en **Create a tunnel** (elige Cloudflared).
4. Asígnale un nombre (ej. `Cerebro-DigitalOcean`).
5. Copia el **Token del túnel** (aparecerá en la sección de instalación para Docker).

### Paso 2: Despliegue del Daemon en DigitalOcean
Accede por SSH a tu servidor de DigitalOcean y ejecuta el despliegue del túnel asegurándote de que esté en la red interna de tu ecosistema:

```bash
docker run -d \
  --name cloudflare_tunnel \
  --network sistema_vivo_rag_network \
  --restart unless-stopped \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run --token <AQUI_TU_TOKEN>
```
*Nota:* Al estar en la red `sistema_vivo_rag_network`, el túnel puede referirse a la IA simplemente usando `http://lightrag_server:8000`.

### Paso 3: Configuración de Rutas (Ingress Rules)
En el panel de Cloudflare Zero Trust, ve a la pestaña **Public Hostname** dentro de tu túnel y crea dos reglas:

**Ruta 1: La API de la Inteligencia Artificial**
* **Public Hostname:** `ia-brain.tudominio.com`
* **Service:** `HTTP` -> `lightrag_server:8000`

**Ruta 2: La Base de Datos Neo4j**
* **Public Hostname:** `neo4j.tudominio.com`
* **Service:** `HTTP` -> `neo4j_lightrag:7474`

### Paso 4: Cierre Definitivo de Puertos (UFW Firewall)
Una vez que verifiques que los dominios funcionan, procedemos a cerrar tu servidor al mundo exterior. Ejecuta en tu DigitalOcean:

```bash
# Mantener abierto solo SSH
ufw allow ssh
# Bloquear el acceso directo a los puertos de la IA y BD
ufw deny 8000
ufw deny 7474
ufw deny 7687
ufw reload
```

---

## 🛡️ 3. Seguridad Adicional: Service Tokens (Cloudflare Access)
Dado que tu endpoint `ia-brain` aceptará inyección de texto libre, debemos asegurarlo:
1. En Cloudflare Zero Trust, ve a **Access** -> **Applications** y crea una para `ia-brain.tudominio.com`.
2. Crea una política ("Policy") configurada para validar **Service Auth**.
3. En la sección **Service Auth**, genera un par de credenciales:
   - `CF-Access-Client-Id`
   - `CF-Access-Client-Secret`

Nadie en el mundo podrá acceder a `ia-brain.tudominio.com` sin estas cabeceras.

---

## 🔧 4. Configuración del Workflow en n8n
Debes modificar los 3 nodos de **HTTP Request** en el archivo de tu flujo (`n8n_unificado_nativo_v2.json`):

### 1. Nodo "Consultar Grafo" e "Indexar Conocimiento"
* **URL Nueva:** Cambiar de `http://159.203.164.103:8000/...` a `https://ia-brain.tudominio.com/...`
* **Cabeceras Adicionales (Send Headers):** Activar y agregar:
  - `CF-Access-Client-Id`: `[TU_CLIENT_ID]`
  - `CF-Access-Client-Secret`: `[TU_CLIENT_SECRET]`

### 2. Nodo "Extraer Métricas Neo4j"
* **URL Nueva:** Cambiar de `http://159.203.164.103:7474/db/neo4j/tx/commit` a `https://neo4j.tudominio.com/db/neo4j/tx/commit`
* *Nota:* Para Neo4j, ya tienes el header de `Authorization: Basic ...` configurado, lo cual te protege, pero de todas formas se recomienda agregar Cloudflare Access y poner los headers `CF-Access` aquí también.

**¡Completado!** Tu ecosistema ahora es indestructible, opera sobre protocolos HTTP/2 y TLS de grado militar, y se mantiene invisible para cualquier atacante.
