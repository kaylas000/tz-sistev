"""Sandbox: исполнение артефактов в изоляции (ТЗ §10.1 E2B / Docker / Local).

Local — по умолчанию, без внешних зависимостей (подпроцесс с таймаутом).
Docker/E2B — адаптеры; используются если докеры/SDK доступны.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class SandboxResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    error: str = ""


class Sandbox(ABC):
    name: str = "abstract"

    @abstractmethod
    def run_python(self, code: str, timeout: int = 30) -> SandboxResult: ...

    @abstractmethod
    def write_file(self, rel_path: str, content: str) -> Path: ...

    def cleanup(self) -> None:  # pragma: no cover - хук
        pass


class LocalSandbox(Sandbox):
    """Локальная песочница: временный каталог + подпроцесс python с таймаутом."""
    name = "local"

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.dir = Path(root) if root else Path(tempfile.mkdtemp(prefix="autogen-sbx-"))
        self.dir.mkdir(parents=True, exist_ok=True)

    def write_file(self, rel_path: str, content: str) -> Path:
        p = self.dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def run_python(self, code: str, timeout: int = 30) -> SandboxResult:
        script = self.write_file("main.py", code)
        try:
            proc = subprocess.run(
                ["python3", str(script)], capture_output=True, text=True,
                timeout=timeout, cwd=str(self.dir),
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(ok=False, error=f"L-01: превышен таймаут песочницы ({timeout}s)")
        except FileNotFoundError:
            return SandboxResult(ok=False, error="L-01: python3 не найден")
        return SandboxResult(
            ok=proc.returncode == 0, stdout=proc.stdout, stderr=proc.stderr,
            exit_code=proc.returncode,
        )

    def cleanup(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


class DockerSandbox(LocalSandbox):
    """Запуск через `docker run` (если docker доступен), иначе деградация к local."""
    name = "docker"

    def __init__(self, image: str = "python:3.12-slim") -> None:
        super().__init__()
        self.image = image
        self._has_docker = shutil.which("docker") is not None

    def run_python(self, code: str, timeout: int = 30) -> SandboxResult:
        if not self._has_docker:
            result = super().run_python(code, timeout)
            result.error = (result.error + " [docker недоступен, использован local]").strip()
            return result
        script = self.write_file("main.py", code)
        cmd = ["docker", "run", "--rm", "-v", f"{self.dir}:/sbx", "-w", "/sbx",
               "--network", "none", self.image, "python", "main.py"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return SandboxResult(ok=False, error=f"L-01: таймаут docker-песочницы ({timeout}s)")
        return SandboxResult(ok=proc.returncode == 0, stdout=proc.stdout,
                             stderr=proc.stderr, exit_code=proc.returncode)


class E2BSandbox(Sandbox):
    """Песочница E2B (e2b SDK опционален)."""
    name = "e2b"

    def __init__(self, api_key: Optional[str] = None) -> None:
        try:
            from e2b_code_interpreter import Sandbox as _E2B  # type: ignore
            self._sb = _E2B(api_key=api_key)
        except Exception as exc:  # ImportError и любые сетевые ошибки
            raise RuntimeError(f"E2B недоступна: {exc}") from exc

    def write_file(self, rel_path: str, content: str) -> Path:
        self._sb.files.write(f"/home/user/{rel_path}", content)
        return Path(rel_path)

    def run_python(self, code: str, timeout: int = 30) -> SandboxResult:
        try:
            ex = self._sb.run_code(code, timeout=timeout)
            return SandboxResult(ok=ex.error is None, stdout="".join(ex.logs.stdout or []),
                                 stderr=str(ex.error or ""), exit_code=0 if ex.error is None else 1)
        except Exception as exc:
            return SandboxResult(ok=False, error=f"L-01: {exc}")


def make_sandbox(kind: str = "local", **kw) -> Sandbox:
    kinds = {"local": LocalSandbox, "docker": DockerSandbox, "e2b": E2BSandbox}
    if kind not in kinds:
        raise ValueError(f"Неизвестный тип песочницы: {kind}")
    return kinds[kind](**kw)
