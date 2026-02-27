# Esquema de Base de Datos para el Oráculo de Datos del Contribuyente (CCFE)

## 🗄️ Propuesta Inicial (PostgreSQL)

Para que el Oráculo sea capaz de analizar patrones y predecir el IVA, necesitamos una estructura relacional sólida. Aquí tienes el primer borrador:

### 1. Tabla `users` (El Dueño de los Datos)
- `id`: UUID (Primary Key)
- `username`: String (Unique)
- `email`: String (Unique)
- `hashed_password`: String
- `created_at`: Timestamp

### 2. Tabla `companies` (Perfil del Emisor)
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key -> users.id)
- `ruc`: String (Unique)
- `name`: String
- `address`: String
- `timbrado_number`: String
- `economic_activity`: String

### 3. Tabla `clients` (Receptores de Facturas)
- `id`: UUID (Primary Key)
- `company_id`: UUID (Foreign Key -> companies.id)
- `ruc`: String
- `name`: String
- `email`: String

### 4. Tabla `invoices` (El Corazón del Oráculo)
- `id`: UUID (Primary Key)
- `company_id`: UUID (Foreign Key -> companies.id)
- `client_id`: UUID (Foreign Key -> clients.id)
- `number`: String (Establecimiento-Punto-Secuencia)
- `cdc`: String (Código de Control SIFEN)
- `issue_date`: Timestamp
- `total_amount`: Numeric(15, 2)
- `total_iva10`: Numeric(15, 2)
- `total_iva5`: Numeric(15, 2)
- `total_exempt`: Numeric(15, 2)
- `currency`: String (Default: PYG)
- `status`: String (BORRADOR, APROBADA, ANULADA)

### 5. Tabla `invoice_items` (Detalle para Análisis de Gastos)
- `id`: UUID (Primary Key)
- `invoice_id`: UUID (Foreign Key -> invoices.id)
- `description`: String
- `quantity`: Integer
- `unit_price`: Numeric(15, 2)
- `vat_rate`: Integer (0, 5, 10)
- `category`: String (SUPERMERCADO, COMBUSTIBLE, SERVICIOS, etc. - *Aquí entra la IA*)

---

## 🚀 Próximos Pasos Técnicos:
1. **Modelos Pydantic:** Actualizar `backend/main.py` para usar estos modelos.
2. **Integración ORM:** Configurar SQLAlchemy para conectar FastAPI con PostgreSQL.
3. **Script de Migración:** Crear un script en Python para leer tus actuales `invoices.csv` y `clients.csv` e inyectarlos en esta nueva estructura.
