from ..extensions import db
from sqlalchemy import text

# Placeholder provinsi — 34 provinsi Indonesia dengan kode BPS
_PROVINSI_PLACEHOLDER = [
    {'provinsi_kode': '11', 'provinsi_nama': 'Aceh',                    'mustahik': 42000,  'penyaluran': 85000000000,  'laz_count': 3},
    {'provinsi_kode': '12', 'provinsi_nama': 'Sumatera Utara',           'mustahik': 78000,  'penyaluran': 210000000000, 'laz_count': 5},
    {'provinsi_kode': '13', 'provinsi_nama': 'Sumatera Barat',           'mustahik': 35000,  'penyaluran': 95000000000,  'laz_count': 3},
    {'provinsi_kode': '14', 'provinsi_nama': 'Riau',                     'mustahik': 29000,  'penyaluran': 75000000000,  'laz_count': 2},
    {'provinsi_kode': '15', 'provinsi_nama': 'Jambi',                    'mustahik': 18000,  'penyaluran': 42000000000,  'laz_count': 2},
    {'provinsi_kode': '16', 'provinsi_nama': 'Sumatera Selatan',         'mustahik': 45000,  'penyaluran': 110000000000, 'laz_count': 3},
    {'provinsi_kode': '17', 'provinsi_nama': 'Bengkulu',                 'mustahik': 12000,  'penyaluran': 28000000000,  'laz_count': 1},
    {'provinsi_kode': '18', 'provinsi_nama': 'Lampung',                  'mustahik': 52000,  'penyaluran': 120000000000, 'laz_count': 3},
    {'provinsi_kode': '19', 'provinsi_nama': 'Kepulauan Bangka Belitung','mustahik': 8000,   'penyaluran': 20000000000,  'laz_count': 1},
    {'provinsi_kode': '21', 'provinsi_nama': 'Kepulauan Riau',           'mustahik': 11000,  'penyaluran': 35000000000,  'laz_count': 1},
    {'provinsi_kode': '31', 'provinsi_nama': 'DKI Jakarta',              'mustahik': 95000,  'penyaluran': 850000000000, 'laz_count': 12},
    {'provinsi_kode': '32', 'provinsi_nama': 'Jawa Barat',               'mustahik': 320000, 'penyaluran': 780000000000, 'laz_count': 15},
    {'provinsi_kode': '33', 'provinsi_nama': 'Jawa Tengah',              'mustahik': 285000, 'penyaluran': 620000000000, 'laz_count': 13},
    {'provinsi_kode': '34', 'provinsi_nama': 'DI Yogyakarta',            'mustahik': 42000,  'penyaluran': 130000000000, 'laz_count': 4},
    {'provinsi_kode': '35', 'provinsi_nama': 'Jawa Timur',               'mustahik': 310000, 'penyaluran': 720000000000, 'laz_count': 14},
    {'provinsi_kode': '36', 'provinsi_nama': 'Banten',                   'mustahik': 88000,  'penyaluran': 210000000000, 'laz_count': 5},
    {'provinsi_kode': '51', 'provinsi_nama': 'Bali',                     'mustahik': 9000,   'penyaluran': 25000000000,  'laz_count': 1},
    {'provinsi_kode': '52', 'provinsi_nama': 'Nusa Tenggara Barat',      'mustahik': 65000,  'penyaluran': 145000000000, 'laz_count': 4},
    {'provinsi_kode': '53', 'provinsi_nama': 'Nusa Tenggara Timur',      'mustahik': 38000,  'penyaluran': 68000000000,  'laz_count': 2},
    {'provinsi_kode': '61', 'provinsi_nama': 'Kalimantan Barat',         'mustahik': 28000,  'penyaluran': 65000000000,  'laz_count': 2},
    {'provinsi_kode': '62', 'provinsi_nama': 'Kalimantan Tengah',        'mustahik': 15000,  'penyaluran': 38000000000,  'laz_count': 1},
    {'provinsi_kode': '63', 'provinsi_nama': 'Kalimantan Selatan',       'mustahik': 32000,  'penyaluran': 88000000000,  'laz_count': 3},
    {'provinsi_kode': '64', 'provinsi_nama': 'Kalimantan Timur',         'mustahik': 22000,  'penyaluran': 72000000000,  'laz_count': 2},
    {'provinsi_kode': '65', 'provinsi_nama': 'Kalimantan Utara',         'mustahik': 7000,   'penyaluran': 18000000000,  'laz_count': 1},
    {'provinsi_kode': '71', 'provinsi_nama': 'Sulawesi Utara',           'mustahik': 12000,  'penyaluran': 30000000000,  'laz_count': 1},
    {'provinsi_kode': '72', 'provinsi_nama': 'Sulawesi Tengah',          'mustahik': 22000,  'penyaluran': 48000000000,  'laz_count': 2},
    {'provinsi_kode': '73', 'provinsi_nama': 'Sulawesi Selatan',         'mustahik': 68000,  'penyaluran': 165000000000, 'laz_count': 5},
    {'provinsi_kode': '74', 'provinsi_nama': 'Sulawesi Tenggara',        'mustahik': 18000,  'penyaluran': 40000000000,  'laz_count': 2},
    {'provinsi_kode': '75', 'provinsi_nama': 'Gorontalo',                'mustahik': 10000,  'penyaluran': 22000000000,  'laz_count': 1},
    {'provinsi_kode': '76', 'provinsi_nama': 'Sulawesi Barat',           'mustahik': 9000,   'penyaluran': 19000000000,  'laz_count': 1},
    {'provinsi_kode': '81', 'provinsi_nama': 'Maluku',                   'mustahik': 15000,  'penyaluran': 32000000000,  'laz_count': 1},
    {'provinsi_kode': '82', 'provinsi_nama': 'Maluku Utara',             'mustahik': 12000,  'penyaluran': 26000000000,  'laz_count': 1},
    {'provinsi_kode': '91', 'provinsi_nama': 'Papua Barat',              'mustahik': 8000,   'penyaluran': 18000000000,  'laz_count': 1},
    {'provinsi_kode': '94', 'provinsi_nama': 'Papua',                    'mustahik': 18000,  'penyaluran': 38000000000,  'laz_count': 2},
]

