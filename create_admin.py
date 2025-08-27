import os
import sys
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_deportivo.settings')
django.setup()

from authentication.models import CustomUser

def create_admin_user():
    """
    Crear usuario administrador por defecto
    """
    admin_email = 'admin@deportes.com'
    admin_password = 'admin123456'
    
    try:
        # Verificar si ya existe
        if CustomUser.objects.filter(email=admin_email).exists():
            print(f"❌ El usuario administrador con email '{admin_email}' ya existe.")
            user = CustomUser.objects.get(email=admin_email)
            print(f"📧 Email: {user.email}")
            print(f"🔐 Contraseña: {admin_password}")
            print(f"👑 Es admin: {user.is_admin}")
            return
        
        # Crear nuevo usuario administrador
        admin_user = CustomUser.objects.create(
            email=admin_email,
            username=admin_email,
            first_name='Administrador',
            last_name='Sistema',
            password=make_password(admin_password),
            is_admin=True,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        print("✅ Usuario administrador creado exitosamente!")
        print("="*50)
        print(f"📧 Email: {admin_email}")
        print(f"🔐 Contraseña: {admin_password}")
        print(f"👑 Es admin: {admin_user.is_admin}")
        print(f"🆔 ID: {admin_user.id}")
        print("="*50)
        print("🚀 Puedes usar estas credenciales para:")
        print("   • Acceder al panel de administración Django: /admin/")
        print("   • Hacer login en el frontend como administrador")
        print("   • Gestionar usuarios y torneos")
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    create_admin_user()