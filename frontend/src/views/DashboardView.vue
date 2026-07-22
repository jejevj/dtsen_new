<template>
  <AppLayout>
    <div class="dash-wrapper">
      <div class="dash-content">
        <div v-if="datatableLoading" class="loading-overlay">
          <div class="loading-box">
            <i class="pi pi-spin pi-spinner"></i>
            <p>Memuat data...</p>
          </div>
        </div>
        <!-- Header -->
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;">
          <div>
            <h2 style="font-size:1.5rem;font-weight:800;color:#1e293b;margin:0 0 4px;">Dashboard</h2>
            <p style="font-size:13px;color:#64748b;margin:0;">
              Dashboard Analisis Pendistribusian dan Pendayagunaan <strong>{{ authStore.user?.user_fullname || authStore.user?.nama_lengkap || 'Pengguna' }}</strong>
              <span style="margin-left:8px;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;"
                :style="roleBadgeStyle">{{ authStore.user?.user_grup || authStore.user?.jabatan || 'operator' }}</span>
            </p>
            <p style="font-size:11px;color:#94a3b8;margin:4px 0 0;">
              Berdasarkan Data Baseline DTSEN dan Laporan Penerima Manfaat
            </p>
          </div>
          <!--
          <span style="background:#fef3c7;color:#92400e;padding:4px 12px;border-radius:8px;font-size:11px;font-weight:600;">PROTOTYPE · Data Simulasi</span>
          -->
        </div>

        <div class="bg-white border border-slate-200 rounded-2xl shadow-sm px-5 py-4">
          <div class="flex flex-wrap items-end gap-4">
            <div class="flex flex-col gap-1 flex-[3]" v-if="paramLembaga.length > 1">
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Lembaga</label>
              <Select
                v-model="selectedLembaga"
                :options="paramLembaga"
                optionLabel="nama"
                optionValue="kode"
                placeholder="Semua"
                class="w-full text-sm"
                filter show-clear
              />
            </div>
            <div class="flex flex-col gap-1 flex-1">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Tahun</label>
              <Select
                v-model="selectedYear"
                :options="paramTahun"
                optionLabel="tahun"
                optionValue="tahun"
                placeholder="Pilih"
                class="w-full text-sm"
                filter show-clear
              />
            </div>
            <div class="flex flex-col gap-1 flex-[3]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Provinsi</label>
              <Select
                v-model="selectedProvinsi"
                :options="paramProv"
                :loading="wilayahLoading"
                option-label="nama"
                option-value="kode"
                placeholder="Semua Provinsi"
                class="w-full text-sm"
                filter show-clear
                @change="optKabupaten"
              />
            </div>
            <div class="flex flex-col gap-1 flex-[3]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kabupaten / Kota</label>
              <Select
                v-model="selectedKabupaten"
                :options="paramKab"
                :loading="wilayahLoading"
                option-label="nama"
                option-value="kode"
                placeholder="Semua"
                class="w-full text-sm"
                filter show-clear
                @change="optKecamatan"
              />
            </div>
            <div class="flex flex-col gap-1 flex-[3]">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Kacamatan</label>
              <Select
                v-model="selectedKecamatan"
                :options="paramKec"
                :loading="wilayahLoading"
                option-label="nama"
                option-value="kode"
                placeholder="Semua"
                class="w-full text-sm"
                filter show-clear
              />
            </div>
            <div class="flex items-end gap-2">
              <Button
                label="Tampilkan" icon="pi pi-search" size="small"
                @click="loadData"
              />
              <Button
                label="Reset" icon="pi pi-times" size="small"
                severity="secondary" outlined
                @click="resetOption"
              />
            </div>
          </div>
        </div>     
        
        <div class="hero-grid" style="display:grid;gap:16px;">
          <div class="detail-card" style="display:flex;flex-direction:column;padding-left: 0px;padding-right: 0px;padding-bottom: 0px;">
            <p class="section-title" style="padding-left: 10px;padding-right: 10px;">
            <i class="pi pi-map"></i> Sebaran Mustahik Berdasarkan Data Baseline
            <span style="margin-left:auto;border-radius:99px;font-size:12px;font-weight:800;"
              :style="roleBadgeStyle">&ensp;{{ formatAngka(wilayahBase.length) }}&ensp;</span>
            </p>
            <template v-if="wilayahBase.length">
              <div style="overflow-x:auto;">
                <DataTable
                  stripedRows
                  showGridlines
                  paginator
                  paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
                  currentPageReportTemplate="{first} - {last} dari {totalRecords}"
                  responsiveLayout="scroll"
                  class="p-datatable-sm"
                  sortMode="single"
                  :loading="datatableLoading"
                  :value="wilayahBase"
                  :rows="10"
                  :rowsPerPageOptions="[10, 25, 50, 100]"
                  :first="no_wilayahBase"
                  @page="onPage_wilayahBase"
                >
                  <Column header="No" style="width:1%">
                    <template #body="slotProps">
                      <div class="text-center">
                        {{ no_wilayahBase + slotProps.index + 1 }}
                      </div>
                    </template>
                  </Column>

                  <Column header="Wilayah" field="nama" sortable >
                    <template #body="{ data }">
                      {{ data.nama ?? '-' }}
                    </template>
                  </Column>

                  <Column header="Mustahik" field="nama" sortable style="width:30%">
                    <template #body="{ data }">
                      <div class="text-right">
                        {{ formatAngka(data.baseline ?? 0) }}
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </template>
            <div v-else style="text-align:center;padding:30px;color:#94a3b8;font-size:12px;">
              <i class="pi pi-map" style="font-size:24px;display:block;margin-bottom:8px;"></i>
              Data Sebaran Mustahik Berdasarkan Data Baseline tidak ditemukan
            </div>
          </div>

          <div class="detail-card" style="display:flex;flex-direction:column;padding-left: 0px;padding-right: 0px;padding-bottom: 0px;">
            <p class="section-title" style="padding-left: 10px;padding-right: 10px;">
              <i class="pi pi-map"></i> Sebaran Mustahik per Desil Berdasarkan Data Baseline
              <span style="margin-left:auto;border-radius:99px;font-size:12px;font-weight:800;"
                :style="roleBadgeStyle">&ensp;{{ formatAngka(desilBase.length) }}&ensp;</span>
            </p>
            <template v-if="desilBase.length">
              <div style="overflow-x:auto;">
                <DataTable
                  stripedRows
                  showGridlines
                  paginator
                  paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
                  currentPageReportTemplate="{first} - {last} dari {totalRecords}"
                  responsiveLayout="scroll"
                  class="p-datatable-sm"
                  sortMode="single"
                  :loading="datatableLoading"
                  :value="desilBase"
                  :rows="10"
                  :rowsPerPageOptions="[10, 25, 50, 100]"
                  :first="no_desilBase"
                  @page="onPage_desilBase"
                >
                  <Column header="No" style="width:1%">
                    <template #body="slotProps">
                      <div class="text-center">
                        {{ no_desilBase + slotProps.index + 1 }}
                      </div>
                    </template>
                  </Column>

                  <Column field="nama" sortable header="Provinsi">
                    <template #body="{ data }">
                      {{ data.nama ?? '-' }}
                    </template>
                  </Column>

                  <Column field="desil_1" header="Desil 1" sortable>
                    <template #body="{ data }">
                      <div class="text-right">
                        {{ formatAngka(data.desil_1 ?? 0) }}
                      </div>
                    </template>
                  </Column>

                  <Column field="desil_1" header="Desil 2" sortable>
                    <template #body="{ data }">
                      <div class="text-right">
                        {{ formatAngka(data.desil_2 ?? 0) }}
                      </div>
                    </template>
                  </Column>

                  <Column field="desil_1" header="Desil 3" sortable>
                    <template #body="{ data }">
                      <div class="text-right">
                        {{ formatAngka(data.desil_3 ?? 0) }}
                      </div>
                    </template>
                  </Column>

                  <Column field="desil_1" header="Desil 4" sortable>
                    <template #body="{ data }">
                      <div class="text-right">
                        {{ formatAngka(data.desil_4 ?? 0) }}
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </template>
            <div v-else style="text-align:center;padding:30px;color:#94a3b8;font-size:12px;">
              <i class="pi pi-map" style="font-size:24px;display:block;margin-bottom:8px;"></i>
              Data Sebaran Mustahik per Desil Berdasarkan Data Baseline tidak ditemukan
            </div>
          </div>
          
        </div>

        <div class="detail-card" style="display:flex;flex-direction:column;padding-left: 0px;padding-right: 0px;padding-bottom: 0px;">
          <p class="section-title" style="padding-left: 10px;padding-right: 10px;">
            <i class="pi pi-map"></i> Pendistribusian dan Pendayagunaan per Wilayah
            <span style="margin-left:auto;border-radius:99px;font-size:12px;font-weight:800;"
              :style="roleBadgeStyle">&ensp;{{ formatAngka(wilayahData.length) }}&ensp;</span>
          </p>
          <template v-if="wilayahData.length">
            <div style="overflow-x:auto;">
              <DataTable
                stripedRows
                showGridlines
                paginator
                paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
                currentPageReportTemplate="{first} - {last} dari {totalRecords}"
                responsiveLayout="scroll"
                class="p-datatable-sm"
                sortMode="single"
                :loading="datatableLoading"
                :value="wilayahData"
                :rows="10"
                :rowsPerPageOptions="[10, 25, 50, 100]"
                :first="no_wilayahData"
                @page="onPage_wilayahData"
              >
                <Column header="No" style="width:1%">
                  <template #body="slotProps">
                    <div class="text-center">
                      {{ no_wilayahData + slotProps.index + 1 }}
                    </div>
                  </template>
                </Column>

                <Column field="lvl_1" sortable header="Provinsi">
                  <template #body="{ data }">
                    {{ data.lvl_1 ?? '-' }}
                  </template>
                </Column>

                <Column field="lvl_2" sortable header="Kab/kota">
                  <template #body="{ data }">
                    {{ data.lvl_2 ?? '-' }}
                  </template>
                </Column>

                <Column field="lvl_3" sortable header="Kecamatan">
                  <template #body="{ data }">
                    {{ data.lvl_3 ?? '-' }}
                  </template>
                </Column>

                <Column field="mustahik" header="Mustahik" sortable style="width:10%">
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.mustahik ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="rupiah" header="Total" sortable style="width:15%">
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatRupiah(data.rupiah ?? 0) }}
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </template>
          <div v-else style="text-align:center;padding:30px;color:#94a3b8;font-size:12px;">
            <i class="pi pi-map" style="font-size:24px;display:block;margin-bottom:8px;"></i>
            Data Pendistribusian dan Pendayagunaan per Wilayah tidak ditemukan
          </div>
        </div>

        <div class="detail-card" style="display:flex;flex-direction:column;padding-left: 0px;padding-right: 0px;padding-bottom: 0px;">
          <p class="section-title" style="padding-left: 10px;padding-right: 10px;">
            <i class="pi pi-map"></i> Pendistribusian dan Pendayagunaan per Desil
            <span style="margin-left:auto;border-radius:99px;font-size:12px;font-weight:800;"
              :style="roleBadgeStyle">&ensp;{{ formatAngka(desilData.length) }}&ensp;</span>
          </p>
          <template v-if="desilData.length">
            <div style="overflow-x:auto;">
              <DataTable
                stripedRows
                showGridlines
                paginator
                paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
                currentPageReportTemplate="{first} - {last} dari {totalRecords}"
                responsiveLayout="scroll"
                class="p-datatable-sm"
                sortMode="single"
                :loading="datatableLoading"
                :value="desilData"
                :rows="10"
                :rowsPerPageOptions="[10, 25, 50, 100]"
                :first="no_desilData"
                @page="onPage_desilData"
              >
                <Column header="No" style="width:1%">
                  <template #body="slotProps">
                    <div class="text-center">
                      {{ no_desilData + slotProps.index + 1 }}
                    </div>
                  </template>
                </Column>

                <Column field="nama" sortable header="Wilayah">
                  <template #body="{ data }">
                    {{ data.nama ?? '-' }}
                  </template>
                </Column>

                <Column field="desil_1" header="Desil 1" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_1 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_2" header="Desil 2" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_2 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_3" header="Desil 3" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_3 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_4" header="Desil 4" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_4 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_5" header="Desil 5" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_5 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_6" header="Desil 6" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_6 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_7" header="Desil 7" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_7 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_8" header="Desil 8" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_8 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_9" header="Desil 9" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_9 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_10" header="Desil 10" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_10 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column field="desil_na" header="N/A" sortable>
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.desil_na ?? 0) }}
                    </div>
                  </template>
                </Column>
                
              </DataTable>
            </div>
          </template>
          <div v-else style="text-align:center;padding:30px;color:#94a3b8;font-size:12px;">
            <i class="pi pi-map" style="font-size:24px;display:block;margin-bottom:8px;"></i>
            Data Sebaran Penerima Manfaat per Desil Berdasarkan Pendistribusian dan Pendayagunaan tidak ditemukan
          </div>
        </div>

        <!-- Desil breakdown cards -->
        <div>
          <!-- <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 12px;">Distribusi Mustahik per Desil</p> -->
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;" class="desil-grid">
            <div v-for="d in desilStats" :key="d.label"
              style="border-radius:14px;padding:18px;text-align:center;"
              :style="{ background:d.iconBg, border:`1px `, borderColor:black}">
              <p style="font-size:1.4rem;font-weight:900;letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px;" :style="{ color:d.iconColor}">Desil {{ d.label }}</p>
              <p style="font-size:1.4rem;font-weight:900;margin:0 0 2px;" :style="{ color:d.iconColor}">{{ d.base_val }}</p>
              <p style="font-size:11px;color:#64748b;margin:0 0 6px;">Mustahik Berdasarkan Data Baseline</p>
              <p style="font-size:1.4rem;font-weight:900;margin:0 0 2px;" :style="{ color:d.iconColor}">{{ d.lap_val }}</p>
              <p style="font-size:11px;color:#64748b;margin:0 0 6px;">Penerima Manfaat Lembaga</p>
              <p style="font-size:1.2rem;font-weight:600;margin:0;" :style="{ color:d.iconColor}">{{ d.agg_val }}</p>
              <p style="font-size:11px;color:#64748b;margin:0 0 6px;">Total Pendistribusian dan Pendayagunaan</p>
            </div>
          </div>
        </div>

        <!-- Stat Cards -->
        <div class="grid-1-2-1">
          <div v-for="stat in statCards" :key="stat.label" class="stat-card">
            <div :style="{ width:'44px', height:'44px', borderRadius:'12px', background:stat.iconBg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'14px' }">
              <i :class="stat.icon" :style="{ color:stat.iconColor, fontSize:'18px' }"></i>
            </div>
            <p style="font-size:1.5rem;font-weight:800;color:#1e293b;margin:0 0 3px;">{{ stat.value }}</p>
            <p style="font-size:13px;font-weight:600;color:#374151;margin:0 0 2px;">{{ stat.label }}</p>
            <p style="font-size:11px;color:#94a3b8;margin:0;">{{ stat.sub }}</p>
          </div>
        </div>

        <!-- Charts row -->
        <!-- key berubah saat lebar container berubah → Chart.js re-mount & resize otomatis -->
        <div style="display:grid;grid-template-columns:1fr 2fr;gap:16px;" class="chart-row">
          <div class="card-box">
            <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Gender Penerima</p>
            <Chart :key="'pie-'+chartKey" type="pie" :data="genderChartData" :options="pieOpts" style="height:200px;" />
            <div style="display:flex;gap:16px;justify-content:center;margin-top:12px;">
              <span style="font-size:12px;color:#374151;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#3b82f6;margin-right:5px;"></span>Laki-laki: {{ formatAngka(genderDataM) }}</span>
              <span style="font-size:12px;color:#374151;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f472b6;margin-right:5px;"></span>Perempuan: {{ formatAngka(genderDataF) }}</span>
            </div>
          </div>
          <div class="card-box">
            <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">Jumlah Penerima Manfaat per Desil</p>
            <Chart :key="'bar-'+chartKey" type="bar" :data="desilBarData" :options="barOpts" style="height:200px;" />
          </div>
        </div>

        <div class="detail-card" style="display:flex;flex-direction:column;padding-left: 0px;padding-right: 0px;">
          <p class="section-title" style="padding-left: 10px;padding-right: 10px;">
            <i class="pi pi-map"></i> Sebaran Penerima Manfaat Berdasarkan Usia
            <span style="margin-left:auto;font-size:11px;font-weight:500;color:#94a3b8;font-family:monospace;"></span>
          </p>
          <template v-if="usiaData.length">
            <div style="overflow-x:auto;">
              <DataTable
                stripedRows
                showGridlines
                paginator
                paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
                currentPageReportTemplate="{first} - {last} dari {totalRecords}"
                responsiveLayout="scroll"
                class="p-datatable-sm"
                sortMode="single"
                :loading="datatableLoading"
                :value="usiaData"
                :rows="10"
                :rowsPerPageOptions="[10, 25, 50, 100]"
                :first="no_usiaData"
                @page="onPage_usiaData"
              >
                <Column header="No" style="width:1%">
                  <template #body="slotProps">
                    <div class="text-center">
                      {{ no_usiaData + slotProps.index + 1 }}
                    </div>
                  </template>
                </Column>

                <Column header="Wilayah" field="nama" sortable >
                  <template #body="{ data }">
                    {{ data.nama ?? '-' }}
                  </template>
                </Column>

                <Column header="Usia 0 - 10" field="usia_1" sortable >
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.usia_1 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column header="Usia 11 - 20" field="usia_2" sortable >
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.usia_2 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column header="Usia 21 - 30" field="usia_3" sortable >
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.usia_3 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column header="Usia 31 - 40" field="usia_4" sortable >
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.usia_4 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column header="Usia 41 - 50" field="usia_5" sortable >
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.usia_5 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column header="Usia 51 - 60" field="usia_6" sortable >
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.usia_6 ?? 0) }}
                    </div>
                  </template>
                </Column>

                <Column header="Usia 60+" field="usia_7" sortable >
                  <template #body="{ data }">
                    <div class="text-right">
                      {{ formatAngka(data.usia_7 ?? 0) }}
                    </div>
                  </template>
                </Column>

              </DataTable>
            </div>
          </template>
          <div v-else style="text-align:center;padding:30px;color:#94a3b8;font-size:12px;">
            <i class="pi pi-map" style="font-size:24px;display:block;margin-bottom:8px;"></i>
            Data Sebaran Penerima Manfaat Berdasarkan Usia tidak ditemukan
          </div>
        </div>

        <!-- Sebaran Wilayah -->
        <!--
        <div class="card-box">
          <p style="font-size:13px;font-weight:700;color:#374151;margin:0 0 16px;">
            Sebaran Mustahik
            <span style="font-weight:400;color:#94a3b8;">per {{ wilayahGroupLabel }}</span>
          </p>
          <div v-if="stats.by_provinsi.length === 0" style="text-align:center;padding:32px;color:#94a3b8;font-size:13px;">
            Tidak ada data mustahik di wilayah ini.
          </div>
          <div v-else style="display:flex;gap:16px;flex-wrap:wrap;">
            <div v-for="p in stats.by_provinsi" :key="p.nama"
              style="flex:1;min-width:160px;background:#f8fafc;border-radius:10px;padding:14px;border:1px solid #e2e8f0;">
              <p style="font-size:12px;color:#64748b;margin:0 0 4px;">{{ p.nama }}</p>
              <p style="font-size:1.4rem;font-weight:800;color:#1e293b;margin:0;">{{ p.jumlah }}</p>
              <div style="margin-top:8px;background:#e2e8f0;border-radius:4px;height:6px;">
                <div :style="{ width: stats.total_mustahik ? (p.jumlah/stats.total_mustahik*100)+'%' : '0%', height:'6px', borderRadius:'4px', background:'#3b82f6' }"></div>
              </div>
            </div>
          </div>
        </div>
        -->

        <!-- Quick nav -->
        <!--
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;" class="quick-nav">
          <div v-for="nav in quickNav" :key="nav.label" class="nav-card" @click="$router.push(nav.to)">
            <div :style="{ width:'40px', height:'40px', borderRadius:'10px', background:nav.iconBg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'12px' }">
              <i :class="nav.icon" :style="{ color:nav.iconColor, fontSize:'17px' }"></i>
            </div>
            <p style="font-size:14px;font-weight:700;color:#1e293b;margin:0 0 2px;">{{ nav.label }}</p>
            <p style="font-size:12px;color:#94a3b8;margin:0;">{{ nav.desc }}</p>
          </div>
        </div>
        -->
        <div class="grid-3" style="display:grid;gap:16px;">
          <div
            v-for="(bidang, i) in bidangProgram"
            :key="bidang.bidang_label"
            style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,0.05);"
            :style="{ background:bidangColors[i%bidangColors.length].back, borderRadius:'16px', border:bidangColors[i%bidangColors.length].bordersize + ' solid ' + bidangColors[i%bidangColors.length].border, padding:'24px', boxShadow:'0 1px 4px rgba(0,0,0,0.05)' }"
          >
            <div :style="{ width:'44px', height:'44px', borderRadius:'12px', background:bidangColors[i%bidangColors.length].bg, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:'14px' }">
              <i :class="bidangIcons[i%bidangIcons.length]" :style="{ color:bidangColors[i%bidangColors.length].icon, fontSize:'18px' }"></i>
            </div>
            <h3 style="font-size:14px;font-weight:700;color:#1e293b;margin:0 0 4px;">{{ bidang.bidang_label }}</h3>
            <p style="font-size:1.3rem;font-weight:800;color:#15803d;margin:0 0 4px;">{{ formatRupiah(bidang.total_penyaluran) }}</p>
            <p style="font-size:11px;color:#94a3b8;margin:0 0 12px;">kepada {{ formatAngka(bidang.total_mustahik) }} Penerima Manfaat</p>
          </div>
        </div>

      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart      from 'primevue/chart'
