import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from apps.agenda.models import Event, UserAgenda
from apps.notificacoes.models import Notificacao
from apps.notificacoes.push import send_push_to_user
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Sends notifications to users for events starting in the next 24 hours.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to send event reminders...'))

        now = timezone.now()
        tomorrow = now + datetime.timedelta(days=1)

        # Find events starting between now and 24 hours from now
        upcoming_events = Event.objects.filter(
            start_time__gte=now, 
            start_time__lte=tomorrow
        ).prefetch_related('useragenda_set__user')

        if not upcoming_events.exists():
            self.stdout.write(self.style.SUCCESS('No upcoming events in the next 24 hours to notify about.'))
            return

        notification_count = 0
        for event in upcoming_events:
            # Get all users who have this event in their agenda
            for user_agenda in event.useragenda_set.all():
                user = user_agenda.user
                if not user:
                    self.stdout.write(self.style.WARNING(f'Skipping agenda entry - no user associated'))
                    continue

                # Create the notification message
                title = f'Lembrete de Evento: {event.titulo}'
                message = f'O evento "{event.titulo}" começará em breve no local: {event.local}.'

                # Avoid creating duplicate notifications
                existing_notification = Notificacao.objects.filter(
                    usuario=user,
                    titulo=title,
                    mensagem=message,
                    evento=event
                ).exists()

                if not existing_notification:
                    notif = Notificacao.objects.create(
                        usuario=user,
                        titulo=title,
                        mensagem=message,
                        tipo='info',
                        evento=event
                    )
                    notification_count += 1
                    self.stdout.write(f'Notification created for user {user.email} for event "{event.titulo}"')

                    # Send Web Push via OneSignal (best-effort)
                    try:
                        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
                        event_url = f"{site_url}/agenda/evento/{event.id}/"
                        send_push_to_user(
                            user_external_id=str(user.id),
                            title=title,
                            message=message,
                            url=event_url
                        )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Failed to send push for user {user.email}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully sent {notification_count} event reminders.'))