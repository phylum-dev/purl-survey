from pathlib import Path
import asyncio
import json
import inspect
import subprocess

from . import Error, Parts

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
        subprocess.run(("docker", "build", ".", "--iidfile", self._iidfile(), "--progress", "plain"), cwd=self._path(), check=True)

    async def parser(self):
        return await DockerParser.create(self._iid())

    async def formatter(self):
        return await DockerFormatter.create(self._iid())

class DockerParser:
    @classmethod
    async def create(cls, iid):
        this = DockerParser()
        this.process = await asyncio.create_subprocess_exec("docker", "run", "--rm", "-i", iid, "parse", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
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
                except Exception:
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
        this.process = await asyncio.create_subprocess_exec("docker", "run", "--rm", "-i", iid, "format", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return this

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        # The Python documentation says communicate always closes stdin,
        # but it only closes if a value is passed.
        try:
            await self.process.communicate(b"")
        except:
            try:
                self.process.kill()
            except:
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
