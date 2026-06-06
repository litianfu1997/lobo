"""粉笔网批量爬取协调服务"""
from __future__ import annotations

import datetime
import hashlib
import logging

from sqlalchemy.orm import Session

from app.analysis.engine import analyze as default_analyze
from app.db.models import Announcement
from app.scrapers.fenbi import FenbiScraper
from app.services.analysis_service import analyze_and_store

logger = logging.getLogger(__name__)


def crawl_fenbi(
    db: Session,
    exam_type: int = 9,
    year: int | None = None,
    dry_run: bool = False,
    analyze_fn=default_analyze,
    limit: int | None = None,
) -> dict:
    """
    爬取粉笔网招聘公告并分析入库。

    导航路径（四层）：
      首页(省份) → 地区公告列表 → 公告概览(子区域) → 岗位表(每行一职位)

    - 每行职位生成一条独立分析记录
    - 通过 source_url + content_hash 去重，避免重复入库
    - 默认仅爬取当前年份数据（粉笔网对国企不跟踪报名状态，以年份过滤）

    返回 {"scraped": int, "skipped": int, "failed": int}
    """
    if year is None:
        year = datetime.date.today().year

    stats = {"scraped": 0, "skipped": 0, "failed": 0}

    with FenbiScraper() as scraper:
        # Level 1: 遍历所有省份/地区
        region_items = list(scraper.iter_region_urls(exam_type=exam_type, year=year))
        logger.info("发现 %d 个地区", len(region_items))

        for region_id, region_url in region_items:
            logger.info("处理地区: %s", region_url)

            # Level 2: 获取该地区的公告列表
            ann_links = scraper.fetch_announcement_links(region_url, exam_type=exam_type)
            logger.info("  发现 %d 条公告", len(ann_links))

            for ann_link in ann_links:
                ann_url = ann_link["url"]
                ann_title = ann_link["title"]
                try:
                    # Level 3: 从公告概览页获取岗位子页URL
                    sub_urls = scraper.fetch_positions_sub_urls(ann_url, exam_type=exam_type)
                    if not sub_urls:
                        logger.debug("无岗位子页: %s", ann_url)
                        stats["failed"] += 1
                        continue

                    for positions_url in sub_urls:
                        try:
                            # Level 4: 解析岗位表，每行一个entry
                            parsed = scraper.parse_positions_table(positions_url, ann_title)
                            if not parsed or not parsed.entries:
                                stats["failed"] += 1
                                continue

                            for entry_text in parsed.entries:
                                content_hash = hashlib.sha256(
                                    entry_text.encode("utf-8")
                                ).hexdigest()

                                # 去重
                                already = (
                                    db.query(Announcement)
                                    .filter(
                                        (Announcement.source_url == positions_url)
                                        & (Announcement.content_hash == content_hash)
                                    )
                                    .first()
                                )
                                if already:
                                    stats["skipped"] += 1
                                    continue

                                if dry_run:
                                    preview = entry_text[:100].replace("\n", " / ")
                                    logger.info("[DRY-RUN] %s", preview)
                                    stats["scraped"] += 1
                                    continue

                                analyze_and_store(
                                    text=entry_text,
                                    db=db,
                                    analyze_fn=analyze_fn,
                                    source_type="crawl",
                                    source_url=positions_url,
                                )
                                stats["scraped"] += 1

                                if limit and stats["scraped"] >= limit:
                                    logger.info("已达到限制 %d 条，停止爬取", limit)
                                    return stats

                        except Exception as exc:
                            logger.warning("处理岗位页失败 %s: %s", positions_url, exc)
                            stats["failed"] += 1

                except Exception as exc:
                    logger.warning("处理公告失败 %s: %s", ann_url, exc)
                    stats["failed"] += 1

    return stats
