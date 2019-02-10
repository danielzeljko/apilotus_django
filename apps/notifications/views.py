from django.utils import timezone
from django.http.response import JsonResponse
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404

from radiocms.decorators import staff_required

from .models import Notification


@method_decorator(staff_required, 'dispatch')
class NotificationListView(ListView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        user = request.user
        notifications = user.get_notifications()
        unseen_msg_count = user.unseen_notification_count()
        notifications = notifications.order_by('-id')
        ctx = dict(notifications=notifications, unseen_msg_count=unseen_msg_count)
        return render(request, 'notifications/notification_home.html', ctx)


@staff_required
def goto(request, pk=None):
    referer = request.META.get('HTTP_REFERER', '/')
    if not pk:
        return redirect(referer)
    notification = get_object_or_404(Notification, user=request.user, id=pk)
    notification.seen_at = timezone.now()
    notification.save()
    if notification.notice_type.url:
        return redirect(notification.notice_type.url)
    return redirect(referer)


@staff_required
def mark_read(request, id_lte=None, id_gte=None):
    filter_kwargs = dict(user=request.user, deleted=False)

    if id_lte:
        filter_kwargs['id__lte'] = id_lte

    if id_gte:
        filter_kwargs['id__gte'] = id_gte

    Notification.objects.filter(**filter_kwargs).update(seen_at=timezone.now())

    return JsonResponse(data={'success': True})


@staff_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, deleted=False, user=request.user)
    notification.deleted = True
    notification.save()
    if request.is_ajax():
        return JsonResponse(data={'success': True})
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)
