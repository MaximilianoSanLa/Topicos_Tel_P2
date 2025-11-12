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

## 🧠 2. Diseño de alto nivel y arquitectura

### 🧱 Objetivo 1 – Arquitectura monolítica con 2 VMs


<img width="382" height="431" alt="image" src="https://github.com/user-attachments/assets/1259afe6-ba1a-488b-a327-84736b7ce9b9" />



Patrón: Arquitectura monolítica tradicional con separación de capas (app y base de datos).  
Buenas prácticas: Uso de proxy inverso, variables de entorno, aislamiento con Docker y acceso restringido por Security Groups.

### ☁️ Objetivo 2 – Arquitectura monolítica escalable con servicios gestionados


<img width="733" height="747" alt="image" src="https://github.com/user-attachments/assets/4c757ad1-b9f9-4ec4-8d75-d3c2d5b81a8f" />



Patrón: Monolithic Web App con escalamiento elástico y almacenamiento compartido (ALB + ASG + RDS + EFS).  
Buenas prácticas: Infraestructura redundante, health checks en ALB/ASG y persistencia compartida en EFS.

# Proyecto 2 – Detalle Técnico por Objetivos (Docker, ALB, TG, SG, MySQL)
### 1.1 Componentes

- Servidor Flask (172.31.31.7)
  - Contenedor Docker con Flask App
  - Gunicorn como servidor WSGI
  - Puerto 5000 expuesto
  - Variables de entorno desde `.env`
- Servidor MySQL (172.31.25.142)
  - MySQL Server escuchando en 0.0.0.0:3306
  - Base de datos `bookstore`
- Security Groups
  - SG1: Permite puerto 5000 para usuarios externos
  - SG2: Permite puerto 3306 solo desde 172.31.31.7

### 1.2 Infraestructura Cloud

| Componente                 | Especificación                          | Versión/Detalles                 |
|---------------------------|------------------------------------------|----------------------------------|
| Proveedor Cloud           | Amazon Web Services (AWS)                | -                                |
| Región                    | US-East-1 (Virginia del Norte)          | -                                |
| Servicio de Cómputo       | EC2 (Elastic Compute Cloud)              | -                                |
| Tipo de Instancia - App   | t2.micro                                 | 1 vCPU, 1 GB RAM                 |
| Tipo de Instancia - DB    | t2.micro                                 | 1 vCPU, 1 GB RAM                 |
| Sistema Operativo         | Ubuntu Server                            | 22.04 LTS (Jammy Jellyfish)      |
| Arquitectura              | x86_64                                   | 64-bit                           |

### 1.3 Servidor de Aplicación (IP: 172.31.31.7)

#### 1.3.1 Sistema Base

- Sistema Operativo: Ubuntu 22.04 LTS
- Kernel: Linux 5.15.0-1023-aws
- Arquitectura: x86_64
- Hostname: ip-172-31-31-7

#### 1.3.2 Plataforma de Contenedores

| Componente    | Versión  | Descripción                          |
|---------------|----------|--------------------------------------|
| Docker Engine | 24.0.7   | Motor de contenedores                |
| Docker Compose| 2.21.0   | Orquestación de contenedores         |
| containerd    | 1.6.24   | Runtime de contenedores              |
| Docker API    | 1.43     | API para gestión de contenedores     |

Instalación realizada:

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

#### 1.3.3 Lenguaje de Programación y Runtime

| Componente  | Versión  | Fuente                               |
|-------------|----------|--------------------------------------|
| Python      | 3.10.12  | Imagen base Docker: python:3.10-slim |
| pip         | 23.3.1   | Gestor de paquetes Python            |
| setuptools  | 68.2.2   | Herramientas de empaquetado          |
| wheel       | 0.41.3   | Formato de distribución Python       |

Imagen base Docker:

```dockerfile
FROM python:3.10-slim
# Debian 12 (Bookworm) como sistema base
# Python 3.10.12 preinstalado
```

#### 1.3.4 Framework Web y Dependencias (requirements.txt)

