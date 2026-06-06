<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const isSubmit = computed(() => route.path === '/submit')
</script>

<template>
  <div id="root">
    <nav class="topnav">
      <RouterLink to="/" class="logo">
        <span class="logo-icon">⚖</span>
        <span class="logo-text">萝卜岗识别</span>
      </RouterLink>
      <div class="nav-links">
        <RouterLink to="/" class="nav-link" exact-active-class="active">案件库</RouterLink>
        <RouterLink to="/submit" class="nav-link" active-class="active">
          <span class="submit-btn">提交公告</span>
        </RouterLink>
      </div>
    </nav>
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </div>
</template>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #07070C;
  --surface: #0E0E16;
  --surface-2: #131320;
  --border: rgba(255,255,255,0.07);
  --border-2: rgba(255,255,255,0.04);

  --red: #E8192C;
  --red-soft: rgba(232,25,44,0.13);
  --amber: #E87820;
  --amber-soft: rgba(232,120,32,0.13);
  --teal: #12B89A;
  --teal-soft: rgba(18,184,154,0.13);

  --text: #DDD5C8;
  --text-2: #7A7585;
  --text-3: #3A3548;

  --nav-h: 56px;

  --ff-display: 'ZCOOL XiaoWei', 'Noto Serif SC', 'Songti SC', 'SimSun', serif;
  --ff-mono: 'Space Mono', 'Courier New', monospace;
  --ff-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--ff-body);
  font-size: 14px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}

#root { min-height: 100vh; }

/* ── Top Nav ─────────────────────────────────────────────── */
.topnav {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--nav-h);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  background: rgba(7,7,12,0.88);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text);
  transition: opacity 0.2s;
}
.logo:hover { opacity: 0.8; }

.logo-icon {
  font-size: 18px;
  opacity: 0.7;
}

.logo-text {
  font-family: var(--ff-display);
  font-size: 16px;
  letter-spacing: 0.04em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  text-decoration: none;
  color: var(--text-2);
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
}
.nav-link:hover { color: var(--text); background: var(--surface); }
.nav-link.active { color: var(--text); }

.submit-btn {
  display: inline-block;
  padding: 5px 14px;
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text);
  letter-spacing: 0.03em;
  transition: border-color 0.2s, background 0.2s;
}
.nav-link:hover .submit-btn,
.nav-link.active .submit-btn {
  border-color: var(--red);
  background: var(--red-soft);
  color: #FF5566;
}

/* ── Page Transitions ────────────────────────────────────── */
.page-enter-active, .page-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.page-enter-from { opacity: 0; transform: translateY(8px); }
.page-leave-to   { opacity: 0; transform: translateY(-6px); }

/* ── Shared utilities ────────────────────────────────────── */
a { color: inherit; }
</style>
