import asyncio
import logging
import threading
import time
from collections import defaultdict
from functools import wraps
import random
from typing import Any, Callable, Tuple, Optional

from common.contants import TIME_OUT_5


# ===== 同步版 retry =====
def retry(
        retries: int = 3,
        delay: float = 5,
        retry_condition: Callable[[Any], bool] = lambda result: not result,
        exceptions: Tuple[type, ...] = (Exception,),
):
    """
    同步函数重试装饰器。

    - retries: 最大重试次数
    - delay: 每次重试等待秒数
    - retry_condition: 返回 True 时触发重试
    - exceptions: 哪些异常需要重试
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Optional[BaseException] = None
            for attempt in range(1, retries + 1):
                try:
                    logging.info(f"\n==== Sync Retry 第 {attempt} 次 ====")
                    result = func(*args, **kwargs)
                    # 只有当 retry_condition 返回 True 时，才继续重试
                    if not retry_condition(result):
                        return result
                    logging.warning("条件未满足，准备重试…")
                except exceptions as exc:
                    last_exc = exc
                    logging.warning(f"第 {attempt} 次调用异常：{exc!r}")
                if attempt < retries:
                    logging.info(f"等待 {delay}s 后重试…")
                    time.sleep(delay)
            logging.error("重试次数用尽（Sync），操作失败。")
            if last_exc:
                raise last_exc
            return None

        return wrapper

    return decorator


# ===== 异步版 retry =====
def retry_async(
        retries: int = 3,
        delay: float = 5,
        retry_condition: Callable[[Any], bool] = lambda result: not result,
        exceptions: Tuple[type, ...] = (Exception,),
):
    """
    异步函数重试装饰器。

    - retries: 最大重试次数
    - delay: 每次重试等待秒数
    - retry_condition: 返回 True 时触发重试
    - exceptions: 哪些异常需要重试
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc: Optional[BaseException] = None
            for attempt in range(1, retries + 1):
                try:
                    logging.info(f"\n==== Async Retry 第 {attempt} 次 ====")
                    result = await func(*args, **kwargs)
                    if not retry_condition(result):
                        return result
                    logging.warning("条件未满足，准备重试…")
                except exceptions as exc:
                    last_exc = exc
                    logging.warning(f"第 {attempt} 次调用异常：{exc!r}")
                if attempt < retries:
                    logging.info(f"等待 {delay}s 后重试…")
                    await asyncio.sleep(random.uniform(1, delay))  # 使用随机延迟增加不确定性
            logging.error("重试次数用尽（Async），操作失败。")
            if last_exc:
                raise last_exc
            return None

        return wrapper

    return decorator


# ===== 同步版 print_after_return =====
def print_after_return(
        print_func: Callable[[Any], None],
        print_condition: Callable[[Any], bool] = lambda x: True
):
    """
    同步函数返回后打印装饰器。

    - print_func: 成功后调用的打印函数
    - print_condition: 返回 True 时才调用 print_func
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                if print_condition(result):
                    print_func(result)
            except Exception as e:
                logging.error(f"打印失败（Sync）：{e!r}")
            return result

        return wrapper

    return decorator


# ===== 异步版 print_after_return =====
def print_after_return_async(
        print_func: Callable[[Any], None],
        print_condition: Callable[[Any], bool] = lambda x: False
):
    """
    异步函数返回后打印装饰器。

    - print_func: 成功后调用的打印函数
    - print_condition: 返回 True 时才调用 print_func
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            try:
                if print_condition(result):
                    print_func(result)
            except Exception as e:
                logging.error(f"打印失败（Async）：{e!r}")
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
                logs_info = f"⏱️ {func.__name__}: {format_time(elapsed)}"
                if elapsed > TIME_OUT_5:  # 如果耗时超过5秒
                    logging.warning(logs_info)
                else:
                    logging.debug(logs_info)

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
                log_info = f"⏱️ [ASYNC] {func.__name__}: {format_time(elapsed)}"
                if elapsed > TIME_OUT_5:  # 如果耗时超过5秒
                    logging.warning(log_info)
                else:
                    logging.debug(log_info)

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


def print_performance_metrics(func):
    """输出程序运行的性能统计"""
    stats = func.get_stats()
    res = [f"\n📊 {stats['function']} 性能统计:",
           f"  调用次数: {stats['total_calls']}",
           f"  总耗时: {stats['total_time'] * 1000:.2f}ms",
           f"  平均耗时: {stats['avg_time'] * 1000:.2f}ms",
           f"  最快: {stats['min_time'] * 1000:.2f}ms | 最慢: {stats['max_time'] * 1000:.2f}ms"]
    print("\n".join(res))


# ===== 使用示例 =====

@retry(retries=4, delay=1, retry_condition=lambda x: x is None, exceptions=(ValueError,))
def sync_job():
    import random
    if random.random() < 0.7:
        raise ValueError("同步失败")
    return "Sync OK"


@retry_async(retries=4, delay=1, retry_condition=lambda x: x != "Async OK", exceptions=(RuntimeError,))
async def async_job():
    import random
    if random.random() < 0.7:
        raise RuntimeError("异步失败")
    return "Async OK"


@print_after_return(print_func=print, print_condition=lambda r: r is not None)
def sync_task(x):
    return x * 2


@print_after_return_async(print_func=lambda r: print(f"Async got: {r}"))
async def async_task(x):
    await asyncio.sleep(0.1)
    return x * 3


if __name__ == "__main__":
    # 同步测试
    print("sync_job():", sync_job())
    print("sync_task(5):", sync_task(5))


    # 异步测试
    async def main():
        print("async_job():", await async_job())
        print("async_task(7):", await async_task(7))


    asyncio.run(main())
