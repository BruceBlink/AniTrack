import json
import logging
import os
import time
from functools import wraps
from typing import Callable, Any

from common import Result

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


def save_after_return(filename: str = "results.json", save_condition: Callable[[Any], bool] = lambda r: bool(r)):
    """
    自动保存函数返回值到 JSON 文件的装饰器。

    参数：
    - filename: 保存的 JSON 文件名（默认：results.json）
    - save_condition: 判断是否需要保存的条件函数，默认只要返回值非空就保存
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if save_condition(result):
                file_path = os.path.join(os.getcwd(), filename)

                # 尝试转换为可序列化格式
                def convert(obj):
                    if isinstance(obj, Result):
                        return obj.to_dict()
                    elif isinstance(obj, list):
                        return [convert(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {k: convert(v) for k, v in obj.items()}
                    else:
                        return obj

                serializable_result = convert(result)

                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(serializable_result, f, ensure_ascii=False, indent=2)
                    logger.info(f"结果已保存到 {file_path}")
                except Exception as e:
                    logger.error(f"保存结果失败: {e}")
            else:
                logger.info("结果为空，不保存文件。")
            return result

        return wrapper

    return decorator
