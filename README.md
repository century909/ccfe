# Ficha de Proyecto: CCFE (Sistema de Facturación Electrónica - Paraguay)

## 🌟 Resumen Ejecutivo
Prototipo avanzado de un sistema de facturación electrónica adaptado a la normativa paraguaya (SIFEN). La aplicación permite la gestión integral de emisores y clientes, garantizando cálculos fiscales precisos y la generación de documentos legales en formato digital.

## 🛠️ Stack Tecnológico
- **Backend:** FastAPI (Python) - Seleccionado por su alto rendimiento y validación de datos automática.
- **Frontend:** React + TypeScript + Bootstrap - Interfaz dinámica, segura y responsiva.
- **Generación de Documentos:** ReportLab (Python) para la creación de PDFs dinámicos.
- **Persistencia:** Estructura de datos optimizada en JSON y CSV para máxima agilidad.

## 🚀 Funcionalidades Clave
- **Generación de KuDE (PDF):** Creación automática de la Representación Gráfica de la Factura Electrónica, incluyendo placeholders para códigos CDC y QR conforme a SIFEN.
- **Motor de Cálculo Fiscal:** Desglose automático y preciso de IVA (10%, 5% y Exenta) basado en los ítems de la factura.
- **Gestión de Emisor (Timbrado):** Configuración completa del perfil de empresa, incluyendo datos de timbrado y actividades económicas.
- **Módulo de Clientes:** Base de datos con búsqueda inteligente y autocompletado por RUC para agilizar la emisión.
- **API RESTful:** Arquitectura limpia con endpoints validados para integración con sistemas externos.

## 💡 Desafío Técnico Superado
**El Problema:** La complejidad de cumplir con el formato visual y los cálculos matemáticos exigidos por la SET (Secretaría de Estado de Tributación) para los documentos electrónicos.
**La Solución:** Desarrollé un motor de renderizado dinámico utilizando **ReportLab** que traduce objetos de datos complejos en un documento PDF (KuDE) profesional. Implementé una lógica de redondeo y prorrateo de IVA que asegura que los totales coincidan exactamente con las exigencias legales, facilitando la futura transición a una integración real con los servidores de SIFEN.

---
*Proyecto desarrollado por Diego Centurión.*
