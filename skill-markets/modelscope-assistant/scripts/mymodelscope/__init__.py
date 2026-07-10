# mymodelscope — 本地模型管理工具
#
# 模块:
#   config      - .mymodelscope.env 配置加载
#   db          - SQLite 数据库管理
#   scanner     - 本地仓库扫描器
#   query       - 模型查询引擎
#   dedup       - 重复文件检测
#   metadata    - 元数据解析（SHA256/URL/文件识别）
#   downloader  - 模型下载（HF/CivitAI/ModelScope）
#   known       - 种子数据导入
#   kb          - 知识库管理
#   registry/   - 外部平台 API 客户端
"""
MyModelScope — 本地 AI 模型资产管理系统。

对标魔搭社区的本地模型管理体验，提供：
- 扫描索引入库
- 多维度查询
- 跨平台元数据识别（HF/CivitAI/ModelScope）
- 模型下载
- 去重检测
- 知识库文档
"""