# Placeholder kabkota — beberapa kabkota per provinsi
_KABKOTA_PLACEHOLDER = [
    # Jawa Barat (32)
    {'provinsi_kode': '32', 'kabkota_kode': '3201', 'kabkota_nama': 'Kab. Bogor',         'mustahik': 45000, 'penyaluran': 110000000000, 'laz_count': 4},
    {'provinsi_kode': '32', 'kabkota_kode': '3202', 'kabkota_nama': 'Kab. Sukabumi',      'mustahik': 28000, 'penyaluran': 65000000000,  'laz_count': 2},
    {'provinsi_kode': '32', 'kabkota_kode': '3203', 'kabkota_nama': 'Kab. Cianjur',       'mustahik': 22000, 'penyaluran': 48000000000,  'laz_count': 2},
    {'provinsi_kode': '32', 'kabkota_kode': '3204', 'kabkota_nama': 'Kab. Bandung',       'mustahik': 38000, 'penyaluran': 90000000000,  'laz_count': 3},
    {'provinsi_kode': '32', 'kabkota_kode': '3271', 'kabkota_nama': 'Kota Bogor',         'mustahik': 18000, 'penyaluran': 55000000000,  'laz_count': 2},
    {'provinsi_kode': '32', 'kabkota_kode': '3273', 'kabkota_nama': 'Kota Bandung',       'mustahik': 35000, 'penyaluran': 95000000000,  'laz_count': 4},
    {'provinsi_kode': '32', 'kabkota_kode': '3275', 'kabkota_nama': 'Kota Bekasi',        'mustahik': 42000, 'penyaluran': 115000000000, 'laz_count': 4},
    {'provinsi_kode': '32', 'kabkota_kode': '3276', 'kabkota_nama': 'Kota Depok',         'mustahik': 25000, 'penyaluran': 72000000000,  'laz_count': 2},
    # Jawa Tengah (33)
    {'provinsi_kode': '33', 'kabkota_kode': '3301', 'kabkota_nama': 'Kab. Cilacap',       'mustahik': 32000, 'penyaluran': 68000000000,  'laz_count': 2},
    {'provinsi_kode': '33', 'kabkota_kode': '3302', 'kabkota_nama': 'Kab. Banyumas',      'mustahik': 28000, 'penyaluran': 58000000000,  'laz_count': 2},
    {'provinsi_kode': '33', 'kabkota_kode': '3374', 'kabkota_nama': 'Kota Semarang',      'mustahik': 22000, 'penyaluran': 75000000000,  'laz_count': 3},
    {'provinsi_kode': '33', 'kabkota_kode': '3375', 'kabkota_nama': 'Kota Surakarta',     'mustahik': 15000, 'penyaluran': 42000000000,  'laz_count': 2},
    # Jawa Timur (35)
    {'provinsi_kode': '35', 'kabkota_kode': '3501', 'kabkota_nama': 'Kab. Pacitan',       'mustahik': 18000, 'penyaluran': 35000000000,  'laz_count': 1},
    {'provinsi_kode': '35', 'kabkota_kode': '3502', 'kabkota_nama': 'Kab. Ponorogo',      'mustahik': 22000, 'penyaluran': 45000000000,  'laz_count': 1},
    {'provinsi_kode': '35', 'kabkota_kode': '3578', 'kabkota_nama': 'Kota Surabaya',      'mustahik': 48000, 'penyaluran': 155000000000, 'laz_count': 5},
    {'provinsi_kode': '35', 'kabkota_kode': '3573', 'kabkota_nama': 'Kota Malang',        'mustahik': 25000, 'penyaluran': 65000000000,  'laz_count': 2},
    # DKI Jakarta (31)
    {'provinsi_kode': '31', 'kabkota_kode': '3171', 'kabkota_nama': 'Jakarta Pusat',      'mustahik': 18000, 'penyaluran': 180000000000, 'laz_count': 4},
    {'provinsi_kode': '31', 'kabkota_kode': '3172', 'kabkota_nama': 'Jakarta Utara',      'mustahik': 15000, 'penyaluran': 140000000000, 'laz_count': 3},
    {'provinsi_kode': '31', 'kabkota_kode': '3173', 'kabkota_nama': 'Jakarta Barat',      'mustahik': 20000, 'penyaluran': 165000000000, 'laz_count': 3},
    {'provinsi_kode': '31', 'kabkota_kode': '3174', 'kabkota_nama': 'Jakarta Selatan',    'mustahik': 22000, 'penyaluran': 185000000000, 'laz_count': 4},
    {'provinsi_kode': '31', 'kabkota_kode': '3175', 'kabkota_nama': 'Jakarta Timur',      'mustahik': 20000, 'penyaluran': 180000000000, 'laz_count': 4},
    # Sulawesi Selatan (73)
    {'provinsi_kode': '73', 'kabkota_kode': '7301', 'kabkota_nama': 'Kab. Selayar',       'mustahik': 6000,  'penyaluran': 12000000000,  'laz_count': 1},
    {'provinsi_kode': '73', 'kabkota_kode': '7371', 'kabkota_nama': 'Kota Makassar',      'mustahik': 32000, 'penyaluran': 85000000000,  'laz_count': 3},
    # Banten (36)
    {'provinsi_kode': '36', 'kabkota_kode': '3601', 'kabkota_nama': 'Kab. Pandeglang',    'mustahik': 18000, 'penyaluran': 38000000000,  'laz_count': 1},
    {'provinsi_kode': '36', 'kabkota_kode': '3671', 'kabkota_nama': 'Kota Tangerang',     'mustahik': 25000, 'penyaluran': 68000000000,  'laz_count': 2},
    {'provinsi_kode': '36', 'kabkota_kode': '3674', 'kabkota_nama': 'Kota Tangerang Sel.','mustahik': 22000, 'penyaluran': 72000000000,  'laz_count': 2},
]


