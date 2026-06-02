import json

from app.analysis.features import feature_checklist_text

_SYSTEM = """你是分析中国事业单位、国企招聘公告是否存在"萝卜岗/萝卜招聘"嫌疑的助手。
萝卜岗指为内定人选量身定制招聘条件、使实际上只有特定一人符合的岗位。

判定原则：
1. 客观中立，只依据公告文本给出依据，不臆断、不针对具体个人。
2. 用"疑似"而非确定性结论；你的输出仅供参考。
3. 依据下列特征清单逐项判断命中情况，命中越多、越极端，疑似度越高。

特征清单：
{checklist}

请先从公告中抽取岗位关键字段，再做疑似度分析。
严格只输出一个 JSON 对象（不要 markdown 代码块、不要多余文字），结构如下：
{{
  "position": {{"org_name": 字符串或null, "position_name": 字符串或null,
    "major_req": 字符串或null, "age_req": 字符串或null, "education_req": 字符串或null,
    "experience_req": 字符串或null, "cert_req": 字符串或null, "headcount": 整数或null}},
  "suspicion_score": 0到100的整数,
  "hit_features": [{{"key": 特征清单中的key, "evidence": 命中说明, "quote": 公告原文片段}}],
  "reasoning": 总体分析理由,
  "highlights": [{{"text": 公告中的可疑原文片段, "reason": 可疑原因}}]
}}"""

_FEWSHOT_USER = "招聘1名研究人员，要求古生物学专业，全日制博士，1995年8月至1996年2月出生，需具备某特定研究所2年工作经历。"

_FEWSHOT_ASSISTANT = json.dumps({
    "position": {
        "org_name": None, "position_name": "研究人员", "major_req": "古生物学",
        "age_req": "1995年8月-1996年2月出生", "education_req": "全日制博士",
        "experience_req": "某特定研究所2年经历", "cert_req": None, "headcount": 1,
    },
    "suspicion_score": 90,
    "hit_features": [
        {"key": "precise_age", "evidence": "年龄精确到月且区间极窄", "quote": "1995年8月至1996年2月出生"},
        {"key": "major_too_narrow", "evidence": "专业极冷门", "quote": "古生物学专业"},
        {"key": "specific_experience", "evidence": "限定特定研究所经历", "quote": "某特定研究所2年工作经历"},
        {"key": "few_slots_many_limits", "evidence": "1人却多重限制", "quote": "招聘1名"},
    ],
    "reasoning": "多项条件高度具体且相互叠加，理论符合人数极少，疑似为特定人选量身定制。",
    "highlights": [
        {"text": "1995年8月至1996年2月出生", "reason": "年龄异常精确"},
        {"text": "古生物学专业", "reason": "专业限定过窄"},
    ],
}, ensure_ascii=False)

_FEWSHOT_USER_NORMAL = "招聘5名行政管理人员，要求本科及以上学历，管理类相关专业，年龄35周岁以下。"

_FEWSHOT_ASSISTANT_NORMAL = json.dumps({
    "position": {
        "org_name": None, "position_name": "行政管理人员", "major_req": "管理类相关专业",
        "age_req": "35周岁以下", "education_req": "本科及以上", "experience_req": None,
        "cert_req": None, "headcount": 5,
    },
    "suspicion_score": 8,
    "hit_features": [],
    "reasoning": "条件宽泛、名额较多，符合常规公开招聘特征，无明显萝卜岗信号。",
    "highlights": [],
}, ensure_ascii=False)


def build_messages(text: str) -> list[dict]:
    system = _SYSTEM.format(checklist=feature_checklist_text())
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": _FEWSHOT_USER},
        {"role": "assistant", "content": _FEWSHOT_ASSISTANT},
        {"role": "user", "content": _FEWSHOT_USER_NORMAL},
        {"role": "assistant", "content": _FEWSHOT_ASSISTANT_NORMAL},
        {"role": "user", "content": f"请分析以下招聘公告：\n{text}"},
    ]
