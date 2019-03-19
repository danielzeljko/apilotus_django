from django import template

register = template.Library()


@register.filter
def check_enable_menu(user, permissions):
    if user.user_role == 'admin':
        return True

    if user.page_permissions:
        page_permissions = user.page_permissions.split(',')
        permissions = permissions.split(',')
        for permission in permissions:
            if permission in page_permissions:
                return True
        return False
    return False


@register.filter
def get_by_index(l, i):
    return l[i]
