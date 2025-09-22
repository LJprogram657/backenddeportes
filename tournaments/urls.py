from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TournamentViewSet, TeamViewSet
from . import views

router = DefaultRouter()
router.register(r'', TournamentViewSet, basename='tournament')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints públicos adicionales
    # /tournaments/active/ -> Ya está incluido en el ViewSet
    
    # Endpoints para administradores
    path('admin/teams/', views.admin_team_list, name='admin-team-list'),
    path('admin/teams/<int:pk>/', views.admin_team_detail, name='admin-team-detail'),
    path('admin/teams/<int:pk>/status/', views.admin_update_team_status, name='admin-update-team-status'),
    path('admin/tournaments/<int:tournament_id>/teams/', views.admin_tournament_teams, name='admin-tournament-teams'),
    path('admin/dashboard/stats/', views.admin_dashboard_stats, name='admin-dashboard-stats'),
]