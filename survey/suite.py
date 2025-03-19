"""Runs the PURL test suite against all implementations."""

import asyncio
import json
import sys
from dataclasses import dataclass
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

    all_drivers = [d for d in drivers()]

    with tqdm(total=len(suite) * len(all_drivers)) as pbar:

        async def main():
            tasks = []
            for driver in all_drivers:

                async def run(driver):
                    failures = []

                    async with await (
                        driver.parser()
                    ) as parser, await driver.formatter() as formatter:
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
                                            code="unexpected success",
                                            test=test["description"],
                                            reason=f"Expected an error parsing invalid PURL {test['purl']}",
                                            expected="[error]",
                                            actual=error.to_json(),
                                        )
                                    )
                                [error] = await formatter.format([parts])
                                if not isinstance(error, Error):
                                    failures.append(
                                        Failure(
                                            implementation=driver.name,
                                            code="unexpected success",
                                            test=test["description"],
                                            reason=f"Expected an error formatting invalid PURL {test['purl']}",
                                            expected="[error]",
                                            actual=error,
                                        )
                                    )
                            else:
                                [purl, canonical] = await parser.parse(
                                    [test["purl"], test["canonical_purl"]]
                                )
                                formatted = iter(
                                    await formatter.format(
                                        [
                                            p.normalize()
                                            for p in [purl, canonical]
                                            if not isinstance(p, Error)
                                        ]
                                        + [parts]
                                    )
                                )
                                if isinstance(purl, Error):
                                    purl_formatted = None
                                else:
                                    purl_formatted = next(formatted)
                                if isinstance(canonical, Error):
                                    canonical_formatted = None
                                else:
                                    canonical_formatted = next(formatted)
                                parts_formatted = next(formatted)

                                async def compare_to_canonical(
                                    parsed, formatted, name, is_from_parts=False
                                ):
                                    if formatted == test["canonical_purl"]:
                                        return
                                    [reparsed] = await parser.parse([formatted])
                                    if isinstance(reparsed, Error):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="unexpected failure",
                                                test=test["description"],
                                                reason=f"Parsing and re-formatting {name} PURL resulted in an invalid PURL",
                                                expected=test["canonical_purl"],
                                                actual=formatted,
                                            )
                                        )
                                    elif (
                                        is_from_parts
                                        and canonical.normalize()
                                        == reparsed.normalize()
                                    ):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="non-canonical",
                                                test=test["description"],
                                                reason=f"Formatting {name} PURL resulted in non-canonical PURL",
                                                expected=test["canonical_purl"],
                                                actual=formatted,
                                            )
                                        )
                                    elif (
                                        not is_from_parts
                                        and parsed.normalize() != reparsed.normalize()
                                    ):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="wrong values",
                                                test=test["description"],
                                                reason=f"Parsing and re-formatting {name} PURL resulted in a different PURL",
                                                expected=test["canonical_purl"],
                                                actual=formatted,
                                            )
                                        )
                                    elif unquote(canonical_formatted) == unquote(
                                        test["canonical_purl"]
                                    ):
                                        # This isn't exactly right, but other encoding problems should cause wrong_format first.
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="non-canonical",
                                                test=test["description"],
                                                reason=f"Parsing and re-formatting {name} PURL resulted in wrong encoding",
                                                expected=test["canonical_purl"],
                                                actual=formatted,
                                            )
                                        )
                                    elif (
                                        unquote(formatted).casefold()
                                        == unquote(test["canonical_purl"]).casefold()
                                    ):
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="wrong case",
                                                test=test["description"],
                                                reason=f"Parsing and re-formatting {name} PURL resulted in wrong casing",
                                                expected=test["canonical_purl"],
                                                actual=formatted,
                                            )
                                        )
                                    else:
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="wrong values",
                                                test=test["description"],
                                                reason=f"Parsing and re-formatting {name} PURL resulted in wrong PURL",
                                                expected=test["canonical_purl"],
                                                actual=formatted,
                                            )
                                        )

                                if isinstance(canonical, Error):
                                    failures.append(
                                        Failure(
                                            implementation=driver.name,
                                            code="unexpected failure",
                                            test=test["description"],
                                            reason=f"Unexpected error parsing canonical purl {test['canonical_purl']}",
                                            expected="[no error]",
                                            actual=canonical.to_json(),
                                        )
                                    )
                                elif (
                                    isinstance(canonical_formatted, Error)
                                    or canonical_formatted == ""
                                ):
                                    failures.append(
                                        Failure(
                                            implementation=driver.name,
                                            code="unexpected failure",
                                            test=test["description"],
                                            reason=f"Unexpected error formatting canonical purl {json.dumps(canonical.to_json())}",
                                            expected=test["canonical_purl"],
                                            actual=canonical_formatted.to_json(),
                                        )
                                    )
                                else:
                                    await compare_to_canonical(
                                        canonical, canonical_formatted, "canonical"
                                    )

                                if isinstance(purl, Error):
                                    failures.append(
                                        Failure(
                                            implementation=driver.name,
                                            code="unexpected failure",
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
                                            code="unexpected failure",
                                            test=test["description"],
                                            reason=f"Unexpected error formatting test purl {json.dumps(purl.to_json())}",
                                            expected=test["canonical_purl"],
                                            actual=purl_formatted.to_json(),
                                        )
                                    )
                                elif purl.normalize() != canonical.normalize():
                                    purl_folded = dict(
                                        (
                                            (
                                                k,
                                                v.casefold()
                                                if isinstance(v, str)
                                                else v,
                                            )
                                            for k, v in purl.normalize()
                                            .to_json()
                                            .items()
                                        )
                                    )
                                    canonical_folded = dict(
                                        (
                                            (
                                                k,
                                                v.casefold()
                                                if isinstance(v, str)
                                                else v,
                                            )
                                            for k, v in canonical.normalize()
                                            .to_json()
                                            .items()
                                        )
                                    )
                                    if purl_folded == canonical_folded:
                                        failures.append(
                                            Failure(
                                                implementation=driver.name,
                                                code="wrong case",
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
                                                code="wrong values",
                                                test=test["description"],
                                                reason="Parsing of canonical PURL and test PURL had different results",
                                                expected=canonical.to_json(),
                                                actual=purl.to_json(),
                                            )
                                        )
                                else:
                                    await compare_to_canonical(
                                        purl, purl_formatted, "test"
                                    )

                                if (
                                    isinstance(parts_formatted, Error)
                                    or parts_formatted == ""
                                ):
                                    failures.append(
                                        Failure(
                                            implementation=driver.name,
                                            code="unexpected failure",
                                            test=test["description"],
                                            reason=f"Unexpected error formatting {json.dumps(parts.to_json())}",
                                            expected=test["canonical_purl"],
                                            actual=parts_formatted.to_json(),
                                        )
                                    )
                                else:
                                    await compare_to_canonical(
                                        parts, parts_formatted, "from parts"
                                    )

                            pbar.update()
                    return failures

                tasks.append(run(driver))
            return await asyncio.gather(*tasks)

        all_failures = asyncio.run(main())
    all_failures = (failure for suite in all_failures for failure in suite)
    result = {
        "suite": suite,
        "failures": [f.to_json() for f in all_failures],
        "implementations": [
            {"name": d.name, "version": d.version} for d in all_drivers
        ],
    }

    json.dump(result, sys.stdout, indent=2)
