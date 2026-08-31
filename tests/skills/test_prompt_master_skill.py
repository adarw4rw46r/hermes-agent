"""Tests for the prompt-master optional skill (vendored from upstream)."""
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "optional-skills" / "mlops" / "prompt-master"
SKILL_PATH = SKILL_DIR / "SKILL.md"
UPSTREAM = "https://github.com/nidhinjs/prompt-master"


def _frontmatter_and_body():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert content.startswith("---")
    m = re.search(r"\n---\s*\n", content[3:])
    assert m, "frontmatter must close with ---"
    fm = yaml.safe_load(content[3 : m.start() + 3])
    body = content[m.end() + 3 :]
    return fm, body


def test_skill_file_exists():
    assert SKILL_PATH.is_file()


def test_frontmatter_required_fields():
    fm, _ = _frontmatter_and_body()
    for field in ("name", "description", "version", "author", "license", "platforms"):
        assert field in fm, f"missing frontmatter field: {field}"
    assert fm["name"] == "prompt-master" == SKILL_DIR.name
    assert fm["license"] == "MIT"
    assert fm["platforms"] == ["linux", "macos", "windows"]
    hermes = fm["metadata"]["hermes"]
    assert hermes["tags"]
    assert "related_skills" in hermes


def test_description_hardline():
    fm, _ = _frontmatter_and_body()
    desc = fm["description"]
    assert len(desc) <= 60, f"description is {len(desc)} chars; hardline is 60"
    assert desc.endswith(".")


def test_author_credits_upstream_human_first():
    fm, _ = _frontmatter_and_body()
    assert not fm["author"].startswith("Hermes Agent")
    assert "nidhinjs" in fm["author"]


def test_related_skills_resolve_in_repo():
    fm, _ = _frontmatter_and_body()
    for name in fm["metadata"]["hermes"]["related_skills"]:
        hits = list(REPO_ROOT.glob(f"skills/*/{name}/SKILL.md")) + list(
            REPO_ROOT.glob(f"optional-skills/*/{name}/SKILL.md")
        )
        assert hits, f"related_skills entry does not resolve in-repo: {name}"


def test_vendored_license_and_attribution():
    """MIT-licensed upstream content stays attributed and license-shipped."""
    license_text = (SKILL_DIR / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in license_text
    assert "Nidhin Joseph Nelson" in license_text
    fm, body = _frontmatter_and_body()
    assert fm["metadata"]["hermes"]["upstream"] == UPSTREAM
    assert UPSTREAM in body, "body must link the upstream source"
    assert "MIT license" in body


def test_references_are_shipped_and_linked():
    _, body = _frontmatter_and_body()
    for ref in ("patterns.md", "templates.md"):
        assert (SKILL_DIR / "references" / ref).is_file()
        assert f"references/{ref}" in body


def test_no_machine_local_paths():
    _, body = _frontmatter_and_body()
    assert not re.search(r"/home/(?!runner\b)[a-z0-9_-]+/", body)


def test_size_under_limit():
    assert len(SKILL_PATH.read_text(encoding="utf-8")) <= 100_000
