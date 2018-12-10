# -*- coding: utf-8 -*-

from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache

from .signals import currency_changed
from .models import Currency
from .conf import SESSION_KEY


@never_cache
def set_currency(request):
    next, currency_code = (
        request.POST.get('next') or request.GET.get('next'),
        request.POST.get('currency_code', None) or
        request.GET.get('currency_code', None))

    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'

    response = HttpResponseRedirect(next)
    if currency_code and Currency.active.filter(code=currency_code).exists():
        # Set cookie irrespective for page cache visibility
        response.set_cookie(SESSION_KEY, currency_code)
        if hasattr(request, 'session'):
            request.session[SESSION_KEY] = currency_code
            currency_changed.send(sender=Currency,code=currency_code,request=request)

    return response
