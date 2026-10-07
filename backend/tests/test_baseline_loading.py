import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from app.api.v1 import baseline
from app.utils.crypto import encrypt_identifier, decrypt_identifier


class BaselineLoadingTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_mustahik_accepts_frontend_token_without_padding(self):
        token = 'Lyzf_Zg9k5GBha9KlIeqWQ'
        nik = decrypt_identifier(token)
        self.assertRegex(nik, r'^\d{16}$')
        self.assertEqual(encrypt_identifier(nik).rstrip('='), token)
        with self.app.test_request_context(), patch.object(
            baseline.MustahikService, 'get_detail_by_nik', return_value={'data': []}
        ) as lookup:
            response, status = baseline.baseline_anggota_mustahik_hash.__wrapped__(token)
        self.assertEqual(status, 200)
        lookup.assert_called_once_with(nik)
        self.assertEqual(response.get_json(), {'data': []})

    def test_mustahik_rejects_invalid_tokens(self):
        for token in ('invalid!', encrypt_identifier('abc'), encrypt_identifier('123')):
            with self.subTest(token=token), self.app.test_request_context(), patch.object(
                baseline.MustahikService, 'get_detail_by_nik'
            ) as lookup:
                _, status = baseline.baseline_anggota_mustahik_hash.__wrapped__(token)
                self.assertEqual(status, 400)
                lookup.assert_not_called()

    def response(self, kind, total, cursor=''):
        query = MagicMock()
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        with self.app.test_request_context(
            f'/baseline/{kind}?provinsi=32&cursor={cursor}'
        ), patch.object(baseline, '_current_identity', return_value={'type': 'admin'}), \
                patch.object(baseline, '_allowed_provinsi_slugs', return_value=None), \
                patch.object(baseline, f'_build_{kind}_db_query', return_value=query), \
                patch.object(baseline, f'_count_{kind}_db_query', return_value=total):
            handler = getattr(baseline, f'baseline_{kind}')
            response, status = handler.__wrapped__()
        self.assertEqual(status, 200)
        return response.get_json()

    def test_first_page_has_total_and_next_cursor(self):
        for kind in ('anggota', 'keluarga'):
            with self.subTest(kind=kind):
                data = self.response(kind, baseline.DB_PAGE_SIZE + 1)
                self.assertEqual(data['meta']['currentPage'], 1)
                self.assertEqual(data['meta']['totalItems'], baseline.DB_PAGE_SIZE + 1)
                self.assertEqual(data['meta']['nextCursor'], 'db:page_2')

    def test_second_page(self):
        for kind in ('anggota', 'keluarga'):
            with self.subTest(kind=kind):
                data = self.response(kind, baseline.DB_PAGE_SIZE + 1, 'db:page_2')
                self.assertEqual(data['meta']['currentPage'], 2)
                self.assertTrue(data['meta']['hasPreviousPage'])
                self.assertFalse(data['meta']['hasNextPage'])

    def test_empty_results(self):
        for kind in ('anggota', 'keluarga'):
            with self.subTest(kind=kind):
                data = self.response(kind, 0)
                self.assertEqual(data['data'], [])
                self.assertEqual(data['meta']['totalItems'], 0)

    def test_anggota_query_accepts_and_derives_province_slug(self):
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        baseline.db.init_app(self.app)
        with self.app.app_context():
            for slug in (None, 'jabar'):
                query = baseline._build_anggota_db_query(
                    bps_kode='32', kabkota_filter=None, kecamatan_filter=None,
                    search='', provinsi_slug=slug,
                )
                self.assertIn('jabar', query.statement.compile().params.values())

    def test_province_access_preserves_scope(self):
        for codes, expected in ((None, None), ([], []), (['32'], ['jabar'])):
            with self.subTest(codes=codes), patch.object(
                baseline, '_allowed_provinsi_kodes', return_value=codes
            ):
                self.assertEqual(baseline._allowed_provinsi_slugs({}), expected)

    def test_member_wilayah_matches_plain_and_dotted_codes(self):
        filters = {
            'kode_provinsi_ktp': '11',
            'kode_kabupaten_kota_ktp': '1107',
            'kode_kecamatan_ktp': '110725',
        }
        item = dict(filters, kode_kabupaten_kota_ktp='11.07', kode_kecamatan_ktp='11.07.25')
        self.assertTrue(baseline._matches_anggota_wilayah(item, filters))
        for column in filters:
            with self.subTest(column=column):
                self.assertFalse(baseline._matches_anggota_wilayah(dict(item, **{column: '99'}), filters))
                self.assertFalse(baseline._matches_anggota_wilayah(dict(item, **{column: None}), filters))
        self.assertTrue(baseline._matches_anggota_wilayah({}, {}))

    def test_member_local_query_applies_all_wilayah_filters(self):
        anggota = MagicMock()
        anggota.query.filter_by.return_value.filter.return_value = anggota.query.filter_by.return_value
        anggota.query.filter_by.return_value.all.return_value = [object()]
        keluarga = MagicMock()
        with self.app.test_request_context(
            '/baseline/anggota/by-nkk?nkk=1107250801180001&provinsi=11&kabkota_kode=1107&kecamatan_kode=110725'
        ), patch.object(baseline, '_current_identity', return_value={'type': 'admin'}), \
                patch.object(baseline, 'ZawaAnggota', anggota), \
                patch.object(baseline, 'ZawaKeluarga', keluarga), \
                patch.object(baseline, '_kode_filter', return_value=True) as kode_filter, \
                patch.object(baseline, '_row_to_dict', return_value={'nomor_induk_kependudukan': '1107250801180002'}):
            response, status = baseline.baseline_anggota_by_nkk.__wrapped__()
        self.assertEqual(status, 200)
        self.assertEqual(response.get_json()['meta']['source'], 'local_db')
        self.assertEqual([call.args[1] for call in kode_filter.call_args_list], ['11', '1107', '110725'])


if __name__ == '__main__':
    unittest.main()
