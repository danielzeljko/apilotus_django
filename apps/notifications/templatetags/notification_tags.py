from django.template import Library
from django.contrib.humanize.templatetags.humanize import naturaltime

register = Library()


@register.inclusion_tag('notifications/nav_link.html')
def notifications_link(user, limit=None):
    notifications = user.get_notifications()

    unseen_msg_count = user.unseen_notification_count()

    notifications = notifications.order_by('-id')
    notifications = notifications.prefetch_related('notice_type')

    if limit is not None:
        notifications = notifications[:limit]

    return {
        'success': True,
        'total_unseen_count': unseen_msg_count,
        'last_id': notifications.first().pk if notifications.first() else None,  # for mark all as read link
        'notifications': [
            {'pk': n.pk,
             'title': n.notice_type.title,
             'url': n.notice_type.url,
             'seen': n.seen,
             'label': n.notice_type.label,
             'since': naturaltime(n.notice_type.created_at)} for n in notifications]}
