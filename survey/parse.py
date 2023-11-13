"""Read PURLs from stdin and describe them on stdout."""

import asyncio
import json
from contextlib import AsyncExitStack

from tqdm import tqdm

if __name__ == "__main__":
    from . import drivers

    async def main():
        async with AsyncExitStack() as exit_stack:
            with tqdm() as pbar:
                tasks = []
                async def run(driver):
                    parser = await exit_stack.enter_async_context(await driver.parser())
                    pbar.update()
                    return (driver, parser)

                for driver in drivers():
                    pbar.total = (pbar.total or 0) + 1
                    pbar.update(0)
                    tasks.append(run(driver))

                parsers = await asyncio.gather(*tasks)

            while True:
                try:
                    line = await asyncio.to_thread(input)
                except EOFError:
                    break
                line = line.strip()
                if line == "":
                    continue

                with tqdm(len(parsers)) as pbar:
                    tasks = []
                    async def parse(driver, parser):
                        [parts] = await parser.parse([line])
                        pbar.update()
                        return (driver, parts)

                    for (driver, parser) in parsers:
                        tasks.append(parse(driver, parser))

                    results = await asyncio.gather(*tasks)

                results.sort(key=lambda r: r[0].name)
                for (driver, result) in results:
                    print(f"{driver.name}: {json.dumps(result.normalize().to_json())}")

    asyncio.run(main())
