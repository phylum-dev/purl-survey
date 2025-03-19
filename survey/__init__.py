from dataclasses import dataclass
from pathlib import Path
import importlib
from typing import Optional


@dataclass(frozen=True)
class Error:
    error: str

    def normalize(self):
        return self

    def to_json(self):
        return {"error": self.error}


@dataclass(frozen=True)
class Parts:
    type: str
    name: str
    namespace: Optional[str]
    version: Optional[str]
    qualifiers: Optional[dict[str, str]]
    subpath: Optional[str]

    def normalize(self):
        """
        Replace empty values with None and sorts dictionary keys.

        This makes comparison easier, and some of the format implementations behave differently when given an empty value.
        """
        type = self.type if self.type != "" else None
        name = self.name if self.name != "" else None
        namespace = self.namespace if self.namespace != "" else None
        version = self.version if self.version != "" else None
        if self.qualifiers is None or self.qualifiers == {}:
            qualifiers = None
        else:
            qualifiers = dict(sorted((self.qualifiers).items()))
        subpath = self.subpath if self.subpath != "" else None
        return Parts(
            type=type,
            name=name,
            namespace=namespace,
            version=version,
            qualifiers=qualifiers,
            subpath=subpath,
        )

    def casefold(self):
        """
        Casefold values.

        This is an invalid operation, but we use it for differentiating errors that are likely caused by unsupported type-specific rules.
        """
        # Type and the qualifier keys are not folded because the rules are clear and they are typically used in case sensitive matches.
        return Parts(
            type=self.type,
            name=self.name.casefold(),
            namespace=self.namespace.casefold() if self.namespace is not None else None,
            version=self.version.casefold() if self.version is not None else None,
            qualifiers={k: v.casefold() for k, v in self.qualifiers.items()}
            if self.qualifiers is not None
            else None,
            subpath=self.subpath.casefold() if self.subpath is not None else None,
        )

    @classmethod
    def from_json(cls, json):
        return Parts(
            type=json.get("type"),
            name=json.get("name"),
            namespace=json.get("namespace"),
            version=json.get("version"),
            qualifiers=json.get("qualifiers"),
            subpath=json.get("subpath"),
        )

    def to_json(self):
        d = {}
        if self.type is not None:
            d["type"] = self.type
        if self.name is not None:
            d["name"] = self.name
        if self.namespace is not None:
            d["namespace"] = self.namespace
        if self.version is not None:
            d["version"] = self.version
        if self.qualifiers is not None:
            d["qualifiers"] = self.qualifiers
        if self.subpath is not None:
            d["subpath"] = self.subpath
        return d


def drivers():
    """Enumerate all drivers."""

    root: Path = Path(__file__).parent / "drivers"
    owners = (
        owner
        for owner in root.iterdir()
        if owner.is_dir() and (owner / "__init__.py").exists()
    )
    repos = (
        repo
        for owner in owners
        for repo in owner.iterdir()
        if repo.is_dir() and (repo / "__init__.py").exists()
    )

    def make_module_path(path):
        return f"survey.drivers.{path.parent.name}.{path.name}"

    modules = (importlib.import_module(make_module_path(repo)) for repo in repos)
    classes = (
        c
        for c in (module.__dict__.get("Driver") for module in modules)
        if isinstance(c, type)
    )
    drivers = (c() for c in classes)

    return drivers
