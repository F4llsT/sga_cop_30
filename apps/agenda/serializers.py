from rest_framework import serializers
from django.utils import timezone
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'titulo', 'descricao', 'local', 'palestrante',
            'start_time', 'end_time', 'tags', 'importante',
            'created_at', 'created_by', 'latitude', 'longitude'
        ]
        read_only_fields = ('created_at', 'created_by')
    
    def to_representation(self, instance):
        """Formata os dados para o frontend"""
        data = super().to_representation(instance)
        
        # Formata as datas para ISO 8601
        if instance.start_time:
            data['start_time'] = instance.start_time.isoformat()
        if instance.end_time:
            data['end_time'] = instance.end_time.isoformat()
        if instance.created_at:
            data['created_at'] = instance.created_at.isoformat()
            
        # Garante que campos opcionais tenham valores padrão
        data['palestrante'] = data.get('palestrante', '')
        data['descricao'] = data.get('descricao', '')
        data['tags'] = data.get('tags', 'sustentabilidade')
        data['importante'] = data.get('importante', False)
        data['latitude'] = data.get('latitude')
        data['longitude'] = data.get('longitude')
        
        return data
    
    def validate(self, data):
        """
        Valida e ajusta as datas para incluir o fuso horário.
        """
        if 'start_time' in data and data['start_time'] and not timezone.is_aware(data['start_time']):
            data['start_time'] = timezone.make_aware(data['start_time'])
            
        if 'end_time' in data and data['end_time'] and not timezone.is_aware(data['end_time']):
            data['end_time'] = timezone.make_aware(data['end_time'])
            
        # Validação para garantir que a data final seja maior que a data inicial
        if 'start_time' in data and 'end_time' in data and data['start_time'] and data['end_time']:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError({
                    'end_time': 'A data/hora de término deve ser posterior à data/hora de início.'
                })
                
        return data
