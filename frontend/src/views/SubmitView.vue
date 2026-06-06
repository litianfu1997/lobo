<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router  = useRouter()
const text    = ref('')
const sourceUrl = ref('')
const loading = ref(false)
const error   = ref('')
const result  = ref(null)

const LEVEL_COLOR = { low:'#48BB78', mid:'#ED8936', high:'#E53E3E' }
const LEVEL_LABEL = { low:'低疑似',   mid:'中疑似',   high:'高疑似' }
const LEVEL_SOFT  = { low:'rgba(72,187,120,0.08)', mid:'rgba(237,137,54,0.08)', high:'rgba(229,62,62,0.08)' }
const LEVEL_BG    = { low:'#F0FFF4', mid:'#FFFAF0', high:'#FFF5F5' }
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

const ana   = computed(() => result.value?.analysis)
const lc    = computed(() => ana.value ? LEVEL_COLOR[ana.value.level] : '#8B7E6A')
const ls    = computed(() => ana.value ? LEVEL_SOFT[ana.value.level]  : 'transparent')
const lb    = computed(() => ana.value ? LEVEL_BG[ana.value.level]    : 'transparent')

async function submit() {
  error.value  = ''
  result.value = null
  if (!text.value.trim()) { error.value = '请粘贴招聘公告正文'; return }
  loading.value = true
  try {
    const resp = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text.value, source_url: sourceUrl.value || null }),
    })
    if (!resp.ok) throw new Error('分析失败，请稍后重试')
    result.value = await resp.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="submit-page">
    <header class="page-header">
      <h1 class="page-title">提交公告</h1>
      <p class="page-sub">粘贴事业单位 / 国企招聘公告，AI 分析其萝卜岗嫌疑</p>
    </header>

    <div class="form-card">
      <input
        v-model="sourceUrl"
        type="url"
        placeholder="公告原网址（选填）"
        class="url-input"
        :disabled="loading"
      />
      <textarea
        v-model="text"
        rows="12"
        placeholder="在此粘贴招聘公告正文……"
        class="text-input"
        :disabled="loading"
      ></textarea>
      <div class="form-actions">
        <span class="char-count">{{ text.length }} 字</span>
        <button class="submit-btn" :disabled="loading || !text.trim()" @click="submit">
          <span v-if="loading" class="btn-spin"></span>
          {{ loading ? '分析中…' : '🥕 开始分析' }}
        </button>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>

    <!-- Result -->
    <div v-if="result" class="result-section">
      <!-- Score hero -->
      <div class="result-hero" :style="{ '--lc': lc, '--ls': ls, '--lb': lb }">
        <div class="result-score-block">
          <div class="result-num">{{ ana.suspicion_score }}</div>
          <div class="result-track">
            <div class="result-fill" :style="{ width: ana.suspicion_score + '%' }"></div>
          </div>
        </div>
        <div class="result-meta">
          <span class="level-badge">{{ LEVEL_LABEL[ana.level] }}</span>
          <p class="result-pos">{{ result.position.org_name || '' }}
            {{ result.position.position_name ? '· ' + result.position.position_name : '' }}</p>
          <button class="view-detail-btn"
            @click="router.push('/analysis/' + ana.id)">
            查看完整报告 →
          </button>
        </div>
      </div>

      <!-- Features -->
      <div v-if="ana.hit_features?.length" class="result-block">
        <div class="block-label">命中特征</div>
        <div class="feat-tags">
          <span v-for="f in ana.hit_features" :key="f.key" class="feat-tag"
                :style="{ color: lc, background: ls }">
            {{ FEATURE_NAMES[f.key] || f.key }}
          </span>
        </div>
      </div>

      <!-- Reasoning -->
      <div v-if="ana.reasoning" class="result-block">
        <div class="block-label">分析理由</div>
        <p>{{ ana.reasoning }}</p>
      </div>

      <!-- Highlights -->
      <div v-if="ana.highlights?.length" class="result-block">
        <div class="block-label">可疑条款原文</div>
        <div v-for="(h, i) in ana.highlights" :key="i" class="highlight-row">
          <mark>{{ h.text }}</mark>
          <span class="hl-reason">{{ h.reason }}</span>
        </div>
      </div>
    </div>

    <footer class="page-footer">
      免责声明：AI 自动推测，仅供参考，不构成任何确定性结论，不针对任何具体单位或个人。
    </footer>
  </div>
