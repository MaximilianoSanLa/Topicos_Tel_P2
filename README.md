# Proyecto 2 – Despliegue en AWS (BookStore Monolítica Escalable)

**Materia:** ST0263 – Tópicos Especiales en Telemática  
**Estudiante:** Juan Camilo Villa – jcvillac@eafit.edu.co  
**Profesor:** [Nombre del profesor] – [correo@eafit.edu.co]

---

## 🧩 1. Breve descripción de la actividad

El proyecto consiste en desplegar una aplicación web monolítica desarrollada en Flask (BookStore) en AWS, cumpliendo con dos objetivos:

1) Desplegar la aplicación BookStore Monolítica en dos (2) Máquinas Virtuales
en AWS, con un dominio propio, certificado SSL y Proxy inverso en NGINX. (un servidor para
la base de datos y otro servidor para la aplicación + nginx). 
2) Objetivo 2: Realizar el escalamiento en nube de la aplicación monolítica, siguiente
algún patrón de arquitectura de escalamiento de apps monolíticas en AWS. La aplicación
debe ser escalada utilizando Máquinas Virtuales (VM) con autoescalamiento, base de datos
aparte Administrada o si es implementada con VM con Alta Disponibilidad, y Archivos
compartidos vía NFS (como un servicio o una VM con NFS con Alta Disponibilidad), base de
datos en RDS.


---

## ✅ 1.1. Aspectos cumplidos

- Despliegue funcional de la app monolítica Flask con MySQL.
- Configuración de NGINX como proxy inverso con Certbot (SSL HTTPS).
- Dockerización del servicio Flask usando `docker-compose`.
- Conexión estable entre instancias privadas (APP ↔ DB) vía red 172.31.0.0/16.
- Creación de AMI “Golden” con configuración productiva.
- Implementación de Auto Scaling Group (ASG), Application Load Balancer (ALB) y Target Groups.
- Integración de almacenamiento compartido EFS entre instancias del ASG.
- Alta disponibilidad y balanceo de carga a través de AWS.

---

## ⚠️ 1.2. Aspectos no implementados o pendientes
- No se pudo implementar HTTPS con el balanceador de carga
- Justificación:
   No hay presupuesto para registrar un dominio (~$10-15 USD/año)
   No se puede usar el dominio de la universidad sin permisos administrativos
   Los dominios gratuitos (Freenom) no son aceptados por ACM en muchos casos

---

## 2. Diseño de alto nivel y arquitectura

### Objetivo 1 – Arquitectura monolítica con 2 VMs


<img width="382" height="431" alt="image" src="https://github.com/user-attachments/assets/1259afe6-ba1a-488b-a327-84736b7ce9b9" />



Patrón: Arquitectura monolítica tradicional con separación de capas (app y base de datos).  
Buenas prácticas: Uso de proxy inverso, variables de entorno, aislamiento con Docker y acceso restringido por Security Groups.

### ☁️ Objetivo 2 – Arquitectura monolítica escalable con servicios gestionados


<img width="733" height="747" alt="image" src="https://github.com/user-attachments/assets/4c757ad1-b9f9-4ec4-8d75-d3c2d5b81a8f" />



Patrón: Monolithic Web App con escalamiento elástico y almacenamiento compartido (ALB + ASG + RDS + EFS).  
Buenas prácticas: Infraestructura redundante, health checks en ALB/ASG y persistencia compartida en EFS.

# 3.Descripción del ambiente de desarrollo y técnico
## Cómo se Compila y Ejecuta
### Requisitos Previos

#### Servidor de Aplicación (172.31.31.7)

```bash
# Conectarse al servidor
ssh -i "tu-clave.pem" ubuntu@<IP-PUBLICA-SERVIDOR-APP>

# Verificar que Docker esté instalado
docker --version
docker-compose --version

# Si no están instalados, instalar:
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Cerrar sesión y volver a conectar para que los cambios surtan efecto
exit
ssh -i "tu-clave.pem" ubuntu@<IP-PUBLICA-SERVIDOR-APP>
```

####  Servidor de Base de Datos (172.31.25.142)

