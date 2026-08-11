# 反例 1：把 project-health 当必走流程

**违反**: 铁律 1 异步非阻塞

**现象**: project-health 阻塞主流程。

**正确替代**: project-health 是异步支线，可与任一 stage 并行；不阻塞主流程。