# -*- coding: utf-8 -*-
from dataclasses import dataclass

CATEGORIES = {"A", "B", "C", "D"}


@dataclass(frozen=True)
class Feature:
    key: str
    category: str
    name: str
    description: str
    judge_hint: str


FEATURES: list[Feature] = [
    Feature("major_too_narrow", "A", "专业限定过窄",
            "要求极冷门或高度细分的专业，甚至具体到某研究方向",
            "看专业是否窄到只对应极少数毕业生"),
    Feature("rare_edu_combo", "A", "院校学历罕见叠加",
            "特定层次院校 + 特定学历 + 特定专业等多重叠加",
            "看学历/院校/专业的组合是否罕见到指向极少人"),
    Feature("precise_age", "A", "年龄异常精确",
            "年龄区间异常窄（窄于2年）或精确到月/日，排除了常规的'XX周岁以下'等宽泛年龄限制",
            "常规岗位通常要求'XX周岁以下'或'XX-XX岁'，区间≥5年属正常。"
            "只有年龄区间窄于2年、精确到月/日（如'1995年8月至1996年2月出生'）、"
            "或限定特定出生年月日时才应判定命中。"
            "'XX周岁以下'、'18-35周岁'等宽泛年龄要求不算命中。"),
    Feature("specific_experience", "A", "工作经历高度特定",
            "要求特定单位类型/特定岗位/精确年限的经历",
            "看经历要求是否指向特定个人履历"),
    Feature("tricky_certs", "A", "证书资格刁钻",
            "要求多个罕见证书/资格叠加",
            "看证书组合是否罕见且非岗位必需"),
    Feature("specific_award_name", "A", "指定获奖名称",
            '要求获得特定名称的奖项或荣誉（如"XX部优秀成果奖"）',
            "看奖项名称是否具体到指向极少数人"),
    Feature("competition_ranking", "A", "指定竞赛名次",
            '要求在特定比赛中达到指定名次或等级（如"XX大赛全国前10名"）',
            "看比赛+名次组合是否高度限定"),
    Feature("specific_publication", "A", "指定论文主题",
            "要求发表过特定主题/方向的论文",
            "看论文主题是否窄到指向特定研究经历"),
    Feature("specific_journal", "A", "指定期刊级别",
            "要求论文发表于特定期刊或特定级别期刊（如CSSCI核心期刊）",
            "看期刊要求是否超出岗位合理需要"),
    Feature("unjustified_restriction", "B", "无正当理由的限定",
            "无正当理由的性别、政治面貌、户籍等限定",
            "看限制是否缺乏岗位相关性"),
    Feature("directional_wording", "B", "定向专项措辞",
            "出现\"定向/专项招聘\"等缩小范围的措辞",
            "看是否用定向措辞排除一般竞争者"),
    Feature("few_slots_many_limits", "C", "名额极少却堆叠限制",
            "招聘名额极少（常 1 人）却叠加大量限制条件",
            "看名额与限制条件数量是否失衡"),
    Feature("near_unique_combo", "C", "组合后符合人数极少",
            "多条件组合后理论符合人数极少",
            "综合所有条件估计可能符合的人群规模"),
    Feature("short_window", "D", "报名窗口极短",
            "报名时间异常短促，变相限制竞争",
            "看报名期是否明显短于常规"),
    Feature("obscure_publish", "D", "发布隐蔽",
            "公告发布渠道隐蔽、不易被发现",
            "看公告可见性/传播范围是否异常低"),
]

FEATURE_KEYS = {f.key for f in FEATURES}


def feature_checklist_text() -> str:
    lines = []
    for f in FEATURES:
        lines.append(f"- [{f.category}] {f.key}（{f.name}）：{f.description}。判断要点：{f.judge_hint}")
    return "\n".join(lines)
