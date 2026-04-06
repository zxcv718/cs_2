import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "app"
FORBIDDEN_ABBREVIATIONS = {"cfg", "ctx", "svc", "repo", "ui", "val", "msg"}


def production_files() -> list[Path]:
    return sorted(path for path in APP_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def module_name(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).with_suffix("").as_posix().replace("/", ".")


def attribute_depth(node: ast.Attribute) -> int:
    depth = 1
    current = node.value
    while isinstance(current, ast.Attribute):
        depth += 1
        current = current.value
    if isinstance(current, ast.Call):
        depth += 1
    return depth


def attribute_root(node: ast.Attribute):
    current = node
    while isinstance(current, ast.Attribute):
        current = current.value
    if isinstance(current, ast.Call) and isinstance(current.func, ast.Attribute):
        return attribute_root(current.func)
    return current


def control_depth(node: ast.FunctionDef) -> int:
    maximum_depth = 0

    def walk(current: ast.AST, depth: int) -> None:
        nonlocal maximum_depth
        if isinstance(
            current,
            (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match, ast.AsyncFor, ast.AsyncWith),
        ):
            depth += 1
            maximum_depth = max(maximum_depth, depth)
        for child in ast.iter_child_nodes(current):
            walk(child, depth)

    walk(node, 0)
    return maximum_depth


def annotations(node: ast.FunctionDef) -> list[str]:
    values: list[str] = []
    for argument in (
        list(node.args.posonlyargs)
        + list(node.args.args)
        + list(node.args.kwonlyargs)
    ):
        if argument.annotation is not None:
            values.append(ast.unparse(argument.annotation))
    variable_argument = node.args.vararg
    keyword_argument = node.args.kwarg
    if variable_argument and variable_argument.annotation is not None:
        values.append(ast.unparse(variable_argument.annotation))
    if keyword_argument and keyword_argument.annotation is not None:
        values.append(ast.unparse(keyword_argument.annotation))
    if node.returns is not None:
        values.append(ast.unparse(node.returns))
    return values


class ArchitectureRulesTestCase(unittest.TestCase):
    def test_no_else_or_elif_in_production_code(self):
        for path in production_files():
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.If) and node.orelse:
                    self.fail(f"{path} contains if/else or elif")
                if isinstance(node, ast.For) and node.orelse:
                    self.fail(f"{path} contains for/else")
                if isinstance(node, ast.While) and node.orelse:
                    self.fail(f"{path} contains while/else")
                if isinstance(node, ast.Try) and node.orelse:
                    self.fail(f"{path} contains try/else")

    def test_no_getters_setters_or_properties(self):
        for path in production_files():
            tree = ast.parse(path.read_text())
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        self.assertFalse(
                            item.name.startswith("get_"),
                            f"{path}:{item.name} uses getter naming",
                        )
                        self.assertFalse(
                            item.name.startswith("set_"),
                            f"{path}:{item.name} uses setter naming",
                        )
                        for decorator in item.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == "property":
                                self.fail(f"{path}:{item.name} uses @property")

    def test_every_class_has_at_most_two_instance_fields(self):
        for path in production_files():
            tree = ast.parse(path.read_text())
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                fields: list[str] = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        fields.append(item.target.id)
                    if not isinstance(item, ast.FunctionDef):
                        continue
                    for subnode in ast.walk(item):
                        if not isinstance(subnode, (ast.Assign, ast.AnnAssign)):
                            continue
                        targets = subnode.targets if isinstance(subnode, ast.Assign) else [subnode.target]
                        for target in targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                                if target.value.id == "self" and target.attr not in fields:
                                    fields.append(target.attr)
                self.assertLessEqual(
                    len(fields),
                    2,
                    f"{path}:{node.name} has more than two instance fields: {fields}",
                )

    def test_model_and_repository_layer_dependencies_stay_clean(self):
        for path in production_files():
            tree = ast.parse(path.read_text())
            imports = []
            for node in tree.body:
                if isinstance(node, ast.ImportFrom) and node.module is not None:
                    imports.append(node.module)
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)

            if "model" in path.parts:
                forbidden_prefixes = (
                    "app.console",
                    "app.repository",
                    "app.presentation",
                    "app.application",
                )
                for imported in imports:
                    self.assertFalse(
                        imported.startswith(forbidden_prefixes),
                        f"{path} imports forbidden dependency {imported}",
                    )

            if "repository" in path.parts:
                for imported in imports:
                    self.assertFalse(
                        imported.startswith("app.console"),
                        f"{path} imports forbidden dependency {imported}",
                    )

    def test_application_layer_avoids_direct_io_and_json(self):
        for path in production_files():
            if "application" not in path.parts:
                continue
            tree = ast.parse(path.read_text())
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotEqual(alias.name, "json", f"{path} imports json")
                if isinstance(node, ast.ImportFrom) and node.module == "json":
                    self.fail(f"{path} imports json")
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotEqual(node.func.id, "input", f"{path} calls input() directly")
                    self.assertNotEqual(node.func.id, "print", f"{path} calls print() directly")

    def test_boundary_methods_avoid_raw_dict_and_list_annotations(self):
        targets = {"application", "model", "presentation", "repository", "console"}
        for path in production_files():
            if not set(path.parts).intersection(targets):
                continue
            tree = ast.parse(path.read_text())
            for node in tree.body:
                items = node.body if isinstance(node, ast.ClassDef) else [node]
                for item in items:
                    if not isinstance(item, ast.FunctionDef):
                        continue
                    for annotation in annotations(item):
                        self.assertNotIn("list[", annotation, f"{path}:{item.name} exposes raw list annotation")
                        self.assertNotIn("dict[", annotation, f"{path}:{item.name} exposes raw dict annotation")
                        self.assertNotIn("Any", annotation, f"{path}:{item.name} exposes Any annotation")

    def test_methods_use_single_level_of_indentation(self):
        for path in production_files():
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                self.assertLessEqual(
                    control_depth(node),
                    1,
                    f"{path}:{node.name} uses nested control flow deeper than one level",
                )

    def test_identifiers_avoid_short_abbreviations(self):
        for path in production_files():
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    self.assertNotIn(
                        node.id,
                        FORBIDDEN_ABBREVIATIONS,
                        f"{path}:{node.lineno} uses abbreviated identifier {node.id}",
                    )
                if isinstance(node, ast.arg):
                    self.assertNotIn(
                        node.arg,
                        FORBIDDEN_ABBREVIATIONS,
                        f"{path}:{node.lineno} uses abbreviated identifier {node.arg}",
                    )

    def test_runtime_code_avoids_train_wreck_calls(self):
        for path in production_files():
            if "config" in path.parts:
                continue
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if not isinstance(node, ast.Attribute):
                    continue
                if attribute_depth(node) <= 1:
                    continue
                root = attribute_root(node)
                if isinstance(root, ast.Name) and root.id == "self":
                    continue
                if isinstance(root, ast.Call) and isinstance(root.func, ast.Name):
                    if root.func.id == "super":
                        continue
                self.fail(f"{path} contains chained attribute access")


if __name__ == "__main__":
    unittest.main()
