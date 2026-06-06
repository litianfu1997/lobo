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
        <span class="logo-icon">🥕</span>
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
  /* ── Carrot warm palette — healing / fresh ── */
  --carrot:        #ED8936;
  --carrot-light:  #FBD38D;
  --carrot-deep:   #DD6B20;
  --carrot-soft:   #FFF8F0;

  /* ── Backgrounds ── */
  --bg:            #FBF7F0;
  --surface:       #FFFFFF;
  --surface-2:     #FFF9F2;
  --surface-3:     #FFF3E6;

  /* ── Borders ── */
  --border:        rgba(200,170,130,0.2);
  --border-2:      rgba(200,170,130,0.1);

  /* ── Suspicion levels ── */
  --red:           #E53E3E;
  --red-soft:      rgba(229,62,62,0.08);
  --amber:         #ED8936;
  --amber-soft:    rgba(237,137,54,0.08);
  --green:         #48BB78;
  --green-soft:    rgba(72,187,120,0.08);

  /* ── Text ── */
  --text:          #3D3228;
  --text-2:        #8B7E6A;
  --text-3:        #B8AD9E;

  /* ── Misc ── */
  --nav-h:         56px;
  --radius:        10px;
  --shadow-sm:     0 1px 3px rgba(120,90,50,0.06);
  --shadow-md:     0 4px 16px rgba(120,90,50,0.08);
  --shadow-lg:     0 8px 30px rgba(120,90,50,0.10);

  /* ── Typography ── */
  --ff-display: 'Noto Serif SC', 'Songti SC', 'SimSun', serif;
  --ff-mono:    'JetBrains Mono', 'Courier New', monospace;
  --ff-body:    'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
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
  background: rgba(251,247,240,0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text);
  transition: opacity 0.2s;
}
.logo:hover { opacity: 0.85; }

.logo-icon {
  font-size: 22px;
}

.logo-text {
  font-family: var(--ff-display);
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--carrot-deep);
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
  border-radius: 8px;
  transition: color 0.2s, background 0.2s;
}
.nav-link:hover { color: var(--text); background: var(--surface-3); }
.nav-link.active { color: var(--text); }

.submit-btn {
  display: inline-block;
  padding: 6px 16px;
  border: 1px solid var(--carrot-light);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--carrot-deep);
  letter-spacing: 0.03em;
  background: var(--carrot-soft);
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.nav-link:hover .submit-btn,
.nav-link.active .submit-btn {
  border-color: var(--carrot);
  background: rgba(237,137,54,0.12);
  box-shadow: 0 2px 8px rgba(237,137,54,0.15);
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
