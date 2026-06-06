"""粉笔网招聘公告爬虫

四层导航结构：
1. 省份索引  /page/positions-exams/{exam_type}
2. 公告列表  /page/positions-exams/{exam_type}?region={region_id}&year={year}
3. 公告概览  /page/positions-exams/{exam_type}/{announcement_id}
4. 岗位表    /page/positions/{exam_type}/{announcement_id}?region={sub_region_id}

注意：岗位详情 /page/position-detail/{id} 需登录，故不采集。

说明：粉笔网对国企(exam_type=9)不跟踪报名状态（API 返回 totalSignUp=-1），
因此只能按年份过滤——仅爬取当前年份数据，视为有效公告。
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Generator

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://www.fenbi.com"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 岗位表中需要提取的字段（忽略纯序号/代码类列）
_SKIP_FIELDS = {"职位代码", "报考人数", "职位详情", "序号", "备注"}


@dataclass
class PositionEntry:
    """单条岗位记录的结构化数据"""
    raw_text: str               # 拼接好的文本，可直接送入 analyze()
    department: str | None      # 部门名称
    position_name: str | None   # 职位名称
    headcount: str | None       # 招考人数
    major: str | None           # 专业要求
    education: str | None       # 学历要求
    work_address: str | None    # 工作地点
    age: str | None             # 年龄要求
    experience: str | None      # 经验要求
    other: str | None           # 其他要求


@dataclass
class ParsedAnnouncement:
    source_url: str       # 岗位表 URL（/page/positions/...）
    org_name: str | None  # 公告标题或机构名
    # 每个 entry 是一段可直接送入 analyze() 的文本。
    # 一行职位 → 一个 entry；一页可能有多行。
    entries: list[str] = field(default_factory=list)
    # 结构化岗位数据
    positions: list[PositionEntry] = field(default_factory=list)


def _extract_embedded_json(html: str) -> dict | None:
    """从页面 HTML 的 <script> 标签中提取内嵌的 JSON API 数据。

    粉笔网 SPA 会在 HTML 中预加载 API 响应，格式为：
    {"clientContextId":"...","G.URL":{body:{...},...},...}
    其中 URL 的 / ? & = 等字符被转义为 /a; &a; =a; 等。
    """
    for script in BeautifulSoup(html, "lxml").find_all("script"):
        text = script.string or ""
        if not text or "clientContextId" not in text:
            continue
        try:
            # 还原粉笔的特殊转义: &q; -> "
            decoded = text.replace("&q;", '"')
            data = json.loads(decoded)
            return data
        except (json.JSONDecodeError, ValueError):
            continue
    return None


class FenbiScraper:
    def __init__(self, delay: float = 1.5):
        self._client = httpx.Client(
            headers=_HEADERS, timeout=15, follow_redirects=True
        )
        self.delay = delay

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ─── 内部工具 ─────────────────────────────────────────────────────────

    def _get(self, url: str) -> httpx.Response | None:
        try:
            resp = self._client.get(url)
            resp.encoding = "utf-8"
            resp.raise_for_status()
            return resp
        except httpx.HTTPError:
            return None
        finally:
            time.sleep(self.delay)

    def _soup(self, resp: httpx.Response) -> BeautifulSoup:
        return BeautifulSoup(resp.text, "lxml")

    # ─── Level 1：提取所有省份/地区 URL ─────────────────────────────────

    def iter_region_urls(
        self, exam_type: int = 9, year: int | None = None
    ) -> Generator[tuple[int, str], None, None]:
        """从首页提取所有省份的区域 ID 和 URL。

        优先从内嵌 JSON 提取（更可靠），回退到 HTML 解析。
        Yields: (district_id, region_url)
        """
        import datetime
        if year is None:
            year = datetime.date.today().year

        resp = self._get(f"{BASE_URL}/page/positions-exams/{exam_type}")
        if resp is None:
            return

        # 尝试从内嵌 JSON 提取
        embedded = _extract_embedded_json(resp.text)
        if embedded:
            found = False
            for key, val in embedded.items():
                if "catalogByCondition" not in key:
                    continue
                body = val.get("body", {})
                data = body.get("data", {})
                catalog = data.get("catalogByDistrict", {})
                for dist in catalog.get("districtExams", []):
                    did = dist.get("districtId")
                    if did:
                        url = (
                            f"{BASE_URL}/page/positions-exams/{exam_type}"
                            f"?region={did}&year={year}"
                        )
                        yield did, url
                found = True
                break
            if found:
                return  # 成功从 JSON 提取，不再走 HTML

        # 回退：从 HTML 解析
        soup = self._soup(resp)
        seen: set[str] = set()
        pattern = re.compile(
            rf"/page/positions-exams/{exam_type}\?region=(\d+)&year=\d+"
        )
        for a in soup.find_all("a", href=True):
            href: str = a["href"]
            m = pattern.match(href)
            if m:
                region_id = m.group(1)
                url = (
                    f"{BASE_URL}/page/positions-exams/{exam_type}"
                    f"?region={region_id}&year={year}"
                )
                if url not in seen:
                    seen.add(url)
                    yield int(region_id), url

    # ─── Level 2：从地区页提取公告列表 ──────────────────────────────────

    def fetch_announcement_links(
        self, region_url: str, exam_type: int = 9
    ) -> list[dict]:
        """从地区列表页提取各公告链接，返回 [{"url": ..., "title": ...}]

        优先从内嵌 JSON 提取。
        """
        resp = self._get(region_url)
        if resp is None:
            return []

        # 尝试从内嵌 JSON 提取
        embedded = _extract_embedded_json(resp.text)
        if embedded:
            for key, val in embedded.items():
                if "queryExams" not in key:
                    continue
                body = val.get("body", {})
                data = body.get("data", {})
                table = data.get("table", {})
                items = table.get("items", [])
                if not items:
                    continue
                results = []
                for item in items:
                    exam_id = item.get("examId")
                    name = item.get("name", "")
                    if exam_id:
                        results.append({
                            "url": f"{BASE_URL}/page/positions-exams/{exam_type}/{exam_id}",
                            "title": name,
                        })
                return results

        # 回退：从 HTML 解析
        soup = self._soup(resp)
        pattern = re.compile(rf"/page/positions-exams/{exam_type}/(\d+)$")
        seen: set[str] = set()
        results = []

        for a in soup.find_all("a", href=True):
            href: str = a["href"]
            if pattern.match(href):
                url = BASE_URL + href
                if url not in seen:
                    seen.add(url)
                    results.append({"url": url, "title": a.get_text(strip=True)})

        return results

    # ─── Level 3：从公告概览页提取岗位子页链接 ───────────────────────────

    def fetch_positions_sub_urls(
        self, announcement_url: str, exam_type: int = 9
    ) -> list[str]:
        """从公告概览页提取所有 /page/positions/{exam_type}/{id}?... 子页URL"""
        resp = self._get(announcement_url)
        if resp is None:
            return []

        ann_id = announcement_url.rstrip("/").split("/")[-1]
        soup = self._soup(resp)
        pattern = re.compile(rf"/page/positions/{exam_type}/{ann_id}\?")
        seen: set[str] = set()
        results = []

        for a in soup.find_all("a", href=True):
            href: str = a["href"]
            if pattern.match(href):
                url = BASE_URL + href
                if url not in seen:
                    seen.add(url)
                    results.append(url)

        return results

    # ─── Level 4：解析岗位表 ─────────────────────────────────────────────

    def parse_positions_table(
        self, positions_url: str, announcement_title: str
    ) -> ParsedAnnouncement | None:
        """解析 /page/positions/{exam_type}/{id}?... 页面的岗位数据

        优先从内嵌 JSON（listByAddress API 响应）提取结构化数据，
        回退到 HTML 表格解析。
        每个表格行生成一个文本 entry 送入分析流水线。
        """
        resp = self._get(positions_url)
        if resp is None:
            return None

        # 尝试从内嵌 JSON 提取 API 数据
        embedded = _extract_embedded_json(resp.text)
        if embedded:
            for key, val in embedded.items():
                if "listByAddress" not in key and "listByDepartment" not in key:
                    continue
                body = val.get("body", {})
                data = body.get("data", {})
                api_positions = data.get("positions", [])
                if not api_positions:
                    continue

                entries = []
                positions = []
                for p in api_positions:
                    lines = [f"招聘公告：{announcement_title}"]
                    dept = p.get("department") or None
                    pos_name = p.get("positionName") or None
                    hc = p.get("employCountDesc") or None
                    major = p.get("major") or None
                    degree = p.get("majorDegree") or None
                    address = p.get("workAddress") or None
                    age = p.get("birthday") or None

                    if dept:
                        lines.append(f"部门名称：{dept}")
                    if pos_name:
                        lines.append(f"职位名称：{pos_name}")
                    if hc:
                        lines.append(f"招考人数：{hc}")
                    if major:
                        lines.append(f"专业：{major}")
                    if degree:
                        lines.append(f"学历：{degree}")
                    if address:
                        lines.append(f"工作地点：{address}")
                    if age:
                        lines.append(f"年龄：{age}")

                    if len(lines) > 1:
                        entry_text = "\n".join(lines)
                        entries.append(entry_text)
                        positions.append(PositionEntry(
                            raw_text=entry_text,
                            department=dept,
                            position_name=pos_name,
                            headcount=hc,
                            major=major,
                            education=degree,
                            work_address=address,
                            age=age,
                            experience=None,
                            other=None,
                        ))

                if entries:
                    org_name = self._extract_org_name(announcement_title)
                    return ParsedAnnouncement(
                        source_url=positions_url,
                        org_name=org_name,
                        entries=entries,
                        positions=positions,
                    )

        # 回退：HTML 表格解析
        soup = self._soup(resp)
        table = soup.find("table")
        if table is None:
            return None

        rows = table.find_all("tr")
        if len(rows) < 2:
            return None

        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        entries = []

        for row in rows[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if not cells or all(not c for c in cells):
                continue

            lines = [f"招聘公告：{announcement_title}"]
            for header, value in zip(headers, cells):
                if header in _SKIP_FIELDS:
                    continue
                if value and value.strip() and value != "详情":
                    lines.append(f"{header}：{value}")

            if len(lines) > 1:  # 至少有一个有效字段
                entries.append("\n".join(lines))

        if not entries:
            return None

        org_name = self._extract_org_name(announcement_title)
        return ParsedAnnouncement(
            source_url=positions_url,
            org_name=org_name,
            entries=entries,
        )

    @staticmethod
    def _extract_org_name(title: str) -> str | None:
        """从公告标题中提取机构名（年份之前的部分）"""
        for year_str in ("2026", "2025", "2024"):
            if year_str in title:
                return title.split(year_str)[0].strip() or None
        return title.strip() or None
