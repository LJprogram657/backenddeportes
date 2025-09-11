# Comandos Django

Esta guía contiene los comandos básicos de Django utilizados en el desarrollo del Sistema Deportivo.

## Servidor de Desarrollo

```bash
python manage.py runserver
```

Inicia el servidor de desarrollo en http://127.0.0.1:8000/

## Migraciones de Base de Datos

```bash
# Crear migraciones basadas en los cambios en los modelos
python manage.py makemigrations

# Aplicar migraciones pendientes a la base de datos
python manage.py migrate
```

## Gestión de Usuarios

```bash
# Crear un superusuario
python manage.py createsuperuser
```

## Shell de Django

```bash
python manage.py shell
```

Abre una consola interactiva de Python con el entorno de Django cargado.

## Pruebas

```bash
python manage.py test
```

Ejecuta las pruebas del proyecto.

## Recolección de Archivos Estáticos

```bash
python manage.py collectstatic
```

Recopila todos los archivos estáticos en la carpeta definida en STATIC_ROOT.