# 🛡️ Guía Técnica: Creación y Optimización de Memoria Swap en VPS Linux

Esta guía detalla los pasos para crear, activar y optimizar un archivo de memoria de intercambio (*Swap*) de forma segura en cualquier servidor virtual privado (VPS) Linux (DigitalOcean, Azure, AWS, etc.).

---

## 🧐 ¿Cuánto Swap se necesita? (Regla de Oro)

El tamaño del archivo Swap se determina en función de la memoria RAM física disponible en el VPS:

* **RAM < 2 GB**: El swap debe ser de **2 veces la RAM** (ej: VPS de 1GB RAM ➡️ 2GB Swap).
* **RAM entre 2 GB y 8 GB**: El swap debe ser **igual a la RAM** (ej: VPS de 4GB RAM ➡️ 4GB Swap).
* **RAM > 8 GB**: El swap debe ser de al menos **4 GB** (para absorber picos y evitar OOM).

---

## 🛠️ Procedimiento de Creación (Paso a Paso)

Ejecuta los siguientes comandos en la terminal de tu servidor con permisos de administrador (`root` o usando `sudo`):

### 1. Verificar si ya existe Swap activo
Antes de empezar, comprueba si el sistema ya tiene algún archivo swap configurado:
```bash
sudo swapon --show
# o también:
free -h
```
*(Si no muestra nada en la sección Swap, el servidor está operando únicamente con RAM física).*

### 2. Crear el archivo Swap (Ejemplo para 2 GB)
Utiliza `fallocate` para crear un archivo del tamaño deseado en la raíz del sistema.
* **Para 2 GB (Recomendado para VPS de 1GB RAM)**:
  ```bash
  sudo fallocate -l 2G /swapfile
  ```
* **Para 4 GB (Recomendado para VPS de 2GB/4GB RAM)**:
  ```bash
  sudo fallocate -l 4G /swapfile
  ```

> [!NOTE]
> Si `fallocate` falla o muestra un error de incompatibilidad con el sistema de archivos, puedes crearlo usando `dd` (tarda unos segundos más):
> ```bash
> sudo dd if=/dev/zero of=/swapfile bs=1M count=2048 # (para 2 GB)
> ```

### 3. Ajustar permisos del archivo
Por seguridad, restringe los permisos para que solo el usuario `root` pueda leer y escribir en el archivo swap:
```bash
sudo chmod 600 /swapfile
```

### 4. Formatear el archivo como Swap
Prepara el archivo para que el kernel de Linux lo reconozca como memoria de intercambio:
```bash
sudo mkswap /swapfile
```

### 5. Activar el Swap en caliente
Habilita el archivo swap recién creado:
```bash
sudo swapon /swapfile
```

### 6. Validar que se ha activado correctamente
Verifica que el swap esté asignado y consumiendo espacio virtual:
```bash
sudo swapon --show
free -h
```

---

## 🔄 Hacer el Swap Permanente

Para que el archivo swap se monte automáticamente cada vez que el servidor se reinicie, debes añadirlo al archivo de configuración del sistema:

1. Realiza una copia de seguridad preventiva de `/etc/fstab`:
   ```bash
   sudo cp /etc/fstab /etc/fstab.bak
   ```
2. Añade la entrada del swap al final del archivo fstab:
   ```bash
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

---

## ⚙️ Optimización del Rendimiento (Swappiness)

El parámetro **`swappiness`** determina qué tan agresivamente el kernel de Linux moverá datos de la RAM física al swap (es un porcentaje de 0 a 100).
* Por defecto, Linux viene con un swappiness de `60`.
* En un VPS con disco SSD/NVMe, es altamente recomendable **bajarlo a 10**. Esto obliga al sistema a usar toda la RAM física disponible antes de escribir en disco, lo que evita lentitudes y desgaste innecesario en los discos.

### 1. Comprobar el valor de swappiness actual
```bash
cat /proc/sys/vm/swappiness
```

### 2. Cambiar temporalmente a 10 (en caliente)
```bash
sudo sysctl vm.swappiness=10
```

### 3. Hacer el ajuste persistente en reinicios
Añade la directiva de configuración al final del archivo sysctl:
```bash
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```
