# 示例：监听新增 Skill（配合外部调度）

skills-security-scan 的 `main.py` 专注单次扫描。  
监听模式建议由平台调度器或 CI 定时触发，例如每 5 分钟执行一次：

```bash
python main.py d:\trea\skills\skills
```
