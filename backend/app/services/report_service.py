from ..models.report import Report
from datetime import datetime
from ..extensions import db
from sqlalchemy import text

class ReportService:
    @staticmethod
    def get_by_param_tahun(params: dict) -> list:
        return Report.get_param_tahun(params)

    @staticmethod
    def get_by_param_lembaga(params: dict) -> list:
        return Report.get_param_lembaga()
    
    @staticmethod
    def get_summary(params: dict) -> dict:
        bzn = Report.get_skala_bzn()
        laz = Report.get_skala_laz()
        desil_baseline = Report.get_desil_baseline()
        desil_mustahik = Report.get_desil_mustahik(params)
        total = Report.get_bidang(params)

        bzn_nasional_sub = sum((p.get('bzn_count') or 0) for p in (bzn or []) if p.get("skala") == 1)
        bzn_provinsi_sub = sum((p.get('bzn_count') or 0) for p in (bzn or []) if p.get("skala") == 2)
        bzn_kabkota_sub = sum((p.get('bzn_count') or 0) for p in (bzn or []) if p.get("skala") == 3)
        
        laz_nasional_sub = sum((p.get('laz_count') or 0) for p in (laz or []) if p.get("skala") == 1 and p.get("laz_status") in ("aktif", "daftar_ulang"))
        laz_provinsi_sub = sum((p.get('laz_count') or 0) for p in (laz or []) if p.get("skala") == 2 and p.get("laz_status") in ("aktif", "daftar_ulang"))
        laz_kabkota_sub = sum((p.get('laz_count') or 0) for p in (laz or []) if p.get("skala") == 3 and p.get("laz_status") in ("aktif", "daftar_ulang"))

        laz_nasional_ina = sum((p.get('laz_count') or 0) for p in (laz or []) if p.get("skala") == 1 and p.get("laz_status"))
        laz_provinsi_ina = sum((p.get('laz_count') or 0) for p in (laz or []) if p.get("skala") == 2 and p.get("laz_status"))
        laz_kabkota_ina = sum((p.get('laz_count') or 0) for p in (laz or []) if p.get("skala") == 3 and p.get("laz_status"))

        desil_1_sub = sum((p.get('nik_count') or 0) for p in (desil_baseline or []) if p.get("desil") == "1")
        desil_2_sub = sum((p.get('nik_count') or 0) for p in (desil_baseline or []) if p.get("desil") == "2")
        desil_3_sub = sum((p.get('nik_count') or 0) for p in (desil_baseline or []) if p.get("desil") == "3")
        desil_4_sub = sum((p.get('nik_count') or 0) for p in (desil_baseline or []) if p.get("desil") == "4")

        desil_1 = sum((p.get('nik_count') or 0) for p in (desil_mustahik or []) if p.get("desil") == 1)
        desil_2 = sum((p.get('nik_count') or 0) for p in (desil_mustahik or []) if p.get("desil") == 2)
        desil_3 = sum((p.get('nik_count') or 0) for p in (desil_mustahik or []) if p.get("desil") == 3)
        desil_4 = sum((p.get('nik_count') or 0) for p in (desil_mustahik or []) if p.get("desil") == 4)

        desil_1_agg = sum((p.get('rupiah') or 0) for p in (desil_mustahik or []) if p.get("desil") == 1)
        desil_2_agg = sum((p.get('rupiah') or 0) for p in (desil_mustahik or []) if p.get("desil") == 2)
        desil_3_agg = sum((p.get('rupiah') or 0) for p in (desil_mustahik or []) if p.get("desil") == 3)
        desil_4_agg = sum((p.get('rupiah') or 0) for p in (desil_mustahik or []) if p.get("desil") == 4)

        desil_all = sum((p.get('total_mustahik') or 0) for p in (total or []))
        desil_agg = sum((p.get('total_penyaluran') or 0) for p in (total or []))

        return {
            'bzn_nasional_sub': bzn_nasional_sub, 
            'bzn_provinsi_sub': bzn_provinsi_sub, 
            'bzn_kabkota_sub': bzn_kabkota_sub, 
            'laz_nasional_sub': laz_nasional_sub, 
            'laz_provinsi_sub': laz_provinsi_sub, 
            'laz_kabkota_sub': laz_kabkota_sub,
            'laz_nasional_ina': laz_nasional_ina,
            'laz_provinsi_ina': laz_provinsi_ina,
            'laz_kabkota_ina': laz_kabkota_ina,
            'desil_1': desil_1,
            'desil_2': desil_2,
            'desil_3': desil_3,
            'desil_4': desil_4,
            'desil_1_sub': desil_1_sub,
            'desil_2_sub': desil_2_sub,
            'desil_3_sub': desil_3_sub,
            'desil_4_sub': desil_4_sub,
            'desil_1_agg': desil_1_agg,
            'desil_2_agg': desil_2_agg,
            'desil_3_agg': desil_3_agg,
            'desil_4_agg': desil_4_agg,
            'desil_all': desil_all,
            'desil_agg': desil_agg
        }

    @staticmethod
    def get_by_gender(params: dict) -> dict:
        map_gender = Report.get_gender(params)
        male   =  next((x for x in map_gender if x["jenis_kelamin"] == "M"), {'mustahik': 0})
        female =  next((x for x in map_gender if x["jenis_kelamin"] == "F"), {'mustahik': 0})
        total_mustahik = int(male['mustahik']) + int(female['mustahik'])  
        return {'male_count': int(male['mustahik']), 'female_count': int(female['mustahik']), 'total': total_mustahik}

    @staticmethod
    def get_by_bidang(params: dict) -> list:
        return Report.get_bidang(params)

    @staticmethod
    def get_timeseries(params: dict) -> list:
        return Report.get_tren(params)

    @staticmethod
    def get_desil_summary(params: dict) -> dict:
        return {str(i): 0 for i in range(11)}

    @staticmethod
    def get_tabulate(params: dict) -> dict:
        return {'data': [], 'meta': {}}

    @staticmethod
    def get_map_data(params: dict) -> list:
        """
        level='1' → per provinsi
        level='2' → per kabkota (filter by provinsi_kode jika diberikan)
        level='3' → per kecamatan (filter by kabkota_kode, wajib)
        """
        
        provinsi_kode = params.get('provinsi_kode')
        kabkota_kode = params.get('kabkota_kode')
        tahun = params.get('tahun')

        if kabkota_kode != None:
            data = Report.get_map_kabkota({'tahun': tahun})
            if kabkota_kode:
                data = [d for d in data if d['kabkota_kode'] == kabkota_kode]
            return data
        elif provinsi_kode != None:
            data = Report.get_map_kabkota({'tahun': tahun})
            if provinsi_kode:
                data = [d for d in data if d['provinsi_kode'] == provinsi_kode]
            return data
        else:
            return Report.get_map_provinsi({'tahun': tahun})
    
    @staticmethod 
    def get_map_data_old(level: str, provinsi_kode: str = None, kabkota_kode: str = None, tahun: str = None) -> list:
        """
        level='1' → per provinsi
        level='2' → per kabkota (filter by provinsi_kode jika diberikan)
        level='3' → per kecamatan (filter by kabkota_kode, wajib)
        """
        if level == '3':
            data = Report.get_map_kabkota({'tahun': tahun})
            if kabkota_kode:
                data = [d for d in data if d['kabkota_kode'] == kabkota_kode]
            return data
        elif level == '2':
            data = Report.get_map_kabkota({'tahun': tahun})
            if provinsi_kode:
                data = [d for d in data if d['provinsi_kode'] == provinsi_kode]
            return data
        else:
            return Report.get_map_provinsi({'tahun': tahun})

# ==============================================================================================================================  
# DASHBOARD 
# ==============================================================================================================================

    @staticmethod
    def get_param_laz(params: dict) -> list:
        return Report.get_param_laz(params)
    
    @staticmethod
    def get_param_prov(params: dict) -> list:
        return Report.get_param_provinsi(params)
    
    @staticmethod
    def get_param_kab(params: dict) -> list:
        return Report.get_param_kabkota(params)
    
    @staticmethod
    def get_param_kec(params: dict) -> list:
        return Report.get_param_kecamatan(params)
    
    @staticmethod
    def get_baseline_wilayah(params: dict) -> list:
        return Report.get_baseline_wilayah(params)
    
    @staticmethod
    def get_data_wilayah(params: dict) -> list:
        return Report.get_data_wilayah(params)
    
    @staticmethod
    def get_baseline_desil(params: dict) -> list:
        return Report.get_baseline_desil(params)
    
    @staticmethod
    def get_data_desil(params: dict) -> list:
        return Report.get_data_desil(params)
    
    @staticmethod
    def get_data_bidang(params: dict) -> list:
        return Report.get_data_bidang(params)
    
    @staticmethod
    def get_data_usia(params: dict) -> list:
        return Report.get_data_usia(params)
