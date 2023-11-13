"""Runs the PURL test suite against all implementations."""

import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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

# Suppress these failures.
allowed = []
for allow_file in (Path(__file__).parent / "suite/allowed").glob("*.json"):
    with allow_file.open() as f:
        for allowed_failure in json.load(f):
            allowed.append(Failure.from_json(allowed_failure))

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
                                if test["is_invalid"]:
                                    [error] = await parser.parse([test["purl"]])
                                    if not isinstance(error, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_success",
                                                test=test["description"],
                                                reason=f"Expected an error for invalid purl {test['purl']}",
                                                expected="[error]",
                                                actual=error.normalize().to_json(),
                                            )
                                        )
                                else:
                                    expected = Parts(
                                        type=test["type"],
                                        name=test["name"],
                                        namespace=test["namespace"],
                                        version=test["version"],
                                        qualifiers=test["qualifiers"],
                                        subpath=test["subpath"],
                                    ).normalize()
                                    [purl, canonical] = await parser.parse(
                                        [test["purl"], test["canonical_purl"]]
                                    )
                                    if isinstance(purl, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Expected no error for valid purl {test['purl']}",
                                                expected=expected.to_json(),
                                                actual=purl.to_json(),
                                            )
                                        )
                                    elif isinstance(canonical, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Expected no error for canonical purl {test['canonical_purl']}",
                                                expected=expected.to_json(),
                                                actual=canonical.to_json(),
                                            )
                                        )
                                    else:
                                        if (
                                            expected.casefold()
                                            != purl.normalize().casefold()
                                        ):
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_parse",
                                                    test=test["description"],
                                                    reason=f"Wrong parse for valid purl {test['purl']}",
                                                    expected=expected.to_json(),
                                                    actual=purl.normalize().to_json(),
                                                )
                                            )
                                        elif (
                                            expected.normalize().casefold()
                                            != canonical.normalize().casefold()
                                        ):
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_parse",
                                                    test=test["description"],
                                                    reason=f"Wrong parse for canonical purl {test['canonical_purl']}",
                                                    expected=expected.to_json(),
                                                    actual=canonical.normalize().to_json(),
                                                )
                                            )
                                        elif expected.normalize() != purl.normalize():
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_parse_case",
                                                    test=test["description"],
                                                    reason=f"Wrong case for valid purl {test['purl']}",
                                                    expected=expected.to_json(),
                                                    actual=purl.normalize().to_json(),
                                                )
                                            )
                                        elif (
                                            expected.normalize()
                                            != canonical.normalize()
                                        ):
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_parse_case",
                                                    test=test["description"],
                                                    reason=f"Wrong case for canonical purl {test['canonical_purl']}",
                                                    expected=expected.normalize().to_json(),
                                                    actual=purl.normalize().to_json(),
                                                )
                                            )

                                    [formatted] = await formatter.format([expected])
                                    if isinstance(formatted, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Unexpected error formatting {json.dumps(expected.normalize().to_json())}",
                                                expected=test["canonical_purl"],
                                                actual=formatted.to_json(),
                                            )
                                        )
                                    elif formatted == "":
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected_failure",
                                                test=test["description"],
                                                reason=f"Unexpected error formatting {json.dumps(expected.normalize().to_json())}",
                                                expected=test["canonical_purl"],
                                                actual="",
                                            )
                                        )
                                    else:
                                        # Before we check that it's exactly right, check if it's right at all.
                                        [round_trip] = await parser.parse(
                                            [formatted]
                                        )
                                        if isinstance(round_trip, Error):
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="unexpected_failure",
                                                    test=test["description"],
                                                    reason=f"Unexpected error parsing serialized purl {formatted}",
                                                    expected=expected.to_json(),
                                                    actual=round_trip.to_json(),
                                                )
                                            )
                                        elif round_trip.normalize() != expected:
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="round_trip",
                                                    test=test["description"],
                                                    reason=f"Serialized purl {formatted} did not parse as its input",
                                                    expected=expected.normalize().to_json(),
                                                    actual=round_trip.normalize().to_json(),
                                                )
                                            )
                                        elif (
                                            formatted.casefold()
                                            != test["canonical_purl"].casefold()
                                        ):
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_format",
                                                    test=test["description"],
                                                    reason=f"Wrong format for {json.dumps(expected.normalize().to_json())}",
                                                    expected=test[
                                                        "canonical_purl"
                                                    ],
                                                    actual=formatted,
                                                )
                                            )
                                        elif (
                                            formatted != test["canonical_purl"]
                                        ):
                                            failures.append(
                                                Failure(
                                                    implementation=driver.name,
                                                    code="wrong_format_case",
                                                    test=test["description"],
                                                    reason=f"Wrong case for {json.dumps(expected.normalize().to_json())}",
                                                    expected=test[
                                                        "canonical_purl"
                                                    ],
                                                    actual=formatted,
                                                )
                                            )

                                pbar.update()
                    return failures

                tasks.append(run(driver))
            return await asyncio.gather(*tasks)

        all_failures = asyncio.run(main())
    all_failures = (failure for suite in all_failures for failure in suite)
    result = []
    for failure in sorted(all_failures):
        skip = False
        for allow in allowed:
            if (
                (
                    allow.implementation is None
                    or allow.implementation == failure.implementation
                )
                and (allow.code is None or allow.code == failure.code)
                and (allow.test is None or allow.test == failure.test)
                and (allow.reason is None or allow.reason == failure.reason)
                and (allow.expected is None or allow.expected == failure.expected)
                and (allow.actual is None or allow.actual == failure.actual)
            ):
                skip = True
                break
        if not skip:
            result.append(failure.to_json())

    print(json.dumps(result, indent=2))
    if len(result) > 0:
        sys.exit(1)
