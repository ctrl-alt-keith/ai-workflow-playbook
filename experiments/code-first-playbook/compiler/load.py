"""A restricted profile over PyYAML's parser, never arbitrary construction."""

import re
from pathlib import Path
import yaml

from .model import Invalid, require, shape, LANGUAGE


def safe_path(root, relative):
    require(type(relative) is str and relative and not Path(relative).is_absolute(),
            "relative path required")
    path = Path(relative)
    require(".." not in path.parts, "path escape")
    current = Path(root)
    for part in path.parts:
        current /= part
        require(not current.is_symlink(), "symlink input/output rejected")
    require(current.resolve().is_relative_to(Path(root).resolve()), "path escape")
    return current


def parse(raw):
    require(len(raw) <= 262144 and not raw.startswith(b"\xef\xbb\xbf"), "input size/BOM")
    try:
        text = raw.decode("utf-8")
        require("\r" not in text and "\x00" not in text, "UTF-8 LF text required")
        require(not re.search(r"\$\{|\$\(", text), "interpolation unsupported")
        events = list(yaml.parse(text, Loader=yaml.BaseLoader))
        for event in events:
            require(not isinstance(event, yaml.AliasEvent) and not getattr(event, "anchor", None),
                    "aliases/anchors unsupported")
            require(getattr(event, "tag", None) is None, "explicit/custom tags unsupported")
        roots = list(yaml.compose_all(text, Loader=yaml.BaseLoader))
        require(len(roots) == 1 and roots[0] is not None, "one document required")

        def convert(node, depth=0):
            require(depth <= 32, "YAML depth limit")
            if isinstance(node, yaml.MappingNode):
                result = {}
                for key, value in node.value:
                    require(isinstance(key, yaml.ScalarNode), "string key required")
                    name = key.value
                    require(name not in result and name != "<<", f"duplicate/merge key: {name}")
                    require(name not in ("true", "false", "null", "~") and
                            not re.fullmatch(r"-?[0-9]+", name), "string key required")
                    result[name] = convert(value, depth + 1)
                return result
            if isinstance(node, yaml.SequenceNode):
                return [convert(n, depth + 1) for n in node.value]
            require(isinstance(node, yaml.ScalarNode), "unsupported node")
            if node.style is None and node.value in ("true", "false"):
                return node.value == "true"
            if node.style is None and re.fullmatch(r"0|[1-9][0-9]*", node.value):
                return int(node.value)
            require(node.style is not None or node.value not in
                    ("null", "~", "yes", "no", "on", "off", "True", "False"), "ambiguous scalar")
            return node.value
        return convert(roots[0])
    except (UnicodeError, yaml.YAMLError) as error:
        raise Invalid(f"YAML parse: {error}") from error


def load_modules(root, paths):
    modules, locations = {}, {}
    for path in paths:
        module = parse(safe_path(root, path).read_bytes())
        shape(module, {"language", "module", "owner", "imports", "records"})
        require(module["language"] == LANGUAGE, "unsupported language")
        name = module["module"]
        require(type(name) is str and name not in modules, "duplicate module")
        require(type(module["records"]) is list, "records must be list")
        modules[name] = module
        for record in module["records"]:
            require(type(record) is dict and type(record.get("id")) is str, "record identity")
            require(record["id"] not in locations, "duplicate ID")
            locations[record["id"]] = {"module": name, "path": path}
    return modules, locations
