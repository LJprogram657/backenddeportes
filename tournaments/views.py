from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.utils import timezone
from .models import Tournament, Team, Player
from .serializers import (
    TournamentSerializer, TournamentCreateSerializer, TournamentListSerializer,
    TeamSerializer, TeamRegistrationSerializer, PlayerSerializer
)

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TournamentCreateSerializer
        elif self.action == 'list':
            return TournamentListSerializer
        return TournamentSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'active']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Endpoint público: Torneos activos disponibles para registro"""
        active_tournaments = Tournament.objects.filter(
            status='active'
        ).order_by('-created_at')
        
        # Filtrar por categoría si se especifica
        category = request.query_params.get('category', None)
        if category:
            active_tournaments = active_tournaments.filter(category=category)
        
        serializer = TournamentListSerializer(active_tournaments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def teams(self, request, pk=None):
        """Equipos aprobados de un torneo específico"""
        tournament = self.get_object()
        teams = Team.objects.filter(tournament=tournament, status='approved')
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Estadísticas de un torneo específico"""
        tournament = self.get_object()
        stats = {
            'tournament_info': TournamentSerializer(tournament).data,
            'teams_registered': tournament.teams_count,
            'teams_pending': tournament.teams.filter(status='pending').count(),
            'teams_approved': tournament.teams.filter(status='approved').count(),
            'teams_rejected': tournament.teams.filter(status='rejected').count(),
            'max_teams': tournament.max_teams,
            'is_full': tournament.is_full,
            'is_registration_open': tournament.is_registration_open,
            'registration_deadline': tournament.registration_deadline,
        }
        return Response(stats)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamRegistrationSerializer
        return TeamSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Crear equipo con validaciones adicionales"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validar torneo antes de crear
        tournament_id = request.data.get('tournament')
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            if not tournament.is_registration_open:
                return Response(
                    {'error': 'El registro para este torneo está cerrado'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            if tournament.is_full:
                return Response(
                    {'error': 'El torneo ha alcanzado el máximo de equipos permitidos'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Torneo no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Equipo registrado exitosamente. Pendiente de aprobación.',
                'team': serializer.data
            }, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        teams = Team.objects.filter(status='pending')
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        team = self.get_object()
        team.status = 'approved'
        team.save()
        return Response({'status': 'team approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        team = self.get_object()
        team.status = 'rejected'
        team.save()
        return Response({'status': 'team rejected'})


# Endpoints específicos para administradores
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_team_list(request):
    """
    Endpoint para administradores: Lista todas las solicitudes de equipos
    con opciones de filtrado por estado y torneo
    """
    status_filter = request.query_params.get('status', None)
    tournament_filter = request.query_params.get('tournament', None)
    
    teams = Team.objects.all()
    
    if status_filter:
        teams = teams.filter(status=status_filter)
    
    if tournament_filter:
        teams = teams.filter(tournament_id=tournament_filter)
    
    teams = teams.order_by('-created_at')
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_team_detail(request, pk):
    """
    Endpoint para administradores: Ver detalles de un equipo específico
    incluyendo sus jugadores
    """
    try:
        team = Team.objects.get(pk=pk)
    except Team.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    team_serializer = TeamSerializer(team)
    players = Player.objects.filter(team=team)
    players_serializer = PlayerSerializer(players, many=True)
    
    response_data = {
        'team': team_serializer.data,
        'players': players_serializer.data
    }
    
    return Response(response_data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def admin_update_team_status(request, pk):
    """
    Endpoint para administradores: Actualizar el estado de un equipo
    (aprobar o rechazar)
    """
    try:
        team = Team.objects.get(pk=pk)
    except Team.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if new_status not in ['pending', 'approved', 'rejected']:
        return Response({'error': 'Estado no válido'}, status=status.HTTP_400_BAD_REQUEST)
    
    team.status = new_status
    team.save()
    
    serializer = TeamSerializer(team)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_tournament_teams(request, tournament_id):
    """
    Endpoint para administradores: Listar equipos por torneo
    """
    try:
        tournament = Tournament.objects.get(pk=tournament_id)
    except Tournament.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    status_filter = request.query_params.get('status', None)
    
    teams = Team.objects.filter(tournament=tournament)
    if status_filter:
        teams = teams.filter(status=status_filter)
    
    teams = teams.order_by('-created_at')
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """
    Endpoint para administradores: Estadísticas generales del dashboard
    """
    stats = {
        'total_tournaments': Tournament.objects.count(),
        'active_tournaments': Tournament.objects.filter(status='active').count(),
        'total_teams': Team.objects.count(),
        'pending_teams': Team.objects.filter(status='pending').count(),
        'approved_teams': Team.objects.filter(status='approved').count(),
        'total_players': Player.objects.count(),
        'recent_registrations': Team.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
    }
    return Response(stats)