import AppLayout  from '@/components/layout/AppLayout.vue'
import Button     from 'primevue/button'
import Select     from 'primevue/select'
import DataTable  from 'primevue/datatable'
import Column     from 'primevue/column'
import { useAuthStore } from '@/stores/auth'
import { formatShortM } from '@/utils/formatter'
import { formatRupiah } from '@/utils/formatter'
import { formatShort }  from '@/utils/formatter'
import { formatAngka }  from '@/utils/formatter'
import { DESIL_COLORS, getMockByWilayah, buildSummaryStats } from '@/data/mockMustahik'
import ReportService from '@/services/report'

const authStore = useAuthStore()
const userEmail = computed(() => {
  const u = authStore.user
  if (!u) return 'CONFIDENTIAL'
  return u.email || u.tuser_email || u.notelp || u.user_id || 'CONFIDENTIAL'
})

const selectedYear      = ref(new Date().getFullYear())
const wilayahLoading    = ref(false)
const datatableLoading  = ref(false)
const selectedLembaga   = ref(null)
const selectedProvinsi  = ref(null)
const selectedKabupaten = ref(null)
const selectedKecamatan = ref(null)

const paramLembaga  = ref([])
const paramTahun    = ref([])
const paramProv     = ref([])
const paramKab      = ref([])
const paramKec      = ref([])
const summary       = ref([])
const genderData    = ref([])
const bidangData    = ref([])
const usiaData      = ref([])
const trendData     = ref([])
const wilayahBase   = ref([])
const wilayahData   = ref([])
const desilBase     = ref([])
const desilData     = ref([])

