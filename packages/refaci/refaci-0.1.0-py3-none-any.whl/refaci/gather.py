import ast
import json
import os
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Symbol:
    path: str
    name: str


def parse_file(filepath: Path) -> list[str]:
    root = ast.parse(filepath.read_text())
    # Note that we only look at the top level of the file. We do not concern ourselves with nested classes or functions.
    return [node.name for node in root.body if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)]


def find_py_files(path: Path) -> list[Path]:
    py_files = []
    for root, dirs, files in os.walk(path):
        if "tests" in dirs:
            dirs.remove("tests")
        if "venv" in dirs:
            dirs.remove("venv")
        if ".venv" in dirs:
            dirs.remove(".venv")
        for file in files:
            if file.endswith(".py"):
                py_files.append(Path(root, file))

    return py_files


def gather_names(package: Path) -> list[Symbol]:
    py_files = find_py_files(package)
    result = []
    for py_file in py_files:
        symbols = parse_file(py_file)
        # I wish I had the strength to rewrite it using pathlib but who cares
        relative_path = os.path.relpath(py_file, start=package).replace("\\", "/").replace(".py", "").replace("/", ".")
        for symbol in symbols:
            result.append(Symbol(f"{relative_path}.{symbol}", symbol))
    return result


def main(original_packages: Collection[Path], new_packages: Collection[Path]) -> None:
    main_package_result = {p.name: p.path for path in original_packages for p in gather_names(path)}
    subpackage_results = {p.name: p.path for path in new_packages for p in gather_names(path)}

    moved_symbols = {}
    removed_symbols = {}
    new_symbols = {}

    for p, ppath in main_package_result.items():
        if p in subpackage_results:
            moved_symbols[p] = (ppath.rsplit(".", 1)[0], subpackage_results[p].rsplit(".", 1)[0])
        else:
            removed_symbols[p] = ppath.rsplit(".", 1)[0]

    for p, ppath in subpackage_results.items():
        if p not in main_package_result and p not in moved_symbols:
            new_symbols[p] = subpackage_results[p].rsplit(".", 1)[0]
    print(
        json.dumps(
            {
                "moved": moved_symbols,
                "removed": removed_symbols,
                "new": new_symbols,
            },
            ensure_ascii=False,
            indent=4,
        ),
    )
