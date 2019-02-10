from django import template
import re

numeric_test = re.compile("^\d+$")
register = template.Library()


@register.filter
def get_by_index(l, i):
    return l[i]


@register.filter
def limit_location_description(description):
    return ' '.join(description.split(' ')[:20]) + '...'


@register.filter
def odd_even(index):
    return True if index % 2 == 0 else False


@register.filter
def blog_order(index):
    return index % 4


@register.filter
def get_attr(obj, args):
    """ Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    args = args.split(',')
    if len(args) == 1:
        (attribute, default) = [args[0], '']
    else:
        (attribute, default) = args

    try:
        return obj.__getattribute__(attribute)
    except AttributeError:
        return obj.__dict__.get(attribute, default)
    except:
        return default


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)