const no_wilayahBase= ref(0)
const no_wilayahData= ref(0)
const no_desilBase  = ref(0)
const no_desilData  = ref(0)
const no_usiaData   = ref(0)

const onPage_wilayahBase = (event) => {
  no_wilayahBase.value = event.first
}
const onPage_wilayahData = (event) => {
  no_wilayahData.value = event.first
}
const onPage_desilBase = (event) => {
  no_desilBase.value = event.first
}
const onPage_desilData = (event) => {
  no_desilData.value = event.first
}
const onPage_usiaData = (event) => {
  no_usiaData.value = event.first
}

const mustahikData_desil = computed(() =>
  desilData.value.reduce((total, item) => total + (item.desil_1 || 0) + (item.desil_2 || 0) + (item.desil_3 || 0) + (item.desil_4 || 0), 0)
)

const mustahikData_all = computed(() =>
  desilData.value.reduce((total, item) => total + (item.desil_na || 0) + (item.desil_1 || 0) + (item.desil_2 || 0) + (item.desil_3 || 0) + (item.desil_4 || 0) + (item.desil_5 || 0) + (item.desil_6 || 0) + (item.desil_7 || 0) + (item.desil_8 || 0) + (item.desil_9 || 0) + (item.desil_10 || 0), 0)
)

