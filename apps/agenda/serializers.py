from rest_framework import serializers
from django.utils import timezone
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
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
