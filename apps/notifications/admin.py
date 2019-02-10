from django.contrib import admin
from django.contrib.auth import get_user_model


from .models import NoticeType, Notification


class NoticeTypeAdmin(admin.ModelAdmin):
    fields = ("label", "title", "description", "author", "url", "target_usergroups", "created_at", "expire_at",)
    readonly_fields = ("author",)
    list_display = ("label", "title", "description", "url", "created_at", "expire_at", "author",)

    def save_model(self, request, instance, form, change):
        user = request.user
        instance = form.save(commit=False)
        if not change or not instance.author:
            instance.author = user
        instance.save()
        form.save_m2m()

        if not change:
            qs = get_user_model().objects.filter(is_staff=True)

            # QS with groups
            target_groups = instance.target_usergroups.all()
            if target_groups:
                qs = qs.filter(groups__in=target_groups).distinct()

            Notification.send(instance, qs)

        return instance


admin.site.register(NoticeType, NoticeTypeAdmin)
