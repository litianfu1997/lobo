#!/usr/bin/env python
"""粉笔网招聘数据爬取入口

用法示例：
  # 爬取国企(9)当年数据，仅打印不入库
  python scripts/crawl_fenbi.py --dry-run

  # 爬取指定地区和年份
  python scripts/crawl_fenbi.py --exam-type 9 --regions 2 3 --years 2025 2026

  # 调试：检查单个页面的原始HTML结构
  python scripts/crawl_fenbi.py --debug-url https://www.fenbi.com/page/positions-exams/9/2
"""
import argparse
import logging
import sys

sys.path.insert(0, ".")  # 允许从项目根目录直接运行

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def cmd_crawl(args):
    from app.db.session import SessionLocal, init_db
    from app.services.crawl_service import crawl_fenbi

    init_db()
    db = SessionLocal()
    try:
        stats = crawl_fenbi(
            db=db,
            exam_type=args.exam_type,
            year=args.year or None,
            dry_run=args.dry_run,
            limit=args.limit,
        )
    finally:
        db.close()

    print(
        f"\n完成: 入库/预览 {stats['scraped']} 条，"
        f"跳过 {stats['skipped']} 条，"
        f"失败 {stats['failed']} 条"
    )


def cmd_debug(args):
    """打印指定URL的原始HTML，用于分析页面结构"""
    from app.scrapers.fenbi import FenbiScraper

    with FenbiScraper(delay=0) as scraper:
        resp = scraper._get(args.debug_url)
        if resp is None:
            print("请求失败")
            return
        print(f"状态码: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type')}")
        print("─" * 60)
        print(resp.text[:5000])


def main():
    parser = argparse.ArgumentParser(description="爬取粉笔网招聘公告并分析入库")
    parser.add_argument(
        "--exam-type", type=int, default=9,
        help="考试类型 (默认: 9=国企, 12=银行)"
    )
    parser.add_argument(
        "--year", type=int,
        help="年份 (默认: 当前年)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只打印，不调用AI也不写入数据库"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="最多入库条数（默认不限制）"
    )
    parser.add_argument(
        "--debug-url",
        help="打印指定URL的原始HTML（用于调试页面结构）"
    )
    args = parser.parse_args()

    if args.debug_url:
        cmd_debug(args)
    else:
        cmd_crawl(args)


if __name__ == "__main__":
    main()
