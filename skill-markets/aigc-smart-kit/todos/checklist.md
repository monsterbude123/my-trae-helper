# AIGC-smart-kit 验收清单(acceptance-discipline §7 子集)

## §A 主入口 SKILL.md

- [x] frontmatter 含 `name: aigc-smart-kit`
- [x] frontmatter `description` 含触发关键词: I2V / 图生视频 / H3 / Seedance / Hailuo / 上传图片
- [x] 行数 ≤350(vibe-coding-standards v2.5 阈值)
- [x] 路由表清晰:3 子 skill(analyzer + h3 + seedance)
- [x] §2 加载协议明确 3 类触发(图 / 纯文字 / 指定平台)
- [x] §5.1 改造钩子模板固化
- [x] 不写具体子 skill 内容(职责分离,只指针)
- [x] 子 skill 之间不互相重复主入口

## §B i2v-image-analyzer/SKILL.md

- [x] frontmatter `name: i2v-image-analyzer`
- [x] description 含: 上传图片 / 分析画面 / 主体识别 / 影视级 prompt
- [x] 行数 ≤350
- [x] §1 5 步流程清晰
- [x] §2 vision 调用协议明确(prompt 模板 + 模型选型)
- [x] §3 用户关键词合并协议(优先级)
- [x] §4 image-report.json 输出 schema 引用 references
- [x] §5 默认路由 H3 + 改造钩子
- [x] §6 反例 6 条

## §C i2v-h3-prompt/SKILL.md

- [x] frontmatter `name: i2v-h3-prompt`
- [x] description 含: H3 / Hailuo / 图生视频 / 提示词 三段式 / 自然语言运镜
- [x] 行数 ≤350
- [x] H3 公式:description + soundscape + music
- [x] 运镜三件套:类型 + 振幅 + 速度
- [x] 标"不接管 Hailuo 02 方括号运镜(已废)"

## §D i2v-seedance-prompt/SKILL.md

- [x] frontmatter `name: i2v-seedance-prompt`
- [x] description 含: Seedance 2.0 / 2.5 / 30s / 四拍 / @Image @Audio 标签
- [x] 行数 ≤350
- [x] 四拍公式:Opening + Progression + Turn + Resolution
- [x] 参考素材预算表(30 图 + 10 视频 + 10 音频)
- [x] @Image / @Video / @Audio / @Clay Render 标签语法

## §E 反例(必避免)

- [x] ❌ 主入口长篇展开子 skill 公式(职责重叠)— 已避
- [x] ❌ 子 skill SKILL.md 超 350 行未拆分 references/ — 已避
- [x] ❌ 子 skill 之间复制粘贴同一公式(双源漂移)— 已避
- [x] ❌ description 缺触发词导致不激活 — 已含
- [x] ❌ 硬编码 API Key / 私钥 / 内部 URL — 已避
- [x] ❌ references/*.md 链接写绝对路径或跨 skill 任意路径 — 已避
- [x] ❌ 用户给图却跳过 analyzer 直接给公式 — 已固化 §2 场景 A
- [x] ❌ 输出 prompt 后忘给改造钩子 — 已固化 §5.1

## §F 端到端流水线自检(端到端任务场景)

- [ ] 场景 A 跑通(给图 + 关键词 → prompt + 改造钩子)— 待实跑 case
- [ ] 场景 B 跑通(纯文字 → H3 T2V)— 待实跑 case
- [ ] 场景 C 跑通(指定平台 → Seedance prompt)— 待实跑 case
- [ ] analyzer → h3 跨子 skill JSON 数据流通畅 — 待实跑 case
- [ ] analyzer → seedance 跨平台切换 — 待实跑 case