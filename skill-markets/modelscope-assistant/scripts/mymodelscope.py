#!/usr/bin/env python3
"""
MyModelScope CLI — 本地模型管理命令行入口。

用法:
    python scripts/mymodelscope.py <command> [options]

命令:
    init            初始化配置（创建 .env 和数据库）
    scan            扫描本地仓库，增量索引入库
    query           查询本地模型
    stats           仓库统计信息
    dedup           重复文件检测
    identify        识别模型身份（--file / --url / --sha256）
    download        下载模型到本地仓库
    search-online   跨平台搜索模型
    import-known    导入 known-models.yaml 种子数据
    kb              知识库管理（add / list / get / search）

示例:
    mymodelscope scan
    mymodelscope query --type checkpoint --task text-to-image
    mymodelscope identify --file "D:\\models\\unknown.safetensors"
    mymodelscope identify --url "https://huggingface.co/stabilityai/sd-xl-base-1.0"
    mymodelscope search-online "人像写真"
    mymodelscope download --url "https://huggingface.co/black-forest-labs/FLUX.1-dev"
    mymodelscope kb add --model "Fun-CosyVoice3" --type deployment_guide --title "部署指南" --content "..."

环境:
    配置文件 .mymodelscope.env（仓库根目录或 %USERPROFILE%）
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# 将 scripts/ 目录加入 path，以便 import mymodelscope
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mymodelscope.config import load_config
from mymodelscope.db import Database
from mymodelscope.scanner import scan
from mymodelscope.query import query as query_models, stats as get_stats
from mymodelscope.dedup import find_duplicates
from mymodelscope.metadata import identify_by_file, identify_by_url, identify_by_sha256, search_online
from mymodelscope.downloader import download_from_url, download_from_source
from mymodelscope.known import import_known
from mymodelscope.kb import (
    ensure_table as ensure_kb, add_entry, query_by_model, get_entry,
    search as search_kb, list_models as list_kb_models,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("mymodelscope")


def _get_db(config):
    """获取数据库连接"""
    if not config.db_path:
        print("错误：未配置数据库路径（检查 .mymodelscope.env 中的 MYMODELSCOPE_DB_PATH）", file=sys.stderr)
        sys.exit(1)
    db = Database(config.db_path)
    db.connect()
    db.init_schema()
    ensure_kb(db)  # 确保知识库表存在
    return db


def cmd_init(args):
    """初始化配置"""
    config = load_config()
    print("MyModelScope 配置：")
    print(f"  仓库路径:       {config.repo_path or '(未设置)'}")
    print(f"  冷库路径:       {config.cold_storage or '(未设置)'}")
    print(f"  数据库路径:     {config.db_path or '(未设置)'}")
    print(f"  扫描排除:       {', '.join(config.scan_exclude)}")
    print()

    if not config.repo_path:
        print("请在 .mymodelscope.env 中设置 MYMODELSCOPE_REPO_PATH")
        return

    db = _get_db(config)
    print(f"✓ 数据库已初始化: {config.db_path}")
    db.close()


def cmd_scan(args):
    config = load_config()
    if not config.repo_path:
        print("错误：未设置 MYMODELSCOPE_REPO_PATH", file=sys.stderr)
        sys.exit(1)
    db = _get_db(config)
    found, new, updated, deleted, errors = scan(db, config.repo_path, config.scan_exclude)
    print(f"扫描完成：发现 {found} 个模型，新增 {new}，更新 {updated}，删除 {deleted}")
    if errors:
        print(f"错误: {'; '.join(errors[:5])}")
    db.close()


def cmd_query(args):
    config = load_config()
    db = _get_db(config)
    results = query_models(
        db,
        task=args.task or "",
        model_type=args.type or "",
        family=args.family or "",
        capability=args.capability or "",
        keyword=args.keyword or "",
        limit=args.limit or 20,
    )
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("未找到匹配的模型")
        for m in results:
            quality_str = f"★{m['avg_quality']}" if m["avg_quality"] else "—"
            print(f"[{m['type']:12s}] {m['name']:30s} {m['file_size_gb']:6.1f}GB  {quality_str:6s}  {m.get('family', '')}")
            if m.get("recommendations"):
                print(f"  推荐用途: {', '.join(m['recommendations'][:3])}")
            if m.get("capabilities"):
                print(f"  能力: {', '.join(m['capabilities'][:5])}")
    db.close()


def cmd_stats(args):
    config = load_config()
    db = _get_db(config)
    s = get_stats(db)
    if args.format == "json":
        print(json.dumps(s, ensure_ascii=False, indent=2))
    else:
        print(f"模型总数: {s['total_models']}")
        print(f"总大小:   {s['total_size_gb']:.1f} GB")
        print()
        print("按类型:")
        for t, info in s.get("by_type", {}).items():
            print(f"  {t:20s} {info['count']:4d} 个  {info['size_gb']:8.1f} GB")
        if s.get("last_scan"):
            print(f"\n最后扫描: {s['last_scan']}")
    db.close()


def cmd_dedup(args):
    config = load_config()
    db = _get_db(config)
    dups = find_duplicates(db, config.repo_path)
    if args.format == "json":
        print(json.dumps(dups, ensure_ascii=False, indent=2))
    else:
        if not dups:
            print("未发现重复模型")
        total_wasted = 0
        for g in dups:
            total_wasted += g["wasted_gb"]
            print(f"\nSHA256: {g['sha256'][:16]}...  浪费: {g['wasted_gb']:.1f} GB")
            for m in g["models"]:
                print(f"  {m['file_path']}  ({m['size_gb']:.1f} GB)")
        if total_wasted:
            print(f"\n总计可回收: {total_wasted:.1f} GB")
    db.close()


def cmd_identify(args):
    config = load_config()
    db = None
    if not args.no_db:
        db = _get_db(config)

    result = None
    if args.file:
        result = identify_by_file(args.file, db)
    elif args.url:
        result = identify_by_url(args.url)
    elif args.sha256:
        result = identify_by_sha256(args.sha256, db)
    else:
        print("请指定 --file / --url / --sha256", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if db:
        db.close()


def cmd_search_online(args):
    results = search_online(args.keyword, limit=args.limit or 5)
    print(json.dumps(results, ensure_ascii=False, indent=2))


def cmd_download(args):
    config = load_config()
    if not config.repo_path:
        print("错误：未设置 MYMODELSCOPE_REPO_PATH", file=sys.stderr)
        sys.exit(1)

    result = None
    if args.url:
        result = download_from_url(args.url, config.repo_path)
    elif args.source and args.model_id:
        result = download_from_source(args.source, args.model_id, config.repo_path, args.type or "")
    else:
        print("请指定 --url 或 (--source + --model-id)", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2) if result else "下载失败")


def cmd_import_known(args):
    config = load_config()
    db = _get_db(config)
    yaml_path = args.yaml or str(Path(__file__).parent / "skill-markets" / "modelscope-assistant" / "references" / "known-models.yaml")
    # 如果默认路径不存在，尝试相对路径
    if not Path(yaml_path).exists():
        yaml_path = str(Path(__file__).parent.parent / "references" / "known-models.yaml")
    if not Path(yaml_path).exists():
        print(f"找不到 known-models.yaml: {yaml_path}", file=sys.stderr)
        print("请用 --yaml 指定路径", file=sys.stderr)
        sys.exit(1)

    result = import_known(db, yaml_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    db.close()


def cmd_kb(args):
    config = load_config()
    db = _get_db(config)

    if args.kb_action == "add":
        if not args.kb_model or not args.kb_title:
            print("错误: kb add 需要 --model 和 --title", file=sys.stderr)
            sys.exit(1)
        # 从 stdin 或 --content 读取内容
        content = args.kb_content or sys.stdin.read()
        eid = add_entry(
            db,
            model_name=args.kb_model,
            content_type=args.kb_type or "model_info",
            title=args.kb_title,
            content=content.strip(),
            source_url=args.kb_url or "",
            tags=args.kb_tags.split(",") if args.kb_tags else [],
        )
        print(f"知识库条目已添加: id={eid}")

    elif args.kb_action == "get":
        if args.kb_model:
            entries = query_by_model(db, args.kb_model)
            for e in entries:
                print(f"\n## {e['title']} [{e['content_type']}]")
                print(f"来源: {e['source_url']}")
                print(e['content'])
                print(f"---")
        elif args.kb_id:
            e = get_entry(db, int(args.kb_id))
            if e:
                print(f"\n## {e['title']} [{e['content_type']}]")
                print(f"模型: {e['model_name']}  来源: {e['source_url']}")
                print()
                print(e['content'])

    elif args.kb_action == "list":
        models = list_kb_models(db)
        if models:
            print("知识库中的模型:")
            for m in models:
                entries = query_by_model(db, m)
                types = set(e["content_type"] for e in entries)
                print(f"  {m} ({len(entries)} 条目, 类型: {', '.join(sorted(types))})")
        else:
            print("知识库为空")

    elif args.kb_action == "search":
        results = search_kb(db, args.kb_keyword or "", limit=20)
        for e in results:
            print(f"[{e['content_type']}] {e['model_name']} — {e['title']}")
            print(f"  {e['content'][:100]}...")
            print()

    db.close()


def main():
    parser = argparse.ArgumentParser(description="MyModelScope — 本地 AI 模型管理工具")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # init
    sub.add_parser("init", help="初始化配置")

    # scan
    sub.add_parser("scan", help="扫描本地仓库")

    # query
    p = sub.add_parser("query", help="查询本地模型")
    p.add_argument("--type", help="模型类型")
    p.add_argument("--task", help="任务类型")
    p.add_argument("--family", help="模型家族")
    p.add_argument("--capability", help="能力筛选")
    p.add_argument("--keyword", help="关键词搜索")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--format", choices=["json", "table"], default="table")

    # stats
    p = sub.add_parser("stats", help="仓库统计")
    p.add_argument("--format", choices=["json", "table"], default="table")

    # dedup
    p = sub.add_parser("dedup", help="重复检测")
    p.add_argument("--format", choices=["json", "table"], default="table")

    # identify
    p = sub.add_parser("identify", help="识别模型身份")
    p.add_argument("--file", help="本地文件路径")
    p.add_argument("--url", help="模型 URL")
    p.add_argument("--sha256", help="SHA256 哈希")
    p.add_argument("--no-db", action="store_true", help="不查询本地数据库")

    # search-online
    p = sub.add_parser("search-online", help="跨平台在线搜索")
    p.add_argument("keyword", help="搜索关键词")
    p.add_argument("--limit", type=int, default=5)

    # download
    p = sub.add_parser("download", help="下载模型")
    p.add_argument("--url", help="模型下载 URL")
    p.add_argument("--source", choices=["huggingface", "civitai", "modelscope"], help="下载来源")
    p.add_argument("--model-id", help="模型平台 ID")
    p.add_argument("--type", help="模型类型（用于确定保存目录）")

    # import-known
    p = sub.add_parser("import-known", help="导入精品模型种子数据")
    p.add_argument("--yaml", help="known-models.yaml 路径")

    # kb
    p = sub.add_parser("kb", help="知识库管理")
    p.add_argument("action", metavar="ACTION", choices=["add", "get", "list", "search"],
                   help="操作: add/get/list/search")
    p.add_argument("--model", dest="kb_model", help="模型名称")
    p.add_argument("--type", dest="kb_type", help="内容类型")
    p.add_argument("--title", dest="kb_title", help="标题")
    p.add_argument("--content", dest="kb_content", help="内容（或从 stdin 读取）")
    p.add_argument("--url", dest="kb_url", help="来源 URL")
    p.add_argument("--tags", dest="kb_tags", help="标签（逗号分隔）")
    p.add_argument("--id", dest="kb_id", help="条目 ID")
    p.add_argument("--keyword", dest="kb_keyword", help="搜索关键词")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "init": cmd_init,
        "scan": cmd_scan,
        "query": cmd_query,
        "stats": cmd_stats,
        "dedup": cmd_dedup,
        "identify": cmd_identify,
        "search-online": cmd_search_online,
        "download": cmd_download,
        "import-known": cmd_import_known,
        "kb": cmd_kb,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