const activeFilterCount = computed(() => {
  const drawerCount = Object.values(currentFilters.value).filter(v => v !== '' && v != null).length
  return drawerCount
})

onMounted(async () => {
  const params = { email: authStore.user.email, tahun: selectedYear.value }
  datatableLoading.value = true

  const [
    paramLembagaRes,
    paramTahunRes,
    paramProvRes,
    bidangRes,
    usiaRes,
    trendRes,
    basewilayahRes,
    datawilayahRes,
    basedesilRes,
    datadesilRes
  ] = await Promise.allSettled([
    ReportService.getDashParamLembaga(params),
    ReportService.getDashParamTahun(params),
    ReportService.getDashParamProv(params),
    ReportService.getDashDataBidang(params),
    ReportService.getDashDataUsia(params),
    ReportService.getDashTimeseries(params),
    ReportService.getDashBaseWilayah(params),
    ReportService.getDashDataWilayah(params),
    ReportService.getDashBaseDesil(params),
    ReportService.getDashDataDesil(params),
  ])

  datatableLoading.value = false

  if (paramLembagaRes.status === 'fulfilled')
    paramLembaga.value = paramLembagaRes.value

  if (paramTahunRes.status === 'fulfilled')
    paramTahun.value = paramTahunRes.value

  if (paramProvRes.status === 'fulfilled')
    paramProv.value = paramProvRes.value

  if (bidangRes.status === 'fulfilled')
    bidangData.value = bidangRes.value
  
  if (usiaRes.status === 'fulfilled')
    usiaData.value = usiaRes.value

  if (basewilayahRes.status === 'fulfilled')
    wilayahBase.value = basewilayahRes.value

  if (datawilayahRes.status === 'fulfilled')
    wilayahData.value = datawilayahRes.value

  if (basedesilRes.status === 'fulfilled')
    desilBase.value = basedesilRes.value

  if (datadesilRes.status === 'fulfilled')
    desilData.value = datadesilRes.value
/*
  if (paramProv.value.length === 1){
    selectedProvinsi.value = paramProv.value[0].kode
    await optKabupaten()
  }
*/
})

