## 1.1 Aspectos CUMPLIDOS de la actividad propuesta

### 🎯 Objetivo 1 - Despliegue Monolítico

- Aplicación **Flask + MySQL** en 2 VMs separadas  
- **NGINX** como proxy reverso configurado  
- **Dominio DuckDNS** funcionando  
- **Security Groups AWS** configurados correctamente  
- Todas las funcionalidades de **BookStore** operativas  
- Comunicación entre VMs vía red privada AWS  

---

### ☁️ Objetivo 2 - Escalamiento en AWS

- **Amazon RDS MySQL** implementado y funcional  
- **Amazon EFS** configurado y montado en instancias  
- **AMI personalizada** creada con aplicación preinstalada  
- **Launch Template** y **Auto Scaling Group** operativos  
- **Application Load Balancer** configurado  
- **Target Group** con health checks  
- Políticas de **auto-scaling basadas en CPU**  
- Tráfico compartido con aplicación **RDS-EFS**

---

### 🐳 Objetivo 3 - Kubernetes EKS

- Despliegue funcional de app **BookStore monolítica** en clúster EKS  
- **Almacenamiento persistente** para MySQL  
- **Exposición del servicio mediante NodePort**  
- **Imagen Docker** publicada en **Amazon ECR**  
- Recursos Kubernetes: *Namespace, PersistentVolume, Deployments, Services*  
- Comunicación interna por red de Kubernetes  

---
