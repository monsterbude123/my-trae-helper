# voice-acting-skill

> **中文配音剧本自动化注音技能包** — Trae IDE 技能包
> 
> 将 Markdown 格式的中文配音剧本自动解析、分配方言音色、切分 15 秒批次、生成 QwenTTS / CosyVoice / OmniVoice 三引擎注音规则，并可执行配音合成。

## 目录

```
voice-acting-skill/
├── SKILL.md                            # ⭐ 编排器主入口
├── pyproject.toml                      # 依赖: click, httpx, pydantic
├── skills/                             # 5 个子技能
│   ├── script-parser/SKILL.md
│   ├── voice-assigner/SKILL.md
│   ├── batch-manager/SKILL.md
│   ├── annotation-generator/SKILL.md
│   └── tts-synthesizer/SKILL.md
├── scripts/                            # Python 实现
│   ├── vaslib/                         # 核心库
│   │   ├── parser/script_parser.py
│   │   ├── analyzer/voice_assigner.py
│   │   ├── batcher/batch_manager.py
│   │   ├── annotator/annotation_generator.py
│   │   ├── annotator/markdown_formatter.py
│   │   ├── synthesizer/{cosyvoice,omnivoice,project_generator}.py
│   │   ├── config/voices.py            # 方言映射 + 81 词多音字词典
│   │   └── types/                      # pydantic 数据模型
│   ├── vascli/main.py                  # click CLI: vas analyze, vas synthesize
│   └── tests/test_core.py              # 35 个 pytest 测试用例
├── references/                         # 深度资料
│   ├── ARCHITECTURE.md                 # 架构图 + 数据流
│   ├── CONSTRAINTS.md                  # 业务铁律
│   ├── DECISIONS.md                    # ADR 决策记录
│   ├── modules/                        # 4 个模块细节
│   ├── chats/                          # 历史对话
│   └── superpowers/                    # 实施计划
├── assets/
│   ├── examples/                       # 剧本样例
│   └── configs/                        # 配置导出
├── agents/                             # 预留：角色 / 音色调优代理
└── workflows/                          # 端到端工作流
```

## 快速开始

```bash
# 安装
pip install -e .

# 一键试运行（基于样例剧本）
vas analyze assets/examples/demo-script.md -o output

# 查看生成的注音报告
cat output/annotated/all-engines.md

# 启动 TTS 服务后合成
vas synthesize -o output
```

## 35 个测试全通过

```bash
python -m pytest scripts/tests/ -v
# 35 passed in 0.21s
```

## 规范约束

- 严格遵守父项目 `d:\workspace\my-trae-helper\AGENTS.md` 的元项目规则
- 不在 skill-markets/ 之外创建/修改技能
- 不暴露 key / 敏感信息
- 模块拆分禁止单文件（保持每模块独立文件）
- ponytail 思维：能用代码解决的事不上 LLM

## 依赖

```
click >= 8.0
httpx >= 0.27
pydantic >= 2.0
Python >= 3.11
```

## 安装到 Trae IDE 全局技能目录

```powershell
Copy-Item -Recurse "d:\workspace\my-trae-helper\skill-markets\Voice-Acting-Script-Skill" "$env:USERPROFILE\.trae-cn\builtin_skills\voice-acting-skill"
```

安装后重启 IDE 即可在对话中触发技能加载。
