# 双层配置体系

> 来源: 原 SKILL.md §9
> 加载时机: 需要调整脚本配置时

所有脚本采用统一的配置加载链: `.env > _config.json > 内置默认值`

---

## 设计原则

- **零依赖**: .env 解析自实现（不依赖 python-dotenv）
- **渐进覆盖**: 缺任何一层都能跑，只覆盖需要改的字段
- **BOM 安全**: utf-8-sig 兼容，自动 strip BOM
- **相对路径**: 配置中的路径相对于项目根目录解析

---

## 命名约定

```
{script}.env.example        ← 环境变量覆盖模板，复制为 {script}.env 生效
{script}_config.example.json ← 结构化配置模板，复制为 {script}_config.json 生效
```

复制后修改。`.example` 文件提交版本控制，`.env`/`_config.json` 加入 .gitignore。

---

## 配置加载链

```python
# 1. 内置默认值 (代码中定义)
_defaults = {"pass_threshold": 85, "conditional_threshold": 60}

# 2. JSON 配置覆盖
_config = _load_json_config("check_config.json")  # 静默回退

# 3. 环境变量覆盖
_env = _load_dotenv("check.env")  # 自实现，零依赖

# 4. 统一访问器
def _cfg(key, default):
    return _env.get(key) or _config.get(key) or _defaults.get(key, default)
```

---

## .env 格式

```ini
# 注释行以 # 开头
# 空行忽略
# BOM (UTF-8 BOM) 自动 strip
KEY=VALUE
KEY2=VALUE2
```

- 键名大写 + 下划线
- 值不含引号
- 布尔值: 0/1
- 路径: 相对于项目根目录

---

## .json 格式

```json
{
  "_schema": "说明文本",
  "_note": "下划线开头的键为元数据，不会被加载为配置",
  "actual_key": "value"
}
```

- 下划线前缀 `_` = 元数据字段，被 _cfg() 忽略
- 删除字段 = 回退到下一层默认值
- 嵌套对象 = 维持原结构

---

## 给 AI Agent 的提醒

1. **改配置不改脚本**: 阈值/权重/关键词 → 改 .env 或 .json，不改 .py
2. **先复制再改**: 永远不改 `.example` 文件，复制后改副本
3. **验证缺省可用**: `python script.py` 必须不依赖任何配置文件就能跑
4. **路径相对项目根**: 配置文件中的路径相对于项目根目录
5. **.env 优先于 .json**: 环境变量覆盖 JSON，JSON 覆盖默认值
