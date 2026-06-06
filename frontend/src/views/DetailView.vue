<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route  = useRoute()
const router = useRouter()
const data    = ref(null)
const loading = ref(true)
const error   = ref(null)

const FEATURE_NAMES = {
  major_too_narrow:       '专业限定过窄',
  rare_edu_combo:         '院校学历罕见叠加',
  precise_age:            '年龄异常精确',
  specific_experience:    '工作经历高度特定',
  tricky_certs:           '证书资格刁钻',
  specific_award_name:    '指定获奖名称',
  competition_ranking:    '指定竞赛名次',
  specific_publication:   '指定论文主题',
  specific_journal:       '指定期刊级别',
  unjustified_restriction:'无正当理由限定',
  directional_wording:    '定向专项措辞',
  few_slots_many_limits:  '名额少却堆叠限制',
  near_unique_combo:      '组合后符合人数极少',
  short_window:           '报名窗口极短',
  obscure_publish:        '发布渠道隐蔽',
}

const LEVEL_COLOR = { high:'#E8192C', mid:'#E87820', low:'#12B89A' }
const LEVEL_LABEL = { high:'高疑似',   mid:'中疑似',   low:'低疑似' }
const LEVEL_SOFT  = { high:'rgba(232,25,44,0.1)', mid:'rgba(232,120,32,0.1)', low:'rgba(18,184,154,0.1)' }
const LEVEL_DESC  = {
  high: '该岗位招聘条件存在多项高度具体的限制，理论上符合条件的候选人极少，萝卜岗嫌疑显著。',
  mid:  '该岗位招聘条件存在部分可疑限制，不排除为特定人选量身定制的可能性。',
  low:  '该岗位招聘条件总体符合常规，暂未发现明显萝卜岗特征。',
}

const ana = computed(() => data.value?.analysis)
const pos = computed(() => data.value?.position)
const sourceUrl = computed(() => data.value?.source_url)
const lc  = computed(() => ana.value ? LEVEL_COLOR[ana.value.level] : '#7A7585')
const ls  = computed(() => ana.value ? LEVEL_SOFT[ana.value.level] : 'transparent')

const posFields = computed(() => {
  if (!pos.value) return []
  const map = [
    ['机构名称', pos.value.org_name],
    ['职位名称', pos.value.position_name],
    ['招聘人数', pos.value.headcount ? pos.value.headcount + ' 人' : null],
    ['专业要求', pos.value.major_req],
    ['学历要求', pos.value.education_req],
    ['年龄要求', pos.value.age_req],
    ['经历要求', pos.value.experience_req],
    ['证书要求', pos.value.cert_req],
  ]
  return map.filter(([, v]) => v)
})

