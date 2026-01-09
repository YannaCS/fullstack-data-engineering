import asyncio

async def fake_non_blocking_IO_task(name):
    print(f"{name} start async I/O task")
    await asyncio.sleep(2)
    print(f"{name} done")

async def async_run():
    start = asyncio.get_event_loop().time()
    await asyncio.gather(*[fake_non_blocking_IO_task(f"task {i}") for i in range(5)])
    print(f"[Async IO] Total time: {asyncio.get_event_loop().time() - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(async_run())