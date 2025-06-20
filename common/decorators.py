import json
import logging
import os
from typing import Callable, Any
from common import Result
import time
import asyncio
from functools import wraps
from collections import defaultdict
import threading


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
                    logging.info(f"\n{'=' * 40}\n第 {attempt} 次尝试\n{'=' * 40}")
                    result = func(*args, **kwargs)
                    try:
                        if not retry_condition(result):
                            return result
                        logging.warning("条件未满足，准备重试...")
                    except Exception as inner:
                        logging.error(f"重试判断条件出错：{inner}")
                        return result
                except exceptions as e:
                    logging.warning(f"第 {attempt} 次调用发生异常：{e}")
                if attempt < retries:
                    logging.info(f"等待 {delay} 秒后进行下一次尝试...")
                    time.sleep(delay)
            logging.error("重试次数已耗尽，操作失败。")
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
                    logging.info(f"结果已保存到 {file_path}")
                except Exception as e:
                    logging.error(f"保存结果失败: {e}")
            else:
                logging.info("结果为空，不保存文件。")
            return result

        return wrapper

    return decorator


def timer(
        enable_stats=True,
        print_report=True,
        unit="ms",
        track_hierarchy=False
):
    """
    高级函数计时装饰器

    参数:
    - enable_stats: 是否启用统计功能（默认开启）
    - print_report: 是否打印执行时间报告（默认开启）
    - unit: 时间单位 ('ms' 毫秒 | 's' 秒 | 'us' 微秒)
    - track_hierarchy: 是否追踪函数调用层级（用于复杂调用链分析）

    功能特点:
    1. 自动识别同步/异步函数
    2. 支持时间单位转换
    3. 提供详细统计功能（调用次数、总耗时、最小/最大耗时等）
    4. 可选调用层级追踪
    5. 线程安全设计
    """
    # 时间单位转换因子
    unit_factors = {
        "us": 1_000_000,
        "ms": 1_000,
        "s": 1
    }
    factor = unit_factors.get(unit, 1_000)  # 默认为毫秒

    def format_time(t):
        """格式化时间输出"""
        if unit == "us":
            return f"{t * factor:.0f}μs"
        elif unit == "ms":
            return f"{t * factor:.2f}ms"
        return f"{t:.4f}s"

    def decorator(func):
        # 线程局部存储确保线程安全
        stats = threading.local()

        # 初始化统计数据结构
        def init_stats():
            return {
                'total_calls': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'last_time': 0.0
            }

        # 调用层级追踪状态
        call_stack = []
        call_hierarchy = defaultdict(lambda: defaultdict(int))

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 初始化线程统计
            if not hasattr(stats, 'data'):
                stats.data = init_stats()

            # 调用层级追踪
            if track_hierarchy:
                call_stack.append(func.__name__)
                if len(call_stack) > 1:
                    caller = call_stack[-2]
                    call_hierarchy[caller][func.__name__] += 1

            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time

            # 更新统计信息
            if enable_stats:
                stats.data['total_calls'] += 1
                stats.data['total_time'] += elapsed
                stats.data['min_time'] = min(stats.data['min_time'], elapsed)
                stats.data['max_time'] = max(stats.data['max_time'], elapsed)
                stats.data['last_time'] = elapsed

            # 打印单次执行报告
            if print_report:
                print(f"⏱️ {func.__name__}: {format_time(elapsed)}")

            # 调用层级追踪清理
            if track_hierarchy:
                call_stack.pop()

            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 初始化线程统计
            if not hasattr(stats, 'data'):
                stats.data = init_stats()

            # 调用层级追踪
            if track_hierarchy:
                call_stack.append(func.__name__)
                if len(call_stack) > 1:
                    caller = call_stack[-2]
                    call_hierarchy[caller][func.__name__] += 1

            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time

            # 更新统计信息
            if enable_stats:
                stats.data['total_calls'] += 1
                stats.data['total_time'] += elapsed
                stats.data['min_time'] = min(stats.data['min_time'], elapsed)
                stats.data['max_time'] = max(stats.data['max_time'], elapsed)
                stats.data['last_time'] = elapsed

            # 打印单次执行报告
            if print_report:
                print(f"⏱️ [ASYNC] {func.__name__}: {format_time(elapsed)}")

            # 调用层级追踪清理
            if track_hierarchy:
                call_stack.pop()

            return result

        # 添加统计访问方法
        def get_stats():
            """获取当前线程的统计信息"""
            if hasattr(stats, 'data'):
                return {
                    'function': func.__name__,
                    'total_calls': stats.data['total_calls'],
                    'total_time': stats.data['total_time'],
                    'avg_time': stats.data['total_time'] / max(1, stats.data['total_calls']),
                    'min_time': stats.data['min_time'],
                    'max_time': stats.data['max_time'],
                    'last_time': stats.data['last_time']
                }
            return None

        def reset_stats():
            """重置当前线程的统计信息"""
            if hasattr(stats, 'data'):
                stats.data = init_stats()

        def get_hierarchy():
            """获取函数调用层级关系"""
            return dict(call_hierarchy)

        # 附加功能到包装器
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper.get_stats = get_stats
        wrapper.reset_stats = reset_stats

        if track_hierarchy:
            wrapper.get_hierarchy = get_hierarchy

        return wrapper

    return decorator
