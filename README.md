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

Este documento complementa el README principal con una descripción técnica detallada de los Objetivos 1 y 2, versiones, configuraciones, diagramas y justificación de HTTPS con ALB.

---

## 1) OBJETIVO 1: Aplicación Flask en Docker con MySQL Externo (Actual)

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
| Character Set  | utf8mb4  | Codificación (soporta emojis)                |
| Collation      | utf8mb4_unicode_ci | Reglas de comparación de strings   |

Instalación:

```bash
sudo apt-get update
sudo apt-get install -y mysql-server
sudo systemctl enable mysql
sudo systemctl start mysql
```

#### 1.4.2 Configuración del Servidor MySQL

Archivo: `/etc/mysql/mysql.conf.d/mysqld.cnf`

```ini
[mysqld]
bind-address = 0.0.0.0
port = 3306
max_connections = 151
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
default-storage-engine = InnoDB
```

#### 1.4.3 Base de Datos y Esquema

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
| Outbound| TCP       | ALL    | 0.0.0.0/0        | Internet para actualizaciones   |

#### 1.5.2 Protocolo de Comunicación

```
Cliente → Flask: HTTP (Puerto 5000)
Flask → MySQL: mysql+pymysql (Puerto 3306)
URI de conexión:
mysql+pymysql://bookstore_user:bookstore_pass@172.31.25.142:3306/bookstore
```

---

## 2) OBJETIVO 2: Balanceo de Carga con Application Load Balancer (Próximo paso)

### 2.1 Componentes adicionales

- Application Load Balancer (ALB): Puerto 80, Round Robin, DNS público, health checks.
- Target Group: Gestiona instancias Flask, verifica salud, elimina fallas.
- Múltiples Servidores Flask: 172.31.31.7 (existente) y nueva instancia (por crear) con Docker + Flask + Gunicorn.
- MySQL Compartido: Mismo servidor MySQL 172.31.25.142 para ambas instancias.
- Security Groups actualizados:
  - SG para ALB: Puerto 80 público.
  - SG para Flask: Puerto 5000 solo desde ALB.
  - SG para MySQL: Puerto 3306 desde ambos Flask servers.

### 2.2 Diagrama – Arquitectura Objetivo 2 (Versión 2, colores profesionales)

Leyenda de colores:

- Azul oscuro: Usuarios/Internet
- Azul: ALB
- Cyan: Apps Flask
- Verde: Base de datos
- Rojo: Security Groups
- Gris claro: EC2

```mermaid
flowchart TB
  %% Nodos
  user[Usuarios / Internet\nHTTP 80]:::user
  alb[Application Load Balancer\nListener: 80 (HTTP)\nAlgoritmo: Round Robin\nDNS público]:::alb
  tg[Target Group\nHealth Check: GET /health\nInterval: 30s • Threshold: 2]:::alb

  subgraph az1[EC2 - AZ a]
    ec2a[EC2 Flask #1\nGunicorn 4 workers\nDocker\n:5000]:::ec2
  end
  subgraph az2[EC2 - AZ b]
    ec2b[EC2 Flask #2\nGunicorn 4 workers\nDocker\n:5000]:::ec2
  end

  db[(MySQL Server\n172.31.25.142:3306\nBind: 0.0.0.0)]:::db

  sg_alb[SG-ALB\nInbound: 80 0.0.0.0/0\nOutbound: 5000 → SG-FLASK]:::sg
  sg_flask[SG-FLASK\nInbound: 5000 desde SG-ALB\nOutbound: 3306 → SG-DB]:::sg
  sg_db[SG-DB\nInbound: 3306 desde SG-FLASK]:::sg

  %% Conexiones
  user -->|HTTP 80| alb --> tg
  tg -->|HTTP 5000| ec2a
  tg -->|HTTP 5000| ec2b
  ec2a -->|mysql+pymysql 3306| db
  ec2b -->|mysql+pymysql 3306| db

  %% Estilos
  classDef user fill:#0a3d62,stroke:#082d49,color:#ffffff;
  classDef alb fill:#2471A3,stroke:#1B4F72,color:#ffffff;
  classDef ec2 fill:#ECECEC,stroke:#B3B3B3,color:#111111;
  classDef db fill:#1E8449,stroke:#145A32,color:#ffffff;
  classDef sg fill:#C0392B,stroke:#922B21,color:#ffffff;
```

