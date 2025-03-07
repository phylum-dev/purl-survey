"""Runs the PURL test suite against all implementations."""

import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

from tqdm import tqdm


@dataclass(frozen=True, order=True)
class Failure:
    implementation: Optional[str]
    code: str
    test: str
    reason: Optional[str]
    expected: Optional[any]
    actual: any

    def to_json(self):
        return {
            "implementation": self.implementation,
            "code": self.code,
            "test": self.test,
            "reason": self.reason,
            "expected": self.expected,
            "actual": self.actual,
        }
    
    @classmethod
    def from_json(cls, j):
        return Failure(
            implementation=j.get("implementation"),
            code=j.get("code"),
            test=j.get("test"),
            reason=j.get("reason"),
            expected=j.get("expected"),
            actual=j.get("actual"),
        )

if __name__ == "__main__":
    from . import drivers, Error, Parts

    with open("spec/test-suite-data.json", "rb") as f:
        suite = json.load(f)

    with tqdm() as pbar:

        async def main():
            tasks = []
            for driver in drivers():
                pbar.total = (pbar.total or 0) + len(suite)
                pbar.update(0)

                async def run(driver):
                    failures = []

                    async with await driver.parser() as parser:
                        async with await driver.formatter() as formatter:
                            for test in suite:
                                parts = Parts(
                                    type=test["type"],
                                    name=test["name"],
                                    namespace=test["namespace"],
                                    version=test["version"],
                                    qualifiers=test["qualifiers"],
                                    subpath=test["subpath"],
                                )

                                if test["is_invalid"]:
                                    [error] = await parser.parse([test["purl"]])
                                    if not isinstance(error, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_success",
                                                test=test["description"],
                                                reason=f"Expected an error parsing invalid purl {test['purl']}",
                                                expected="[error]",
                                                actual=error.to_json(),
                                            )
                                        )
                                    [error] = await formatter.format([parts])
                                    if not isinstance(error, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_success",
                                                test=test["description"],
                                                reason=f"Expected an error formatting invalid purl {test['purl']}",
                                                expected="[error]",
                                                actual=error,
                                            )
                                        )
                                else:
                                    [purl, canonical] = await parser.parse(
                                        [test["purl"], test["canonical_purl"]]
                                    )
                                    formatted = iter(await formatter.format(
                                        [p.normalize() for p in [purl, canonical] if not isinstance(p, Error)] + [parts]
                                    ))
                                    if isinstance(purl, Error):
                                        purl_formatted = None
                                    else:
                                        purl_formatted = next(formatted)
                                    if isinstance(canonical, Error):
                                        canonical_formatted = None
                                    else:
                                        canonical_formatted = next(formatted)
                                    parts_formatted = next(formatted)

                                    async def compare_to_canonical(parsed, formatted, name):
                                        if formatted == test['canonical_purl']:
                                            return
                                        [reparsed] = await parser.parse([formatted])
                                        if isinstance(reparsed, Error):
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_format",
                                                    test=test["description"],
                                                    reason=f"Parsing and re-formatting {name} PURL resulted in an invalid PURL {formatted}",
                                                    expected=test["canonical_purl"],
                                                    actual=formatted,
                                                )
                                            )
                                        elif parsed.normalize() != reparsed.normalize():
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_format",
                                                    test=test["description"],
                                                    reason=f"Parsing and re-formatting {name} PURL resulted in a different PURL",
                                                    expected=test["canonical_purl"],
                                                    actual=canonical_formatted,
                                                )
                                            )
                                        elif unquote(canonical_formatted) == unquote(test["canonical_purl"]):
                                            # This isn't exactly right, but other encoding problems should cause wrong_format first.
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_encode",
                                                    test=test["description"],
                                                    reason=f"Parsing and re-formatting {name} PURL resulted in wrong encoding",
                                                    expected=test["canonical_purl"],
                                                    actual=canonical_formatted,
                                                )
                                            )
                                        elif unquote(formatted).casefold() == unquote(test["canonical_purl"]).casefold():
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_case",
                                                    test=test["description"],
                                                    reason=f"Parsing and re-formatting {name} PURL resulted in wrong casing",
                                                    expected=test["canonical_purl"],
                                                    actual=canonical_formatted,
                                                )
                                            )
                                        else:
                                            # Formatting errors should be caught by the above cases.
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_parse",
                                                    test=test["description"],
                                                    reason=f"Parsing and re-formatting {name} PURL resulted in wrong PURL",
                                                    expected=test["canonical_purl"],
                                                    actual=canonical_formatted,
                                                )
                                            )

                                    if isinstance(canonical, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Unexpected error parsing canonical purl {test['canonical_purl']}",
                                                expected="[no error]",
                                                actual=canonical.to_json(),
                                            )
                                        )
                                    elif isinstance(canonical_formatted, Error) or canonical_formatted == "":
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Unexpected error formatting canonical purl {json.dumps(canonical.to_json())}",
                                                expected=test["canonical_purl"],
                                                actual=formatted.to_json(),
                                            )
                                        )
                                    else:
                                        await compare_to_canonical(canonical, canonical_formatted, "canonical")

                                    if isinstance(purl, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Expected no error parsing test purl {test['purl']}",
                                                expected=canonical.to_json(),
                                                actual=purl.to_json(),
                                            )
                                        )
                                    elif isinstance(purl_formatted, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Unexpected error formatting test purl {json.dumps(purl.to_json())}",
                                                expected=test["canonical_purl"],
                                                actual=formatted.to_json(),
                                            )
                                        )
                                    elif purl.normalize() != canonical.normalize():
                                        purl_folded = dict(((k, v.casefold() if isinstance(v, str) else v) for k, v in purl.normalize().to_json().items()))
                                        canonical_folded = dict(((k, v.casefold() if isinstance(v, str) else v) for k, v in canonical.normalize().to_json().items()))
                                        if purl_folded == canonical_folded:
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_case",
                                                    test=test["description"],
                                                    reason="Parsing of canonical PURL and test PURL had different case",
                                                    expected=canonical.to_json(),
                                                    actual=purl.to_json(),
                                                )
                                            )
                                        else:
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_parse",
                                                    test=test["description"],
                                                    reason="Parsing of canonical PURL and test PURL had different results",
                                                    expected=canonical.to_json(),
                                                    actual=purl.to_json(),
                                                )
                                            )
                                    else:
                                        await compare_to_canonical(purl, purl_formatted, "test")

                                    if isinstance(parts_formatted, Error) or parts_formatted == "":
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Unexpected error formatting {json.dumps(parts.to_json())}",
                                                expected=test["canonical_purl"],
                                                actual="[error]",
                                            )
                                        )
                                    else:
                                        await compare_to_canonical(parts, parts_formatted, "from parts")

                                pbar.update()
                    return failures

                tasks.append(run(driver))
            return await asyncio.gather(*tasks)

        all_failures = asyncio.run(main())
    all_failures = (failure for suite in all_failures for failure in suite)
    result = [f.to_json() for f in sorted(all_failures)]

    print(json.dumps(result, indent=2))
    if len(result) > 0:
        sys.exit(1)
