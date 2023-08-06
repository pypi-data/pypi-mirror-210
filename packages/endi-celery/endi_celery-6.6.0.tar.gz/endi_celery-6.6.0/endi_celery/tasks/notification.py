import datetime
import transaction
from pyramid_celery import celery_app

from endi.models.notification import NotificationEvent, Notification
from endi.utils.notification import (
    publish_event,
    clean_notifications,
)


@celery_app.task
def publish_pending_notifications_task():
    request = celery_app.conf["PYRAMID_REQUEST"]
    now = datetime.datetime.now()
    events = NotificationEvent.query().filter(
        NotificationEvent.due_datetime <= now,
        NotificationEvent.published == False,  # noqa:E712
    )
    for event in events:
        if event.is_valid(request):
            publish_event(request, event)
        else:
            request.dbsession.delete(event)
    transaction.commit()


@celery_app.task
def clean_notifications_task():
    """
    Clean notifications in case

    - Notification Event is outdated, conditions are not met anymore
    (e.g : contractor has left)

    - All Notifications have been read
    """
    request = celery_app.conf["PYRAMID_REQUEST"]
    clean_notifications(request)
    transaction.commit()