async function loadData() {
  const params = { 
    email: authStore.user.email, 
    tahun: selectedYear.value,
    provinsi_kode:  selectedProvinsi.value,
    kabkota_kode:   selectedKabupaten.value,
    kacamatan_kode: selectedKecamatan.value,
    lembaga: selectedLembaga.value
  }
  datatableLoading.value = true

  const [
    bidangRes,
    usiaRes,
    trendRes,
    basewilayahRes,
    datawilayahRes,
    basedesilRes,
    datadesilRes
  ] = await Promise.allSettled([
    ReportService.getDashDataBidang(params),
    ReportService.getDashDataUsia(params),
    ReportService.getDashTimeseries(params),
    ReportService.getDashBaseWilayah(params),
    ReportService.getDashDataWilayah(params),
    ReportService.getDashBaseDesil(params),
    ReportService.getDashDataDesil(params),
  ])
 
  if (bidangRes.status === 'fulfilled')
    bidangData.value = bidangRes.value
  
  if (usiaRes.status === 'fulfilled')
    usiaData.value = usiaRes.value

  if (basewilayahRes.status === 'fulfilled')
    wilayahBase.value = basewilayahRes.value

  if (datawilayahRes.status === 'fulfilled')
    wilayahData.value = datawilayahRes.value

  if (basedesilRes.status === 'fulfilled')
    desilBase.value = basedesilRes.value

  if (datadesilRes.status === 'fulfilled')
    desilData.value = datadesilRes.value

  datatableLoading.value = false
}

