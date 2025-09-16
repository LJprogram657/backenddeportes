from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import Tournament, Team, Player
from .serializers import TournamentSerializer, TeamSerializer, TeamRegistrationSerializer, PlayerSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def teams(self, request, pk=None):
        tournament = self.get_object()
        teams = Team.objects.filter(tournament=tournament, status='approved')
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

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


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_team_list(request):
    """
    Endpoint para administradores: Lista todas las solicitudes de equipos
    con opciones de filtrado por estado
    """
    status_filter = request.query_params.get('status', None)
    
    if status_filter:
        teams = Team.objects.filter(status=status_filter)
    else:
        teams = Team.objects.all()
    
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
    
    if status_filter:
        teams = Team.objects.filter(tournament=tournament, status=status_filter)
    else:
        teams = Team.objects.filter(tournament=tournament)
    
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)
