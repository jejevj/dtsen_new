<template>
  <footer style="background:#052e16; color:white; font-family:Inter,sans-serif;">
    <div style="max-width:1280px; margin:0 auto; padding:56px 24px 32px;">

      <!-- Top grid -->
      <div class="footer-grid" style="padding-bottom:40px; border-bottom:1px solid rgba(255,255,255,0.08);">

        <!-- Brand -->
        <div class="footer-brand">
          <!-- Logo -->
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
            <div
              style="width:36px;height:36px;border-radius:10px;background:#16a34a;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
              <i class="pi pi-chart-bar" style="color:white;font-size:14px;"></i>
            </div>
            <div>
              <div style="font-weight:700;font-size:16px;color:white;line-height:1;">DTSEN</div>
              <div style="font-size:11px;color:#86efac;margin-top:2px;line-height:1;">Zakat </div>
            </div>
          </div>

          <p style="font-size:13.5px;color:#a7f3d0;line-height:1.7;max-width:280px;margin:0 0 20px;">
            Platform pemantauan penyaluran zakat berbasis Data Tunggal Sosial Ekonomi Nasional (DTSEN). Transparan,
            terukur, tepat sasaran.
          </p>

          <!-- Badges -->
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <span v-for="badge in badges" :key="badge"
              style="padding:4px 12px;border-radius:99px;background:rgba(255,255,255,0.08);color:#a7f3d0;font-size:11px;font-weight:500;border:1px solid rgba(255,255,255,0.1);">{{
              badge }}</span>
          </div>
        </div>

        <!-- Navigasi -->
        <div>
          <h4
            style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#6ee7b7;margin:0 0 18px;">
            Navigasi</h4>
          <div style="display:flex;flex-direction:column;gap:10px;">
            <a v-for="item in footerLinks" :key="item.label" :href="item.href" class="footer-link"
              style="display:flex;align-items:center;gap:8px;font-size:13.5px;color:#a7f3d0;text-decoration:none;transition:color 0.15s;">
              <i :class="item.icon" style="font-size:11px;width:14px;text-align:center;color:#4ade80;"></i>
              {{ item.label }}
            </a>
          </div>
        </div>

        <!-- Kontak -->
        <div>
          <h4
            style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#6ee7b7;margin:0 0 18px;">
            Kontak</h4>
          <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:20px;">
            <div style="display:flex;align-items:flex-start;gap:8px;">
              <i class="pi pi-envelope" style="font-size:12px;color:#4ade80;margin-top:2px;flex-shrink:0;"></i>
              <span style="font-size:13px;color:#a7f3d0;line-height:1.5;">bimasislam@kemenag.go.id</span>
            </div>
            <div style="display:flex;align-items:flex-start;gap:8px;">
              <i class="pi pi-map-marker" style="font-size:12px;color:#4ade80;margin-top:2px;flex-shrink:0;"></i>
              <span style="font-size:13px;color:#a7f3d0;line-height:1.5;">Jl. M. H. Thamrin No.6 lantai 6, Jakarta Pusat
                10340</span>
            </div>
          </div>

          <!-- Social icons -->
          <div style="display:flex;gap:8px;">
            <a v-for="social in socials" :key="social.label" href="social.href" :title="social.label" class="social-btn"
              style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;transition:background 0.15s;text-decoration:none;">
              <i :class="social.icon" :style="{ fontSize: '13px', color: social.color }"></i>
            </a>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="footer-bottom"
        style="padding-top:24px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;">
        <span style="font-size:12px;color:#6ee7b7;">&copy; {{ year }} DTSEN &mdash; Hak Cipta Dilindungi</span>
        <div style="display:flex;flex-wrap:wrap;align-items:center;gap:16px;">
          <a href="#" class="footer-link" style="font-size:12px;color:#6ee7b7;text-decoration:none;">Kebijakan
            Privasi</a>
          <a href="#" class="footer-link" style="font-size:12px;color:#6ee7b7;text-decoration:none;">Syarat
            Penggunaan</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()

const badges = ['Kementerian Agama RI', 'BAZNAS', 'LAZ']

const footerLinks = [
  { label: 'Statistik Nasional', href: '#stats', icon: 'pi pi-chart-bar' },
  { label: 'Peta Sebaran', href: '#map', icon: 'pi pi-map' },
  { label: 'Program Zakat', href: '#program', icon: 'pi pi-list' },
  { label: 'Login Sistem', href: '/login', icon: 'pi pi-sign-in' },
]

const socials = [
  { icon: 'pi pi-instagram', color: '#ee2a7b ', label: 'Instagram', href: 'https://www.instagram.com/bimasislam/' },
  { icon: 'pi pi-twitter', color: '#38bdf8', label: 'Twitter', href: 'https://twitter.com/BimasIslam' },
  { icon: 'pi pi-facebook', color: '#1877F2', label: 'Facebook', href: 'https://www.facebook.com/Ditjen.Bimas.Islam' },
  // { icon: 'pi pi-github', color: '#ffffff', label: 'GitHub', href: '' },
  { icon: 'pi pi-youtube', color: '#f87171', label: 'YouTube', href: 'https://www.youtube.com/channel/UCMDwUz44x_O10PRlm_vsYog' },
]
</script>

<style scoped>
.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 48px;
}

.footer-link:hover {
  color: white !important;
}

.social-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  .footer-brand {
    grid-column: 1 / -1;
  }
}

@media (max-width: 480px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