class ReportService:
    @staticmethod
    def get_summary(params: dict) -> dict:
        return {'penerima_manfaat': 0, 'penyaluran': 0}

    @staticmethod
    def get_by_gender(params: dict) -> dict:
        return {'male_count': 0, 'female_count': 0, 'total': 0}

    @staticmethod
    def get_by_bidang(params: dict) -> list:
        return []

    @staticmethod
    def get_timeseries(params: dict) -> list:
        return []

    @staticmethod
    def get_desil_summary(params: dict) -> dict:
        return {str(i): 0 for i in range(11)}

    @staticmethod
    def get_tabulate(params: dict) -> dict:
        return {'data': [], 'meta': {}}

    @staticmethod
    def get_home_summary() -> dict:
        return {'total_penyaluran': 0, 'nasional': 0, 'provinsi': 0, 'kabkota': 0}

    @staticmethod
    def get_map_data(level: str, provinsi_kode: str = None) -> list:
        """Return placeholder map data.
        level='1' → per provinsi
        level='2' → per kabkota (filter by provinsi_kode jika diberikan)
        """
        if level == '2':
            data = _KABKOTA_PLACEHOLDER
            if provinsi_kode:
                data = [d for d in data if d['provinsi_kode'] == provinsi_kode]
            return data
        # Default level 1 — provinsi
        return _PROVINSI_PLACEHOLDER
