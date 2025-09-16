from rest_framework import serializers
from .models import Tournament, Team, Player

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'last_name', 'cedula', 'photo']
        
class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'tournament', 'logo', 'contact_person', 'contact_number', 'status', 'created_at', 'players']
        read_only_fields = ['status', 'created_at']
        
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
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'code', 'category', 'logo', 'status', 'created_at']