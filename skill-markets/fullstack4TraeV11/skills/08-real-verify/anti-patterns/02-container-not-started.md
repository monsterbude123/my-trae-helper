# 反例 2：容器未启声称迁移成功

**违反**: V10 Article XV 障碍诚实

**现象**: postgres 容器未启 → 迁移脚本报 success（实际跳过）→ 主上下文声称 PASS。

**正确替代**: Real Verify 必先 `docker compose ps postgres | grep Up` → 容器运行后才迁移。
