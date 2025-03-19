from functools import cache
from pathlib import Path
import asyncio
import json
import inspect
import subprocess
import traceback
import os

from . import Error, Parts

docker = os.environ.get("PURL_SURVEY_DOCKER", "docker")


class DockerDriver:
    """A driver that builds using a Dockerfile and runs in a container."""

    def __init__(self):
        if not hasattr(self, "name"):
            self.name = type(self).__module__

    def _path(self):
        return Path(inspect.getfile(type(self))).parent

    def _iidfile(self):
        return self._path() / "image"

    def _iid(self):
        return self._iidfile().read_text()

    def build(self):
        version = subprocess.run(
            ("git", "describe", "--tags", "--always"),
            cwd=self._path() / "repo",
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        ).stdout.strip()
        subprocess.run(
            (
                docker,
                "build",
                ".",
                "--iidfile",
                self._iidfile(),
                "--progress",
                "plain",
                f"--label=version={version}",
            ),
            cwd=self._path(),
            stdin=subprocess.DEVNULL,
            check=True,
        )
        if not self._iidfile().exists():
            raise Exception(
                f"Completed build of {self.name} without producing {self._iidfile()}"
            )

    async def parser(self):
        try:
            return await DockerParser.create(self._iid())
        except Exception:
            # asyncio can cause a deadlock if processes are cancelled too soon.
            # print the error now so we can see it
            traceback.print_exc()
            raise

    async def formatter(self):
        try:
            return await DockerFormatter.create(self._iid())
        except Exception:
            # asyncio can cause a deadlock if processes are cancelled too soon.
            # print the error now so we can see it
            traceback.print_exc()
            raise

    @property
    @cache
    def version(self):
        meta = json.loads(
            subprocess.run(
                (docker, "image", "inspect", self._iid()),
                cwd=self._path(),
                stdout=subprocess.PIPE,
                check=True,
            ).stdout
        )
        return meta[0]["Config"]["Labels"]["version"]


class DockerParser:
    @classmethod
    async def create(cls, iid):
        this = DockerParser()
        this.process = await asyncio.create_subprocess_exec(
            docker,
            "run",
            "--rm",
            "-i",
            iid,
            "parse",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        return this

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # The Python documentation says communicate always closes stdin,
        # but it only closes if a value is passed.
        try:
            await self.process.communicate(b"")
        except Exception:
            pass

    async def parse(self, purls):
        async def write_request():
            for purl in purls:
                self.process.stdin.write(f"{purl}\n".encode())
            await self.process.stdin.drain()

        async def read_response():
            results = []
            for _ in purls:
                line = await self.process.stdout.readline()
                try:
                    line = json.loads(line)
                except json.JSONDecodeError:
                    line = {"error": f"invalid json: {line}"}
                error = line.get("error")
                if error is not None:
                    results.append(Error(error))
                else:
                    results.append(Parts.from_json(line).normalize())
            return results

        (_, response) = await asyncio.gather(write_request(), read_response())
        return response


class DockerFormatter:
    @classmethod
    async def create(cls, iid):
        this = DockerFormatter()
        this.process = await asyncio.create_subprocess_exec(
            docker,
            "run",
            "--rm",
            "-i",
            iid,
            "format",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        return this

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # The Python documentation says communicate always closes stdin,
        # but it only closes if a value is passed.
        try:
            await self.process.communicate(b"")
        except Exception:
            try:
                self.process.kill()
            except Exception:
                pass

    async def format(self, purls):
        async def write_request():
            for purl in purls:
                self.process.stdin.write(f"{json.dumps(purl.to_json())}\n".encode())
            await self.process.stdin.drain()

        async def read_response():
            results = []
            for _ in purls:
                line = await self.process.stdout.readline()
                if line.startswith(b"{"):
                    line = json.loads(line)
                    results.append(Error(line.get("error")))
                else:
                    results.append(line.decode().strip())
            return results

        (_, response) = await asyncio.gather(write_request(), read_response())
        return response
