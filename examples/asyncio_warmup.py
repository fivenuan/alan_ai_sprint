"""Day 3 热身：asyncio 最小可运行例子。

跑法（项目根目录）::

    uv run python examples/asyncio_warmup.py

对应学习资料《04-asyncio-day3.md》第 2–4 节。三个演示都是完整可跑的；
最后留了 3 个热身练习的空位（资料第 10 节），写完 3 个练习再进 fetcher.py。
"""

import asyncio
import time


async def boil_water() -> str:
    print("  烧水：开始")
    await asyncio.sleep(3)  # 模拟 I/O 等待：让出控制权，3 秒后回来
    print("  烧水：完成")
    return "开水"


async def cut_vegetables() -> str:
    print("  切菜：开始")
    await asyncio.sleep(2)
    print("  切菜：完成")
    return "菜"


def demo_1_serial() -> None:
    """演示 1：逐个 await —— 还是串行，5 秒。"""
    print("== demo 1: 串行（先等水开，再切菜）==")
    start = time.perf_counter()
    water = asyncio.run(boil_water())
    veg = asyncio.run(cut_vegetables())
    print(f"总耗时 {time.perf_counter() - start:.1f}s，结果: {water} + {veg}\n")


def demo_2_concurrent() -> None:
    """演示 2：gather 同时跑 —— 3 秒（最慢的那个）。"""
    print("== demo 2: 并发（gather 同时发车）==")
    start = time.perf_counter()

    async def main() -> tuple[str, str]:
        return await asyncio.gather(boil_water(), cut_vegetables())

    water, veg = asyncio.run(main())
    print(f"总耗时 {time.perf_counter() - start:.1f}s，结果: {water} + {veg}\n")


def demo_3_gather_exceptions() -> None:
    """演示 3：gather + return_exceptions —— 一个任务炸了，其他照常返回。"""

    async def ok_task(name: str) -> str:
        await asyncio.sleep(0.5)
        return f"{name}: ok"

    async def bad_task() -> str:
        await asyncio.sleep(0.2)
        msg = "模拟 API 返回 500"
        raise RuntimeError(msg)

    async def main() -> list[str | BaseException]:
        return await asyncio.gather(
            ok_task("A"),
            bad_task(),
            ok_task("C"),
            return_exceptions=True,  # 想让一个失败不炸整批，就开这个
        )

    print("== demo 3: gather 异常处理 ==")
    results = asyncio.run(main())
    for item in results:
        if isinstance(item, BaseException):
            print(f"  失败 -> {type(item).__name__}: {item}")
        else:
            print(f"  成功 -> {item}")
    print()


def demo_4_semaphore() -> None:
    """演示 4：Semaphore 限流 —— 100 个任务、最多 10 个同时在跑。"""
    running = {"now": 0, "peak": 0}

    async def limited(name: int, sem: asyncio.Semaphore) -> int:
        async with sem:  # 进入：拿令牌（没拿到就排队）
            running["now"] += 1
            running["peak"] = max(running["peak"], running["now"])
            await asyncio.sleep(0.1)  # 模拟一次请求
            running["now"] -= 1
        return name

    async def main() -> list[int]:
        sem = asyncio.Semaphore(10)
        return await asyncio.gather(*[limited(i, sem) for i in range(100)])

    print("== demo 4: Semaphore 限流 ==")
    start = time.perf_counter()
    results = asyncio.run(main())
    print(
        f"  完成 {len(results)} 个任务，"
        f"峰值并发 = {running['peak']}（应为 10），"
        f"总耗时 {time.perf_counter() - start:.2f}s（约 1s = 10 批 x 0.1s）\n"
    )


if __name__ == "__main__":
    demo_1_serial()
    demo_2_concurrent()
    demo_3_gather_exceptions()
    demo_4_semaphore()

    # ==========================================================
    # 热身练习（资料第 10 节）—— 在下面补全，跑通后进 fetcher.py
    # ==========================================================

    # 练习 1：写一个函数对比 time.sleep 和 asyncio.sleep
    #   5 个并发任务各睡 1 秒：
    #   - 用 asyncio.sleep 的版本总耗时 ≈ 1s
    #   - 换成 time.sleep 的版本总耗时 ≈ 5s（事件循环被冻住）
    #   把两个数字都 print 出来。坑要自己踩过才算认识。

    # 练习 2："最慢者定胜负"实验
    #   5 个协程 delay 分别 0.5/1/1.5/2/2.5s，gather 一起跑，
    #   量总耗时。先心算答案，再跑代码验证。
