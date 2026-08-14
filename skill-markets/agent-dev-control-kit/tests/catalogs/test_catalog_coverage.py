"""tests/catalogs/test_catalog_coverage.py — Catalog 覆盖率守门测试

直接对应你描述的三个场景:
  - 缺管理的模块文档   → TestRequiredDocs 阻断
  - 缺 page 元素       → TestRequiredSections 阻断
  - 缺 schema 字段     → TestRequiredSchemaFields 阻断

每个 fail 都通过 emit_hint() 给出"缺什么 / 在哪补 / 调用哪个 Skill"。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests._helpers.agent_hint import emit_hint, hint_assert
from tests.catalogs._loader import (
    CATALOG_REQUIRED_DOCS_MIN,
    CATALOG_REQUIRED_SECTIONS_MIN,
    SKILL_ROOT,
    dotted_path_exists,
    load_catalog,
    load_yaml,
)

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def catalog():
    """共享 catalog 配置(整 module 一次加载)。"""
    return load_catalog()


@pytest.fixture(scope="module")
def registry_guards(catalog):
    p = SKILL_ROOT / "registry" / "guards.yaml"
    return load_yaml(p).get("guards", []) if p.is_file() else []


# ============================================================================
# TestRequiredDocs — 缺文档阻断
# ============================================================================
class TestRequiredDocs:
    @pytest.mark.trap
    def test_all_required_docs_exist(self, catalog):
        missing = []
        for doc in catalog["required_docs"]:
            p = SKILL_ROOT / doc["path"]
            if not p.is_file():
                missing.append(doc["path"])
        if missing:
            emit_hint(
                trap_id="AP-CAT-001",
                what=f"catalog 声明 {len(missing)} 个文档不存在",
                where="tests/catalogs/skill-catalog.yaml:required_docs",
                minimal_fix=[
                    f"创建 {p}" for p in missing
                ] + [
                    "或在 skill-catalog.yaml 中移除过期声明",
                ],
                next_skill="trae-ponytail",
                next_skill_action="起草缺失文档骨架",
                see_also=["references/traps.md §AP-CAT-DOCS"],
            )
        assert not missing, (
            f"🛑 catalog 缺文档: {missing}\n"
            f"🛠 agent 应当:在 skill-markets/agent-dev-control-kit/ 对应路径补齐缺失文档"
        )

    @pytest.mark.trap
    def test_required_docs_have_required_content(self, catalog):
        """缺章节锚点的文档 → agent 必须补内容(对应 'page 元素'。"""
        bad: list[tuple[str, str]] = []
        for doc in catalog["required_docs"]:
            p = SKILL_ROOT / doc["path"]
            if not p.is_file():
                continue
            content = p.read_text(encoding="utf-8")
            # must_contain: 字符串片段
            for needle in doc.get("must_contain", []) or []:
                if needle not in content:
                    bad.append((doc["path"], f"must_contain: {needle!r}"))
            # must_contain_regex: 正则
            rx = doc.get("must_contain_regex")
            if rx and not re.search(rx, content, re.MULTILINE):
                bad.append((doc["path"], f"must_contain_regex: {rx!r}"))
            # min_lines
            mn = doc.get("min_lines")
            if mn and len(content.splitlines()) < mn:
                bad.append((
                    doc["path"],
                    f"min_lines: <{mn} (实际 {len(content.splitlines())})>",
                ))
        if bad:
            emit_hint(
                trap_id="AP-CAT-002",
                what=f"{len(bad)} 个文档缺内容",
                where="tests/catalogs/skill-catalog.yaml:required_docs[*]",
                minimal_fix=[
                    f"{where} 应当补: {what}"
                    for where, what in bad[:5]
                ] + (
                    [f"...还有 {len(bad) - 5} 处缺失"] if len(bad) > 5 else []
                ),
                next_skill="trae-ponytail",
                see_also=["references/traps.md §AP-CAT-CONTENT"],
            )
        assert not bad, (
            f"🛑 缺内容:{bad[:10]}\n🛠 agent 应当按 catalog 逐项补"
        )

    def test_catalog_has_min_docs(self, catalog):
        """catalog 自身不能空(防御 yaml 退化)。"""
        docs = catalog.get("required_docs", []) or []
        assert len(docs) >= CATALOG_REQUIRED_DOCS_MIN, (
            f"catalog.required_docs 应 ≥ {CATALOG_REQUIRED_DOCS_MIN},"
            f"实际 {len(docs)}"
        )


# ============================================================================
# TestRequiredScripts — 缺脚本 / 缺 CLI 自执行入口(AP-3)
# ============================================================================
class TestRequiredScripts:
    @pytest.mark.trap
    def test_all_required_scripts_exist(self, catalog):
        missing = [
            s["path"] for s in catalog["required_scripts"]
            if not (SKILL_ROOT / s["path"]).is_file()
        ]
        if missing:
            emit_hint(
                trap_id="AP-CAT-003",
                what=f"catalog 声明 {len(missing)} 个脚本不存在",
                minimal_fix=[
                    f"创建 {p}" for p in missing
                ] + [
                    "请确认 path 与 SKILL 根的相对关系",
                ],
                next_skill="trae-ponytail",
            )
        assert not missing, f"🛑 缺脚本:{missing}"

    @pytest.mark.trap
    def test_required_scripts_have_cli_entry(self, catalog):
        """AP-3 反例:任一 CLI 脚本缺 main → 必须阻断。"""
        bad: list[str] = []
        for s in catalog["required_scripts"]:
            if not (s.get("is_cli") and s.get("must_have_main")):
                continue
            p = SKILL_ROOT / s["path"]
            if not p.is_file():
                continue
            content = p.read_text(encoding="utf-8")
            if "__main__" not in content:
                bad.append(s["path"])
        if bad:
            emit_hint(
                trap_id="AP-3",
                what=f"{len(bad)} 个 CLI 脚本缺 `if __name__ == '__main__'` 入口",
                where=", ".join(bad),
                minimal_fix=[
                    f"在 {p} 末尾加: `if __name__ == '__main__': sys.exit(main())`"
                    for p in bad
                ],
                next_skill="trae-ponytail",
                see_also=["references/traps.md §AP-3"],
            )
        assert not bad, (
            f"🛑 {bad} 缺 CLI 自执行入口\n"
            f"🛠 详见 references/traps.md §AP-3"
        )


# ============================================================================
# TestRequiredSections — 缺章节锚点(page 元素)
# ============================================================================
class TestRequiredSections:
    @pytest.mark.trap
    def test_all_required_sections_present(self, catalog):
        """缺章节 → agent 必补文档锚点(直接对应 '缺 page 元素')。"""
        bad: list[tuple[str, str, str]] = []
        for sec in catalog.get("required_sections", []) or []:
            p = SKILL_ROOT / sec["in_file"]
            if not p.is_file():
                bad.append((sec["in_file"], sec.get("heading_match", ""), "<file missing>"))
                continue
            content = p.read_text(encoding="utf-8")
            heading = sec.get("heading", "")
            # heading 是字面标题(不含 # 前缀),level 决定生成 ## / ### 等
            # 用 re.escape 防 heading 里含 regex 特殊字符
            pattern = rf"^{'#' * sec['level']}\s+{re.escape(heading)}\b"
            if not re.search(pattern, content, re.MULTILINE):
                bad.append((sec["in_file"], heading, "<not found>"))
        if bad:
            emit_hint(
                trap_id="AP-CAT-004",
                what=f"{len(bad)} 个章节锚点缺失(缺 page 元素)",
                where="tests/catalogs/skill-catalog.yaml:required_sections",
                minimal_fix=[
                    f"在 {f} 加 `{sec.strip()} <标题>` 章节(至少 50 字)"
                    for f, sec, _ in bad[:8]
                ],
                next_skill="web-app-development",
                next_skill_action="用 prose 模板生成对应章节",
                see_also=["references/traps.md §AP-CAT-SECTIONS"],
            )
        assert not bad, (
            f"🛑 缺章节:{bad[:10]}\n🛠 按 skill-catalog.yaml:required_sections 补齐"
        )

    def test_catalog_has_min_sections(self, catalog):
        secs = catalog.get("required_sections", []) or []
        assert len(secs) >= CATALOG_REQUIRED_SECTIONS_MIN, (
            f"catalog.required_sections 应 ≥ {CATALOG_REQUIRED_SECTIONS_MIN},"
            f"实际 {len(secs)}"
        )


# ============================================================================
# TestRequiredSchemaFields — 缺 schema 字段或交叉引用(AP-7)
# ============================================================================
class TestRequiredSchemaFields:
    @pytest.mark.trap
    def test_all_required_schema_fields_exist(self, catalog):
        bad: list[tuple[str, str, str]] = []
        for fs in catalog.get("required_schema_fields", []) or []:
            p = SKILL_ROOT / fs["in_file"]
            if not p.is_file():
                bad.append((fs["in_file"], fs.get("path", ""), "<file missing>"))
                continue
            try:
                data = load_yaml(p)
            except Exception as e:
                bad.append((fs["in_file"], fs.get("path", ""), f"yaml error: {e}"))
                continue
            dotted = fs.get("path", "")
            if dotted and not dotted_path_exists(data, dotted):
                bad.append((fs["in_file"], dotted, "<not found>"))
        if bad:
            emit_hint(
                trap_id="AP-CAT-005",
                what=f"{len(bad)} 个 schema 路径缺失(新增功能没补 schema)",
                where="tests/catalogs/skill-catalog.yaml:required_schema_fields",
                minimal_fix=[
                    f"在 {f} 添加 dotted path `{p}` 对应字段"
                    for f, p, _ in bad[:6]
                ],
                next_skill="trae-ponytail",
                see_also=["references/traps.md §AP-CAT-SCHEMA"],
            )
        assert not bad, f"🛑 缺 schema:{bad[:10]}"

    @pytest.mark.trap
    def test_cross_references_resolve(self, catalog, registry_guards):
        """AP-7 防御:gate 引用 guard id 必须存在于 registry。"""
        bad: list[tuple[str, str]] = []
        known = {g["id"] for g in registry_guards}
        gates_yaml = load_yaml(SKILL_ROOT / "registry" / "gates.yaml")
        for g in gates_yaml.get("gates", []) or []:
            for gid in g.get("guards", []) or []:
                if gid not in known:
                    bad.append((g["id"], gid))
        if bad:
            emit_hint(
                trap_id="AP-7",
                what=f"gate 引用未在 guards.yaml 注册的 guard id:{bad}",
                where="registry/gates.yaml",
                minimal_fix=[
                    f"选项 A:在 guards.yaml 加 {gid!r}" for _, gid in bad[:3]
                ] + [
                    f"选项 B:从 gates.yaml 删除 {gid!r} 引用" for _, gid in bad[:3]
                ],
                next_skill="trae-ponytail",
                see_also=["references/traps.md §AP-7"],
            )
        assert not bad, f"🛑 交叉引用断:{bad}"


# ============================================================================
# TestCatalogLoader — catalog loader 自身健壮性
# ============================================================================
class TestCatalogLoader:
    def test_dotted_path_wildcard_resolves_to_existing_field(self):
        data = {"stacks": [{"id": "x", "name": "X"}, {"id": "y", "name": "Y"}]}
        assert dotted_path_exists(data, "stacks[*].id") is True
        assert dotted_path_exists(data, "stacks[*].scaffold") is False

    def test_dotted_path_nested_wildcard(self):
        data = {"top": [{"items": [{"k": 1}, {"k": 2}]}, {"items": [{"k": 3}]}]}
        assert dotted_path_exists(data, "top[*].items[*].k") is True

    def test_dotted_path_returns_false_on_nonexistent(self):
        data = {"a": 1}
        assert dotted_path_exists(data, "a.b.c") is False

    def test_load_yaml_raises_on_missing_file(self, tmp_path: Path):
        from tests.catalogs._loader import load_yaml as _load
        with pytest.raises(FileNotFoundError):
            _load(tmp_path / "nope.yaml")


# ============================================================================
# TestAgentHintIntegration — 自验收:emit_hint 写入 + 防退化
# ============================================================================
class TestAgentHintIntegration:
    def test_emit_hint_writes_to_log(self, tmp_path: Path, monkeypatch):
        """emit_hint 写入 logs/agent-hints.jsonl(供聚合脚本消费)。"""
        from tests._helpers import agent_hint

        # 重定向 hint 日志到 tmp,避免污染真实日志
        fake_log = tmp_path / "hints.jsonl"
        monkeypatch.setattr(agent_hint, "HINT_LOG_PATH", fake_log)
        monkeypatch.setattr(agent_hint, "_is_hints_disabled", lambda: False)

        # 重新调用(_is_hints_disabled 已 monkeypatch,需要从模块导入函数)
        h = agent_hint.emit_hint(
            trap_id="AP-DEMO",
            what="demo hint",
            minimal_fix=["xx"],
        )
        assert h["trap_id"] == "AP-DEMO"
        assert fake_log.is_file()
        lines = fake_log.read_text(encoding="utf-8").strip().splitlines()
        assert any("AP-DEMO" in line for line in lines)

    def test_hint_assert_decorator_emits_on_failure(self):
        """@hint_assert 装饰的失败 → emit hint 并把 hint_id 嵌入 msg。"""
        @hint_assert(
            trap_id="AP-DEMO-2",
            what="demo failure",
            minimal_fix=["修复"],
        )
        def _should_fail():
            assert False, "raw reason"

        with pytest.raises(AssertionError) as ei:
            _should_fail()
        msg = str(ei.value)
        assert "HINT-AP-DEMO-2-" in msg
        assert "demo failure" in msg
