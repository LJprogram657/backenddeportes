from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TournamentViewSet, TeamViewSet
from . import views

router = DefaultRouter()
router.register(r'', TournamentViewSet)
router.register(r'teams', TeamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Nuevos endpoints para gestión de registros
    path('admin/teams/', views.admin_team_list, name='admin-team-list'),
    path('admin/teams/<int:pk>/', views.admin_team_detail, name='admin-team-detail'),
    path('admin/teams/<int:pk>/status/', views.admin_update_team_status, name='admin-update-team-status'),
    path('admin/tournaments/<int:tournament_id>/teams/', views.admin_tournament_teams, name='admin-tournament-teams'),
]