onMounted(async () => {
  try {
    const r = await fetch(`/api/analyses/${route.params.id}`)
    if (!r.ok) throw new Error(r.status === 404 ? '记录不存在' : '加载失败')
    data.value = await r.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="detail-page">

    <!-- ── Back button ── -->
    <div class="back-row">
      <button class="back-btn" @click="router.back()">← 返回案件库</button>
    </div>

    <!-- ── Loading ── -->
    <div v-if="loading" class="state-box">
      <div class="spin"></div>
    </div>

    <!-- ── Error ── -->
    <div v-else-if="error" class="state-box">
      <div class="state-icon">⚠</div>
      <p>{{ error }}</p>
    </div>

    <!-- ── Content ── -->
    <template v-else-if="data">

      <!-- Hero -->
      <div class="hero" :style="{ '--lc': lc, '--ls': ls }">
        <div class="hero-score-block">
          <div class="hero-num">{{ ana.suspicion_score }}</div>
          <div class="hero-track">
            <div class="hero-fill" :style="{ width: ana.suspicion_score + '%' }"></div>
          </div>
          <div class="hero-label">萝卜岗指数</div>
        </div>

        <div class="hero-verdict">
          <div class="verdict-badge">{{ LEVEL_LABEL[ana.level] }}</div>
          <h2 class="hero-org">{{ pos.org_name || '未知机构' }}</h2>
          <p class="hero-pos">{{ pos.position_name || '未知职位' }}</p>
          <p class="hero-desc">{{ LEVEL_DESC[ana.level] }}</p>
        </div>
      </div>

      <!-- Position Info -->
      <section class="section">
        <h3 class="section-title">
          <span class="section-line"></span>岗位信息
        </h3>
        <div class="info-grid">
          <div v-for="[label, value] in posFields" :key="label" class="info-row">
            <span class="info-label">{{ label }}</span>
            <span class="info-value">{{ value }}</span>
          </div>
          <div v-if="sourceUrl" class="info-row">
            <span class="info-label">公告来源</span>
            <a class="info-value source-link" :href="sourceUrl" target="_blank" rel="noopener">{{ sourceUrl }}</a>
          </div>
        </div>
      </section>

      <!-- Hit Features -->
      <section v-if="ana.hit_features && ana.hit_features.length" class="section">
        <h3 class="section-title">
          <span class="section-line"></span>命中特征
          <span class="feature-count">{{ ana.hit_features.length }}</span>
        </h3>
        <div class="features-grid">
          <div v-for="f in ana.hit_features" :key="f.key" class="feature-card"
               :style="{ '--lc': lc, '--ls': ls }">
            <div class="feature-name">{{ FEATURE_NAMES[f.key] || f.key }}</div>
            <div class="feature-evidence">{{ f.evidence }}</div>
            <div v-if="f.quote" class="feature-quote">
              <span class="quote-mark">"</span>{{ f.quote }}<span class="quote-mark">"</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Reasoning -->
      <section v-if="ana.reasoning" class="section">
        <h3 class="section-title">
          <span class="section-line"></span>综合分析
        </h3>
        <div class="reasoning-box">
          <p class="reasoning-text">{{ ana.reasoning }}</p>
        </div>
      </section>

      <!-- Highlights -->
      <section v-if="ana.highlights && ana.highlights.length" class="section">
        <h3 class="section-title">
          <span class="section-line"></span>可疑条款原文
        </h3>
        <div class="highlights-list">
          <div v-for="(h, i) in ana.highlights" :key="i" class="highlight-item">
            <div class="highlight-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <div class="highlight-body">
              <div class="highlight-text">
                <mark>{{ h.text }}</mark>
              </div>
              <div class="highlight-reason">{{ h.reason }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Model info -->
      <div class="model-info">
        分析模型：{{ ana.model_version }}
      </div>

    </template>

    <footer class="page-footer">
      免责声明：AI 自动推测，仅供参考，不构成任何确定性结论，不针对任何具体单位或个人。
    </footer>
  </div>
</template>

<style scoped>
.detail-page {
  max-width: 820px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

/* ── Back ─────────────────────────────────────────────────── */
.back-row {
  padding: 20px 0 0;
}
.back-btn {
  background: none;
  border: none;
  color: var(--text-2);
  font-family: var(--ff-body);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.16s;
}
.back-btn:hover { color: var(--text); }

/* ── State ────────────────────────────────────────────────── */
.state-box {
  margin-top: 80px;
  text-align: center;
  color: var(--text-2);
}
.state-icon { font-size: 36px; margin-bottom: 12px; opacity: 0.5; }

@keyframes spin { to { transform: rotate(360deg); } }
.spin {
  width: 32px; height: 32px;
  border: 2px solid var(--border);
  border-top-color: var(--text-2);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 80px auto;
}

/* ── Hero ─────────────────────────────────────────────────── */
.hero {
  display: flex;
  align-items: center;
  gap: 32px;
  margin: 24px 0 0;
  padding: 28px 32px;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-left: 4px solid var(--lc);
  border-radius: 0 12px 12px 0;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 0% 50%, var(--ls) 0%, transparent 70%);
  pointer-events: none;
}

.hero-score-block {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 100px;
}
.hero-num {
  font-family: var(--ff-mono);
  font-size: 72px;
  font-weight: 700;
  line-height: 1;
  color: var(--lc);
}
.hero-track {
  width: 80px;
  height: 4px;
  background: rgba(255,255,255,0.08);
  border-radius: 2px;
  overflow: hidden;
}
.hero-fill {
  height: 100%;
  background: var(--lc);
  border-radius: 2px;
}
.hero-label {
  font-size: 10px;
  letter-spacing: 0.1em;
  color: var(--text-3);
  text-transform: uppercase;
}

.hero-verdict { flex: 1; min-width: 0; }
.verdict-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 3px;
  border: 1px solid var(--lc);
  background: var(--ls);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--lc);
  margin-bottom: 10px;
}
.hero-org {
  font-family: var(--ff-display);
  font-size: 22px;
  font-weight: normal;
  color: var(--text);
  margin-bottom: 4px;
  line-height: 1.3;
}
.hero-pos {
  font-size: 14px;
  color: var(--text-2);
  margin-bottom: 12px;
}
.hero-desc {
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.7;
}

/* ── Sections ─────────────────────────────────────────────── */
.section { margin-top: 32px; }

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-2);
  margin-bottom: 16px;
}
.section-line {
  display: inline-block;
  width: 24px;
  height: 2px;
  background: var(--red);
  border-radius: 1px;
  flex-shrink: 0;
}
.feature-count {
  margin-left: auto;
  font-family: var(--ff-mono);
  font-size: 18px;
  color: var(--text-3);
}

