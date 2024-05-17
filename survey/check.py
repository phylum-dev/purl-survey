"""Read PURLs from stdin and detect differences in parsing."""

import asyncio
import json
from collections import namedtuple
from contextlib import AsyncExitStack

from tqdm import tqdm

from . import Error

Implementation = namedtuple('Implementation', ('driver', 'parser', 'formatter'))

if __name__ == "__main__":
    from . import drivers

    async def main():
        async with AsyncExitStack() as exit_stack:
            with tqdm() as pbar:
                tasks = []
                async def run(driver):
                    parser = await exit_stack.enter_async_context(await driver.parser())
                    formatter = await exit_stack.enter_async_context(await driver.formatter())
                    pbar.update()
                    return Implementation(driver, parser, formatter)

                for driver in drivers():
                    pbar.total = (pbar.total or 0) + 1
                    pbar.update(0)
                    tasks.append(run(driver))

                impls = await asyncio.gather(*tasks)

            while True:
                try:
                    line = await asyncio.to_thread(input)
                except EOFError:
                    break
                line = line.strip()
                if line == "":
                    continue

                seen = {line}
                stack = [line]
                while len(stack) > 0:
                    # Parse the PURL with every implementation.
                    purl = stack.pop()
                    with tqdm(len(impls)) as pbar:
                        tasks = []
                        async def parse(impl):
                            [parts] = await impl.parser.parse([purl])
                            pbar.update()
                            return (impl, parts.normalize())

                        for impl in impls:
                            tasks.append(parse(impl))

                        results = await asyncio.gather(*tasks)

                    # If any of the implementations disagree, that's an error.
                    parse_results = dict()
                    for (impl, parts) in results:
                        parse_results.setdefault(json.dumps(parts.to_json()), (parts, []))[1].append(impl)

                    if len(parse_results) > 1:
                        print("Parsers disagree")
                        for result, result_impls in parse_results.values():
                            print(f"{json.dumps(result.to_json())}: {', '.join((i.driver.name) for i in result_impls)}")
                        break

                    # The implementations agree, so format the parts with every implementation.
                    parts = next(iter(parse_results.values()))[0]
                    print(f"{purl} parsed to {json.dumps(parts.to_json())}")

                    if isinstance(parts, Error):
                        # We can't format the error, and we already printed it, so just break out.
                        break

                    with tqdm(len(impls)) as pbar:
                        tasks = []
                        async def format(impl):
                            [formatted] = await impl.formatter.format([parts])
                            pbar.update()
                            return (impl, formatted)

                        for impl in impls:
                            tasks.append(format(impl))

                        results = await asyncio.gather(*tasks)

                    # If any of the implementations returns something new, report it and mark it for follow up.
                    format_results = dict()
                    for (impl, formatted) in results:
                        if isinstance(formatted, Error):
                            print(f"Error from {impl.driver.name}: {formatted}")
                        else:
                            format_results.setdefault(formatted, []).append(impl)

                    for formatted, result_impls in format_results.items():
                        if formatted not in seen:
                            print(f"Formatted as {json.dumps(formatted)} by {', '.join((i.driver.name) for i in result_impls)}")
                            seen.add(formatted)
                            stack.append(formatted)

    asyncio.run(main())
