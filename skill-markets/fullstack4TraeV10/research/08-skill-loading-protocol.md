---
title: §0.5 Skill 加载协议 + §0.10 启动验证可见产物 Mindmap
description: V10.9 NEW 防首次产物偏离 + V10.10 NEW 启动验证硬约束 + 同类约定 10 项清单
layer: fact
---

# §0.5 Skill 加载协议 + §0.10 启动验证可见产物 Mindmap

> V10.9 NEW — 防首次产物偏离项目惯例（4 轮返工蒸馏）。
> V10.10 NEW — 防虚假交付（[1] 后端类 vs [2] UI 渲染类边界）。
> V10.12 NEW — 同类约定 10 项强制清单 + 启动验证可见产物硬约束。

## 一、§0.5 加载协议 5 步流程

```mermaid
flowchart TD
    Trigger[主上下文收到<br/>Use Skill name 指令]
    S1[Step 1<br/>调 Skill 工具加载 SKILL.md]
    S2[Step 2<br/>必读 references 关键子文档]
    S3[Step 3<br/>Glob 1 次项目同类约定]
    S4[Step 4<br/>如有冲突 → 询问用户]
    S5[Step 5<br/>才进入工作模式]

    Trigger --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5

    S3 -.->|10 项清单<br/>全激活| S3a[强制声明格式<br/>列 10 项激活情况]
    S4 -.->|不冲突| S4a[默认按 skill 推进]

    S5 --> Phase[Phase 0 Plan → Spec → Contract → Implement → Review]

    classDef step fill:#95e1d3,color:#000
    classDef trigger fill:#ffd93d,color:#000
    class Trigger trigger
    class S1,S2,S3,S4,S5,S3a,S4a,Phase step
```

## 二、§0.5.1 同类约定 10 项强制清单

```mermaid
mindmap
  root((§0.5.1 同类约定<br/>10 项强制清单))
    1 截屏
      目录: .trae/skills/screenshot/
      触发: screenshot / 截图 / 视觉证据
    2 视觉验证
      目录: visual-evidence-discipline/
      触发: UI 验收 / 像素验证 / 通过依据
    3 浏览器自动化
      目录: browser-use-cloud/
      触发: browser-use / 网页抓取 / 表单填写
    4 UI 测试
      目录: playwright-best-practices/
      触发: Playwright / E2E / page object
    5 E2E 框架
      目录: e2e-module-audit/
      触发: e2e / 端到端回归 / 视觉审计
    6 录屏
      目录: screenshot/ §录屏模式
      触发: 录屏 / 操作回放 / 失败重演
    7 a11y
      目录: ui-ux-pro-max/
      触发: 可访问性 / WCAG / a11y
    8 性能
      目录: ui-ux-pro-max/
      触发: 性能 / 帧率 / FCP / Web Vitals
    9 契约对齐
      目录: frontend-backend-contract-alignment/
      触发: 前后端契约 / SSE / datetime 格式
    10 时间/时区
      目录: 含 datetime / tz 的 skill
      触发: datetime / 时区 / IANA / 时间戳
```

## 三、§0.5.1 强制声明格式

```mermaid
graph LR
    Format[主上下文回复<br/>必须含]

    Format --> Item1[1 截屏: ✅/⚠️/N/A — 理由]
    Format --> Item2[2 视觉验证: ✅/⚠️/N/A — 理由]
    Format --> Item3[3 浏览器自动化: ✅/⚠️/N/A — 理由]
    Format --> Dot[...]
    Format --> Item10[10 时间/时区: ✅/⚠️/N/A — 理由]

    Item1 --> Compliance{全 10 项列?}
    Item2 --> Compliance
    Item3 --> Compliance
    Dot --> Compliance
    Item10 --> Compliance

    Compliance -->|是| Pass[✅ 达标]
    Compliance -->|否| Ban[�� FAIL<br/>漏 Glob = �� FAIL]

    classDef must fill:#4ecdc4,color:#fff
    classDef fail fill:#ff6b6b,color:#fff
    class Format,Item1,Item2,Item3,Dot,Item10,Pass must
    class Ban fail
```

