<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const items  = ref([])
const total  = ref(0)
const loading = ref(true)
const error   = ref(null)

const FEATURE_NAMES = {
  major_too_narrow:       '专业过窄',
  rare_edu_combo:         '院校叠加',
  precise_age:            '年龄精确',
  specific_experience:    '经历特定',
  tricky_certs:           '证书刁钻',
  specific_award_name:    '指定获奖',
  competition_ranking:    '竞赛名次',
  specific_publication:   '论文主题',
  specific_journal:       '期刊级别',
  unjustified_restriction:'无故限定',
  directional_wording:    '定向措辞',
  few_slots_many_limits:  '名少限多',
  near_unique_combo:      '极少符合',
  short_window:           '窗口极短',
  obscure_publish:        '渠道隐蔽',
}

const LEVEL_COLOR = { high:'#E53E3E', mid:'#ED8936', low:'#48BB78' }
const LEVEL_LABEL = { high:'高疑似',   mid:'中疑似',   low:'低疑似' }
const LEVEL_SOFT  = { high:'rgba(229,62,62,0.08)', mid:'rgba(237,137,54,0.08)', low:'rgba(72,187,120,0.08)' }
const LEVEL_BG    = { high:'#FFF5F5', mid:'#FFFAF0', low:'#F0FFF4' }

const highCount = computed(() => items.value.filter(i => i.level === 'high').length)
const midCount  = computed(() => items.value.filter(i => i.level === 'mid').length)
const lowCount  = computed(() => items.value.filter(i => i.level === 'low').length)

function fmt(iso) {
  return iso ? iso.split('T')[0] : '—'
}
function pad(n) {
  return String(n).padStart(2, '0')
}

onMounted(async () => {
  try {
    const r = await fetch('/api/analyses?limit=200')
    if (!r.ok) throw new Error()
    const d = await r.json()
    items.value = d.items
    total.value = d.total
  } catch {
    error.value = '数据加载失败，请检查后端服务是否运行'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="list-page">

    <!-- ── Page header ── -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-left">
          <h1 class="page-title">案件总库</h1>
          <p class="page-sub">按萝卜岗疑似度由高到低排列</p>
        </div>
        <div v-if="!loading && !error" class="header-stats">
          <div class="stat" style="--sc:#E53E3E; --sb:#FFF5F5">
            <span class="stat-num">{{ highCount }}</span>
            <span class="stat-lbl">高疑似</span>
          </div>
          <div class="stat" style="--sc:#ED8936; --sb:#FFFAF0">
            <span class="stat-num">{{ midCount }}</span>
            <span class="stat-lbl">中疑似</span>
          </div>
          <div class="stat" style="--sc:#48BB78; --sb:#F0FFF4">
            <span class="stat-num">{{ lowCount }}</span>
            <span class="stat-lbl">低疑似</span>
          </div>
          <div class="stat stat-total">
            <span class="stat-num" style="color:var(--text-2)">{{ total }}</span>
            <span class="stat-lbl">共计</span>
          </div>
        </div>
      </div>
    </header>

    <!-- ── Loading ── -->
    <div v-if="loading" class="skeleton-list">
      <div v-for="n in 7" :key="n" class="skeleton-card"
           :style="{ animationDelay: (n-1)*0.07 + 's' }"></div>
    </div>

    <!-- ── Error ── -->
    <div v-else-if="error" class="state-box">
      <div class="state-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <!-- ── Empty ── -->
    <div v-else-if="!items.length" class="state-box">
      <div class="state-icon">🥕</div>
      <h3>档案室空空如也</h3>
      <p>尚无分析记录，先提交一份招聘公告</p>
      <RouterLink to="/submit" class="cta-btn">提交第一条公告 →</RouterLink>
    </div>

    <!-- ── Cards ── -->
    <div v-else class="cards">
      <div
        v-for="(item, idx) in items"
        :key="item.analysis_id"
        class="card"
        :style="{
          '--lc':   LEVEL_COLOR[item.level],
          '--ls':   LEVEL_SOFT[item.level],
          '--lb':   LEVEL_BG[item.level],
          '--delay': (idx * 0.035) + 's',
        }"
        @click="router.push('/analysis/' + item.analysis_id)"
      >
        <!-- Score column -->
        <div class="score-col">
          <div class="rank-label">{{ pad(idx + 1) }}</div>
          <div class="score-num">{{ item.suspicion_score }}</div>
          <div class="score-track">
            <div class="score-fill" :style="{ width: item.suspicion_score + '%' }"></div>
          </div>
          <div class="level-tag">{{ LEVEL_LABEL[item.level] }}</div>
        </div>

        <!-- Info column -->
        <div class="info-col">
          <div class="org-name">{{ item.position.org_name || '未知机构' }}</div>
          <div class="pos-name">{{ item.position.position_name || '未知职位' }}</div>
          <div class="pos-meta">
            <span v-if="item.position.education_req" class="chip">{{ item.position.education_req }}</span>
            <span v-if="item.position.headcount" class="chip">招 {{ item.position.headcount }} 人</span>
            <span v-if="item.position.major_req" class="chip chip-major">
              {{ item.position.major_req.length > 18
                ? item.position.major_req.slice(0, 18) + '…'
                : item.position.major_req }}
            </span>
            <a v-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener"
               class="chip chip-link" @click.stop>来源链接 ↗</a>
          </div>
          <div class="tags">
            <span
              v-for="f in item.hit_features.slice(0, 5)"
              :key="f.key"
              class="tag"
            >{{ FEATURE_NAMES[f.key] || f.key }}</span>
            <span v-if="item.hit_features.length > 5" class="tag tag-more">
              +{{ item.hit_features.length - 5 }}
            </span>
          </div>
        </div>

        <!-- Right: date + arrow -->
        <div class="right-col">
          <span class="date-text">{{ fmt(item.analyzed_at) }}</span>
          <span class="go-arrow">→</span>
        </div>
      </div>
    </div>

    <footer class="page-footer">
      免责声明：AI 自动推测，仅供参考，不构成任何确定性结论，不针对任何具体单位或个人。
    </footer>
  </div>
</template>

<style scoped>
/* ── Layout ───────────────────────────────────────────────── */
.list-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

/* ── Header ───────────────────────────────────────────────── */
.page-header {
  padding: 32px 0 0;
}
.header-inner {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 24px;
  flex-wrap: wrap;
}
.page-title {
  font-family: var(--ff-display);
  font-size: 28px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--text);
  line-height: 1.2;
}
.page-sub {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-3);
  letter-spacing: 0.05em;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 8px 14px;
  background: var(--sb);
  border-radius: var(--radius);
}
.stat-num {
  font-family: var(--ff-mono);
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
  color: var(--sc);
}
.stat-lbl {
  font-size: 10px;
  color: var(--text-3);
  letter-spacing: 0.08em;
  white-space: nowrap;
}
.stat-total {
  background: var(--surface-2);
}

