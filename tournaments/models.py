from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=[
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino')
    ])
    logo = models.ImageField(upload_to='tournament_logos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Activo'),
        ('upcoming', 'Próximamente'),
        ('finished', 'Finalizado')
    ], default='active')
    
    # Nuevos campos agregados
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    registration_deadline = models.DateField(null=True, blank=True)
    max_teams = models.PositiveIntegerField(default=16)
    format = models.CharField(max_length=30, choices=[
        ('round_robin', 'Todos contra Todos'),
        ('knockout', 'Eliminatorias'),
        ('group_stage', 'Fase de Grupos')
    ], default='round_robin')
    location = models.CharField(max_length=200, blank=True, null=True)
    prize_pool = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin')
        
        if self.registration_deadline and self.start_date:
            if self.registration_deadline > self.start_date:
                raise ValidationError('La fecha límite de registro debe ser anterior al inicio del torneo')
    
    @property
    def is_registration_open(self):
        """Verifica si el registro está abierto"""
        if not self.registration_deadline:
            return self.status == 'active'
        return timezone.now().date() <= self.registration_deadline and self.status == 'active'
    
    @property
    def teams_count(self):
        """Cuenta los equipos registrados"""
        return self.teams.filter(status='approved').count()
    
    @property
    def is_full(self):
        """Verifica si el torneo está lleno"""
        return self.teams_count >= self.max_teams

class Team(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    )
    
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    contact_person = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.tournament.name}"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.tournament:
            # Verificar si el registro está abierto
            if not self.tournament.is_registration_open:
                raise ValidationError('El registro para este torneo está cerrado')
            
            # Verificar si el torneo está lleno (solo para nuevos equipos)
            if not self.pk and self.tournament.is_full:
                raise ValidationError('El torneo ha alcanzado el máximo de equipos permitidos')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='player_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} {self.last_name} - {self.team.name}"
    
    class Meta:
        unique_together = ['cedula', 'team']  # Un jugador no puede estar duplicado en el mismo equipo