### 2.3 ALB (Application Load Balancer)

| Parámetro         | Valor                                 |
|-------------------|---------------------------------------|
| Tipo              | Application Load Balancer (L7)        |
| Esquema           | Internet-facing                       |
| IP Version        | IPv4                                  |
| AZs               | us-east-1a, us-east-1b                |
| Listener          | HTTP :80                              |
| DNS Name          | alb-bookstore-xxxxxx.us-east-1.elb.amazonaws.com |

Configuración del Listener (ejemplo):

```json
{
  "Protocol": "HTTP",
  "Port": 80,
  "DefaultActions": [{
    "Type": "forward",
    "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/flask-tg"
  }]
}
```

### 2.4 Target Group

| Parámetro              | Valor            | Descripción                                 |
|------------------------|------------------|---------------------------------------------|
| Target Type            | instance         | Instancias EC2 como targets                 |
| Protocol               | HTTP             | Protocolo de comunicación                   |
| Port                   | 5000             | Puerto de la aplicación Flask               |
| Health Check Protocol  | HTTP             | Protocolo para verificación                 |
| Health Check Path      | /health          | Endpoint de verificación                    |
| Interval               | 30               | Segundos entre verificaciones               |
| Timeout                | 5                | Timeout por verificación                    |
| Healthy Threshold      | 2                | Éxitos para marcar healthy                  |
| Unhealthy Threshold    | 2                | Fallos para marcar unhealthy                |
| Success Codes          | 200              | Código HTTP esperado                        |
| Sticky Sessions        | Disabled         | Sin afinidad de sesión                      |
| Algoritmo              | Round Robin      | Distribución equitativa                     |

Endpoint de health check (en `app.py`):

```python
@app.route('/health')
def health_check():
    try:
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503
```

### 2.5 Servidores de Aplicación

#### 2.5.1 Servidor Flask 1 (Existente)

- IP Privada: 172.31.31.7
- Availability Zone: us-east-1a
- Configuración: Idéntica al Objetivo 1
- Estado: Registrado en Target Group

#### 2.5.2 Servidor Flask 2 (Nueva Instancia)

| Componente       | Especificación                      |
|------------------|--------------------------------------|
| IP Privada       | 172.31.XX.XX (auto-asignada)        |
| Availability Zone| us-east-1b                           |
| Tipo de Instancia| t2.micro                             |
| SO               | Ubuntu 22.04 LTS                     |
| Docker           | 24.0.7                               |
| Docker Compose   | 2.21.0                               |
| Python           | 3.10.12                              |
| Configuración    | Clon exacto del Servidor 1           |

Proceso de clonación:

```bash
# En Servidor 1, crear imagen AMI
aws ec2 create-image --instance-id i-xxxxx --name "flask-app-image"

# Lanzar Servidor 2 desde la AMI
aws ec2 run-instances --image-id ami-xxxxx --instance-type t2.micro

# O manualmente: copiar archivos y configurar
scp -r ~/Topicos_Tel_P2 ubuntu@172.31.XX.XX:~/
```

Mismo stack tecnológico:

- Python 3.10.12, Flask 3.0.0, Gunicorn 21.2.0, y dependencias del `requirements.txt`.

#### 2.5.3 Base de Datos Compartida

Ambos servidores Flask apuntan al mismo MySQL:

```bash
# .env en Servidor 1 y Servidor 2
DB_HOST=172.31.25.142
DB_USER=bookstore_user
DB_PASS=bookstore_pass
DB_NAME=bookstore
```

Ventajas:

- Consistencia de datos, un solo punto de verdad, simplicidad operativa.

Consideraciones de rendimiento:

- Max Connections MySQL: 151
- Conexiones por Flask: ~10-20 (con pooling)
- Total estimado: 20-40 conexiones (suficiente para t2.micro)

### 2.6 Security Groups Actualizados

#### 2.6.1 Security Group - ALB

| Tipo    | Protocolo | Puerto | Origen     | Descripción      |
|---------|-----------|--------|------------|------------------|
| Inbound | TCP       | 80     | 0.0.0.0/0  | HTTP público     |
| Outbound| TCP       | 5000   | sg-flask   | Forward a Flask  |

#### 2.6.2 Security Group - Flask Servers

