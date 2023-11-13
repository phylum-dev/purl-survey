"""Read JSON from stdin and write PURLs on stdout."""

import asyncio
import json
from contextlib import AsyncExitStack

from tqdm import tqdm

from . import Parts

if __name__ == "__main__":
    from . import drivers

    async def main():
        async with AsyncExitStack() as exit_stack:
            with tqdm() as pbar:
                tasks = []
                async def run(driver):
                    formatter = await exit_stack.enter_async_context(await driver.formatter())
                    pbar.update()
                    return (driver, formatter)

                for driver in drivers():
                    pbar.total = (pbar.total or 0) + 1
                    pbar.update(0)
                    tasks.append(run(driver))

                formatters = await asyncio.gather(*tasks)

            while True:
                try:
                    line = await asyncio.to_thread(input)
                except EOFError:
                    break
                line = line.strip()
                if line == "":
                    continue

                try:
                    line = Parts.from_json(json.loads(line))
                except json.JSONDecodeError:
                    print("Invalid json")
                    continue

                with tqdm(len(formatters)) as pbar:
                    tasks = []
                    async def format(driver, formatter):
                        [parts] = await formatter.format([line])
                        pbar.update()
                        return (driver, parts)

                    for (driver, formatter) in formatters:
                        tasks.append(format(driver, formatter))

                    results = await asyncio.gather(*tasks)

                results.sort(key=lambda r: r[0].name)
                for (driver, result) in results:
                    print(f"{driver.name}: {result}")

    asyncio.run(main())
