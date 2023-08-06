from cjen.exceptions import PropertyRangerException, PropertyRequiredException


def required(exception_class=None, err_msg=None):
    """
    属性为必填
    :param exception_class: 抛出自定义的异常
    :param err_msg: 抛出自定义的异常
    :return:
    """

    def __inner__(func):
        def __wrapper__(*args, **kwargs):
            if func(*args, **kwargs) is None:
                msg = f'{func.__name__} 必填' if not err_msg else err_msg
                exception = PropertyRequiredException(msg) if not exception_class else exception_class(msg)
                raise exception
            return func(*args, **kwargs)

        return __wrapper__

    return __inner__


def required_if(proper: str, wish: list, exception_class=None, err_msg=None):
    """
    如果 proper的值 == wish
    则 本属性必填
    :param proper:
    :param wish:
    :param exception_class: 抛出自定义的异常
    :param err_msg
    :return:
    """

    def __inner__(func):
        def __wrapper__(*args, **kwargs):
            if getattr(args[0], proper) in wish:
                if not func(*args, **kwargs):
                    msg = f'{func.__name__} 必填' if not err_msg else err_msg
                    exception = PropertyRequiredException(msg) if not exception_class else exception_class(msg)
                    raise exception
            return func(*args, **kwargs)

        return __wrapper__

    return __inner__


def should_be_in(limits: list[str], ignore_case=False, exception_class=None, err_msg=None):
    """
    字符串应该在范围内
    :param limits:
    :param ignore_case: 是否忽略大小写敏感，默认是敏感
    :param exception_class: 抛出自定义的异常
    :param err_msg: 抛出自定义的异常
    :return:
    """

    def __inner__(func):
        def __wrapper__(*args, **kwargs):
            data = func(*args, **kwargs)
            if not ignore_case:
                if data not in limits:
                    msg = f'{func.__name__} should in {limits}' if not err_msg else err_msg
                    exception = PropertyRangerException(msg) if not exception_class else exception_class(msg)
                    raise exception

            else:
                if data.lower() not in [char.lower() for char in limits]:
                    msg = f'{func.__name__} should in {limits}' if not err_msg else err_msg
                    exception = PropertyRangerException(msg) if not exception_class else exception_class(msg)
                    raise exception
            return data

        return __wrapper__

    return __inner__