/* ── Info grid ────────────────────────────────────────────── */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 8px;
  overflow: hidden;
}
.info-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
  padding: 11px 18px;
  border-bottom: 1px solid var(--border-2);
}
.info-row:last-child { border-bottom: none; }
.info-label {
  flex-shrink: 0;
  width: 72px;
  font-size: 11px;
  color: var(--text-3);
  letter-spacing: 0.06em;
}
.info-value {
  flex: 1;
  font-size: 13px;
  color: var(--text);
  line-height: 1.5;
  word-break: break-all;
}
.source-link {
  color: var(--teal, #12B89A);
  text-decoration: none;
  transition: opacity 0.2s;
}
.source-link:hover { opacity: 0.8; text-decoration: underline; }

/* ── Features grid ────────────────────────────────────────── */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px;
}
.feature-card {
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-left: 3px solid var(--lc);
  border-radius: 0 8px 8px 0;
}
.feature-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--lc);
  margin-bottom: 6px;
  letter-spacing: 0.04em;
}
.feature-evidence {
  font-size: 12px;
  color: var(--text-2);
  line-height: 1.5;
  margin-bottom: 6px;
}
.feature-quote {
  font-size: 11px;
  color: var(--text-3);
  line-height: 1.5;
  font-style: italic;
}
.quote-mark { color: var(--lc); font-style: normal; }

/* ── Reasoning ────────────────────────────────────────────── */
.reasoning-box {
  padding: 20px 22px;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 8px;
}
.reasoning-text {
  font-size: 14px;
  color: var(--text);
  line-height: 1.85;
}

/* ── Highlights ───────────────────────────────────────────── */
.highlights-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.highlight-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  padding: 14px 18px;
  background: var(--surface);
  border: 1px solid var(--border-2);
  border-radius: 8px;
}
.highlight-num {
  flex-shrink: 0;
  font-family: var(--ff-mono);
  font-size: 11px;
  color: var(--text-3);
  padding-top: 2px;
}
.highlight-body { flex: 1; }
.highlight-text {
  font-size: 14px;
  color: var(--text);
  margin-bottom: 4px;
  line-height: 1.5;
}
.highlight-text mark {
  background: rgba(254, 240, 138, 0.2);
  color: #FEF08A;
  padding: 1px 4px;
  border-radius: 2px;
}
.highlight-reason {
  font-size: 12px;
  color: var(--text-2);
}

/* ── Model info ───────────────────────────────────────────── */
.model-info {
  margin-top: 32px;
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text-3);
  text-align: right;
}

/* ── Footer ───────────────────────────────────────────────── */
.page-footer {
  margin-top: 48px;
  font-size: 11px;
  color: var(--text-3);
  text-align: center;
  line-height: 1.8;
}
</style>
