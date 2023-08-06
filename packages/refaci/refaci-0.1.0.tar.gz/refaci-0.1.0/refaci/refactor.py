import ast
import itertools
import json
import re
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Collection


def refactor(
    dir_or_path: Path,
    imports_to_change: dict[str, tuple[str, str]] = {},
    missing_imports_to_add: dict[str, str] = {},
    replacements: dict["PathRegex | ContentsRegex", Sequence[tuple[str, str]]] = {},
):
    if dir_or_path.is_file():
        files = [dir_or_path]
    else:
        files = dir_or_path.glob("**/*.py")

    path_replacements = {
        regex: replacements for regex, replacements in replacements.items() if isinstance(regex, PathRegex)
    }
    contents_re = {
        regex: replacements for regex, replacements in replacements.items() if isinstance(regex, ContentsRegex)
    }

    for file in files:
        print(str(file))
        try:
            contents = file.read_text()
            file_replacements = []
            file_replacements.extend(
                [replacements for regex, replacements in path_replacements.items() if regex.pattern.search(str(file))],
            )
            file_replacements.extend(
                [replacements for regex, replacements in contents_re.items() if regex.pattern.search(contents)],
            )
            file_replacements = itertools.chain.from_iterable(file_replacements)
            contents = refactor_imports(contents, imports_to_change, missing_imports_to_add)
            contents = globally_replace(contents, file_replacements)
            file.write_text(contents)
        except Exception as e:
            print(repr(e))


def refactor_imports(
    contents: str,
    imports_to_change: dict[str, tuple[str, str]] = {},
    missing_imports_to_add: dict[str, str] = {},
):
    modules = to_modules(imports_to_change)
    tree = ast.parse(contents)
    lines: list[str | list[str]] = contents.splitlines()

    for node in ast.walk(tree):
        # TODO
        if isinstance(node, ast.Import):
            for alias in node.names:
                ...
        elif isinstance(node, ast.ImportFrom) and node.module in modules:
            replacing_lines = []
            for alias in node.names:
                if alias.name in modules[node.module]:
                    replacing_lines.append(
                        " " * node.col_offset + f"from {modules[node.module][alias.name]} import {alias.name}",
                    )
                else:
                    replacing_lines.append(" " * node.col_offset + f"from {node.module} import {alias.name}")
            # this trick allows us to replace without changing the number/order of lines
            lines[node.lineno - 1 : node.end_lineno] = [replacing_lines] + [[]] * (node.end_lineno - node.lineno)
    lines.insert(
        0,
        [f"from {module} import {alias}" for alias, module in missing_imports_to_add.items() if alias not in contents],
    )
    new_lines = []
    for line in lines:
        if isinstance(line, list):
            new_lines.extend(line)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def globally_replace(contents: str, replacements: Collection[tuple[str, str]] = ()):
    for old, new in replacements:
        contents = contents.replace(old, new)
    return contents


def to_modules(imports_to_change: dict[str, tuple[str, str]]) -> dict[str, dict[str, str]]:
    modules = defaultdict(dict)
    for alias, (old, new) in imports_to_change.items():
        modules[old][alias] = new
    return modules


class Compiled:
    def __init__(self, pattern: str) -> None:
        self.pattern = re.compile(pattern)


class ContentsRegex(Compiled):
    pass


class PathRegex(Compiled):
    pass


class DirRegex(Compiled):
    pass
