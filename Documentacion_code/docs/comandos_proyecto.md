# Comandos Específicos del Proyecto

Esta guía contiene los comandos específicos desarrollados para el Sistema Deportivo.

## Creación de Usuario Administrador

```bash
python create_admin.py
```

Este script crea un usuario administrador con las siguientes credenciales:

- **Email**: admin@deportes.com
- **Contraseña**: admin123456
- **Permisos**: is_admin=True, is_staff=True, is_superuser=True

El script verifica si el usuario ya existe antes de crearlo y muestra mensajes informativos sobre las credenciales y cómo acceder al panel de administración de Django y al frontend.

### Código Fuente

El script `create_admin.py` contiene la función `create_admin_user()` que:

1. Configura el entorno de Django
2. Importa el modelo CustomUser
3. Verifica si existe un usuario con el email admin@deportes.com
4. Si no existe, crea el usuario con los permisos necesarios
5. Muestra información sobre las credenciales y accesos

Este script es útil para inicializar rápidamente un usuario administrador en entornos de desarrollo o pruebas.