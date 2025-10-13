def enviar_notificacoes(self):
    from django.contrib.auth import get_user_model
    from apps.notificacoes.models import Notificacao
    
    User = get_user_model()
    
    try:
        # Get all active users
        usuarios = User.objects.filter(is_active=True)
        total_usuarios = usuarios.count()
        notificacoes_criadas = 0
        
        # Create notifications in a transaction
        with transaction.atomic():
            for usuario in usuarios:
                Notificacao.objects.create(
                    usuario=usuario,
                    titulo=self.titulo,
                    mensagem=self.mensagem,
                    tipo='info'  # Default type since we removed the tipo field
                )
                notificacoes_criadas += 1
            
            # Update notification status and save
            self.status = 'enviada'
            self.data_envio = timezone.now()
            self.save()
        
        return True, f"Notificações enviadas para {notificacoes_criadas} de {total_usuarios} usuários."
        
    except Exception as e:
        self.status = 'erro'
        self.save()
        return False, f"Erro ao enviar notificações: {str(e)}"