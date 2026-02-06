# Hoja de Ruta Técnica para la Transición a SaaS

Este documento detalla los cambios técnicos necesarios para transformar el prototipo actual en una aplicación SaaS multi-usuario, siguiendo la estructura de planes discutida.

## 1. Base de Datos y Almacenamiento de Datos

El cambio más fundamental es reemplazar el almacenamiento basado en archivos (`.csv`, `.json`) por una base de datos relacional robusta.

*   **Acción:**
    *   Seleccionar una base de datos relacional (ej. PostgreSQL, MySQL).
    *   Diseñar el esquema de la base de datos para almacenar:
        *   Usuarios (con información de autenticación).
        *   Perfiles de Empresa (vinculados a usuarios).
        *   Clientes (vinculados a perfiles de empresa).
        *   Facturas (vinculadas a perfiles de empresa y clientes).
        *   Ítems de Factura.
    *   Migrar los datos existentes (si los hay) de CSV/JSON a la base de datos.
    *   Actualizar el backend de FastAPI para interactuar con la base de datos utilizando un ORM (ej. SQLAlchemy con Pydantic para FastAPI).

## 2. Autenticación y Autorización de Usuarios

Para un modelo SaaS, cada usuario (empresa) necesita su propia cuenta segura.

*   **Acción:**
    *   Implementar un sistema de registro y login de usuarios.
    *   Utilizar JWT (JSON Web Tokens) para la autenticación de API.
    *   Añadir middleware de autenticación en FastAPI para proteger los endpoints.
    *   Implementar autorización para asegurar que un usuario solo pueda acceder a sus propios datos (multi-tenancy).

## 3. Implementación de Multi-tenancy (Multi-empresa)

Cada empresa que use el SaaS debe tener sus datos aislados de otras empresas.

*   **Acción:**
    *   Modificar todos los modelos de datos (clientes, facturas, perfil de empresa) para incluir un `company_id` o `user_id` que los vincule a la empresa/usuario autenticado.
    *   Asegurar que todas las consultas a la base de datos incluyan filtros por este `company_id`/`user_id`.

## 4. Integración Real con SIFEN

Reemplazar la simulación actual por la comunicación real con el sistema de facturación electrónica de Paraguay.

*   **Acción:**
    *   Investigar a fondo la documentación técnica del SIFEN (APIs, formatos XML, requisitos de firma digital).
    *   Implementar la generación de XMLs conforme a los estándares del SIFEN.
    *   Integrar una librería para la firma digital de los XMLs (requiere el certificado digital).
    *   Desarrollar la lógica para enviar los XMLs firmados al SIFEN y procesar sus respuestas (CDC, estado de la factura).
    *   Manejar los errores y reintentos de comunicación con el SIFEN.

## 5. Gestión de Certificados Digitales

Los certificados digitales son un requisito para la firma de DTEs.

*   **Acción:**
    *   Definir cómo los usuarios cargarán y gestionarán sus certificados digitales en la plataforma.
    *   Implementar almacenamiento seguro para los certificados (ej. en un servicio de gestión de secretos o en la base de datos cifrada).

## 6. Envío de Correos Electrónicos

La función actual es un placeholder.

*   **Acción:**
    *   Integrar un servicio de envío de correos (ej. SendGrid, Mailgun, o un servidor SMTP propio).
    *   Diseñar plantillas de correo para el envío de facturas (KUDE + XML).

## 7. Frontend (React/TypeScript)

Adaptar el frontend para interactuar con el nuevo backend autenticado y multi-tenant.

*   **Acción:**
    *   Implementar páginas de registro y login.
    *   Manejar tokens de autenticación (ej. JWT) en el cliente.
    *   Actualizar las llamadas a la API para incluir el token de autenticación.
    *   Añadir lógica para mostrar/ocultar funcionalidades según el plan de suscripción del usuario (ej. si está en el plan gratuito, limitar la cantidad de facturas).

## 8. Despliegue y Escalabilidad

Preparar la aplicación para un entorno de producción.

*   **Acción:**
    *   Contener la aplicación usando Docker.
    *   Configurar un entorno de producción en la nube (ej. AWS, Google Cloud, DigitalOcean, Render) con:
        *   Servidor de aplicaciones (FastAPI con Uvicorn).
        *   Base de datos gestionada.
        *   Balanceador de carga.
        *   Servicio de almacenamiento de archivos (para KUDEs generados, si no se almacenan en la DB).
        *   Monitoreo y logging.

## 9. Implementación de Planes de Suscripción

Integrar la lógica de los planes de pago.

*   **Acción:**
    *   Definir los planes en la base de datos (nombre, precio, límites, características).
    *   Integrar una pasarela de pagos (ej. Stripe, o una local de Paraguay).
    *   Desarrollar la lógica para asignar planes a los usuarios y aplicar los límites correspondientes.
    *   Implementar la lógica para la gestión de la suscripción (cambio de plan, cancelación).

---

Este roadmap proporciona una visión general de las tareas principales. Cada punto se puede desglosar en subtareas más pequeñas.

¿Te parece que este documento captura los cambios técnicos clave que debemos considerar?

---
## 10. Funcionalidades Adicionales (Potenciadas por IA)

Esta sección describe funcionalidades avanzadas que pueden ser implementadas después de la migración a SaaS para añadir un valor diferencial significativo, especialmente para los planes de suscripción más altos.

### 10.1. Consulta de Datos con Lenguaje Natural

*   **Objetivo:** Permitir a los usuarios obtener información y reportes de su negocio haciendo preguntas en lenguaje normal, en lugar de usar filtros y menús complejos.
*   **Arquitectura Propuesta:**
    1.  **Interfaz (Frontend):** Un componente de chat o una barra de búsqueda avanzada en el panel principal de la aplicación.
    2.  **Interpretación (IA):** La pregunta del usuario se envía a un Modelo de Lenguaje Grande (LLM). La tarea principal del LLM es analizar la pregunta y **traducirla a una consulta estructurada** (ej. SQL) que pueda ser ejecutada por la base de datos.
    3.  **Validación y Ejecución (Backend):** El backend recibe la consulta SQL generada por la IA. Por seguridad, se debe validar la consulta para prevenir inyecciones de SQL y asegurar que solo acceda a los datos permitidos para ese usuario. Luego, la ejecuta en la base de datos.
    4.  **Presentación de Resultados (Frontend):** El resultado de la base de datos se envía de vuelta al frontend, que lo formatea de manera legible para el usuario (un texto, una tabla, un gráfico, etc.).
*   **Consideraciones:**
    *   Esta funcionalidad sería un gran atractivo para el "Plan Empresarial".
    *   Requiere una cuidadosa implementación de la capa de validación para garantizar la seguridad.
    *   Se necesita un "prompt" bien diseñado para que el LLM traduzca las preguntas a SQL de manera consistente y correcta según el esquema de la base de datos.