```bash
# Conectarse al servidor MySQL
ssh -i "tu-clave.pem" ubuntu@<IP-PUBLICA-SERVIDOR-MYSQL>

# Verificar que MySQL esté instalado y corriendo
sudo systemctl status mysql

# Si no está instalado:
sudo apt-get update
sudo apt-get install -y mysql-server
sudo systemctl enable mysql
sudo systemctl start mysql
```

###  Configuración del Servidor MySQL

####  Configurar MySQL para Conexiones Remotas

```bash
# Editar configuración de MySQL
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Buscar y cambiar la línea:
# bind-address = 127.0.0.1
# Por:
bind-address = 0.0.0.0

# Guardar (Ctrl+O, Enter) y salir (Ctrl+X)

# Reiniciar MySQL
sudo systemctl restart mysql

# Verificar que esté escuchando en todas las interfaces
sudo netstat -tlnp | grep 3306
# Debe mostrar: 0.0.0.0:3306
```

#### Crear Base de Datos y Usuario

```bash
# Conectarse a MySQL
sudo mysql -u root -p
```

```sql
-- Crear la base de datos
CREATE DATABASE bookstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario con acceso remoto
CREATE USER 'bookstore_user'@'%' IDENTIFIED BY 'bookstore_pass';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON bookstore.* TO 'bookstore_user'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user='bookstore_user';

-- Salir
EXIT;
```

####  Verificar Conectividad desde Servidor Flask

```bash
# Desde el servidor Flask (172.31.31.7)

# Instalar cliente MySQL
sudo apt-get install -y mysql-client

# Probar conexión
mysql -h 172.31.25.142 -u bookstore_user -p
# Ingresar contraseña: bookstore_pass

# Si se conecta exitosamente, escribir:
SHOW DATABASES;
EXIT;
```
####  Crear Archivos de Configuración

1) Crear archivo `.env`:

```bash
nano .env
```

Contenido:

```bash
SECRET_KEY=mi_clave_super_secreta_2024_cambiar_en_produccion
DB_HOST=172.31.25.142
DB_USER=bookstore_user
DB_PASS=bookstore_pass
DB_NAME=bookstore
```

2) Crear archivo `docker-compose.prod.yml`:

```bash
nano docker-compose.prod.yml
```

Contenido:

```yaml
version: '3.8'
services:
  flaskapp:
    build: .
    container_name: topicos_flaskapp
    restart: always
    env_file:
      - .env
    ports:
      - "5000:5000"
    networks:
      - app-network
networks:
  app-network:
    driver: bridge
```

3) Crear archivo `Dockerfile`:

```bash
nano Dockerfile
```

Contenido:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

###  Compilación y Construcción de la Imagen Docker

####  Verificar Estructura del Proyecto

```bash
# Ver estructura de archivos
cd ~/Topicos_Tel_P2
ls -la

# Debe contener al menos:
# - app.py
# - Dockerfile
# - docker-compose.prod.yml
# - requirements.txt
# - .env
# - extensions.py
# - models/
# - controllers/
# - templates/
# - static/
```

####  Construir la Imagen Docker

```bash
# Limpiar contenedores e imágenes antiguas (opcional)
docker-compose -f docker-compose.prod.yml down
docker system prune -f

# Construir la imagen Docker
docker-compose -f docker-compose.prod.yml build

# Ver el progreso (ejemplo de salida):
# Step 1/6 : FROM python:3.10-slim
# Step 2/6 : WORKDIR /app
# Step 3/6 : COPY requirements.txt .
# Step 4/6 : RUN pip install --no-cache-dir -r requirements.txt
# Step 5/6 : COPY . .
# Step 6/6 : EXPOSE 5000
# Successfully built ca7ba7dbd030
# Successfully tagged topicos_tel_p2_flaskapp:latest
```
####  Iniciar el Contenedor

```bash
# Levantar el contenedor en modo detached (background)
docker-compose -f docker-compose.prod.yml up -d

# Ver el proceso de inicio (ejemplo de salida):
# Creating network "topicos_tel_p2_default" with the default driver
# Creating topicos_flaskapp ... done
```
####  Probar la Aplicación Localmente

```bash
# Probar desde el servidor
curl http://localhost:5000
# Debe retornar HTML de la página principal

# Probar un endpoint específico
curl http://localhost:5000/health
# Si configuraste el endpoint de health check, debe retornar:
# {"status":"healthy","database":"connected"}
```







---
