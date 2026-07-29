"""
Delta Spec 机械合并到主 Spec — 零依赖，确定性操作。

用法:
  python spec-merge.py <delta_spec> <main_spec> [--dry-run]

退出码: 0=成功, 1=合并失败

输出 JSON:
  {"ok": true, "applied": {"added": 2, "modified": 1, "removed": 0, "renamed": 1}}
  {"ok": false, "error": "MODIFIED 未找到匹配的 Requirement: ..."}
"""

import re
import sys
import json


class SpecBlock:
    """一个 Requirement block：从 ### Requirement: 标题到下一个同级/上级标题之前。"""
    def __init__(self, title: str, body: str, start_line: int = 0):
        self.title = title
        self.body = body
        self.start_line = start_line

    @property
    def full_text(self) -> str:
        return f"### Requirement: {self.title}\n{self.body}"


class SpecMerger:
    """机械合并器，不依赖 LLM。"""

    REQ_HEADER = re.compile(r'^###\s+Requirement:\s*(.+)$')
    DELTA_SECTION = re.compile(r'^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements')
    RENAME_ENTRY = re.compile(r'^\s*-\s*FROM:\s*`(.+?)`\s*→\s*TO:\s*`(.+?)`')
    MAIN_REQUIREMENTS_HDR = re.compile(r'^##\s+Requirements')

    def __init__(self, delta_path: str, main_path: str):
        self.delta_path = delta_path
        self.main_path = main_path

    # ─── 解析 ──────────────────────────────────────────

    def _parse_requirements(self, lines: list[str], start_from: int = 0) -> list[SpecBlock]:
        """从 lines 中解析所有 ### Requirement: 块。"""
        blocks = []
        i = start_from
        while i < len(lines):
            m = self.REQ_HEADER.match(lines[i])
            if m:
                title = m.group(1).strip()
                body_lines = []
                i += 1
                while i < len(lines):
                    # 遇到下一个 Requirement 或 ## 标题 → 停止
                    if self.REQ_HEADER.match(lines[i]):
                        break
                    if lines[i].startswith('## '):
                        break
                    body_lines.append(lines[i])
                    i += 1
                blocks.append(SpecBlock(title, ''.join(body_lines), start_line=i - len(body_lines) - 1))
            else:
                i += 1
        return blocks

    def _parse_delta(self, lines: list[str]) -> dict:
        """解析 Delta Spec 为结构化操作。
        返回: {"added": [SpecBlock], "modified": [SpecBlock], "removed": [str], "renamed": [{"from":str,"to":str}]}
        """
        result = {"added": [], "modified": [], "removed": [], "renamed": []}
        current_section = None
        i = 0
        while i < len(lines):
            m = self.DELTA_SECTION.match(lines[i])
            if m:
                current_section = m.group(1).lower()
                i += 1
                continue

            if current_section in ('added', 'modified'):
                rm = self.REQ_HEADER.match(lines[i])
                if rm:
                    title = rm.group(1).strip()
                    body_lines = []
                    i += 1
                    while i < len(lines):
                        if self.REQ_HEADER.match(lines[i]) or self.DELTA_SECTION.match(lines[i]):
                            break
                        body_lines.append(lines[i])
                        i += 1
                    result[current_section].append(SpecBlock(title, ''.join(body_lines)))
                    continue

            elif current_section == 'removed':
                rm = self.REQ_HEADER.match(lines[i])
                if rm:
                    result['removed'].append(rm.group(1).strip())

            elif current_section == 'renamed':
                rm = self.RENAME_ENTRY.match(lines[i])
                if rm:
                    result['renamed'].append({"from": rm.group(1).strip(), "to": rm.group(2).strip()})

            i += 1
        return result

    # ─── 合并操作 ──────────────────────────────────────

    def _find_main_requirements_start(self, lines: list[str]) -> int:
        """找到主 spec 的 ## Requirements 位置。"""
        for i, line in enumerate(lines):
            if self.MAIN_REQUIREMENTS_HDR.match(line):
                return i
        return -1

    def merge(self) -> dict:
        """执行合并，返回结果。"""
        try:
            with open(self.main_path, 'r', encoding='utf-8') as f:
                main_lines = f.readlines()
        except FileNotFoundError:
            # 主 spec 不存在 → 视为全新 capability
            with open(self.delta_path, 'r', encoding='utf-8') as f:
                delta_lines = f.readlines()
            # 仅复制 ADDED 部分（去掉 Delta 段头）
            output = self._extract_full_spec_from_delta(delta_lines)
            with open(self.main_path, 'w', encoding='utf-8') as f:
                f.writelines(output)
            return {"ok": True, "applied": {"added": "new_file", "modified": 0, "removed": 0, "renamed": 0}}

        with open(self.delta_path, 'r', encoding='utf-8') as f:
            delta_lines = f.readlines()

        delta = self._parse_delta(delta_lines)
        main_reqs = self._parse_requirements(main_lines)

        # 收集所有 known 标题用于 RENAMED
        title_to_idx = {b.title: i for i, b in enumerate(main_reqs)}

        # 1. REMOVED — 从 main_reqs 中删除
        for title in delta['removed']:
            if title in title_to_idx:
                del main_reqs[title_to_idx[title]]
                # 重建索引
                title_to_idx = {b.title: i for i, b in enumerate(main_reqs)}
            else:
                return {"ok": False, "error": f"REMOVED 未找到匹配: '{title}'"}

        # 2. RENAMED — 更新标题
        for rn in delta['renamed']:
            if rn['from'] not in title_to_idx:
                return {"ok": False, "error": f"RENAMED 未找到: '{rn['from']}'"}
            idx = title_to_idx[rn['from']]
            main_reqs[idx].title = f"Requirement: {rn['to']}"
            title_to_idx = {b.title: i for i, b in enumerate(main_reqs)}

        # 3. MODIFIED — 替换
        for mod_block in delta['modified']:
            if mod_block.title in title_to_idx:
                idx = title_to_idx[mod_block.title]
                main_reqs[idx] = mod_block
            else:
                return {"ok": False, "error": f"MODIFIED 未找到匹配: '{mod_block.title}'"}

        # 4. ADDED — 追加
        for add_block in delta['added']:
            main_reqs.append(add_block)

        # ─── 重建主 spec ─────────────────────────────
        req_start = self._find_main_requirements_start(main_lines)
        if req_start < 0:
            return {"ok": False, "error": "主 spec 缺少 '## Requirements' 段头"}

        # 保留 header 部分（Requirements 段头之前的所有行）
        header_lines = main_lines[:req_start + 1]
        # 找到 Requirements 之后的第一个 ## 标题（如 Invariants / E2E / Acceptance）
        tail_start = req_start + 1
        while tail_start < len(main_lines):
            if main_lines[tail_start].startswith('## ') and not self.MAIN_REQUIREMENTS_HDR.match(main_lines[tail_start]):
                break
            tail_start += 1
        tail_lines = main_lines[tail_start:]

        # 组装
        output = header_lines[:]
        for block in main_reqs:
            output.append(block.full_text)
            if not block.body.endswith('\n'):
                output.append('\n')
            output.append('\n')
        output.extend(tail_lines)

        with open(self.main_path, 'w', encoding='utf-8') as f:
            f.writelines(output)

        return {"ok": True, "applied": {
            "added": len(delta['added']),
            "modified": len(delta['modified']),
            "removed": len(delta['removed']),
            "renamed": len(delta['renamed']),
        }}

    def _extract_full_spec_from_delta(self, lines: list[str]) -> list[str]:
        """主 spec 不存在时，从 delta 提取完整 Spec（跳过 Delta 标记头）。"""
        output = []
        in_skip = False
        for line in lines:
            if self.DELTA_SECTION.match(line):
                in_skip = True
                continue
            if line.startswith('## ') and not line.startswith('### '):
                if line.startswith('## ADDED') or line.startswith('## MODIFIED') or \
                   line.startswith('## REMOVED') or line.startswith('## RENAMED'):
                    in_skip = True
                    continue
                in_skip = False
            if not in_skip:
                output.append(line)
        return output


# ─── CLI ──────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Delta Spec 机械合并到主 Spec")
    parser.add_argument("delta_spec", help="Delta spec.md 路径")
    parser.add_argument("main_spec", help="主 spec.md 路径")
    parser.add_argument("--dry-run", action="store_true", help="仅检查不写入")
    args = parser.parse_args()

    merger = SpecMerger(args.delta_spec, args.main_spec)

    if args.dry_run:
        # 只看 delta 解析结果
        with open(args.delta_spec, 'r', encoding='utf-8') as f:
            delta = merger._parse_delta(f.readlines())
        print(json.dumps({"dry_run": True, "delta_summary": {
            "added": len(delta['added']),
            "modified": len(delta['modified']),
            "removed": len(delta['removed']),
            "renamed": len(delta['renamed']),
        }}, ensure_ascii=False, indent=2))
        return

    result = merger.merge()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