async function optKabupaten() {
  const params = { email: authStore.user.email, provinsi_kode: selectedProvinsi.value }
  wilayahLoading.value = true

  const [
    paramkabRes,
  ] = await Promise.allSettled([
    ReportService.getDashParamkab(params)
  ])
 
  if (paramkabRes.status === 'fulfilled'){
    paramKab.value = paramkabRes.value
    wilayahLoading.value = false
  }

  if (paramKab.value.length === 0){
    paramKab = ref([])
    paramKec = ref([])
  }
/*
  else if (paramKab.value.length === 1){
    selectedKabupaten.value = paramKab.value[0].kode
    await optKecamatan()
  }
*/
}

async function optKecamatan() {
  const params = { email: authStore.user.email, kabkota_kode: selectedKabupaten.value }
  wilayahLoading.value = true

  const [
    paramkecRes,
  ] = await Promise.allSettled([
    ReportService.getDashParamkec(params)
  ])
 
  if (paramkecRes.status === 'fulfilled'){
    paramKec.value = paramkecRes.value
    wilayahLoading.value = false
  }

  if (paramKec.value.length === 0)
    paramKec = ref([])
}

async function resetOption() {
  selectedProvinsi.value  = null
  selectedKabupaten.value = null
  selectedKecamatan.value = null
/*
  if (paramProv.value.length === 1){
    selectedProvinsi.value = paramProv.value[0].kode
    await optKabupaten()
  }

  if (paramKab.value.length === 1){
    selectedKabupaten.value = paramKab.value[0].kode
    await optKecamatan()
  }

  if (paramKec.value.length === 1)
    selectedKecamatan.value = paramKec.value[0].kode
*/
}

const desilStats = computed(() => [
  { 
    label:'Desil 1',  
    base_val:'' + formatAngka(desilBase.value.reduce((total, item) => total + Number(item.desil_1 || 0), 0)), base_sub:'Data DTSEN', 
    icon:'pi pi-users', iconBg:'#fcdcdc', iconColor:'#dc2626', 
    lap_val:'' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_1 || 0), 0)), 
    agg_val:'Rp ' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_sum_1 || 0), 0)), 
    lap_sub:'Penerima Manfaat Lembaga', agg_sub:'Pendistribusian dan Pendayagunaan' 
  },
  { 
    label:'Desil 2',  
    base_val:'' + formatAngka(desilBase.value.reduce((total, item) => total + Number(item.desil_2 || 0), 0)), base_sub:'Data DTSEN', 
    base_sub:'Data DTSEN', icon:'pi pi-users', iconBg:'#faeedc', iconColor:'#e68c05', 
    lap_val:'' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_2 || 0), 0)), 
    agg_val:'Rp ' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_sum_2 || 0), 0)), 
    lap_sub:'Penerima Manfaat Lembaga', agg_sub:'Pendistribusian dan Pendayagunaan' 
  },
  { 
    label:'Desil 3',  
    base_val:'' + formatAngka(desilBase.value.reduce((total, item) => total + Number(item.desil_3 || 0), 0)), base_sub:'Data DTSEN', 
    base_sub:'Data DTSEN', icon:'pi pi-users', iconBg:'#faf1d9', iconColor:'#f5be27', 
    lap_val:'' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_3 || 0), 0)), 
    agg_val:'Rp ' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_sum_3 || 0), 0)), 
    lap_sub:'Penerima Manfaat Lembaga', agg_sub:'Pendistribusian dan Pendayagunaan' 
  },
  { 
    label:'Desil 4',  
    base_val:'' + formatAngka(desilBase.value.reduce((total, item) => total + Number(item.desil_4 || 0), 0)), base_sub:'Data DTSEN', 
    base_sub:'Data DTSEN', icon:'pi pi-users', iconBg:'#f0fdf4', iconColor:'#16a34a', 
    lap_val:'' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_4 || 0), 0)), 
    agg_val:'Rp ' + formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_sum_4 || 0), 0)), 
    lap_sub:'Penerima Manfaat Lembaga', agg_sub:'Pendistribusian dan Pendayagunaan' 
  },
])

