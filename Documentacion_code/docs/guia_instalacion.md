# Guía de Instalación

Esta guía contiene los pasos necesarios para configurar el entorno de desarrollo del backend del Sistema Deportivo.

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Entorno virtual (recomendado)

## Pasos de Instalación

### 1. Clonar el Repositorio

```bash
git clone [URL_DEL_REPOSITORIO]
cd backenddeportes
```

### 2. Crear y Activar Entorno Virtual

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos

```bash
python manage.py migrate
```

### 5. Crear Usuario Administrador

```bash
python create_admin.py
```

Esto creará un usuario administrador con email `admin@deportes.com` y contraseña `admin123456`.

### 6. Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en http://127.0.0.1:8000/

## Acceso al Panel de Administración

Puedes acceder al panel de administración de Django en:

http://127.0.0.1:8000/admin/

Utiliza las credenciales del usuario administrador creado anteriormente.