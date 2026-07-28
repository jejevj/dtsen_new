<template>
  <div class="maintenance-page">
    <div class="maintenance-card">
      <!-- Icon animasi gear -->
      <div class="icon-wrap">
        <svg class="gear-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M32 20a12 12 0 1 0 0 24 12 12 0 0 0 0-24zm0 20a8 8 0 1 1 0-16 8 8 0 0 1 0 16z"
            fill="currentColor"
          />
          <path
            d="M54.9 28.6l-3.5-.6a20.1 20.1 0 0 0-1.6-3.9l2.1-2.9a2 2 0 0 0-.2-2.6l-4.3-4.3a2 2 0 0 0-2.6-.2l-2.9 2.1a20 20 0 0 0-3.9-1.6l-.6-3.5A2 2 0 0 0 35.4 10h-6.8a2 2 0 0 0-2 1.7l-.6 3.5a20 20 0 0 0-3.9 1.6l-2.9-2.1a2 2 0 0 0-2.6.2l-4.3 4.3a2 2 0 0 0-.2 2.6l2.1 2.9a20.1 20.1 0 0 0-1.6 3.9l-3.5.6A2 2 0 0 0 8 30.6v6.8a2 2 0 0 0 1.7 2l3.5.6a20 20 0 0 0 1.6 3.9l-2.1 2.9a2 2 0 0 0 .2 2.6l4.3 4.3a2 2 0 0 0 2.6.2l2.9-2.1a20 20 0 0 0 3.9 1.6l.6 3.5a2 2 0 0 0 2 1.7h6.8a2 2 0 0 0 2-1.7l.6-3.5a20 20 0 0 0 3.9-1.6l2.9 2.1a2 2 0 0 0 2.6-.2l4.3-4.3a2 2 0 0 0 .2-2.6l-2.1-2.9a20.1 20.1 0 0 0 1.6-3.9l3.5-.6A2 2 0 0 0 56 37.4v-6.8a2 2 0 0 0-1.1-2z"
            fill="currentColor"
            opacity="0.35"
          />
        </svg>
      </div>

      <!-- Teks -->
      <h1 class="title">Sedang Pemeliharaan</h1>
      <p class="subtitle">
        {{ store.message || 'Sistem sedang dalam pemeliharaan. Silakan coba beberapa saat lagi.' }}
      </p>

      <!-- Dots animasi -->
      <div class="dots">
        <span /><span /><span />
      </div>

      <p class="hint">Tim kami sedang bekerja keras untuk segera menyelesaikannya.</p>
    </div>
  </div>
</template>

<script setup>
import { useMaintenanceStore } from '@/stores/maintenance'
const store = useMaintenanceStore()
</script>

<style scoped>
.maintenance-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8f5e9 100%);
  padding: 1.5rem;
  font-family: inherit;
}

.maintenance-card {
  background: #ffffff;
  border-radius: 1.5rem;
  padding: 3rem 2.5rem;
  max-width: 480px;
  width: 100%;
  text-align: center;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.06),
    0 16px 48px rgba(0, 0, 0, 0.08);
}

/* ── Icon ─────────────────────────────────────────── */
.icon-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 1.75rem;
}

.gear-icon {
  width: 80px;
  height: 80px;
  color: #2d7dd2;
  animation: spin 6s linear infinite;
  transform-origin: center;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* ── Teks ─────────────────────────────────────────── */
.title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 0.75rem;
  line-height: 1.2;
}

.subtitle {
  font-size: 1rem;
  color: #4a5568;
  margin: 0 0 2rem;
  line-height: 1.6;
}

.hint {
  font-size: 0.85rem;
  color: #a0aec0;
  margin: 1.5rem 0 0;
}

/* ── Dots loader ──────────────────────────────────── */
.dots {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #2d7dd2;
  animation: bounce 1.2s ease-in-out infinite;
}

.dots span:nth-child(1) { animation-delay: 0s; }
.dots span:nth-child(2) { animation-delay: 0.2s; }
.dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40%            { transform: scale(1);   opacity: 1; }
}

/* ── Reduced motion ───────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .gear-icon { animation: none; }
  .dots span  { animation: none; opacity: 0.7; }
}
</style>