const desilBarData = computed(() => ({
  labels:['Desil 1','Desil 2','Desil 3','Desil 4'],
  datasets: [{
    label: 'Jumlah Mustahik',
    data: [
      desilData.value.reduce((total, item) => total + Number(item.desil_1 || 0), 0), 
      desilData.value.reduce((total, item) => total + Number(item.desil_2 || 0), 0), 
      desilData.value.reduce((total, item) => total + Number(item.desil_3 || 0), 0), 
      desilData.value.reduce((total, item) => total + Number(item.desil_4 || 0), 0), 
    ],
    backgroundColor: ['#ef4444','#f97316','#eab308','#22c55e'],
    borderRadius: 6,
  }],
}))

const statCards = computed(() => [
  { 
    label:'Penerima Manfaat',
    value: formatAngka(desilData.value.reduce((total, item) => total + Number(item.desil_all || 0), 0)),
    sub:'Seluruh Desil', icon:'pi pi-users', conBg:'#eff6ff', iconColor:'#2563eb' 
  },
  { 
    label:'Pendistribusian dan Pendayagunaan',
    value: formatRupiah(wilayahData.value.reduce((total, item) => total + Number(item.rupiah_all || 0), 0)),
    sub:'Total nilai bantuan pada seluruh Desil', icon:'pi pi-wallet', iconBg:'#faf5ff', iconColor:'#7c3aed' 
  },
  { 
    label:'Cakupan Wilayah',
    value: formatAngka(wilayahData.value.filter(item => item.mustahik !== 0).length) + '',
    sub: 'dari ' + formatAngka(wilayahBase.value.length) + ' wilayah pengajuan', 
    icon:'pi pi-map-marker', iconBg:'#fff7ed', iconColor:'#ea580c' },
])

const bidangProgram = computed(() => {
  const total = bidangData.value.reduce((s,b)=>s+(b.total_penyaluran||0),0)||1
  return bidangData.value.map(b=>({...b, pct:((b.total_penyaluran||0)/total)*100}))
})

const bidangChartData = computed(() => ({
  labels: bidangData.value.map(d=>d.bidang_label),
  datasets:[{ data:bidangData.value.map(d=>d.total_penyaluran||0), backgroundColor:'rgba(22,163,74,0.7)', borderRadius:4 }]
}))

const bidangColors = [
  { bg:'#c6fcd6', icon:'#16a34a', border:'#16a34a', bordersize:'3px', back:'#f0fdf4' },
  { bg:'#eff6ff', icon:'#2563eb', border:'#eff6ff', bordersize:'1px', back:'white' },
  { bg:'#fef2f2', icon:'#dc2626', border:'#eff6ff', bordersize:'1px', back:'white' },
  { bg:'#fafab6', icon:'#b9bd02', border:'#eff6ff', bordersize:'1px', back:'white' },
  { bg:'#faf5ff', icon:'#7c3aed', border:'#eff6ff', bordersize:'1px', back:'white' },
  { bg:'#fff7ed', icon:'#ea580c', border:'#eff6ff', bordersize:'1px', back:'white' },
]

const bidangIcons = ['pi pi-star','pi pi-users','pi pi-heart','pi pi-book','pi pi-chart-line','pi pi-shield','pi pi-briefcase','pi pi-home']

const genderDataM = computed(() => {
  return wilayahData.value.reduce((total, item) => total + Number(item.mustahik_m || 0), 0)
})

const genderDataF = computed(() => {
  return wilayahData.value.reduce((total, item) => total + Number(item.mustahik_f || 0), 0)
})

const genderChartData = computed(() => ({
  labels:['Laki-laki','Perempuan'],
  datasets:[
    { 
      data:[
        genderDataM, 
        genderDataF
      ], 
      backgroundColor:['#3b82f6','#ec4899'], 
      borderWidth:0 
    }
  ]
}))

const filteredData = computed(() => getMockByWilayah(authStore.userWilayah))
const stats        = computed(() => buildSummaryStats(filteredData.value))

const wilayahGroupLabel = computed(() => {
  const w = authStore.userWilayah
  if (!w || w.level === 'provinsi') return 'Provinsi'
  if (w.level === 'kab_kota')       return 'Kecamatan'
  return 'Wilayah'
})

const roleBadgeStyle = computed(() => {
  const role = authStore.user?.user_grup || authStore.user?.jabatan || ''
  const map = {
    admin:    { background:'#fef9c3', color:'#b45309' },
    operator: { background:'#dcfce7', color:'#15803d' },
    analis:   { background:'#dbeafe', color:'#1d4ed8' },
  }
  return map[role] || map.operator
})

const pieOpts = { plugins:{ legend:{ display:false } }, responsive:true, maintainAspectRatio:false }
const barOpts = {
  plugins:{ legend:{ display:false } },
  responsive:true, maintainAspectRatio:false,
  scales:{ y:{ beginAtZero:true, ticks:{ precision:0 } } },
}

const quickNav = [
  { label:'Data Mustahik', desc:'Lihat & filter daftar penerima', to:'/mustahik',   icon:'pi pi-users',  iconBg:'#eff6ff', iconColor:'#2563eb' },
  { label:'Cari Data',     desc:'Pencarian mustahik & filter NIK', to:'/cari-data', icon:'pi pi-search', iconBg:'#f0fdf4', iconColor:'#16a34a' },
  { label:'Beranda',       desc:'Kembali ke halaman publik',       to:'/',          icon:'pi pi-globe',  iconBg:'#fff7ed', iconColor:'#ea580c' },
]

