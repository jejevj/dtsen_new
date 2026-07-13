<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class ReportModel extends Model
{
    protected $table = 't_mustahik';

    public static function getSummaryWithFilter($params)
    {
        try {
            $query = self::query()
                ->selectRaw('COUNT(DISTINCT t_mustahik.nik) AS penerima_manfaat, SUM(t_mustahik.rupiah) AS penyaluran')

                // ================= JOIN =================
                ->leftJoin('t_laz', 't_mustahik.laz_kode', '=', 't_laz.laz_kode')
                ->leftJoin('t_program', 't_mustahik.program_kode', '=', 't_program.program_kode')
                ->leftJoin('m_bidang', 't_program.bidang_kode', '=', 'm_bidang.bidang_kode');

            // ================= LAZ =================
            $query->when(
                !empty($params['skala']),
                fn($q) =>
                $q->where('t_laz.skala', $params['skala'])
            );

            $query->when(
                !empty($params['nama_laz']),
                fn($q) =>
                $q->where('t_mustahik.laz_kode', $params['nama_laz'])
            );

            // ================= KTP =================
            $query->when(
                !empty($params['provinsi_ktp']),
                fn($q) =>
                $q->where('ktp_provinsi_kode', $params['provinsi_ktp'])
            );

            $query->when(
                !empty($params['kabupaten_ktp']),
                fn($q) =>
                $q->where('ktp_kabkota_kode', $params['kabupaten_ktp'])
            );

            $query->when(
                !empty($params['kecamatan_ktp']),
                fn($q) =>
                $q->where('ktp_kecamatan_kode', $params['kecamatan_ktp'])
            );

            $query->when(
                !empty($params['kelurahan_ktp']),
                fn($q) =>
                $q->where('ktp_kelurahan_kode', $params['kelurahan_ktp'])
            );

            $query->when(
                !empty($params['alamat_ktp']),
                fn($q) =>
                $q->where('ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%')
            );

            // ================= DOMISILI =================
            $query->when(
                !empty($params['provinsi_domisili']),
                fn($q) =>
                $q->where('provinsi_kode', $params['provinsi_domisili'])
            );

            $query->when(
                !empty($params['kabkota_domisili']),
                fn($q) =>
                $q->where('kabkota_kode', $params['kabkota_domisili'])
            );

            $query->when(
                !empty($params['kecamatan_domisili']),
                fn($q) =>
                $q->where('kecamatan_kode', $params['kecamatan_domisili'])
            );

            $query->when(
                !empty($params['kelurahan_domisili']),
                fn($q) =>
                $q->where('kelurahan_kode', $params['kelurahan_domisili'])
            );

            $query->when(
                !empty($params['alamat_domisili']),
                fn($q) =>
                $q->where('alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%')
            );

            // ================= BIODATA =================
            $query->when(
                !empty($params['nik']),
                fn($q) =>
                $q->where('t_mustahik.nik', (int) $params['nik'])
            );

            $query->when(
                !empty($params['nama']),
                fn($q) =>
                $q->where('nama_lengkap', 'LIKE', '%' . $params['nama'] . '%')
            );

            $query->when(
                !empty($params['agama']),
                fn($q) =>
                $q->where('agama', $params['agama'])
            );

            $query->when(
                !empty($params['jenis_kelamin']),
                fn($q) =>
                $q->where('jenis_kelamin', $params['jenis_kelamin'])
            );

            $query->when(
                !empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end']),
                fn($q) =>
                $q->whereBetween('lahir_tanggal', [
                    $params['tgl_lahir_start'],
                    $params['tgl_lahir_end']
                ])
            );

            $query->when(
                isset($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1,
                fn($q) =>
                $q->whereNotNull('ktp_berkas')
            );

            // ================= PROGRAM =================
            $query->when(
                !empty($params['bidang_kode']),
                fn($q) =>
                $q->where('m_bidang.bidang_kode', $params['bidang_kode'])
            );

            $query->when(
                !empty($params['nama_program']),
                fn($q) =>
                $q->where('t_program.program_nama', 'LIKE', '%' . $params['nama_program'] . '%')
            );

            $query->when(
                !empty($params['tipe_program']),
                fn($q) =>
                $q->where('t_mustahik.tipe_penerimaan', $params['tipe_program'])
            );

            $query->when(
                !empty($params['waktu_start']) && !empty($params['waktu_end']),
                fn($q) =>
                $q->whereBetween('t_mustahik.tanggal_terima', [
                    $params['waktu_start'],
                    $params['waktu_end']
                ])
            );

            $query->when(
                !empty($params['valueMin']) && !empty($params['valueMax']),
                fn($q) =>
                $q->whereBetween('t_mustahik.rupiah', [
                    $params['valueMin'],
                    $params['valueMax']
                ])
            );

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            $query->when(
                !empty($desilFilters),
                fn($q) =>
                $q->whereIn('t_mustahik.nik', function($subQuery) use ($desilFilters) {
                    $subQuery->select('nik')
                        ->from('t_mustahik_bappenas')
                        ->whereIn(DB::raw('COALESCE(desil, 0)'), $desilFilters);
                })
            );

            return $query->first();

        } catch (\Exception $e) {
            Log::error('Error fetching report summary: ' . $e->getMessage());

            return [
                'error' => 'Summary gagal diproses. Hubungi pengembang.',
            ];
        }
    }

    public static function getDataByGenderWithFilter($params)
    {
        try {
            $query = self::query()
                ->selectRaw('
                COUNT(DISTINCT CASE WHEN t_mustahik.jenis_kelamin = "m" THEN t_mustahik.nik END) AS male_count,
                COUNT(DISTINCT CASE WHEN t_mustahik.jenis_kelamin = "f" THEN t_mustahik.nik END) AS female_count,
                COUNT(DISTINCT t_mustahik.nik) AS total,
                SUM(t_mustahik.rupiah) AS penyaluran
            ')

                // ================= JOIN =================
                ->leftJoin('t_laz', 't_mustahik.laz_kode', '=', 't_laz.laz_kode')
                ->leftJoin('t_program', 't_mustahik.program_kode', '=', 't_program.program_kode')
                ->leftJoin('m_bidang', 't_program.bidang_kode', '=', 'm_bidang.bidang_kode');

            // ================= LAZ =================
            $query->when(
                !empty($params['skala']),
                fn($q) =>
                $q->where('t_laz.skala', $params['skala'])
            );

            $query->when(
                !empty($params['nama_laz']),
                fn($q) =>
                $q->where('t_mustahik.laz_kode', $params['nama_laz'])
            );

            // ================= KTP =================
            $query->when(
                !empty($params['provinsi_ktp']),
                fn($q) =>
                $q->where('ktp_provinsi_kode', $params['provinsi_ktp'])
            );

            $query->when(
                !empty($params['kabupaten_ktp']),
                fn($q) =>
                $q->where('ktp_kabkota_kode', $params['kabupaten_ktp'])
            );

            $query->when(
                !empty($params['kecamatan_ktp']),
                fn($q) =>
                $q->where('ktp_kecamatan_kode', $params['kecamatan_ktp'])
            );

            $query->when(
                !empty($params['kelurahan_ktp']),
                fn($q) =>
                $q->where('ktp_kelurahan_kode', $params['kelurahan_ktp'])
            );

            $query->when(
                !empty($params['alamat_ktp']),
                fn($q) =>
                $q->where('ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%')
            );

            // ================= DOMISILI =================
            $query->when(
                !empty($params['provinsi_domisili']),
                fn($q) =>
                $q->where('provinsi_kode', $params['provinsi_domisili'])
            );

            $query->when(
                !empty($params['kabkota_domisili']),
                fn($q) =>
                $q->where('kabkota_kode', $params['kabkota_domisili'])
            );

            $query->when(
                !empty($params['kecamatan_domisili']),
                fn($q) =>
                $q->where('kecamatan_kode', $params['kecamatan_domisili'])
            );

            $query->when(
                !empty($params['kelurahan_domisili']),
                fn($q) =>
                $q->where('kelurahan_kode', $params['kelurahan_domisili'])
            );

            $query->when(
                !empty($params['alamat_domisili']),
                fn($q) =>
                $q->where('alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%')
            );

            // ================= BIODATA =================
            $query->when(
                !empty($params['nik']),
                fn($q) =>
                $q->where('t_mustahik.nik', (int) $params['nik'])
            );

            $query->when(
                !empty($params['nama']),
                fn($q) =>
                $q->where('nama_lengkap', 'LIKE', '%' . $params['nama'] . '%')
            );

            $query->when(
                !empty($params['agama']),
                fn($q) =>
                $q->where('agama', $params['agama'])
            );

            $query->when(
                !empty($params['jenis_kelamin']),
                fn($q) =>
                $q->where('t_mustahik.jenis_kelamin', $params['jenis_kelamin'])
            );

            $query->when(
                !empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end']),
                fn($q) =>
                $q->whereBetween('lahir_tanggal', [
                    $params['tgl_lahir_start'],
                    $params['tgl_lahir_end']
                ])
            );

            $query->when(
                isset($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1,
                fn($q) =>
                $q->whereNotNull('ktp_berkas')
            );

            // ================= PROGRAM =================
            $query->when(
                !empty($params['bidang_kode']),
                fn($q) =>
                $q->where('m_bidang.bidang_kode', $params['bidang_kode'])
            );

            $query->when(
                !empty($params['nama_program']),
                fn($q) =>
                $q->where('t_program.program_nama', 'LIKE', '%' . $params['nama_program'] . '%')
            );

            $query->when(
                !empty($params['tipe_program']),
                fn($q) =>
                $q->where('t_mustahik.tipe_penerimaan', $params['tipe_program'])
            );

            $query->when(
                !empty($params['waktu_start']) && !empty($params['waktu_end']),
                fn($q) =>
                $q->whereBetween('t_mustahik.tanggal_terima', [
                    $params['waktu_start'],
                    $params['waktu_end']
                ])
            );

            $query->when(
                !empty($params['valueMin']) && !empty($params['valueMax']),
                fn($q) =>
                $q->whereBetween('t_mustahik.rupiah', [
                    $params['valueMin'],
                    $params['valueMax']
                ])
            );

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            $query->when(
                !empty($desilFilters),
                fn($q) =>
                $q->whereIn('t_mustahik.nik', function($subQuery) use ($desilFilters) {
                    $subQuery->select('nik')
                        ->from('t_mustahik_bappenas')
                        ->whereIn(DB::raw('COALESCE(desil, 0)'), $desilFilters);
                })
            );

            return $query->first();

        } catch (\Exception $e) {
            Log::error('Error fetching gender data: ' . $e->getMessage());

            return [
                'error' => 'Data gender gagal diproses. Hubungi pengembang.',
            ];
        }
    }

    public static function getPenyaluranByGenderWithFilter($params)
    {
        try {
            $query = self::query()
                ->selectRaw('
                SUM(CASE WHEN t_mustahik.jenis_kelamin = "m" THEN t_mustahik.rupiah ELSE 0 END) AS male_total_penyaluran,
                SUM(CASE WHEN t_mustahik.jenis_kelamin = "f" THEN t_mustahik.rupiah ELSE 0 END) AS female_total_penyaluran
            ')

                // ================= JOIN =================
                ->leftJoin('t_laz', 't_mustahik.laz_kode', '=', 't_laz.laz_kode')
                ->leftJoin('t_program', 't_mustahik.program_kode', '=', 't_program.program_kode')
                ->leftJoin('m_bidang', 't_program.bidang_kode', '=', 'm_bidang.bidang_kode');

            // ================= LAZ =================
            $query->when(
                !empty($params['skala']),
                fn($q) =>
                $q->where('t_laz.skala', $params['skala'])
            );

            $query->when(
                !empty($params['nama_laz']),
                fn($q) =>
                $q->where('t_mustahik.laz_kode', $params['nama_laz'])
            );

            // ================= KTP =================
            $query->when(
                !empty($params['provinsi_ktp']),
                fn($q) =>
                $q->where('ktp_provinsi_kode', $params['provinsi_ktp'])
            );

            $query->when(
                !empty($params['kabupaten_ktp']),
                fn($q) =>
                $q->where('ktp_kabkota_kode', $params['kabupaten_ktp'])
            );

            $query->when(
                !empty($params['kecamatan_ktp']),
                fn($q) =>
                $q->where('ktp_kecamatan_kode', $params['kecamatan_ktp'])
            );

            $query->when(
                !empty($params['kelurahan_ktp']),
                fn($q) =>
                $q->where('ktp_kelurahan_kode', $params['kelurahan_ktp'])
            );

            $query->when(
                !empty($params['alamat_ktp']),
                fn($q) =>
                $q->where('ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%')
            );

            // ================= DOMISILI =================
            $query->when(
                !empty($params['provinsi_domisili']),
                fn($q) =>
                $q->where('provinsi_kode', $params['provinsi_domisili'])
            );

            $query->when(
                !empty($params['kabkota_domisili']),
                fn($q) =>
                $q->where('kabkota_kode', $params['kabkota_domisili'])
            );

            $query->when(
                !empty($params['kecamatan_domisili']),
                fn($q) =>
                $q->where('kecamatan_kode', $params['kecamatan_domisili'])
            );

            $query->when(
                !empty($params['kelurahan_domisili']),
                fn($q) =>
                $q->where('kelurahan_kode', $params['kelurahan_domisili'])
            );

            $query->when(
                !empty($params['alamat_domisili']),
                fn($q) =>
                $q->where('alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%')
            );

            // ================= BIODATA =================
            $query->when(
                !empty($params['nik']),
                fn($q) =>
                $q->where('t_mustahik.nik', (int) $params['nik'])
            );

            $query->when(
                !empty($params['nama']),
                fn($q) =>
                $q->where('nama_lengkap', 'LIKE', '%' . $params['nama'] . '%')
            );

            $query->when(
                !empty($params['agama']),
                fn($q) =>
                $q->where('agama', $params['agama'])
            );

            $query->when(
                !empty($params['jenis_kelamin']),
                fn($q) =>
                $q->where('t_mustahik.jenis_kelamin', $params['jenis_kelamin'])
            );

            $query->when(
                !empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end']),
                fn($q) =>
                $q->whereBetween('lahir_tanggal', [
                    $params['tgl_lahir_start'],
                    $params['tgl_lahir_end']
                ])
            );

            $query->when(
                isset($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1,
                fn($q) =>
                $q->whereNotNull('ktp_berkas')
            );

            // ================= PROGRAM =================
            $query->when(
                !empty($params['bidang_kode']),
                fn($q) =>
                $q->where('m_bidang.bidang_kode', $params['bidang_kode'])
            );

            $query->when(
                !empty($params['nama_program']),
                fn($q) =>
                $q->where('t_program.program_nama', 'LIKE', '%' . $params['nama_program'] . '%')
            );

            $query->when(
                !empty($params['tipe_program']),
                fn($q) =>
                $q->where('t_mustahik.tipe_penerimaan', $params['tipe_program'])
            );

            $query->when(
                !empty($params['waktu_start']) && !empty($params['waktu_end']),
                fn($q) =>
                $q->whereBetween('t_mustahik.tanggal_terima', [
                    $params['waktu_start'],
                    $params['waktu_end']
                ])
            );

            $query->when(
                !empty($params['valueMin']) && !empty($params['valueMax']),
                fn($q) =>
                $q->whereBetween('t_mustahik.rupiah', [
                    $params['valueMin'],
                    $params['valueMax']
                ])
            );

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            $query->when(
                !empty($desilFilters),
                fn($q) =>
                $q->whereIn('t_mustahik.nik', function($subQuery) use ($desilFilters) {
                    $subQuery->select('nik')
                        ->from('t_mustahik_bappenas')
                        ->whereIn(DB::raw('COALESCE(desil, 0)'), $desilFilters);
                })
            );

            return $query->first();

        } catch (\Exception $e) {
            Log::error('Error fetching penyaluran by gender: ' . $e->getMessage());

            return [
                'error' => 'Penyaluran data gagal diproses. Hubungi pengembang.',
            ];
        }
    }


    public static function getPenyaluranByProgramWithFilter($params)
    {
        try {
            $query = DB::table('t_mustahik')
                ->selectRaw('
                SUM(CASE WHEN t_mustahik.tipe_penerimaan = "pml" THEN t_mustahik.rupiah ELSE 0 END) AS langsung_total,
                SUM(CASE WHEN t_mustahik.tipe_penerimaan = "pmtl" THEN t_mustahik.rupiah ELSE 0 END) AS tidak_langsung_total
            ')

                // ================= JOIN =================
                ->leftJoin('t_laz', 't_mustahik.laz_kode', '=', 't_laz.laz_kode')
                ->leftJoin('t_program', 't_mustahik.program_kode', '=', 't_program.program_kode')
                ->leftJoin('m_bidang', 't_program.bidang_kode', '=', 'm_bidang.bidang_kode');

            // ================= LAZ =================
            $query->when(
                !empty($params['skala']),
                fn($q) =>
                $q->where('t_laz.skala', $params['skala'])
            );

            $query->when(
                !empty($params['nama_laz']),
                fn($q) =>
                $q->where('t_mustahik.laz_kode', $params['nama_laz'])
            );

            // ================= KTP =================
            $query->when(
                !empty($params['provinsi_ktp']),
                fn($q) =>
                $q->where('ktp_provinsi_kode', $params['provinsi_ktp'])
            );

            $query->when(
                !empty($params['kabupaten_ktp']),
                fn($q) =>
                $q->where('ktp_kabkota_kode', $params['kabupaten_ktp'])
            );

            $query->when(
                !empty($params['kecamatan_ktp']),
                fn($q) =>
                $q->where('ktp_kecamatan_kode', $params['kecamatan_ktp'])
            );

            $query->when(
                !empty($params['kelurahan_ktp']),
                fn($q) =>
                $q->where('ktp_kelurahan_kode', $params['kelurahan_ktp'])
            );

            $query->when(
                !empty($params['alamat_ktp']),
                fn($q) =>
                $q->where('ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%')
            );

            // ================= DOMISILI =================
            $query->when(
                !empty($params['provinsi_domisili']),
                fn($q) =>
                $q->where('provinsi_kode', $params['provinsi_domisili'])
            );

            $query->when(
                !empty($params['kabkota_domisili']),
                fn($q) =>
                $q->where('kabkota_kode', $params['kabkota_domisili'])
            );

            $query->when(
                !empty($params['kecamatan_domisili']),
                fn($q) =>
                $q->where('kecamatan_kode', $params['kecamatan_domisili'])
            );

            $query->when(
                !empty($params['kelurahan_domisili']),
                fn($q) =>
                $q->where('kelurahan_kode', $params['kelurahan_domisili'])
            );

            $query->when(
                !empty($params['alamat_domisili']),
                fn($q) =>
                $q->where('alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%')
            );

            // ================= BIODATA =================
            $query->when(
                !empty($params['nik']),
                fn($q) =>
                $q->where('t_mustahik.nik', (int) $params['nik'])
            );

            $query->when(
                !empty($params['nama']),
                fn($q) =>
                $q->where('nama_lengkap', 'LIKE', '%' . $params['nama'] . '%')
            );

            $query->when(
                !empty($params['agama']),
                fn($q) =>
                $q->where('agama', $params['agama'])
            );

            $query->when(
                !empty($params['jenis_kelamin']),
                fn($q) =>
                $q->where('jenis_kelamin', $params['jenis_kelamin'])
            );

            $query->when(
                !empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end']),
                fn($q) =>
                $q->whereBetween('lahir_tanggal', [
                    $params['tgl_lahir_start'],
                    $params['tgl_lahir_end']
                ])
            );

            $query->when(
                isset($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1,
                fn($q) =>
                $q->whereNotNull('ktp_berkas')
            );

            // ================= PROGRAM =================
            $query->when(
                !empty($params['bidang_kode']),
                fn($q) =>
                $q->where('m_bidang.bidang_kode', $params['bidang_kode'])
            );

            $query->when(
                !empty($params['nama_program']),
                fn($q) =>
                $q->where('t_program.program_nama', 'LIKE', '%' . $params['nama_program'] . '%')
            );

            $query->when(
                !empty($params['tipe_program']),
                fn($q) =>
                $q->where('t_mustahik.tipe_penerimaan', $params['tipe_program'])
            );

            $query->when(
                !empty($params['waktu_start']) && !empty($params['waktu_end']),
                fn($q) =>
                $q->whereBetween('t_mustahik.tanggal_terima', [
                    $params['waktu_start'],
                    $params['waktu_end']
                ])
            );

            $query->when(
                !empty($params['valueMin']) && !empty($params['valueMax']),
                fn($q) =>
                $q->whereBetween('t_mustahik.rupiah', [
                    $params['valueMin'],
                    $params['valueMax']
                ])
            );

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            $query->when(
                !empty($desilFilters),
                fn($q) =>
                $q->whereIn('t_mustahik.nik', function($subQuery) use ($desilFilters) {
                    $subQuery->select('nik')
                        ->from('t_mustahik_bappenas')
                        ->whereIn(DB::raw('COALESCE(desil, 0)'), $desilFilters);
                })
            );

            return $query->first();

        } catch (\Exception $e) {
            \Log::error('Error fetching penyaluran data by program: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the penyaluran data. Please try again later.',
            ];
        }
    }

    public static function getPenyaluranByBidangWithFilter($params)
    {
        try {
            $query = DB::table('t_mustahik as a')
                ->select(
                    'mb.bidang_label',
                    DB::raw('SUM(a.rupiah) AS total_penyaluran')
                )
                ->leftJoin('t_program as t', 'a.program_kode', '=', 't.program_kode')
                ->leftJoin('m_bidang as mb', 't.bidang_kode', '=', 'mb.bidang_kode')
                ->leftJoin('t_laz', 'a.laz_kode', '=', 't_laz.laz_kode')
                ->groupBy('mb.bidang_label');

            // ================= LAZ =================
            $query->when(
                !empty($params['skala']),
                fn($q) =>
                $q->where('t_laz.skala', $params['skala'])
            );

            $query->when(
                !empty($params['nama_laz']),
                fn($q) =>
                $q->where('a.laz_kode', $params['nama_laz'])
            );

            // ================= KTP =================
            $query->when(
                !empty($params['provinsi_ktp']),
                fn($q) =>
                $q->where('a.ktp_provinsi_kode', $params['provinsi_ktp'])
            );

            $query->when(
                !empty($params['kabupaten_ktp']),
                fn($q) =>
                $q->where('a.ktp_kabkota_kode', $params['kabupaten_ktp'])
            );

            $query->when(
                !empty($params['kecamatan_ktp']),
                fn($q) =>
                $q->where('a.ktp_kecamatan_kode', $params['kecamatan_ktp'])
            );

            $query->when(
                !empty($params['kelurahan_ktp']),
                fn($q) =>
                $q->where('a.ktp_kelurahan_kode', $params['kelurahan_ktp'])
            );

            $query->when(
                !empty($params['alamat_ktp']),
                fn($q) =>
                $q->where('a.ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%')
            );

            // ================= DOMISILI =================
            $query->when(
                !empty($params['provinsi_domisili']),
                fn($q) =>
                $q->where('a.provinsi_kode', $params['provinsi_domisili'])
            );

            $query->when(
                !empty($params['kabkota_domisili']),
                fn($q) =>
                $q->where('a.kabkota_kode', $params['kabkota_domisili'])
            );

            $query->when(
                !empty($params['kecamatan_domisili']),
                fn($q) =>
                $q->where('a.kecamatan_kode', $params['kecamatan_domisili'])
            );

            $query->when(
                !empty($params['kelurahan_domisili']),
                fn($q) =>
                $q->where('a.kelurahan_kode', $params['kelurahan_domisili'])
            );

            $query->when(
                !empty($params['alamat_domisili']),
                fn($q) =>
                $q->where('a.alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%')
            );

            // ================= BIODATA =================
            $query->when(
                !empty($params['nik']),
                fn($q) =>
                $q->where('a.nik', (int) $params['nik'])
            );

            $query->when(
                !empty($params['nama']),
                fn($q) =>
                $q->where('a.nama_lengkap', 'LIKE', '%' . $params['nama'] . '%')
            );

            $query->when(
                !empty($params['agama']),
                fn($q) =>
                $q->where('a.agama', $params['agama'])
            );

            $query->when(
                !empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end']),
                fn($q) =>
                $q->whereBetween('a.lahir_tanggal', [$params['tgl_lahir_start'], $params['tgl_lahir_end']])
            );

            $query->when(
                !empty($params['jenis_kelamin']),
                fn($q) => $q->where('a.jenis_kelamin', $params['jenis_kelamin'])
            );

            $query->when(
                isset($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1,
                fn($q) => $q->whereNotNull('a.ktp_berkas')
            );

            // ================= PROGRAM =================
            $query->when(
                !empty($params['bidang_kode']),
                fn($q) =>
                $q->where('mb.bidang_kode', $params['bidang_kode'])
            );

            $query->when(
                !empty($params['nama_program']),
                fn($q) =>
                $q->where('t.program_nama', 'LIKE', '%' . $params['nama_program'] . '%')
            );

            $query->when(
                !empty($params['tipe_program']),
                fn($q) =>
                $q->where('a.tipe_penerimaan', $params['tipe_program'])
            );

            $query->when(
                !empty($params['waktu_start']) && !empty($params['waktu_end']),
                fn($q) =>
                $q->whereBetween('a.tanggal_terima', [$params['waktu_start'], $params['waktu_end']])
            );

            $query->when(
                !empty($params['valueMin']) && !empty($params['valueMax']),
                fn($q) =>
                $q->whereBetween('a.rupiah', [$params['valueMin'], $params['valueMax']])
            );

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            $query->when(
                !empty($desilFilters),
                fn($q) =>
                $q->whereIn('a.nik', function($subQuery) use ($desilFilters) {
                    $subQuery->select('nik')
                        ->from('t_mustahik_bappenas')
                        ->whereIn(DB::raw('COALESCE(desil, 0)'), $desilFilters);
                })
            );

            return $query->get();

        } catch (\Exception $e) {
            \Log::error('Error fetching penyaluran data by bidang: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the penyaluran data by bidang. Please try again later.',
            ];
        }
    }


    public static function getTimeSeriesDataWithFilter($params)
    {
        try {
            $query = DB::table('t_mustahik as a')
                ->select(
                    DB::raw('YEAR(a.created_at) AS tahun'),
                    DB::raw('COALESCE(SUM(CASE WHEN a.tipe_penerimaan = "pml" THEN a.rupiah ELSE 0 END), 0) AS Bantuan_Langsung'),
                    DB::raw('COALESCE(SUM(CASE WHEN a.tipe_penerimaan = "pmtl" THEN a.rupiah ELSE 0 END), 0) AS Bantuan_Tidak_Langsung')
                )
                ->leftJoin('t_program as p', 'a.program_kode', '=', 'p.program_kode')
                ->leftJoin('t_laz', 'a.laz_kode', '=', 't_laz.laz_kode')
                ->leftJoin('m_bidang as mb', 'p.bidang_kode', '=', 'mb.bidang_kode');

            // Filters for program / laz
            if (!empty($params['skala'])) {
                $query->where('t_laz.skala', $params['skala']);
            }
            if (!empty($params['nama_laz'])) {
                $query->where('a.laz_kode', $params['nama_laz']);
            }

            // Filters for KTP / address
            if (!empty($params['provinsi_ktp'])) {
                $query->where('a.ktp_provinsi_kode', $params['provinsi_ktp']);
            }
            if (!empty($params['kabupaten_ktp'])) {
                $query->where('a.ktp_kabkota_kode', $params['kabupaten_ktp']);
            }
            if (!empty($params['kecamatan_ktp'])) {
                $query->where('a.ktp_kecamatan_kode', $params['kecamatan_ktp']);
            }
            if (!empty($params['kelurahan_ktp'])) {
                $query->where('a.ktp_kelurahan_kode', $params['kelurahan_ktp']);
            }
            if (!empty($params['alamat_ktp'])) {
                $query->where('a.ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%');
            }

            // Filters for domisili
            if (!empty($params['provinsi_domisili'])) {
                $query->where('a.provinsi_kode', $params['provinsi_domisili']);
            }
            if (!empty($params['kabkota_domisili'])) {
                $query->where('a.kabkota_kode', $params['kabkota_domisili']);
            }
            if (!empty($params['kecamatan_domisili'])) {
                $query->where('a.kecamatan_kode', $params['kecamatan_domisili']);
            }
            if (!empty($params['kelurahan_domisili'])) {
                $query->where('a.kelurahan_kode', $params['kelurahan_domisili']);
            }
            if (!empty($params['alamat_domisili'])) {
                $query->where('a.alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%');
            }

            // Filters for personal info
            if (!empty($params['nik'])) {
                $query->where('a.nik', (int) $params['nik']);
            }
            if (!empty($params['nama'])) {
                $query->where('a.nama_lengkap', $params['nama']);
            }
            if (!empty($params['agama'])) {
                $query->where('a.agama', $params['agama']);
            }
            if (!empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end'])) {
                $query->whereBetween('a.lahir_tanggal', [$params['tgl_lahir_start'], $params['tgl_lahir_end']]);
            }
            if (!empty($params['jenis_kelamin'])) {
                $query->where('a.jenis_kelamin', $params['jenis_kelamin']);
            }
            if (!empty($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1) {
                $query->whereNotNull('a.ktp_berkas');
            }

            // Filters for program details
            if (!empty($params['bidang_kode'])) {
                $query->where('mb.bidang_kode', $params['bidang_kode']);
            }
            if (!empty($params['nama_program'])) {
                $query->where('p.program_nama', 'LIKE', '%' . $params['nama_program'] . '%');
            }
            if (!empty($params['tipe_program'])) {
                $query->where('a.tipe_penerimaan', $params['tipe_program']);
            }

            // Filters for date and amount
            if (!empty($params['waktu_start']) && !empty($params['waktu_end'])) {
                $query->whereBetween('a.tanggal_terima', [$params['waktu_start'], $params['waktu_end']]);
            }
            if (!empty($params['valueMin']) && !empty($params['valueMax'])) {
                $query->whereBetween('a.rupiah', [$params['valueMin'], $params['valueMax']]);
            }

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            if (!empty($desilFilters)) {
                $query->whereIn('a.nik', function($subQuery) use ($desilFilters) {
                    $subQuery->select('nik')
                        ->from('t_mustahik_bappenas')
                        ->whereIn(DB::raw('COALESCE(desil, 0)'), $desilFilters);
                });
            }

            // return $query->ddRawSql();
            return $query->groupBy(DB::raw('YEAR(a.created_at)'))
                ->orderBy('tahun')
                ->get();
        } catch (\Exception $e) {
            \Log::error('Error fetching time series data: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the time series data. Please try again later.',
            ];
        }
    }


    public static function getTabulateDataWithFilter($params)
    {
        try {
            $query = DB::table('t_mustahik as a')
                ->select(
                    DB::raw('MD5(a.nik) as nik_hashed'),
                    DB::raw('MAX(a.nik) as nik'),
                    DB::raw('MAX(a.nama_lengkap) as nama_pm'),
                    DB::raw('MAX(a.jenis_kelamin) as jenis_kelamin'),
                    DB::raw('MAX(a.alamat_domisili) as domisili'),
                    DB::raw('MAX(a.ktp_alamat) as alamat_ktp'),
                    DB::raw('SUM(a.rupiah) as nominal'),
                    DB::raw('MAX(COALESCE(b.desil, 0)) as desil')
                )
                ->leftJoin('t_mustahik_bappenas as b', 'a.nik', '=', 'b.nik')
                ->leftJoin('t_laz', 'a.laz_kode', '=', 't_laz.laz_kode')
                ->leftJoin('t_program as t', 'a.program_kode', '=', 't.program_kode')
                ->leftJoin('m_bidang as mb', 't.bidang_kode', '=', 'mb.bidang_kode');

            // Filters for program / laz
            if (!empty($params['skala'])) {
                $query->where('t_laz.skala', $params['skala']);
            }
            if (!empty($params['nama_laz'])) {
                $query->where('a.laz_kode', $params['nama_laz']);
            }

            // Filters for KTP / address
            if (!empty($params['provinsi_ktp'])) {
                $query->where('a.ktp_provinsi_kode', $params['provinsi_ktp']);
            }
            if (!empty($params['kabupaten_ktp'])) {
                $query->where('a.ktp_kabkota_kode', $params['kabupaten_ktp']);
            }
            if (!empty($params['kecamatan_ktp'])) {
                $query->where('a.ktp_kecamatan_kode', $params['kecamatan_ktp']);
            }
            if (!empty($params['kelurahan_ktp'])) {
                $query->where('a.ktp_kelurahan_kode', $params['kelurahan_ktp']);
            }
            if (!empty($params['alamat_ktp'])) {
                $query->where('a.ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%');
            }

            // Filters for domisili
            if (!empty($params['provinsi_domisili'])) {
                $query->where('a.provinsi_kode', $params['provinsi_domisili']);
            }
            if (!empty($params['kabkota_domisili'])) {
                $query->where('a.kabkota_kode', $params['kabkota_domisili']);
            }
            if (!empty($params['kecamatan_domisili'])) {
                $query->where('a.kecamatan_kode', $params['kecamatan_domisili']);
            }
            if (!empty($params['kelurahan_domisili'])) {
                $query->where('a.kelurahan_kode', $params['kelurahan_domisili']);
            }
            if (!empty($params['alamat_domisili'])) {
                $query->where('a.alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%');
            }

            // Filters for personal info
            if (!empty($params['nik'])) {
                $query->where('a.nik', (int) $params['nik']);
            }
            if (!empty($params['nama'])) {
                $query->where('a.nama_lengkap', $params['nama']);
            }
            if (!empty($params['agama'])) {
                $query->where('a.agama', $params['agama']);
            }
            if (!empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end'])) {
                $query->whereBetween('a.lahir_tanggal', [$params['tgl_lahir_start'], $params['tgl_lahir_end']]);
            }
            if (!empty($params['jenis_kelamin'])) {
                $query->where('a.jenis_kelamin', $params['jenis_kelamin']);
            }
            if (!empty($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1) {
                $query->whereNotNull('a.ktp_berkas');
            }

            // Filters for program details
            if (!empty($params['bidang_kode'])) {
                $query->where('mb.bidang_kode', $params['bidang_kode']);
            }
            if (!empty($params['nama_program'])) {
                $query->where('t.program_nama', 'LIKE', '%' . $params['nama_program'] . '%');
            }
            if (!empty($params['tipe_program'])) {
                $query->where('a.tipe_penerimaan', $params['tipe_program']);
            }

            // Filters for date and amount
            if (!empty($params['waktu_start']) && !empty($params['waktu_end'])) {
                $query->whereBetween('a.tanggal_terima', [$params['waktu_start'], $params['waktu_end']]);
            }
            if (!empty($params['valueMin']) && !empty($params['valueMax'])) {
                $query->whereBetween('a.rupiah', [$params['valueMin'], $params['valueMax']]);
            }

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            if (!empty($desilFilters)) {
                $query->whereIn('a.nik', function($subQuery) use ($desilFilters) {
                    $subQuery->select('nik')
                        ->from('t_mustahik_bappenas')
                        ->whereIn(DB::raw('COALESCE(desil, 0)'), $desilFilters);
                });
            }

            return $query->groupBy('a.nik')->get();

        } catch (\Exception $e) {
            \Log::error('Error fetching tabulate data: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the tabulate data. Please try again later.',
            ];
        }
    }

    // NO FILTERS
    public static function getSummary()
    {
        try {
            return self::selectRaw('COUNT(DISTINCT nik) AS penerima_manfaat, SUM(rupiah) AS penyaluran')->first();
        } catch (\Exception $e) {
            Log::error('Error fetching report summary: ' . $e->getMessage());

            return [
                'error' => 'Summary gagal diproses. Hubungi pengembang.',
            ];
        }
    }


    public static function getDataByGender()
    {
        try {
            return self::selectRaw('
            COUNT(DISTINCT CASE WHEN jenis_kelamin = "m" THEN nik END) AS male_count,
            COUNT(DISTINCT CASE WHEN jenis_kelamin = "f" THEN nik END) AS female_count,
            COUNT(DISTINCT nik) AS total
        ')->first();
        } catch (\Exception $e) {
            Log::error('Error fetching gender data: ' . $e->getMessage());

            return [
                'error' => 'Data gender gagal diproses. Hubungi pengembang.',
            ];
        }
    }

    public static function getPenyaluranByGender()
    {
        try {
            return self::selectRaw('
                SUM(CASE WHEN jenis_kelamin = "m" THEN rupiah ELSE 0 END) AS male_total_penyaluran,
                SUM(CASE WHEN jenis_kelamin = "f" THEN rupiah ELSE 0 END) AS female_total_penyaluran
            ')->first();
        } catch (\Exception $e) {
            Log::error('Error fetching penyaluran by gender: ' . $e->getMessage());

            return [
                'error' => 'Penyaluran data gagal diproses. Hubungi pengembang.',
            ];
        }
    }

    public static function getPenyaluranByProgram()
    {
        try {
            return DB::table('t_mustahik')
                ->select(
                    DB::raw("SUM(CASE WHEN tipe_penerimaan = 'pml' THEN rupiah ELSE 0 END) AS langsung_total"),
                    DB::raw("SUM(CASE WHEN tipe_penerimaan= 'pmtl' THEN rupiah ELSE 0 END) AS tidak_langsung_total")
                )
                ->first();
        } catch (\Exception $e) {
            // Log the exception and return a custom error message or null
            \Log::error('Error fetching penyaluran data by program: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the penyaluran data. Please try again later.',
            ];
        }
    }

    // Method to run the custom query and return the results for Penyaluran by Bidang
    public static function getPenyaluranByBidang()
    {
        try {
            return DB::table('t_mustahik as a')
                ->select(
                    'mb.bidang_label',
                    DB::raw('SUM(a.rupiah) AS total_penyaluran')
                )
                ->leftJoin('t_program as t', 'a.program_kode', '=', 't.program_kode')
                ->leftJoin('m_bidang as mb', 't.bidang_kode', '=', 'mb.bidang_kode')
                ->groupBy('mb.bidang_label')
                ->get(); // Use get() to return all results
        } catch (\Exception $e) {
            // Log the exception and return a custom error message or null
            \Log::error('Error fetching penyaluran data by bidang: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the penyaluran data by bidang. Please try again later.',
            ];
        }
    }

    public static function getTimeSeriesData()
    {
        try {
            return DB::table('t_mustahik as a')
                ->select(
                    DB::raw('YEAR(a.created_at) AS tahun'),
                    DB::raw('COALESCE(SUM(CASE WHEN a.tipe_penerimaan = "pml" THEN a.rupiah ELSE 0 END), 0) AS Bantuan_Langsung'),
                    DB::raw('COALESCE(SUM(CASE WHEN a.tipe_penerimaan = "pmtl" THEN a.rupiah ELSE 0 END), 0) AS Bantuan_Tidak_Langsung')
                )
                ->leftJoin('t_program as p', 'a.program_kode', '=', 'p.program_kode')
                ->groupBy(DB::raw('YEAR(a.created_at)'))
                ->orderBy('tahun')
                ->get();
        } catch (\Exception $e) {
            \Log::error('Error fetching time series data: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the time series data. Please try again later.',
            ];
        }
    }

    public static function getTabulateData()
    {
        try {
            return DB::table(DB::raw('(
                SELECT 
                    nik,
                    MAX(nama_lengkap) as nama_lengkap,
                    MAX(jenis_kelamin) as jenis_kelamin,
                    MAX(alamat_domisili) as alamat_domisili,
                    MAX(ktp_alamat) as ktp_alamat,
                    SUM(rupiah) as total_rupiah
                FROM t_mustahik
                GROUP BY nik
            ) as a'))
                ->select(
                    DB::raw('MD5(a.nik) as nik_hashed'),
                    'a.nik',
                    'a.nama_lengkap as nama_pm',
                    'a.jenis_kelamin',
                    'a.alamat_domisili as domisili',
                    'a.ktp_alamat as alamat_ktp',
                    'a.total_rupiah as nominal',
                    DB::raw('COALESCE(b.desil, 0) as desil')
                )
                ->leftJoin('t_mustahik_bappenas as b', 'a.nik', '=', 'b.nik')
                ->get();

        } catch (\Exception $e) {
            \Log::error('Error fetching tabulate data: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the tabulate data. Please try again later.',
            ];
        }
    }

    public static function getDesilSummaryWithFilter($params)
    {
        try {
            $query = DB::table('t_mustahik as a')
                ->select(
                    DB::raw('COALESCE(b.desil, 0) as desil'),
                    DB::raw('COUNT(DISTINCT a.nik) as jumlah')
                )
                ->leftJoin('t_mustahik_bappenas as b', 'a.nik', '=', 'b.nik')
                ->leftJoin('t_laz', 'a.laz_kode', '=', 't_laz.laz_kode')
                ->leftJoin('t_program as t', 'a.program_kode', '=', 't.program_kode')
                ->leftJoin('m_bidang as mb', 't.bidang_kode', '=', 'mb.bidang_kode');

            // ================= LAZ =================
            if (!empty($params['skala'])) {
                $query->where('t_laz.skala', $params['skala']);
            }
            if (!empty($params['nama_laz'])) {
                $query->where('a.laz_kode', $params['nama_laz']);
            }

            // ================= KTP =================
            if (!empty($params['provinsi_ktp'])) {
                $query->where('a.ktp_provinsi_kode', $params['provinsi_ktp']);
            }
            if (!empty($params['kabupaten_ktp'])) {
                $query->where('a.ktp_kabkota_kode', $params['kabupaten_ktp']);
            }
            if (!empty($params['kecamatan_ktp'])) {
                $query->where('a.ktp_kecamatan_kode', $params['kecamatan_ktp']);
            }
            if (!empty($params['kelurahan_ktp'])) {
                $query->where('a.ktp_kelurahan_kode', $params['kelurahan_ktp']);
            }
            if (!empty($params['alamat_ktp'])) {
                $query->where('a.ktp_alamat', 'LIKE', '%' . $params['alamat_ktp'] . '%');
            }

            // ================= DOMISILI =================
            if (!empty($params['provinsi_domisili'])) {
                $query->where('a.provinsi_kode', $params['provinsi_domisili']);
            }
            if (!empty($params['kabkota_domisili'])) {
                $query->where('a.kabkota_kode', $params['kabkota_domisili']);
            }
            if (!empty($params['kecamatan_domisili'])) {
                $query->where('a.kecamatan_kode', $params['kecamatan_domisili']);
            }
            if (!empty($params['kelurahan_domisili'])) {
                $query->where('a.kelurahan_kode', $params['kelurahan_domisili']);
            }
            if (!empty($params['alamat_domisili'])) {
                $query->where('a.alamat_domisili', 'LIKE', '%' . $params['alamat_domisili'] . '%');
            }

            // ================= BIODATA =================
            if (!empty($params['nik'])) {
                $query->where('a.nik', (int) $params['nik']);
            }
            if (!empty($params['nama'])) {
                $query->where('a.nama_lengkap', 'LIKE', '%' . $params['nama'] . '%');
            }
            if (!empty($params['kk'])) {
                $query->where('a.kk', 'LIKE', '%' . $params['kk'] . '%');
            }
            if (!empty($params['agama'])) {
                $query->where('a.agama', $params['agama']);
            }
            if (!empty($params['tgl_lahir_start']) && !empty($params['tgl_lahir_end'])) {
                $query->whereBetween('a.lahir_tanggal', [$params['tgl_lahir_start'], $params['tgl_lahir_end']]);
            }
            if (!empty($params['jenis_kelamin'])) {
                $query->where('a.jenis_kelamin', $params['jenis_kelamin']);
            }
            if (!empty($params['dokumen_ktp']) && $params['dokumen_ktp'] == 1) {
                $query->whereNotNull('a.ktp_berkas');
            }

            // ================= PROGRAM =================
            if (!empty($params['bidang_kode'])) {
                $query->where('mb.bidang_kode', $params['bidang_kode']);
            }
            if (!empty($params['nama_program'])) {
                $query->where('t.program_nama', 'LIKE', '%' . $params['nama_program'] . '%');
            }
            if (!empty($params['tipe_program'])) {
                $query->where('a.tipe_penerimaan', $params['tipe_program']);
            }
            if (!empty($params['waktu_start']) && !empty($params['waktu_end'])) {
                $query->whereBetween('a.tanggal_terima', [$params['waktu_start'], $params['waktu_end']]);
            }
            if (!empty($params['valueMin']) && !empty($params['valueMax'])) {
                $query->whereBetween('a.rupiah', [$params['valueMin'], $params['valueMax']]);
            }

            // ================= DESIL FILTER =================
            $desilFilters = [];
            for ($i = 0; $i <= 10; $i++) {
                if (!empty($params['desil' . $i])) {
                    $desilFilters[] = $i;
                }
            }
            
            \Log::info('Desil Filters:', ['filters' => $desilFilters, 'params' => $params]);
            
            if (!empty($desilFilters)) {
                $query->whereIn(DB::raw('COALESCE(b.desil, 0)'), $desilFilters);
                \Log::info('Desil filter applied');
            } else {
                \Log::info('No desil filter applied');
            }

            // Log raw SQL query with bindings replaced
            $sql = $query->groupBy(DB::raw('COALESCE(b.desil, 0)'))->toSql();
            $bindings = $query->getBindings();
            
            // Replace bindings in SQL
            $fullSql = $sql;
            foreach ($bindings as $binding) {
                $value = is_numeric($binding) ? $binding : "'" . $binding . "'";
                $fullSql = preg_replace('/\?/', $value, $fullSql, 1);
            }
            
            \Log::info('Raw SQL Query:', ['sql' => $sql, 'bindings' => $bindings]);
            \Log::info('Full SQL Query with Bindings:', ['query' => $fullSql]);

            $desilSummary = $query->groupBy(DB::raw('COALESCE(b.desil, 0)'))->orderBy(DB::raw('COALESCE(b.desil, 0)'))->get();

            // Format the result as an array with desil as key
            $result = [];
            for ($i = 0; $i <= 10; $i++) {
                $result[$i] = 0;
            }

            foreach ($desilSummary as $item) {
                $desilValue = (int)$item->desil;
                $result[$desilValue] = (int)$item->jumlah;
            }

            return $result;

        } catch (\Exception $e) {
            \Log::error('Error fetching desil summary: ' . $e->getMessage());

            return [
                'error' => 'There was an issue fetching the desil summary. Please try again later.',
            ];
        }
    }
}
