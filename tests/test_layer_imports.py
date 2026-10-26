"""Guard the inward dependency rule of the clean architecture."""

import ast
from pathlib import Path

_SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src" / "sql_guide"

_FORBIDDEN_ROOTS: dict[str, set[str]] = {
    "domain": {
        "fastapi",
        "sqlalchemy",
        "pydantic_settings",
        "crewai",
        "uvicorn",
        "sql_guide.application",
        "sql_guide.infrastructure",
        "sql_guide.presentation",
    },
    "application": {
        "fastapi",
        "sqlalchemy",
        "pydantic_settings",
        "crewai",
        "uvicorn",
        "sql_guide.infrastructure",
        "sql_guide.presentation",
    },
}


def _is_absolute_import(node: ast.ImportFrom) -> bool:
    """Return whether an import-from names a top-level module."""
    return node.module is not None and node.level == 0


def _imported_modules(path: Path) -> set[str]:
    """Collect absolute module names imported by a Python file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and _is_absolute_import(node):
            assert node.module is not None
            modules.add(node.module)
    return modules


def _matches(module: str, banned: str) -> bool:
    """Return whether a module is exactly or nested under a banned root."""
    return module == banned or module.startswith(f"{banned}.")


def _is_forbidden(module: str, forbidden: set[str]) -> bool:
    """Return whether a module belongs to a banned dependency."""
    return any(_matches(module, banned) for banned in forbidden)


def test_inner_layers_do_not_import_outer_frameworks() -> None:
    """Domain and application stay free of frameworks and outer layers."""
    violations: list[str] = []
    for layer, forbidden in _FORBIDDEN_ROOTS.items():
        for path in (_SOURCE_ROOT / layer).rglob("*.py"):
            relative = path.relative_to(_SOURCE_ROOT)
            for module in _imported_modules(path):
                if _is_forbidden(module, forbidden):
                    violations.append(f"{relative} imports {module}")

    assert violations == []