</template>

<style scoped>
.submit-page {
  max-width: 760px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

.page-header { padding: 32px 0 20px; }
.page-title {
  font-family: var(--ff-display);
  font-size: 26px;
  font-weight: 600;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.page-sub { font-size: 12px; color: var(--text-3); letter-spacing: 0.04em; }

/* ── Form card ────────────────────────────────────────────── */
.form-card {
  margin-top: 20px;
  padding: 24px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.url-input {
  width: 100%;
  padding: 11px 16px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-family: var(--ff-body);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.url-input::placeholder { color: var(--text-3); }
.url-input:focus { border-color: var(--carrot-light); box-shadow: 0 0 0 3px rgba(237,137,54,0.1); }
.url-input:disabled { opacity: 0.5; }
.text-input {
  width: 100%;
  padding: 14px 16px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-family: var(--ff-body);
  font-size: 14px;
  line-height: 1.7;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.text-input::placeholder { color: var(--text-3); }
.text-input:focus { border-color: var(--carrot-light); box-shadow: 0 0 0 3px rgba(237,137,54,0.1); }
.text-input:disabled { opacity: 0.5; }

.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.char-count {
  font-family: var(--ff-mono);
  font-size: 11px;
  color: var(--text-3);
}
.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 26px;
  background: var(--carrot);
  color: #fff;
  border: none;
  border-radius: 24px;
  font-family: var(--ff-body);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(237,137,54,0.25);
  transition: opacity 0.2s, transform 0.15s, box-shadow 0.15s;
}
.submit-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }
.submit-btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(237,137,54,0.3);
}

@keyframes spin { to { transform: rotate(360deg); } }
.btn-spin {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.error-msg { font-size: 13px; color: var(--red); }

/* ── Result ───────────────────────────────────────────────── */
.result-section {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-hero {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px 28px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}
.result-hero::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 120px;
  background: linear-gradient(to right, var(--lb), transparent);
  pointer-events: none;
}

.result-score-block { flex-shrink: 0; text-align: center; position: relative; }
.result-num {
  font-family: var(--ff-mono);
  font-size: 56px;
  font-weight: 700;
  line-height: 1;
  color: var(--lc);
}
.result-track {
  width: 60px;
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  margin: 8px auto 0;
  overflow: hidden;
}
.result-fill { height: 100%; background: var(--lc); border-radius: 2px; }

.result-meta { flex: 1; position: relative; }
.level-badge {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 12px;
  background: var(--ls);
  font-size: 12px;
  font-weight: 600;
  color: var(--lc);
  margin-bottom: 8px;
}
.result-pos { font-size: 13px; color: var(--text-2); margin-bottom: 14px; }
.view-detail-btn {
  background: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-2);
  font-family: var(--ff-body);
  font-size: 12px;
  padding: 6px 14px;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}
.view-detail-btn:hover { border-color: var(--lc); color: var(--lc); }

/* Result blocks */
.result-block {
  padding: 16px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
}
.block-label {
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-3);
  margin-bottom: 10px;
  font-weight: 500;
}
.feat-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.feat-tag {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 12px;
  letter-spacing: 0.02em;
}
.result-block p { font-size: 14px; color: var(--text); line-height: 1.8; }

.highlight-row {
  padding: 8px 0;
  border-bottom: 1px solid var(--border-2);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.highlight-row:last-child { border-bottom: none; }
.highlight-row mark {
  background: rgba(237,137,54,0.12);
  color: var(--carrot-deep);
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 14px;
}
.hl-reason { font-size: 12px; color: var(--text-2); }

.page-footer {
  margin-top: 48px;
  font-size: 11px;
  color: var(--text-3);
  text-align: center;
  line-height: 1.8;
}
</style>
