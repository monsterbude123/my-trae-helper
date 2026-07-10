# my-trae-helper

Trae IDE 技能包开发工程。管理、开发和分发 AI 代理技能包（Skills）。

## 技能市场

```
skill-markets/
├── ponytail4Trae/          # 懒人开发模式
├── fullstack4TraeV4/       # 全栈文档驱动开发
├── gitnexus4Trae/          # 代码知识图谱
├── acceptance-discipline/  # 验收测试体系
├── goal-mode/              # 目标追逐协议
├── product-teardown/       # 产品拆解分析
├── shuxia-novel-engine/    # 小说创作引擎
└── trae-professional/      # Trae IDE 专业知识库
```

## 安装

```powershell
Copy-Item -Recurse "d:\workspace\my-trae-helper\{pkg}\skills\{name}" "$env:USERPROFILE\.trae-cn\builtin_skills\{name}"
```

安装后需重启 IDE。

## 许可

MIT