/* ── Skeleton ─────────────────────────────────────────────── */
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.skeleton-list { margin-top: 12px; display: flex; flex-direction: column; gap: 10px; }
.skeleton-card {
  height: 90px;
  border-radius: var(--radius);
  background: linear-gradient(90deg, var(--surface) 25%, var(--surface-2) 50%, var(--surface) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  opacity: 0;
  animation-fill-mode: both;
  box-shadow: var(--shadow-sm);
}
@keyframes skeletonAppear { to { opacity: 1; } }
.skeleton-card { animation: skeletonAppear 0.3s ease both, shimmer 1.4s 0.3s ease-in-out infinite; }

/* ── State boxes ──────────────────────────────────────────── */
.state-box {
  margin-top: 80px;
  text-align: center;
  color: var(--text-2);
}
.state-icon { font-size: 44px; margin-bottom: 16px; }
.state-box h3 { font-family: var(--ff-display); font-size: 18px; margin-bottom: 8px; color: var(--text); font-weight: 600; }
.state-box p  { font-size: 13px; color: var(--text-2); margin-bottom: 20px; }
.cta-btn {
  display: inline-block;
  padding: 10px 24px;
  background: var(--carrot);
  color: #fff;
  border-radius: 24px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(237,137,54,0.25);
  transition: transform 0.2s, box-shadow 0.2s;
}
.cta-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(237,137,54,0.3);
}

/* ── Cards list ───────────────────────────────────────────── */
.cards {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ── Individual Card ──────────────────────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

.card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0;
  cursor: pointer;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: fadeUp 0.3s ease both;
  animation-delay: var(--delay);
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md), 0 0 0 1px var(--lc);
}

/* ── Score column ─────────────────────────────────────────── */
.score-col {
  flex-shrink: 0;
  width: 88px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 10px 16px 16px;
  gap: 4px;
  background: var(--lb);
  border-radius: var(--radius) 0 0 var(--radius);
}
.rank-label {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text-3);
  letter-spacing: 0.1em;
}
.score-num {
  font-family: var(--ff-mono);
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  color: var(--lc);
}
.score-track {
  width: 80%;
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}
.score-fill {
  height: 100%;
  background: var(--lc);
  border-radius: 2px;
  transition: width 0.6s ease;
}
.level-tag {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--lc);
}

/* ── Info column ──────────────────────────────────────────── */
.info-col {
  flex: 1;
  padding: 14px 16px;
  min-width: 0;
}
.org-name {
  font-family: var(--ff-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}
.pos-name {
  font-size: 12px;
  color: var(--text-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 8px;
}

.pos-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 8px;
}
.chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--surface-2);
  font-size: 10px;
  color: var(--text-2);
  white-space: nowrap;
}
.chip-major { color: var(--carrot-deep); background: var(--amber-soft); }
.chip-link { color: var(--green); background: var(--green-soft); text-decoration: none; cursor: pointer; }
.chip-link:hover { text-decoration: underline; }

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--ls);
  font-size: 10px;
  color: var(--lc);
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.tag-more {
  background: var(--surface-2);
  color: var(--text-3);
}

/* ── Right column ─────────────────────────────────────────── */
.right-col {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  padding: 14px 18px 14px 8px;
}
.date-text {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text-3);
}
.go-arrow {
  font-size: 16px;
  color: var(--text-3);
  transition: color 0.16s, transform 0.16s;
}
.card:hover .go-arrow {
  color: var(--lc);
  transform: translateX(3px);
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
