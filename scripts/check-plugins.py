#!/usr/bin/env python3
"""Structural checks for every plugin in this marketplace.

Complements `claude plugin validate` with the conventions in CLAUDE.md that
the validator does not know about. Exits 1 and lists every problem found.

Checks:
- marketplace.json lists exactly the plugin directories, with no entry versions;
  an entry kept in another repo needs a github source and is checked there
- skill, command, and agent frontmatter parses and has the required keys
- no command shares a name with a skill in the same plugin (the command wins)
- agents never grant AskUserQuestion and never pin model: fable
- `plugin:name` references in prose resolve to a real agent, skill, or command
- `${CLAUDE_PLUGIN_ROOT}/...` references resolve to files in the plugin
- hook commands quote ${CLAUDE_PLUGIN_ROOT}
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
AGENT_MODELS = {"inherit", "sonnet", "haiku", "opus"}
PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")


@dataclass
class Plugin:
    name: str
    path: Path
    skills: dict[str, Path] = field(default_factory=dict)
    commands: dict[str, Path] = field(default_factory=dict)
    agents: dict[str, Path] = field(default_factory=dict)

    @property
    def entry_names(self) -> set[str]:
        return set(self.skills) | set(self.commands) | set(self.agents)


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else None


def tool_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(t).strip() for t in value]
    if isinstance(value, str):
        return [t.strip() for t in value.split(",")]
    return []


def load_plugins(errors: list[str]) -> list[Plugin]:
    catalog = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    listed = {}
    for entry in catalog["plugins"]:
        if "version" in entry:
            errors.append(f"marketplace.json: {entry['name']} has a version; it belongs only in plugin.json")
        source = entry["source"]
        if isinstance(source, dict):  # a plugin kept in its own repo; its components are checked there
            if source.get("source") != "github" or not source.get("repo"):
                errors.append(f"marketplace.json: {entry['name']} external source needs source 'github' and a repo")
            continue
        listed[entry["name"]] = (ROOT / source).resolve()
    on_disk = {p.parent.parent.resolve() for p in ROOT.glob("*/.claude-plugin/plugin.json")}
    for missing in on_disk - set(listed.values()):
        errors.append(f"{missing.name}/ has a plugin.json but no marketplace.json entry")

    plugins = []
    for name, path in listed.items():
        manifest = path / ".claude-plugin/plugin.json"
        if not manifest.exists():
            errors.append(f"marketplace.json: {name} source {path} has no plugin.json")
            continue
        declared = json.loads(manifest.read_text())["name"]
        if declared != name:
            errors.append(f"{path.name}/plugin.json name {declared!r} != catalog name {name!r}")
        plugin = Plugin(name, path)
        plugin.skills = {d.name: d / "SKILL.md" for d in sorted((path / "skills").glob("*/")) if (d / "SKILL.md").exists()}
        plugin.commands = {f.stem: f for f in sorted((path / "commands").glob("*.md"))}
        plugin.agents = {f.stem: f for f in sorted((path / "agents").glob("*.md"))}
        plugins.append(plugin)
    return plugins


def check_components(plugin: Plugin, errors: list[str]) -> None:
    rel = lambda p: p.relative_to(ROOT)  # noqa: E731
    for name, path in plugin.skills.items():
        fm = frontmatter(path)
        if not fm or not fm.get("description"):
            errors.append(f"{rel(path)}: missing frontmatter description")
        elif fm.get("name", name) != name:
            errors.append(f"{rel(path)}: name {fm['name']!r} != directory {name!r}")
    for name, path in plugin.commands.items():
        fm = frontmatter(path)
        if not fm or not fm.get("description"):
            errors.append(f"{rel(path)}: missing frontmatter description")
    for clash in sorted(set(plugin.commands) & set(plugin.skills)):
        errors.append(
            f"{plugin.name}: commands/{clash}.md shadows skills/{clash}/ (the command wins; delete one)"
        )
    for name, path in plugin.agents.items():
        fm = frontmatter(path)
        if not fm:
            errors.append(f"{rel(path)}: missing frontmatter")
            continue
        for key in ("name", "description", "tools", "model"):
            if not fm.get(key):
                errors.append(f"{rel(path)}: missing {key}")
        if fm.get("name") and fm["name"] != name:
            errors.append(f"{rel(path)}: name {fm['name']!r} != filename {name!r}")
        if "AskUserQuestion" in tool_list(fm.get("tools")):
            errors.append(f"{rel(path)}: grants AskUserQuestion, which subagents never receive")
        if fm.get("model") and fm["model"] not in AGENT_MODELS:
            errors.append(f"{rel(path)}: model {fm['model']!r} not in {sorted(AGENT_MODELS)} (use inherit, not a fable pin)")


def runtime_files(plugin: Plugin) -> list[Path]:
    files = [*plugin.skills.values(), *plugin.commands.values(), *plugin.agents.values()]
    files += sorted((plugin.path / "skills").glob("*/references/**/*.md"))
    files += [p for p in (plugin.path / "hooks/hooks.json", plugin.path / ".mcp.json") if p.exists()]
    return files


def check_references(plugin: Plugin, by_name: dict[str, Plugin], errors: list[str]) -> None:
    qualified = re.compile(r"(?<![\w@/.-])(" + "|".join(map(re.escape, by_name)) + r"):([a-z0-9][a-z0-9-]*)\b")
    for path in runtime_files(plugin):
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT)
        for ref in sorted(set(PLUGIN_ROOT_REF.findall(text))):
            target = plugin.path / ref.rstrip(".")
            if not target.exists():
                errors.append(f"{where}: ${{CLAUDE_PLUGIN_ROOT}}/{ref} does not exist")
        for owner, entry in sorted(set(qualified.findall(text))):
            if entry not in by_name[owner].entry_names:
                errors.append(f"{where}: {owner}:{entry} is not an agent, skill, or command of {owner}")


def check_hooks(plugin: Plugin, errors: list[str]) -> None:
    hooks_file = plugin.path / "hooks/hooks.json"
    if not hooks_file.exists():
        return
    def commands(node):
        if isinstance(node, dict):
            if node.get("type") == "command" and "command" in node:
                yield node["command"]
            for value in node.values():
                yield from commands(value)
        elif isinstance(node, list):
            for value in node:
                yield from commands(value)
    for cmd in commands(json.loads(hooks_file.read_text())):
        if "${CLAUDE_PLUGIN_ROOT}" in cmd and '"${CLAUDE_PLUGIN_ROOT}' not in cmd:
            errors.append(f"{hooks_file.relative_to(ROOT)}: quote ${{CLAUDE_PLUGIN_ROOT}} in {cmd!r}")


def main() -> int:
    errors: list[str] = []
    plugins = load_plugins(errors)
    by_name = {p.name: p for p in plugins}
    for plugin in plugins:
        check_components(plugin, errors)
        check_references(plugin, by_name, errors)
        check_hooks(plugin, errors)
    for e in errors:
        print(f"FAIL {e}")
    print(f"{len(plugins)} plugins checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
