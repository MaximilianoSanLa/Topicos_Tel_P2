# 📘 Proyecto 2 – Despliegue en AWS (BookStore Monolítica Escalable)

**Materia:** ST0263 – Tópicos Especiales en Telemática  
**Estudiante:** Juan Camilo Villa – jcvillac@eafit.edu.co  
**Profesor:** [Nombre del profesor] – [correo@eafit.edu.co]  

---

## 🧩 1. Breve descripción de la actividad

El proyecto consiste en desplegar una **aplicación web monolítica desarrollada en Flask** (BookStore) en la nube de **Amazon Web Services (AWS)**, cumpliendo con los primeros dos objetivos del proyecto 2:

1. **Objetivo 1:** Desplegar la aplicación BookStore en dos máquinas virtuales (EC2), una para la aplicación Flask y otra para la base de datos MySQL, usando NGINX, Docker y certificado SSL.
2. **Objetivo 2:** Escalar la aplicación mediante un **Auto Scaling Group**, **Load Balancer**, **Amazon RDS (MySQL)** y **Elastic File System (EFS)**, garantizando alta disponibilidad y balanceo de carga.

---

## ✅ 1.1. Aspectos cumplidos

- Despliegue funcional de la app monolítica Flask con MySQL.  
- Configuración de NGINX como proxy inverso con **Certbot (SSL HTTPS)**.  
- Dockerización del servicio Flask usando `docker-compose`.  
- Conexión estable entre instancias privadas (APP ↔ DB) vía red 172.31.0.0/16.  
- Creación de AMI “Golden” con configuración productiva.  
- Implementación de **Auto Scaling Group**, **Application Load Balancer (ALB)** y **Target Groups**.  
- Integración de almacenamiento compartido **EFS** entre instancias del ASG.  
- Configuración del sistema Flask con `systemd` para autoarranque.  

---

## ⚠️ 1.2. Aspectos NO implementados o pendientes

- Automatización completa del pipeline CI/CD (GitHub Actions).  
- Configuración avanzada de métricas en CloudWatch (solo logs básicos).  
- Certificado SSL en ALB (solo configurado en NGINX localmente).  

---

## 🧠 2. Diseño de alto nivel y arquitectura

### 🧱 Objetivo 1 – Arquitectura monolítica con 2 VMs

```text
                       ┌──────────────────────────────────────┐
Usuario ───►  HTTPS/HTTP│   https://bookstore.duckdns.org     │
                       └──────────────────────────────────────┘
                                      │
                                      ▼
                             ┌────────────────┐
                             │    NGINX       │
                             │  (Proxy inverso│
                             │   + Certbot)   │
                             └───────┬────────┘
                     HTTP:80 / HTTPS:443 │
                     Proxy_pass → 127.0.0.1:5000
                                      │
                                      ▼
                          ┌────────────────────┐
                          │  Flask (Docker)    │
                          │  Puerto 5000/TCP   │
                          └────────┬───────────┘
                                   │
                                   ▼
                     ┌────────────────────────────┐
                     │   VM Base de Datos (MySQL)  │
                     │   Puerto 3306/TCP           │
                     │   Red privada 172.31.0.0/16 │
                     └────────────────────────────┘
