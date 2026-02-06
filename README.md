# Sistema de Facturación Electrónica para Paraguay (Prototipo)

Este proyecto es una aplicación web full-stack diseñada para la emisión de facturas electrónicas en Paraguay. Permite la gestión de clientes, perfiles de empresa y la generación de una representación gráfica (KUDE) de la factura en formato PDF.

## Características Implementadas

- **Backend:**
  - API RESTful construida con **FastAPI** (Python).
  - **Gestión de Perfil de Empresa:** Permite guardar y recuperar los datos de la empresa emisora (guardado en `company_profile.json`).
  - **Gestión de Clientes:** Permite registrar nuevos clientes y obtener la lista de clientes existentes (guardado en `clients.csv`).
  - **Generación de Facturas:**
    - Endpoint para recibir datos de la factura.
    - **Generación de KUDE (PDF):** Crea una representación gráfica de la factura en formato PDF utilizando la librería `reportlab`. El diseño está basado en un KUDE real.
    - **Cálculo de IVA Detallado:** Calcula el desglose del IVA (10%, 5%, Exenta) basado en los ítems de la factura.
    - **Registro de Facturas:** Guarda un registro de cada factura emitida en `invoices.csv`.
  - **Simulación de SIFEN y Email:** Contiene funciones placeholder para la integración con SIFEN y el envío de correos, listas para ser implementadas.

- **Frontend:**
  - Aplicación de una sola página (SPA) construida con **React** y **TypeScript**.
  - **Diseño Responsivo:** Utiliza **Bootstrap** para una interfaz limpia y adaptable.
  - **Formulario de Facturación:**
    - Formulario dinámico para añadir múltiples ítems.
    - Selección de tasa de IVA (10%, 5%, Exenta) por ítem.
    - Cálculo de totales en tiempo real.
  - **Gestión de Clientes:**
    - Formulario para registrar nuevos clientes.
    - **Autocompletado:** Campo de búsqueda de clientes por RUC que autocompleta los datos en el formulario de facturación.
  - **Gestión de Perfil de Empresa:** Formulario para que el usuario configure los datos de su empresa.

## Tecnologías Utilizadas

- **Backend:** Python, FastAPI, Uvicorn, ReportLab
- **Frontend:** React, TypeScript, Bootstrap
- **Formato de Datos:** JSON, CSV

## Estructura del Proyecto

```
/
├── backend/
│   ├── venv/                   # Entorno virtual de Python
│   ├── kudes/                  # Directorio donde se guardan los PDFs generados
│   ├── main.py                 # Lógica principal de la API (FastAPI)
│   ├── clients.csv             # Base de datos de clientes
│   ├── invoices.csv            # Registro de facturas emitidas
│   └── company_profile.json    # Datos de la empresa emisora
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.tsx             # Componente principal de la aplicación
│   │   ├── ClientForm.tsx      # Formulario para registrar clientes
│   │   └── CompanyProfileForm.tsx # Formulario para el perfil de la empresa
│   ├── package.json
│   └── ...
│
└── README.md                   # Este archivo
```

## Configuración y Ejecución

### Backend

1.  **Navegar al directorio del backend:**
    ```bash
    cd backend
    ```
2.  **Activar el entorno virtual:**
    ```bash
    source venv/bin/activate
    ```
3.  **Iniciar el servidor:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    El servidor estará disponible en `http://localhost:8000`.

### Frontend

1.  **Navegar al directorio del frontend:**
    ```bash
    cd frontend
    ```
2.  **Instalar dependencias (solo la primera vez):**
    ```bash
    npm install
    ```
3.  **Iniciar el servidor de desarrollo:**
    ```bash
    npm start
    ```
    La aplicación se abrirá automáticamente en `http://localhost:3000`.

## Endpoints de la API (Resumen)

- `GET /`: Mensaje de bienvenida.
- `POST /company-profile`: Guarda o actualiza el perfil de la empresa.
- `GET /company-profile`: Obtiene el perfil de la empresa guardado.
- `POST /clients`: Registra un nuevo cliente.
- `GET /clients`: Obtiene la lista de todos los clientes.
- `POST /invoice`: Crea una nueva factura, genera el KUDE en PDF y la registra.