| Tipo    | Protocolo | Puerto | Origen     | Descripción            |
|---------|-----------|--------|------------|------------------------|
| Inbound | TCP       | 22     | 0.0.0.0/0  | SSH administración     |
| Inbound | TCP       | 5000   | sg-alb     | Tráfico desde ALB      |
| Outbound| TCP       | 3306   | 172.31.25.142/32 | Conexión a MySQL |
| Outbound| TCP       | ALL    | 0.0.0.0/0  | Internet               |

#### 2.6.3 Security Group - MySQL Server

| Tipo    | Protocolo | Puerto | Origen     | Descripción                 |
|---------|-----------|--------|------------|-----------------------------|
| Inbound | TCP       | 22     | 0.0.0.0/0  | SSH administración          |
| Inbound | TCP       | 3306   | sg-flask   | Conexiones desde Flask      |
| Outbound| TCP       | ALL    | 0.0.0.0/0  | Internet                    |

### 2.7 Herramientas de Monitoreo y Gestión

| Herramienta | Versión  | Propósito                                  |
|-------------|----------|--------------------------------------------|
| AWS CLI     | 2.13.25  | Gestión de recursos AWS desde CLI          |
| curl        | 7.81.0   | Testing de endpoints HTTP                  |
| netstat     | 1.60     | Diagnóstico de red                         |
| docker logs | Built-in | Visualización de logs de contenedores      |
| CloudWatch  | AWS      | Métricas y logs (si está habilitado)       |

Comandos útiles:

```bash
# Ver logs del contenedor
docker-compose -f docker-compose.prod.yml logs -f

# Ver estado de targets en ALB
aws elbv2 describe-target-health --target-group-arn arn:xxx

# Probar health check
curl http://localhost:5000/health

# Ver conexiones MySQL activas
mysql -u root -p -e "SHOW PROCESSLIST;"
```

### 2.8 Flujo de Tráfico Completo

```
Usuario
  ↓ HTTP:80
Application Load Balancer
  ↓ Round Robin
  ├→ Flask Server 1 (172.31.31.7:5000)
  │   ↓ mysql+pymysql
  │   MySQL Server (172.31.25.142:3306)
  │
  └→ Flask Server 2 (172.31.XX.XX:5000)
      ↓ mysql+pymysql
      MySQL Server (172.31.25.142:3306)
```

---

## 3) Justificación: Limitaciones para Implementar HTTPS en el ALB

### 3.1 Requisito de Certificado SSL/TLS

- ACM (gratuito) o certificado de terceros requieren dominio registrado y validado.
- No se puede emitir certificado para una IP pública o el DNS genérico del ALB.

Problema:

- No se cuenta con un dominio propio; el DNS del ALB no es certificable sin dominio.

### 3.2 Proceso de Validación de Dominio (ACM)

1) Registrar dominio (Route 53 u otro).  
2) Solicitar certificado en ACM (validación DNS o email).  
3) Apuntar el dominio al ALB (registro Alias A).  

Limitaciones del proyecto:

- Sin presupuesto para dominio; dominios gratuitos suelen fallar con ACM.

### 3.3 Alternativas Evaluadas (y por qué no se usaron)

- Certificado auto-firmado: advertencias de navegador; no apto producción.
- Let’s Encrypt (Certbot): requiere dominio válido y validación HTTP-01.
- Cloudflare Flexible: requiere dominio; no cifra extremo a extremo.

### 3.4 Configuración Actual (HTTP)

```yaml
Application Load Balancer:
  - Listener: Puerto 80 (HTTP)
  - Target Group: Puerto 5000 (HTTP)
  - Security Group: Permite 0.0.0.0/0 en puerto 80
```

Ventajas académicas: simplicidad, sin costos, facilita pruebas y cumple objetivos de balanceo/HA.  
Desventajas: tráfico sin cifrar; no apto para producción.

### 3.5 Recomendaciones Futuras para HTTPS

1) Registrar dominio (~$10–15 USD/año).  
2) Solicitar certificado en ACM (DNS validation).  
3) Configurar Listener 443 con certificado ACM y redirección 80→443.  
4) Apuntar dominio al ALB con Alias en Route 53.  

Costos mínimos: Dominio $10–15 USD/año; Certificado ACM $0.

---

Fin del documento.









