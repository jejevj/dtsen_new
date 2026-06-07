from ..extensions import db
from sqlalchemy import text


class ReportService:
    @staticmethod
    def get_summary(params: dict) -> dict:
        # Placeholder — implementasi query sesuai filter
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
    def get_map_data(type_param: str) -> list:
        return []
