from rest_framework import serializers
from .models import Tournament, Team, Player

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'last_name', 'cedula', 'photo', 'created_at']
        
class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'tournament', 'tournament_name', 'logo', 
            'contact_person', 'contact_number', 'status', 
            'created_at', 'updated_at', 'players'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']
        
class TeamRegistrationSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    
    class Meta:
        model = Team
        fields = ['name', 'tournament', 'logo', 'contact_person', 'contact_number', 'players']
        
    def create(self, validated_data):
        players_data = validated_data.pop('players')
        team = Team.objects.create(**validated_data)
        
        for player_data in players_data:
            Player.objects.create(team=team, **player_data)
            
        return team

class TournamentSerializer(serializers.ModelSerializer):
    teams_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'code', 'category', 'logo', 'status',
            'description', 'start_date', 'end_date', 'registration_deadline',
            'max_teams', 'format', 'location', 'prize_pool',
            'created_at', 'updated_at',
            # Campos calculados
            'teams_count', 'is_registration_open', 'is_full'
        ]
        read_only_fields = ['created_at', 'updated_at']

class TournamentCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear torneos (solo campos necesarios)"""
    class Meta:
        model = Tournament
        fields = [
            'name', 'code', 'category', 'logo', 'description',
            'start_date', 'end_date', 'registration_deadline',
            'max_teams', 'format', 'location', 'prize_pool'
        ]
        
    def validate_code(self, value):
        """Validar que el código sea único"""
        if Tournament.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ya existe un torneo con este código.")
        return value

class TournamentListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar torneos"""
    teams_count = serializers.ReadOnlyField()
    is_registration_open = serializers.ReadOnlyField()
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'code', 'category', 'logo', 'status',
            'start_date', 'registration_deadline', 'max_teams',
            'teams_count', 'is_registration_open'
        ]