"""插入演示数据（无需 AI API）"""
import hashlib, sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal, engine
from app.db.models import Base, Announcement, Position, Analysis

Base.metadata.create_all(engine)
db = SessionLocal()

SAMPLES = [
    {
        'text': '某市人力资源和社会保障局公开招聘事业单位工作人员公告，招聘研究员1名，要求古生物学专业，全日制博士研究生，1995年8月至1996年2月期间出生，须具有某特定研究所2年以上工作经历，持有国家古生物研究特定资格证书。报名时间为公告发布之日起2日内。',
        'org': '某市人力资源和社会保障局', 'pos': '研究员（古生物学方向）',
        'major': '古生物学', 'age': '1995年8月-1996年2月出生', 'edu': '全日制博士',
        'exp': '某特定研究所2年以上工作经历', 'cert': '国家古生物研究特定资格证书', 'hc': 1,
        'score': 94, 'level': 'high',
        'features': [
            {'key':'precise_age','evidence':'年龄精确到月且区间仅6个月','quote':'1995年8月至1996年2月'},
            {'key':'major_too_narrow','evidence':'古生物学极度冷门，全国博士极少','quote':'古生物学专业'},
            {'key':'specific_experience','evidence':'要求特定研究所经历，指向性强','quote':'某特定研究所2年以上工作经历'},
            {'key':'tricky_certs','evidence':'非岗位必需的冷门证书','quote':'国家古生物研究特定资格证书'},
            {'key':'short_window','evidence':'仅2日报名窗口严重偏短','quote':'2日内'},
            {'key':'few_slots_many_limits','evidence':'仅招1人却叠加5条以上限制','quote':'招聘研究员1名'},
        ],
        'reasoning': '该岗位限制条件高度叠加：年龄精确到月（6个月窗口）、专业极度冷门、须特定单位经历、罕见证书、报名仅2天。理论上同时满足所有条件的候选人极少，疑似为内定人员量身定制。',
        'highlights': [
            {'text':'1995年8月至1996年2月期间出生','reason':'年龄区间异常精确，仅6个月'},
            {'text':'某特定研究所2年以上工作经历','reason':'高度特定的工作经历指向特定人选'},
            {'text':'报名时间为公告发布之日起2日内','reason':'报名窗口极短，阻止外部竞争者'},
        ]
    },
    {
        'text': '某市文化局下属事业单位招聘副研究馆员1名，要求音乐学（钢琴演奏方向）博士学位，曾在某市音乐学院进修满2年，年龄30周岁以下，能熟练演奏肖邦夜曲Op.27，发表SCI论文不少于2篇。',
        'org': '某市文化馆', 'pos': '副研究馆员',
        'major': '音乐学（钢琴演奏方向）', 'age': '30周岁以下', 'edu': '博士学位',
        'exp': '某市音乐学院进修满2年', 'cert': None, 'hc': 1,
        'score': 91, 'level': 'high',
        'features': [
            {'key':'specific_experience','evidence':'特定院校进修经历，极强指向性','quote':'某市音乐学院进修满2年'},
            {'key':'specific_award_name','evidence':'具体到特定曲目的演奏要求','quote':'能熟练演奏肖邦夜曲Op.27'},
            {'key':'rare_edu_combo','evidence':'音乐演奏博士+SCI论文组合极罕见','quote':'音乐学（钢琴演奏方向）博士学位，发表SCI论文不少于2篇'},
            {'key':'major_too_narrow','evidence':'专业方向极细，符合者极少','quote':'钢琴演奏方向'},
            {'key':'few_slots_many_limits','evidence':'1人岗位堆叠5条以上荒诞限制','quote':None},
        ],
        'reasoning': '该岗位将音乐演奏与SCI论文强行叠加，同时指定特定院校进修和特定乐曲，现实中几乎不存在自然候选人，极大概率为特定人员量身定制。',
        'highlights': [
            {'text':'能熟练演奏肖邦夜曲Op.27','reason':'荒诞地具体，等同于给特定人量身定制'},
            {'text':'某市音乐学院进修满2年','reason':'特定院校特定年限，指向性极强'},
            {'text':'发表SCI论文不少于2篇','reason':'演奏岗位要求SCI论文，本身即不合常规'},
        ]
    },
    {
        'text': '某省国有企业公开招聘财务总监1名，要求注册会计师（CPA），同时持有资产评估师执业资格，硕士及以上学历，金融学或会计学专业，具有国有大型企业集团财务负责人5年以上经验，年龄40-45周岁，户籍要求本省户口。',
        'org': '某省能源集团有限公司', 'pos': '财务总监',
        'major': '金融学或会计学', 'age': '40-45周岁', 'edu': '硕士及以上',
        'exp': '国有大型企业集团财务负责人5年以上', 'cert': 'CPA+资产评估师双证', 'hc': 1,
        'score': 82, 'level': 'high',
        'features': [
            {'key':'tricky_certs','evidence':'同时要求CPA和资产评估师，双证叠加极罕见','quote':'注册会计师（CPA），同时持有资产评估师执业资格'},
            {'key':'specific_experience','evidence':'限定国有大型企业集团财务负责人5年','quote':'国有大型企业集团财务负责人5年以上经验'},
            {'key':'unjustified_restriction','evidence':'户籍要求与职责无关','quote':'户籍要求本省户口'},
            {'key':'few_slots_many_limits','evidence':'1人岗位叠加多项严苛限制','quote':None},
            {'key':'near_unique_combo','evidence':'双证+5年特定经验+户籍，符合者寥寥','quote':None},
        ],
        'reasoning': '该岗位要求同时持有CPA和资产评估师双执业资格，叠加5年国有大企业集团财务负责人经验，并附加户籍限制，各条件叠加后符合条件者极少，定向嫌疑较强。',
        'highlights': [
            {'text':'注册会计师（CPA），同时持有资产评估师执业资格','reason':'双证叠加要求，同时持有者稀少'},
            {'text':'国有大型企业集团财务负责人5年以上经验','reason':'高度特定的岗位经历'},
            {'text':'户籍要求本省户口','reason':'与财务总监岗位无关的限制'},
        ]
    },
    {
        'text': '某市人才服务中心招聘综合管理岗1名，要求全日制本科，管理学类相关专业，35周岁以下，中共党员，具有2年以上党务工作经验，户籍要求本市户口，报名时间3日内。',
        'org': '某市人才服务中心', 'pos': '综合管理岗',
        'major': '管理学类', 'age': '35周岁以下', 'edu': '全日制本科',
        'exp': '2年以上党务工作经验', 'cert': None, 'hc': 1,
        'score': 55, 'level': 'mid',
        'features': [
            {'key':'unjustified_restriction','evidence':'户籍限制与管理岗无关','quote':'户籍要求本市户口'},
            {'key':'short_window','evidence':'3日报名时间明显偏短','quote':'报名时间3日内'},
            {'key':'few_slots_many_limits','evidence':'1人岗位附加户籍+党员+经验多重条件','quote':None},
        ],
        'reasoning': '该岗位附加了本市户籍要求，报名窗口仅3天，1人岗位叠加多项条件，中度疑似定向招聘。但整体比最高风险岗位条件宽泛，属中等疑似范围。',
        'highlights': [
            {'text':'户籍要求本市户口','reason':'与岗位职责无关的限制条件'},
            {'text':'报名时间3日内','reason':'报名窗口偏短'},
        ]
    },
    {
        'text': '某市卫生健康委员会下属医院招聘主治医师2名，要求临床医学专业，执业医师资格证书，中级职称及以上，年龄40周岁以下，具有三甲医院工作经历优先。',
        'org': '某市人民医院', 'pos': '主治医师（内科）',
        'major': '临床医学', 'age': '40周岁以下', 'edu': '本科及以上',
        'exp': '三甲医院工作经历（优先）', 'cert': '执业医师资格证书', 'hc': 2,
        'score': 22, 'level': 'low',
        'features': [],
        'reasoning': '岗位要求属于临床医师正常标准，执业资格证书是法定要求而非刁钻附加条件，招聘2名且报名期充足，不存在明显定向嫌疑。',
        'highlights': []
    },
    {
        'text': '某央企子公司招聘人工智能算法工程师5名，要求计算机科学与技术、人工智能相关专业，硕士及以上学历，熟悉PyTorch/TensorFlow，有NLP或CV项目经验，35周岁以下，应届生优先。',
        'org': '某央企数字科技公司', 'pos': '人工智能算法工程师',
        'major': '计算机科学与技术或人工智能', 'age': '35周岁以下', 'edu': '硕士及以上',
        'exp': None, 'cert': None, 'hc': 5,
        'score': 12, 'level': 'low',
        'features': [],
        'reasoning': '技术类招聘岗位条件正常：专业范围宽泛，招5人，应届生优先，技术要求合理，无不当限制。',
        'highlights': []
    },
    {
        'text': '某区政府办公室招聘文字综合岗位工作人员1名，要求汉语言文学或新闻传播学专业，全日制本科，年龄28岁以下，要求1994年1月至1996年12月出生，须具有省级机关文秘工作经历不少于1年，发表过省级以上刊物文章不少于3篇。',
        'org': '某区政府办公室', 'pos': '文字综合岗',
        'major': '汉语言文学或新闻传播学', 'age': '1994年1月-1996年12月出生', 'edu': '全日制本科',
        'exp': '省级机关文秘工作经历不少于1年', 'cert': None, 'hc': 1,
        'score': 71, 'level': 'high',
        'features': [
            {'key':'precise_age','evidence':'年龄精确到年份范围，隐性限制','quote':'1994年1月至1996年12月出生'},
            {'key':'specific_experience','evidence':'特定级别机关文秘经历','quote':'省级机关文秘工作经历不少于1年'},
            {'key':'specific_journal','evidence':'要求省级以上刊物发表记录','quote':'省级以上刊物文章不少于3篇'},
            {'key':'few_slots_many_limits','evidence':'1名岗位叠加多项特定限制','quote':None},
        ],
        'reasoning': '该岗位为本科岗位却要求省级机关经历和论文发表，年龄限定到出生年份区间，条件组合指向性较强，高疑似。',
        'highlights': [
            {'text':'省级机关文秘工作经历不少于1年','reason':'本科岗位要求省级机关经历门槛过高'},
            {'text':'省级以上刊物文章不少于3篇','reason':'文秘岗位要求论文发表不合常规'},
        ]
    },
]

for s in SAMPLES:
    text = s['text']
    ann = Announcement(
        raw_text=text, source_type='submit',
        content_hash=hashlib.sha256(text.encode()).hexdigest(),
        org_name=s['org'],
    )
    db.add(ann); db.flush()

    pos = Position(
        announcement_id=ann.id,
        org_name=s['org'], position_name=s['pos'],
        major_req=s['major'], age_req=s['age'],
        education_req=s['edu'], experience_req=s['exp'],
        cert_req=s['cert'], headcount=s['hc'],
    )
    db.add(pos); db.flush()

    ana = Analysis(
        position_id=pos.id,
        suspicion_score=s['score'], level=s['level'],
        hit_features=s['features'], reasoning=s['reasoning'],
        highlights=s['highlights'], model_version='demo-seed',
    )
    db.add(ana)

db.commit()
print(f'Seeded {len(SAMPLES)} demo records OK')
db.close()
