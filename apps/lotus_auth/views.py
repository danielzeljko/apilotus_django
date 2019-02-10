from django.shortcuts import redirect
from django.utils import translation


def switch_language(request, language):
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect('/admin')
