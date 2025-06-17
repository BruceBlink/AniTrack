import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry(
        retries: int = 3,
        delay: float = 5,
        retry_condition: Callable[[Any], bool] = lambda result: not result,
        exceptions: tuple = (Exception,)
):
    """
    自动重试装饰器。

    参数：
    - retries: 最大重试次数。
    - delay: 每次重试的间隔时间（秒）。
    - retry_condition: 一个函数，接受返回值，返回 True 表示需要重试。
    - exceptions: 哪些异常会触发重试。
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    logger.info(f"\n{'=' * 40}\n第 {attempt} 次尝试\n{'=' * 40}")
                    result = func(*args, **kwargs)
                    if not retry_condition(result):
                        return result
                    logger.warning("结果不满足条件，准备重试...")
                except exceptions as e:
                    logger.warning(f"第 {attempt} 次调用发生异常：{e}")
                if attempt < retries:
                    logger.info(f"等待 {delay} 秒后进行下一次尝试...")
                    time.sleep(delay)
            logger.error("重试次数已耗尽，操作失败。")
            return None

        return wrapper

    return decorator


from functools import wraps
from typing import Callable, Any


def print_after_return(print_func: Callable[[Any], None], print_condition: Callable[[Any], bool] = lambda x: True):
    """
    成功返回后调用指定的打印函数。

    参数：
    - print_func: 打印函数（如 print_results）
    - print_condition: 一个判断函数，返回 True 才调用 print_func
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if print_condition(result):
                print_func(result)
            return result

        return wrapper

    return decorator
