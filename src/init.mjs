/**
 * src/init.mjs — trae-skills init <skill-name>
 *
 * 在 skill-markets/ 下创建一个新的 skill 模板
 */
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { SKILL_MARKETS_DIR } from './utils.mjs';

const TEMPLATE = (name, description) => `---
name: ${name}
version: "0.1.0"
description: "${description}"
---

# ${name}

{简短描述这个 skill 做什么。}

## When to Use

{什么场景下触发。包含触发词。}

## How It Works

1. 步骤 1
2. 步骤 2
3. 步骤 3

## Inputs

- \`arg1\` — 描述 (默认: xxx)

## Examples

\`\`\`bash
{示例调用}
\`\`\`

## Output

{预期输出示例}

## Troubleshooting

- 常见问题 1
- 常见问题 2
`;

export async function runInit(args) {
  const [name] = args;
  if (!name) {
    console.error('用法: trae-skills init <skill-name>  [description]');
    console.error('例:   trae-skills init my-cool-skill "这个 skill 做 X 用"');
    process.exit(1);
  }
  const description = args[1] || 'TODO: 在 SKILL.md 里写清这个 skill 做什么';

  const target = join(SKILL_MARKETS_DIR, name);
  if (existsSync(target)) {
    console.error(`✗ 目录已存在: ${target}`);
    process.exit(1);
  }

  mkdirSync(target, { recursive: true });
  const skillMd = join(target, 'SKILL.md');
  writeFileSync(skillMd, TEMPLATE(name, description), 'utf-8');

  // 可选子目录
  mkdirSync(join(target, 'references'), { recursive: true });
  writeFileSync(
    join(target, 'references', 'README.md'),
    `# References\n\n按需加载的详细文档放这里（避免污染 SKILL.md 主体）。\n`,
    'utf-8',
  );

  console.log(`✓ 已创建 skill 模板: ${target}`);
  console.log(`  下一步: 编辑 ${skillMd} 然后跑 'trae-skills add ${name}'`);
}
