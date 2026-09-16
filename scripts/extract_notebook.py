import ast
import json
from pathlib import Path

NOTEBOOK_PATH = Path("python_programming_exercises.ipynb")
OUTPUT_PATH = Path("student_solution.py")
TARGET_FUNCTIONS = {
    "full", "get", "set", "equal", "copy",
    "transpose", "flatten", "reshape", "compute", "mean"
}


def is_import_or_class(node: ast.AST) -> bool:
    return isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef))


def collect_code_from_notebook(notebook_path: Path) -> str:
    nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    selected_chunks = []

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        keep = False
        for node in tree.body:
            if is_import_or_class(node):
                keep = True
                break
            if isinstance(node, ast.FunctionDef) and node.name in TARGET_FUNCTIONS:
                keep = True
                break
        if keep:
            selected_chunks.append(source.rstrip() + "\n")

    return "\n".join(selected_chunks)


def main() -> None:
    if not NOTEBOOK_PATH.exists():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK_PATH}")
    code = collect_code_from_notebook(NOTEBOOK_PATH)
    if not code.strip():
        raise RuntimeError("No import/class/function code was extracted from the notebook.")
    OUTPUT_PATH.write_text(code, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