```txt
# Framework Web
Flask==3.0.0
Werkzeug==3.0.1
Jinja2==3.1.2
itsdangerous==2.1.2
click==8.1.7

# ORM y Base de Datos
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
PyMySQL==1.1.0
cryptography==41.0.7

# Autenticación y Sesiones
Flask-Login==0.6.3

# Servidor WSGI de Producción
gunicorn==21.2.0

# Gestión de Variables de Entorno
python-dotenv==1.0.0

# Utilidades
MarkupSafe==2.1.3
greenlet==3.0.1
```

Descripción de dependencias (propósitos principales):

- Flask 3.0.0: Framework web principal.
- Flask-SQLAlchemy 3.1.1 y SQLAlchemy 2.0.23: ORM y capa de acceso a datos.
- PyMySQL 1.1.0: Driver MySQL.
- Flask-Login 0.6.3: Autenticación/sesiones.
- cryptography 41.0.7: Cifrado.
- gunicorn 21.2.0: Servidor WSGI de producción.
- python-dotenv 1.0.0: Carga de variables de entorno.

#### 1.3.5 Configuración de Docker

Archivo: `Dockerfile`

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

Archivo: `docker-compose.prod.yml`

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

Especificaciones:

- Directorio de trabajo: `/app`
- Puerto expuesto: 5000
- Inicio: Gunicorn con 4 workers en 0.0.0.0:5000
- Restart: `always`
- Network driver: `bridge`

#### 1.3.6 Variables de Entorno

Archivo: `.env`

```bash
# Seguridad
SECRET_KEY=clave_secreta_flask_para_sesiones_y_csrf

# Configuración de Base de Datos
DB_HOST=172.31.25.142
DB_USER=bookstore_user
DB_PASS=bookstore_pass
DB_NAME=bookstore
```

Propósito:

- SECRET_KEY: Firmar sesiones y tokens CSRF.
- DB_HOST/USER/PASS/NAME: Conexión a MySQL.

### 1.4 Servidor de Base de Datos (IP: 172.31.25.142)

#### 1.4.1 Sistema Gestor de Base de Datos

| Componente     | Versión  | Descripción                                  |
|----------------|----------|----------------------------------------------|
| MySQL Server   | 8.0.35   | Sistema gestor de base de datos relacional   |
| MySQL Client   | 8.0.35   | Cliente de línea de comandos                 |
| InnoDB         | 8.0.35   | Motor de almacenamiento transaccional        |


Instalación:

```bash
sudo apt-get update
sudo apt-get install -y mysql-server
sudo systemctl enable mysql
sudo systemctl start mysql
```



#### 1.4.2 Base de Datos y Esquema

```sql
-- Base de datos
CREATE DATABASE bookstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usuario y permisos
CREATE USER 'bookstore_user'@'%' IDENTIFIED BY 'bookstore_pass';
GRANT ALL PRIVILEGES ON bookstore.* TO 'bookstore_user'@'%';
FLUSH PRIVILEGES;
```

Tablas principales (conceptual):

- `users`, `books`, `purchases`, `payments`, `deliveries`, `delivery_providers`.

### 1.5 Seguridad y Networking

#### 1.5.1 Security Groups

Security Group 1 - Servidor Flask (172.31.31.7):

| Tipo    | Protocolo | Puerto | Origen           | Descripción                 |
|---------|-----------|--------|------------------|-----------------------------|
| Inbound | TCP       | 22     | 0.0.0.0/0        | SSH para administración     |
| Inbound | TCP       | 5000   | 0.0.0.0/0        | Acceso a aplicación Flask   |
| Outbound| TCP       | 3306   | 172.31.25.142/32 | Conexión a MySQL            |
| Outbound| TCP       | ALL    | 0.0.0.0/0        | Internet para actualizaciones |

Security Group 2 - Servidor MySQL (172.31.25.142):

| Tipo    | Protocolo | Puerto | Origen           | Descripción                     |
|---------|-----------|--------|------------------|---------------------------------|
| Inbound | TCP       | 22     | 0.0.0.0/0        | SSH para administración         |
| Inbound | TCP       | 3306   | 172.31.31.7/32   | Conexión desde Flask (app)      |

#### 1.5.2 Protocolo de Comunicación

```
Cliente → Flask: HTTP (Puerto 5000)
Flask → MySQL: mysql+pymysql (Puerto 3306)
URI de conexión:
mysql+pymysql://bookstore_user:bookstore_pass@172.31.25.142:3306/bookstore
```

---
