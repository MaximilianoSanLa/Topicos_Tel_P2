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






