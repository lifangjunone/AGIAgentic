

import sniffio

# 检测当前使用的异步框架
async def run():
    current_framework = sniffio.current_async_library()
    print(f"当前异步框架是：{current_framework}")


if __name__ == "__main__":
  # 在 asyncio 中运行
  import asyncio
  asyncio.run(run())

  # 在 trio 中运行
  import trio
  trio.run(run)
