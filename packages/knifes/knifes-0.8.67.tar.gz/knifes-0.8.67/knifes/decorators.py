from django.http import HttpRequest
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext as _
from .results import ApiResult
from typing import List, Set, Union
from itertools import repeat
import time
import functools
import json
import pickle
from knifes.digests import md5
from knifes import aes
import logging
logger = logging.getLogger(__name__)
default_func_cache_timeout = 3600


# 装饰器 修饰的方法 第1个参数是 key
def func_cache(cache_key_prefix: Union[tuple, str]):
    if not isinstance(cache_key_prefix, tuple):
        cache_key_prefix = (cache_key_prefix, default_func_cache_timeout)

    def outer_wrapper(func):
        def wrapper(*args, **kwargs):
            if not args:  # 参数校验
                raise Exception('方法缺少缓存key')
            key = cache_key_prefix[0] + md5(str(args[0]))  # 避免args[0]过长
            result = cache.get(key)  # 尝试读取缓存
            if result:
                return pickle.loads(result)  # 使用pickle支持枚举、自定义类等
            result = func(*args, **kwargs)
            cache.set(key, pickle.dumps(result), timeout=cache_key_prefix[1])  # 写缓存
            return result
        return wrapper
    return outer_wrapper


def update_func_cache(cache_key_prefix: Union[tuple, str], args_0, result):
    if not isinstance(cache_key_prefix, tuple):
        cache_key_prefix = (cache_key_prefix, default_func_cache_timeout)
    key = cache_key_prefix[0] + md5(str(args_0))
    cache.set(key, pickle.dumps(result), timeout=cache_key_prefix[1])


def login_required(view_func):
    def wrapper(request: HttpRequest, *args, **kwargs):
        if settings.TOKEN_KEY not in request.headers or not request.headers[settings.TOKEN_KEY]:
            return ApiResult.tokenInvalid()
        request.token = request.headers[settings.TOKEN_KEY]
        data = cache.get(settings.TOKEN_KEY + request.token)
        if not data:
            return ApiResult.tokenInvalid()
        # 只能反序列化简单类型数据
        request.user = pickle.loads(data)
        return view_func(request, *args, **kwargs)
    return wrapper


def params_required(param_keys: List, is_get=False):
    def outer_wrapper(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            if param_keys and is_get:
                for param_key in param_keys:
                    if param_key not in request.GET or not request.GET[param_key]:
                        return ApiResult.missingParam()
            elif param_keys:
                for param_key in param_keys:
                    if param_key not in request.POST or not request.POST[param_key]:
                        return ApiResult.missingParam()
            return view_func(request, *args, **kwargs)
        return wrapper
    return outer_wrapper


def decrypt_and_check_params(param_keys: Set = None, header_param_keys: Set = None, aes_body_key: str = None, aes_header_key: str = None):
    if param_keys is None:
        param_keys = {'timestamp'}
    else:
        param_keys.add('timestamp')

    def outer_wrapper(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not request.body:
                return ApiResult.missingParam()
            request.params = json.loads(request.body)

            # body params   TODO 判断timestamp是否过期
            if next((True for param_key in param_keys if param_key not in request.params), False):
                return ApiResult.missingParam()

            if not settings.DEBUG:
                encrypt_params = json.loads(aes.decrypt(request.params.get('xBody', request.params.get('vs')), aes_body_key or settings.AES_BODY_KEY))
                request.params.pop('xBody', None)
                request.params.pop('vs', None)
                if request.params != encrypt_params:
                    return ApiResult.missingParam(_('参数非法'))

            # header params
            if not (request.headers.get('xHeader') or request.headers.get('vi')):
                ApiResult.missingParam(_('header缺少参数'))

            request.header_params = json.loads(aes.decrypt(request.headers.get('xHeader') or request.headers.get('vi'), aes_header_key or settings.AES_HEADER_KEY))
            if header_param_keys and next((True for param_key in header_param_keys if param_key not in request.header_params), False):
                return ApiResult.missingParam(_('header缺少参数'))

            return view_func(request, *args, **kwargs)
        return wrapper
    return outer_wrapper


def decrypt_and_check_body_params(param_keys: Set = None, aes_body_key: str = None):
    if param_keys is None:
        param_keys = {'timestamp'}
    else:
        param_keys.add('timestamp')

    def outer_wrapper(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not request.body:
                return ApiResult.missingParam()
            request.params = json.loads(request.body)
            if next((True for param_key in param_keys if param_key not in request.params), False):
                return ApiResult.missingParam()

            if not settings.DEBUG:
                encrypt_params = json.loads(aes.decrypt(request.params.get('xBody', request.params.get('vs')), aes_body_key or settings.AES_BODY_KEY))
                request.params.pop('xBody', None)
                request.params.pop('vs', None)
                if request.params != encrypt_params:
                    return ApiResult.missingParam(_('参数非法'))

            return view_func(request, *args, **kwargs)
        return wrapper
    return outer_wrapper


def decrypt_and_check_header_params(header_param_keys: Set = None, aes_header_key: str = None):
    def outer_wrapper(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not (request.headers.get('xHeader') or request.headers.get('vi')):
                ApiResult.missingParam(_('header缺少参数'))

            request.header_params = json.loads(aes.decrypt(request.headers.get('xHeader') or request.headers.get('vi'), aes_header_key or settings.AES_HEADER_KEY))
            if header_param_keys and next((True for param_key in header_param_keys if param_key not in request.header_params), False):
                return ApiResult.missingParam(_('header缺少参数'))
            return view_func(request, *args, **kwargs)
        return wrapper
    return outer_wrapper


# json请求 参数校验
def decode_and_check_body_params(param_keys: Set = None):
    def outer_wrapper(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            if not request.body:
                return ApiResult.missingParam()
            request.params = json.loads(request.body)
            # 检查参数
            for param_key in param_keys:
                if param_key not in request.params:
                    return ApiResult.missingParam()
            return view_func(request, *args, **kwargs)
        return wrapper
    return outer_wrapper



def retry(times=3, interval=(1, 5, 10), exclude_exception_tuple=()):
    """auto retry when function fails.

    This is designed as a decorator creator. To use the decorator, either use
    @retry() or @retry(times=3, interval=5) or @retry(times=3, interval=[1, 5,
    10])

    A function is considered failed when it raised an unhandled exception.

    Args:
        times: max retry times. so function may run 1 + times in worst case.
        interval: if set to an int/float, means retry after these many seconds. no interval if 0.
                  if set to an iterable, means retry interval for each retry;
                  if interval iterable is shorter than times, the last value
                  will be used for remaining retries.
                  default interval is (1, 5, 10).
        exclude_exception_tuple: exclude exception class

    Return:
        a decorator which when used, will return what the decorated func
        returns, but with auto retry support.

    """
    def gen_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_time = 0
            if isinstance(interval, (int, float)):
                interval_iter = repeat(interval)
            else:
                interval_iter = iter(interval)
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:    # pylint: disable=broad-except
                    if retry_time >= times:
                        logger.error(f'{func.__name__}, max retry reached, {retry_time}')
                        raise
                    if exclude_exception_tuple and isinstance(e, exclude_exception_tuple):
                        raise
                    try:
                        seconds = next(interval_iter)  # pylint: disable=redefined-outer-name
                    except StopIteration:
                        interval_iter = repeat(seconds)  # last loop value
                    time.sleep(seconds)
                    retry_time += 1
                    logger.debug(f'{func.__name__} sleeping {seconds} before auto retry')
        return wrapper
    return gen_wrapper
