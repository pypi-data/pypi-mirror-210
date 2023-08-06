from typing import TypeVar
from django.http import HttpRequest
T = TypeVar('T')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_request_param_strip_spaces(request: HttpRequest, key):
    value = request.POST.get(key, request.GET.get(key))
    return value.strip() if value else value


def get_param_values_from_request(request, *param_names):
    values = []
    for param in param_names:
        values.append(request.POST.get(param, request.GET.get(param)))
    return tuple(values)


def get_object_or_None(T, **kwargs) -> T:
    objs = T.objects.filter(**kwargs)
    return objs[0] if objs else None


def get_value_or_None(T, **kwargs) -> T:
    objs = T.objects.filter(**kwargs).values()
    return objs[0] if objs else None

