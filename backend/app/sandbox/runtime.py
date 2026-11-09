import shutil
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ULTRON.LanguageRuntime")


class LanguageRuntime(ABC):
    """Abstract Base Class for pluggable language runtimes."""

    def __init__(self, language: str, file_extensions: List[str]):
        self.language = language
        self.file_extensions = file_extensions

    @abstractmethod
    def is_available(self) -> bool:
        """Check if compiler/interpreter for language is installed and available."""
        pass

    @abstractmethod
    def is_compiled(self) -> bool:
        """Return True if language requires a compilation step."""
        pass

    @abstractmethod
    def get_compile_command(self, entrypoint: str, output_binary: str = "main_exec") -> List[str]:
        """Return compile command list."""
        pass

    @abstractmethod
    def get_run_command(self, entrypoint: str, output_binary: str = "main_exec", args: Optional[List[str]] = None) -> List[str]:
        """Return execution command list."""
        pass

    def get_test_command(self, test_file: str) -> List[str]:
        """Return default test execution command list."""
        return self.get_run_command(test_file)


class PythonRuntime(LanguageRuntime):

    def __init__(self):
        super().__init__("python", [".py"])

    def is_available(self) -> bool:
        return shutil.which("python") is not None or shutil.which("python3") is not None

    def is_compiled(self) -> bool:
        return False

    def get_compile_command(self, entrypoint: str, output_binary: str = "main_exec") -> List[str]:
        return []

    def get_run_command(self, entrypoint: str, output_binary: str = "main_exec", args: Optional[List[str]] = None) -> List[str]:
        py_bin = shutil.which("python") or shutil.which("python3") or "python"
        if entrypoint.startswith("-c"):
            code_part = entrypoint[2:].strip()
            cmd = [py_bin, "-c", code_part]
        else:
            cmd = [py_bin, entrypoint]
        if args:
            cmd.extend(args)
        return cmd

    def get_test_command(self, test_file: str) -> List[str]:
        py_bin = shutil.which("python") or shutil.which("python3") or "python"
        return [py_bin, "-m", "unittest", test_file]


class JavaScriptRuntime(LanguageRuntime):

    def __init__(self):
        super().__init__("javascript", [".js", ".cjs", ".mjs"])

    def is_available(self) -> bool:
        return shutil.which("node") is not None

    def is_compiled(self) -> bool:
        return False

    def get_compile_command(self, entrypoint: str, output_binary: str = "main_exec") -> List[str]:
        return []

    def get_run_command(self, entrypoint: str, output_binary: str = "main_exec", args: Optional[List[str]] = None) -> List[str]:
        node_bin = shutil.which("node") or "node"
        cmd = [node_bin, entrypoint]
        if args:
            cmd.extend(args)
        return cmd

    def get_test_command(self, test_file: str) -> List[str]:
        node_bin = shutil.which("node") or "node"
        return [node_bin, "--test", test_file]


class CRuntime(LanguageRuntime):

    def __init__(self):
        super().__init__("c", [".c", ".h"])

    def is_available(self) -> bool:
        return shutil.which("gcc") is not None or shutil.which("clang") is not None or shutil.which("cl") is not None

    def is_compiled(self) -> bool:
        return True

    def get_compile_command(self, entrypoint: str, output_binary: str = "main_exec") -> List[str]:
        gcc_bin = shutil.which("gcc") or shutil.which("clang") or "gcc"
        out_name = f"{output_binary}.exe" if shutil.which("gcc") and "win" in gcc_bin.lower() else output_binary
        return [gcc_bin, entrypoint, "-o", out_name]

    def get_run_command(self, entrypoint: str, output_binary: str = "main_exec", args: Optional[List[str]] = None) -> List[str]:
        bin_path = f"./{output_binary}.exe" if shutil.which("gcc") and "win" in (shutil.which("gcc") or "").lower() else f"./{output_binary}"
        cmd = [bin_path]
        if args:
            cmd.extend(args)
        return cmd


class CppRuntime(LanguageRuntime):

    def __init__(self):
        super().__init__("cpp", [".cpp", ".hpp", ".cc", ".cxx"])

    def is_available(self) -> bool:
        return shutil.which("g++") is not None or shutil.which("clang++") is not None or shutil.which("cl") is not None

    def is_compiled(self) -> bool:
        return True

    def get_compile_command(self, entrypoint: str, output_binary: str = "main_exec") -> List[str]:
        gpp_bin = shutil.which("g++") or shutil.which("clang++") or "g++"
        out_name = f"{output_binary}.exe" if shutil.which("g++") and "win" in gpp_bin.lower() else output_binary
        return [gpp_bin, entrypoint, "-o", out_name]

    def get_run_command(self, entrypoint: str, output_binary: str = "main_exec", args: Optional[List[str]] = None) -> List[str]:
        bin_path = f"./{output_binary}.exe" if shutil.which("g++") and "win" in (shutil.which("g++") or "").lower() else f"./{output_binary}"
        cmd = [bin_path]
        if args:
            cmd.extend(args)
        return cmd


class RuntimeRegistry:

    def __init__(self):
        self._runtimes: Dict[str, LanguageRuntime] = {
            "python": PythonRuntime(),
            "javascript": JavaScriptRuntime(),
            "js": JavaScriptRuntime(),
            "c": CRuntime(),
            "cpp": CppRuntime(),
            "c++": CppRuntime()
        }

    def get_runtime(self, language: str) -> LanguageRuntime:
        lang_clean = language.lower().strip()
        runtime = self._runtimes.get(lang_clean)
        if not runtime:
            raise ValueError(f"UNSUPPORTED_LANGUAGE: Language '{language}' is not supported.")
        return runtime


default_runtime_registry = RuntimeRegistry()
