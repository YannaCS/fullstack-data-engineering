import asyncio

async def fake_non_blocking_IO_task(name, delay):
    print(f"{name} start")
    for i in range(delay):
        print(f"{name} running step {i+1}/{delay}")
        await asyncio.sleep(1)  # simulates async work
    print(f"{name} done")
    return f"{name} result"

async def async_run():
    # Create tasks instead of directly awaiting
    tasks = [
        asyncio.create_task(fake_non_blocking_IO_task(f"task {i}", 3))
        for i in range(3)
    ]

    # Show initial status
    for t in tasks:
        print(f"{t.get_name() if hasattr(t, 'get_name') else t} done? {t.done()}")

    # Wait for first task to finish partially (simulate pause/resume)
    await asyncio.sleep(2)
    print("\n--- After 2 seconds ---")
    for i, t in enumerate(tasks):
        print(f"Task {i} done? {t.done()}")

    # Optionally cancel a task
    print("\n--- Canceling task 1 ---")
    tasks[1].cancel()

    # Wait for remaining tasks to finish
    results = []
    for t in tasks:
        try:
            res = await t
            results.append(res)
        except asyncio.CancelledError:
            print(f"{t.get_name() if hasattr(t, 'get_name') else t} was cancelled")
    
    print("\nAll results:", results)


if __name__ == "__main__":
    asyncio.run(async_run())