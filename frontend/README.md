# Frontend — Vue.js 3 + Vite

## Stack
- Vue.js 3 (Composition API)
- Vite 5 (build tool)
- Vue Router 4 (routing)
- Pinia (state management)
- Axios (HTTP client)
- Tailwind CSS (styling)
- Chart.js + vue-chartjs (visualisasi data)
- Leaflet + vue-leaflet (peta interaktif)

## Struktur

```
frontend/
├── public/              # Static assets
├── src/
│   ├── assets/          # Images, fonts, global CSS
│   ├── components/      # Reusable components
│   │   ├── common/      # Button, Input, Modal, Table, Pagination
│   │   ├── charts/      # BarChart, LineChart, PieChart, MapChart
│   │   └── layout/      # Navbar, Sidebar, Footer
│   ├── views/           # Halaman utama (route-level components)
│   │   ├── HomeView.vue
│   │   ├── DashboardView.vue
│   │   ├── MustahikView.vue
│   │   ├── MustahikDetailView.vue
│   │   ├── ReportView.vue
│   │   └── LoginView.vue
│   ├── router/          # Vue Router config
│   │   └── index.js
│   ├── stores/          # Pinia stores
│   │   ├── auth.js
│   │   ├── mustahik.js
│   │   └── report.js
│   ├── services/        # Axios API calls
│   │   ├── api.js       # Axios instance + interceptors
│   │   ├── auth.js
│   │   ├── mustahik.js
│   │   └── report.js
│   ├── composables/     # Reusable Vue composables
│   │   ├── useFilter.js
│   │   └── usePagination.js
│   ├── utils/           # Helper functions
│   │   ├── formatter.js # Format currency, date, NIK
│   │   └── constants.js
│   ├── App.vue
│   └── main.js
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.js
```
