<script setup>
import { ref, computed } from 'vue'

const text = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)

const levelLabel = { low: '低疑似', mid: '中疑似', high: '高疑似' }
const levelColor = { low: '#16a34a', mid: '#d97706', high: '#dc2626' }

const score = computed(() => result.value?.analysis.suspicion_score ?? 0)
const level = computed(() => result.value?.analysis.level ?? 'low')

async function submit() {
  error.value = ''
  result.value = null
  if (!text.value.trim()) {
    error.value = '请粘贴招聘公告正文'
    return
  }
  loading.value = true
  try {
    const resp = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text.value }),
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
  <main class="wrap">
    <h1>萝卜岗识别</h1>
    <p class="sub">粘贴一份事业单位 / 国企招聘公告，AI 分析其"疑似萝卜岗"程度。</p>

    <textarea
      v-model="text"
      rows="10"
      placeholder="在此粘贴招聘公告正文……"
    ></textarea>
    <button :disabled="loading" @click="submit">
      {{ loading ? '分析中…' : '开始分析' }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>

    <section v-if="result" class="report">
      <div class="score" :style="{ borderColor: levelColor[level] }">
        <div class="num" :style="{ color: levelColor[level] }">{{ score }}</div>
        <div class="lvl" :style="{ color: levelColor[level] }">
          {{ levelLabel[level] }}
        </div>
      </div>

      <h3>分析理由</h3>
      <p>{{ result.analysis.reasoning }}</p>

      <h3 v-if="result.analysis.hit_features.length">命中的可疑特征</h3>
      <ul>
        <li v-for="(f, i) in result.analysis.hit_features" :key="i">
          <strong>{{ f.key }}</strong>：{{ f.evidence }}
          <em v-if="f.quote">（"{{ f.quote }}"）</em>
        </li>
      </ul>

      <h3 v-if="result.analysis.highlights.length">可疑条件原文</h3>
      <ul>
        <li v-for="(h, i) in result.analysis.highlights" :key="i">
          <mark>{{ h.text }}</mark> — {{ h.reason }}
        </li>
      </ul>
    </section>

    <footer class="disclaimer">
      免责声明：本结果由 AI 基于公开招聘文本自动推测，仅供参考，<strong>不构成任何确定性结论</strong>，
      不针对任何具体单位或个人。如有异议可申请纠错。
    </footer>
  </main>
</template>

<style>
body {
  margin: 0;
  font-family: system-ui, -apple-system, 'Microsoft YaHei', sans-serif;
  background: #f8fafc;
  color: #1e293b;
}

.wrap {
  max-width: 760px;
  margin: 0 auto;
  padding: 32px 20px;
}

h1 {
  margin-bottom: 4px;
}

.sub {
  color: #64748b;
  margin-top: 0;
}

textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 15px;
}

button {
  margin-top: 12px;
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #dc2626;
}

.report {
  margin-top: 24px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.score {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  border: 3px solid;
  border-radius: 12px;
}

.score .num {
  font-size: 40px;
  font-weight: 700;
  line-height: 1;
}

.score .lvl {
  font-size: 14px;
  margin-top: 4px;
}

mark {
  background: #fef08a;
  padding: 0 2px;
}

.disclaimer {
  margin-top: 28px;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.6;
}
</style>
