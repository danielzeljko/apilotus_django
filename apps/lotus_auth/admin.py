from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import format_html
from django.urls import reverse, NoReverseMatch

try:
    from hijack_admin.admin import HijackUserAdminMixin
except ImportError:
    HIJACK_INSTALLED = False
else:
    HIJACK_INSTALLED = True

from lotus_auth.models import LotusUser


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'gender', 'date_of_birth', 'phone')}),
        # (_('Location'), {'fields': ('address', 'city', 'state', 'zipcode', 'latitude', 'longitude', 'signup_ip_address', 'signup_country_code')}),
        (_('Location'), {'fields': ('address', 'city', 'state', 'zipcode', 'latitude', 'longitude')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('User Options'), {'fields': ('sites_subscribed', )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'site_joined')}),
    )
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'gender', 'date_of_birth', 'address', 'city', 'state', 'zipcode', 'accept_terms')
            }
        ),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-is_staff', 'username',)


if HIJACK_INSTALLED:
    CustomUserAdmin.__bases__ += (HijackUserAdminMixin,)
    CustomUserAdmin.list_display.append('hijack_field')


class LogEntryAdmin(admin.ModelAdmin):
    '''
    Support for superusers to view the Django admin Log entries under Administration
    '''

    date_hierarchy = 'action_time'

    readonly_fields = [f.name for f in LogEntry._meta.get_fields()]

    list_filter = [
        'content_type',
    ]

    search_fields = [
        'object_repr',
        'change_message',
        'user__username'  # The sidebar filter is too slow
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',  # Calculated field
        'action_flag',
        'change_message',
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(LogEntryAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

    def _make_html_no_link(self, obj, old_app_label=None):
        if old_app_label:
            link = format_html(
                u'({old_app_label}/{obj_id}) {obj_repr}',
                old_app_label=old_app_label,
                obj_id=obj.object_id,
                obj_repr=obj.object_repr)
        else:
            link = format_html(
                u'{obj_repr}',
                obj_repr=obj.object_repr)
        return link

    def object_link(self, obj):
        '''
        User friendly view of obj.object_repr
        '''
        if obj.action_flag == DELETION:
            link = self._make_html_no_link(obj)
        else:
            ct = obj.content_type
            if ct:
                try:
                    link = format_html(
                        u'<a href="{href}">{obj_repr}</a>',
                        href=reverse('admin:{app_label}_{model}_change'.format(
                            app_label=ct.app_label, model=ct.model),
                            args=[obj.object_id]),
                        obj_repr=obj.object_repr)
                except NoReverseMatch:
                    # Support for apps that don't exist anymore
                    link = self._make_html_no_link(obj, ct.app_label)
            else:
                link = self._make_html_no_link(obj)

        return link

    object_link.admin_order_field = 'object_repr'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request).prefetch_related('content_type')


admin.site.register(LotusUser, CustomUserAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
