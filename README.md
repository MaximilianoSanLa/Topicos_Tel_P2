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

---

## 💻 3. Ambiente de desarrollo

- Lenguaje: Python 3.10
- Framework: Flask
- Servidor de aplicación: Gunicorn
- Web Server: NGINX
- Base de datos: MySQL
- Contenedores: Docker / Docker Compose
- SO: Ubuntu Server 22.04 LTS
- Certificados SSL: Let’s Encrypt (Certbot)

### 🔧 Dependencias principales (`requirements.txt`)

```
flask==2.3.3
flask_sqlalchemy
flask_login
pymysql
werkzeug
gunicorn
```

---

## 🌐 4. Ambiente de ejecución (producción)

| Recurso              | Descripción                                 |
|----------------------|---------------------------------------------|
| Región AWS           | us-east-1                                   |
| App Flask            | EC2 (Auto Scaling Group)                    |
| Balanceador          | Application Load Balancer (HTTP:80/HTTPS:443)|
| Base de datos        | Amazon RDS (MySQL 8.0)                      |
| Storage compartido   | Elastic File System (EFS)                   |
| Certificado SSL      | ACM (en ALB) o Certbot (NGINX)              |
| Sistema operativo    | Ubuntu Server 22.04                         |
| Dominio              | bookstore.duckdns.org                       |
| Puertos abiertos     | 22, 80, 443, 5000 (interno), 3306, 2049     |

---

## 🧾 5. Variables de entorno (`.env`)

```
SECRET_KEY=mi-clave-super-secreta-12345
DB_HOST=172.31.xx.xx
DB_USER=bookstore_user
DB_PASS=bookstore_pass
DB_NAME=bookstore
FLASK_ENV=production
```

> Nota: En el Objetivo 2, `DB_HOST` debe apuntar al endpoint de Amazon RDS.

---

## ⚙️ 6. Comandos clave

### Construir contenedor Flask
```
docker-compose -f docker-compose.prod.yml build
```

### Ejecutar aplicación
```
docker-compose -f docker-compose.prod.yml up -d
```

### Inicializar base de datos (tablas)
```
docker-compose -f docker-compose.prod.yml exec flaskapp python -c \
"from app import app, db; app.app_context().push(); db.create_all()"
```

### Verificar el servicio
```
curl http://localhost:5000/
```

---

## 🚀 7. Ejecución como servicio (systemd)

Archivo `bookstore.service` para ejecutar Flask como servicio persistente:

```
[Unit]
Description=BookStore Flask Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/st0263-252/proyecto2/BookStore-monolith
EnvironmentFile=/home/ubuntu/st0263-252/proyecto2/BookStore-monolith/.env
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Comandos de operación
```
sudo systemctl start bookstore.service
sudo systemctl status bookstore.service
sudo systemctl enable bookstore.service
```

---

## 📦 8. Docker Compose (producción / ejemplo)

> Nota: Para Objetivo 2 (RDS), el servicio `db` no se utiliza; se reemplaza por RDS. Este archivo es útil para desarrollo/local o para Objetivo 1.

```
version: "3.8"
services:
  flaskapp:
    build: .
    container_name: bookstore-flask
    restart: always
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - .:/app
  db:
    image: mysql:8.0
    container_name: bookstore-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: bookstore
      MYSQL_DATABASE: bookstore
    ports:
      - "3306:3306"
```

---

## 👩‍💻 9. Flujo de uso de la aplicación

1) El usuario accede por el dominio público (HTTPS).  
2) NGINX (o ALB) redirige el tráfico al backend Flask (puerto 5000).  
3) Flask se conecta a MySQL (en VM o RDS) para almacenamiento persistente.  
4) Los archivos estáticos/subidas se guardan en EFS compartido entre instancias del ASG.

---

## 📷 10. Evidencias y pruebas

| Fase        | Descripción                                | Evidencia |
|-------------|--------------------------------------------|-----------|
| Objetivo 1  | Flask + MySQL con NGINX (2 VMs)            | [Agregar] |
| Objetivo 2  | ALB + ASG + RDS + EFS (Escalable)          | [Agregar] |
| Docker      | Contenedores Flask y MySQL (Compose)       | [Agregar] |

> Recomendado: incluir capturas de ALB, ASG (instancias InService), RDS (endpoint/seguridad), EFS (mount targets), NGINX/certbot (certificado válido) y pruebas de balanceo.

---

## 📊 11. Comparación entre Objetivos

| Característica         | Objetivo 1          | Objetivo 2                       |
|------------------------|---------------------|----------------------------------|
| Escalabilidad          | Manual (2 VMs)      | Automática (ASG)                 |
| Balanceo de carga      | NGINX local         | Application Load Balancer (ALB)  |
| Base de datos          | MySQL en VM         | Amazon RDS (MySQL)               |
| Almacenamiento         | Local               | EFS compartido                   |
| Alta disponibilidad    | No                  | Sí (Multi-AZ)                    |
| Recuperación automática| No                  | Sí                               |
| Costo estimado         | ~$15/mes            | ~$75/mes                         |

---

## 🌎 12. Dominio y acceso

- Dominio: `https://bookstore.duckdns.org`
- Puertos: 22 (SSH), 80 (HTTP), 443 (HTTPS), 5000 (interno app), 3306 (MySQL), 2049 (NFS)

---

## 🛡️ 13. Buenas prácticas implementadas

- Separación de roles y segmentos (app y base de datos en redes/SG distintos).
- Proxy inverso con TLS (Let’s Encrypt) o ACM en ALB.
- Uso de variables de entorno para secretos y configuración.
- Aislamiento de la app con Docker y `systemd` para resiliencia.
- AMI “Golden” para escalar rápidamente con ASG.
- EFS para compartir almacenamiento entre réplicas del ASG.
- Health checks configurados en ALB para alta disponibilidad.

---

## 🚧 14. Pendientes / Próximos pasos

- Pipeline CI/CD con GitHub Actions (build, test, deploy).
- Métricas y alarmas avanzadas con CloudWatch (CPU, latencia, errores).
- Migración completa a SSL gestionado por ALB (ACM) y HTTP→HTTPS redirect.
- Backups y rotación de contraseñas/secretos (AWS Secrets Manager).

---

## 📜 Licencia

Proyecto académico para la materia ST0263. Uso educativo.