// ── Fix: chart resize saat sidebar collapse ─────────────────────────────────
// ResizeObserver memantau lebar container. Setiap kali lebar berubah (saat
// sidebar expand/collapse), chartKey di-increment → Chart remount & fit ulang.
const dashContent = ref(null)
const chartKey    = ref(0)
let   ro          = null
let   prevWidth   = 0

onMounted(() => {
  if (!dashContent.value) return
  ro = new ResizeObserver((entries) => {
    const w = Math.round(entries[0].contentRect.width)
    if (w !== prevWidth) {
      prevWidth = w
      // Tunda sedikit agar transisi sidebar selesai dulu (300ms)
      setTimeout(() => { chartKey.value++ }, 320)
    }
  })
  ro.observe(dashContent.value)
})

onBeforeUnmount(() => {
  ro?.disconnect()
})
</script>

<style scoped>
.dash-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: #f8fafc;
}
.wm-overlay {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  user-select: none;
  -webkit-user-select: none;
}
.wm-svg {
  display: block;
  width: 100%;
  height: 100%;
}
.dash-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
:deep(.text-right) {
  text-align: right !important;
}
:deep(.p-datatable) {
  font-size: 12px;
}
:deep(.p-datatable-column-header-content),
:deep(.p-datatable .p-datatable-thead > tr > th){
  justify-content: center !important;
}
:deep(.p-datatable .p-datatable-thead > tr > th),
:deep(.p-datatable .p-datatable-tbody > tr > td),
:deep(.p-datatable .p-paginator) {
  font-size: 12px;
}
:deep(.p-paginator) {
  padding: 0px;
  font-size: 12px;
  justify-content: right !important;
  display: flex;
  align-items: center;
}
:deep(.p-paginator-current) {
  margin-right: auto; /* pindah ke kiri */
}
:deep(.p-paginator-prev),
:deep(.p-paginator-next) {
  margin-left: 0rem;
}
.hero-grid { display:grid; grid-template-columns:1fr 2fr; gap:48px; align-items:center; }
.detail-card { background:white; border-radius:14px; border:1px solid #f1f5f9; padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.section-title { font-size:13px; font-weight:700; color:#374151; margin:0 0 14px; display:flex; align-items:center; gap:6px; }
.kk-table { width:100%; border-collapse:collapse; font-size:12px; }
.kk-table tbody tr:not(.kk-active-row):hover .nik-link { color:#1d4ed8; }
.kk-table thead tr { background:#f8fafc; }
.kk-table th { padding:8px 10px; text-align:left; font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.4px; border-bottom:1px solid #f1f5f9; }
.kk-table td { padding:9px 10px; border-bottom:1px solid #f8fafc; color:#374151; font-weight:500; vertical-align:middle; }
.kk-table tr:last-child td { border-bottom:none; }
.kk-table tbody tr:hover td { background:#f8fafc; }
.text-center {text-align: center !important;}
.text-right {text-align: right !important;}
.td-label { font-size:12px; color:#94a3b8; font-weight:500; padding:9px 4px; width:45%; vertical-align:top; }
.td-value  { font-size:13px; color:#374151; font-weight:600; padding:9px 4px; text-align:right; }
.grid-2 { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }
.grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
.grid-4 { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.grid-1-2-1 { display: grid; grid-template-columns: 1fr 2fr 1fr; gap: 16px; }
.chart-row { grid-template-columns:1fr 2fr; }
.quick-nav { grid-template-columns:repeat(3,1fr); }
.stat-card {
  background:white; border-radius:16px; border:1px solid #f1f5f9;
  padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.card-box {
  background:white; border-radius:16px; border:1px solid #f1f5f9;
  padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.nav-card {
  background:white; border-radius:16px; border:1px solid #f1f5f9;
  padding:20px; box-shadow:0 1px 4px rgba(0,0,0,0.05);
  cursor:pointer; transition:box-shadow 0.2s;
}
.nav-card:hover { box-shadow:0 4px 16px rgba(0,0,0,0.1); }
.loading-overlay {
    position: absolute;
    inset: 0;
    background: rgba(255,255,255,.7);
    backdrop-filter: blur(2px);

    display: flex;
    justify-content: center;
    align-items: flex-start;

    z-index: 100;
    border-radius: 12px;
}

.loading-box {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: .75rem;
    background: #fff;
    margin-top: 50px;
    padding: 24px 32px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,.1);
}

.loading-box i {
    font-size: 2rem;
    color: #16a34a;
}

.loading-box p {
    margin: 0;
    color: #475569;
    font-size: 14px;
}
@media (max-width:1024px) {
  .grid-4    { grid-template-columns:repeat(2,1fr); }
  .grid-1-2-1 { grid-template-columns: 1fr 2fr; }
  .chart-row { grid-template-columns:1fr; }
  .desil-grid { grid-template-columns:repeat(2,1fr) !important; }
}
@media (max-width:640px) {
  .grid-4 { grid-template-columns:1fr 1fr; }
  .grid-3 { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
  .grid-1-2-1 { grid-template-columns: 1fr; }
  .quick-nav { grid-template-columns:1fr; }
  .desil-grid { grid-template-columns:repeat(2,1fr) !important; }
}
</style>