## 四、§0.10 启动验证可见产物 (5 类项目)

```mermaid
mindmap
  root((§0.10 启动验证<br/>可见产物硬约束))
    1 Web 项目
      curl localhost port 200
      Playwright 截图 ≥ 1 张 ≥ 5KB
      强约束 file:line 路径
    2 Tauri 应用
      tauri dev 进程存活
      主窗口 screenshot ≥ 1 张
      evidence_summary
    3 CLI / 脚本
      end-to-end 命令 实际跑 1 次
      输出片段 ≥ 10 行
      不可看到进程即通过
    4 Library / API
      集成测试 真实调用
      返回 200 / 正确字段
      不可 mock
    5 后端服务
      健康检查端点 200
      日志无 ERROR
      完整命令日志
    边界
      实施者层 Phase 3.5
      启动是否跑通
      与 §通过依据 [2] 区分
      Review 层 用户可见 UI
```

## 五、§0.10 5 项必做 机械门禁

```mermaid
flowchart LR
    Step1[1 环境依赖检查]
    Step2[2 真实验证执行]
    Step3[3 启动验证可见产物]
    Step4[4 阻塞处理]
    Step5[5 必查项 主上下文]

    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5

    Step1 --> S1a[数据库容器 Up]
    Step1 --> S1b[缓存容器 Up]
    Step1 --> S1c[.env 存在]
    Step1 --> S1d[端口可达]

    Step2 --> S2a[迁移成功]
    Step2 --> S2b[全量测试 PASS]
    Step2 --> S2c[tsc 0 错误]
    Step2 --> S2d[dev server 可启动]

    Step3 --> S3a[Web curl 200 + 截图]
    Step3 --> S3b[Tauri dev 存活 + 截图]
    Step3 --> S3c[CLI 输出 ≥ 10 行]
    Step3 --> S3d[API 整合测试 200]
    Step3 --> S3e[后端 health 200]

    Step4 --> S4a[5 字段阻塞报告]
    Step4 --> S4b[禁止跳过]
    Step4 --> S4c[禁止声称完成]

    Step5 --> S5a[完整命令日志]
    Step5 --> S5b[不是 PASS/FAIL 字符串]
    Step5 --> S5c[不得隐藏]

    classDef step fill:#95e1d3,color:#000
    classDef ban fill:#ff6b6b,color:#fff
    class Step1,Step2,Step3,Step4,Step5,S1a,S1b,S1c,S1d,S2a,S2b,S2c,S2d,S3a,S3b,S3c,S3d,S3e,S5a,S5b,S5c step
    class S4a,S4b,S4c ban
```

## 六、§0.5 与 §0.10 边界澄清

```mermaid
graph TB
    subgraph Phase_3_5[Phase 3.5 实施者层]
        P35[§0.10 启动验证<br/>实施者交付]
        P35_1[启动是否真实跑通]
        P35_2[环境 + 迁移 + 测试 + 启动]
        P35_3[主上下文启动动作]
    end

    subgraph Phase_4[Phase 4 Review 层]
        P4[§通过依据 [2]<br/>Review 验收]
        P4_1[用户可见 UI 真渲染]
        P4_2[vision-audit 像素]
        P4_3[3 类分层后端/UI/用户]
    end

    P35 --> P35_1
    P35 --> P35_2
    P35 --> P35_3

    P4 --> P4_1
    P4 --> P4_2
    P4 --> P4_3

    P35 -.->|不同层| P4
    P4 -.->|不同层| P35

    classDef phase35 fill:#95e1d3,color:#000
    classDef phase4 fill:#ffd93d,color:#000
    class P35,P35_1,P35_2,P35_3 phase35
    class P4,P4_1,P4_2,P4_3 phase4
```

## 七、关键引用

- §0.5 Skill 加载协议: [SKILL.md §0.5](../SKILL.md)
- §0.5.1 同类约定 10 项: [SKILL.md §0.5.1](../SKILL.md)
- §0.10 启动