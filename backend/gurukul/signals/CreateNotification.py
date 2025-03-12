from django.db.models.signals import Signal
from django.dispatch import receiver
from ..models import UserNotification
from datetime import datetime

notificationSignal = Signal()

@receiver(notificationSignal)
def notification_receiver(sender, **kwargs):
    data = kwargs.get('data', {})
    user = data.get('user')
    view = data.get('view')
    object = data.get('object')

    if user and view and object:
        UserNotification.objects.create(
                    user = user,
                    content = view,
                    object = object,
                    timestamp = datetime.now()
                )
