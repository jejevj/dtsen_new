<?php

namespace App\Models;

use DB;
use Illuminate\Database\Eloquent\Model;

class DetailPenerima extends Model
{
    //

    public static function getDetailMustahik($id)
    {
        try {
            return DB::table('t_mustahik as a')
                ->select(
                    'a.*',
                    'b.laz_nama',
                    'b.skala as skala',
                    'c.program_nama',
                    'mp.provinsi_nama',
                    'kab.kabkota_nama',
                    'mk.kecamatan_nama',
                    'kl.kelurahan_nama'
                )
                ->leftJoin('t_laz as b', 'a.laz_kode', '=', 'b.laz_kode')
                ->leftJoin('t_program as c', 'a.program_kode', '=', 'c.program_kode')
                ->leftJoin('m_provinsi as mp', 'a.provinsi_kode', '=', 'mp.provinsi_kode')
                ->leftJoin('m_kabkota as kab', 'a.kabkota_kode', '=', 'kab.kabkota_kode')
                ->leftJoin('m_kecamatan as mk', 'a.kecamatan_kode', '=', 'mk.kecamatan_kode')
                ->leftJoin('m_kelurahan as kl', 'a.kelurahan_kode', '=', 'kl.kelurahan_kode')
                ->where(DB::raw('MD5(a.nik)'), '=', $id)  // Compare MD5 of nik with the hashed value of $id
                ->where(function ($query) {
                    $query->where('b.laz_status', '=', 'aktif')
                        ->orWhere('b.laz_status', '=', 'daftar_ulang');
                })
                ->orderByDesc('a.created_at')
                ->get();  // Use get() to return multiple results
        } catch (\Exception $e) {
            \Log::error('Error fetching detail mustahik: '.$e->getMessage());

            return null;  // Handle errors gracefully
        }
    }
    public static function getDetailMustahikNotHashed($id)
    {
        try {
            return DB::table('t_mustahik as a')
                ->select(
                    'a.*',
                    'b.laz_nama',
                    'b.skala as skala',
                    'c.program_nama',
                    'mp.provinsi_nama',
                    'kab.kabkota_nama',
                    'mk.kecamatan_nama',
                    'kl.kelurahan_nama'
                )
                ->leftJoin('t_laz as b', 'a.laz_kode', '=', 'b.laz_kode')
                ->leftJoin('t_program as c', 'a.program_kode', '=', 'c.program_kode')
                ->leftJoin('m_provinsi as mp', 'a.provinsi_kode', '=', 'mp.provinsi_kode')
                ->leftJoin('m_kabkota as kab', 'a.kabkota_kode', '=', 'kab.kabkota_kode')
                ->leftJoin('m_kecamatan as mk', 'a.kecamatan_kode', '=', 'mk.kecamatan_kode')
                ->leftJoin('m_kelurahan as kl', 'a.kelurahan_kode', '=', 'kl.kelurahan_kode')
                ->where(DB::raw('a.nik'), '=', $id)  // Compare MD5 of nik with the hashed value of $id
                ->where(function ($query) {
                    $query->where('b.laz_status', '=', 'aktif')
                        ->orWhere('b.laz_status', '=', 'daftar_ulang');
                })
                ->orderByDesc('a.created_at')
                ->get();  // Use get() to return multiple results
        } catch (\Exception $e) {
            \Log::error('Error fetching detail mustahik: '.$e->getMessage());

            return null;  // Handle errors gracefully
        }
    }

    public static function getReallyDetaiMustahik($id)
    {
        try {

            $data = DB::table('t_mustahik as a')
                ->leftJoin('t_laz as t', 'a.laz_kode', '=', 't.laz_kode')
                ->leftJoin('t_program as p', 'a.program_kode', '=', 'p.program_kode')
                ->leftJoin('m_provinsi as prov', 'a.provinsi_kode', '=', 'prov.provinsi_kode')
                ->leftJoin('m_kabkota as k', 'a.kabkota_kode', '=', 'k.kabkota_kode')
                ->leftJoin('m_kecamatan as mk', 'a.kecamatan_kode', '=', 'mk.kecamatan_kode')
                ->leftJoin('m_kelurahan as ml', 'a.kelurahan_kode', '=', 'ml.kelurahan_kode')
                ->leftJoin('m_provinsi as ktp_provinsi', 'a.ktp_provinsi_kode', '=', 'ktp_provinsi.provinsi_kode')
                ->leftJoin('m_kabkota as ktp_kabkota', 'a.ktp_kabkota_kode', '=', 'ktp_kabkota.kabkota_kode')
                ->leftJoin('m_kecamatan as ktp_kecamatan', 'a.ktp_kecamatan_kode', '=', 'ktp_kecamatan.kecamatan_kode')
                ->leftJoin('m_kelurahan as ktp_kelurahan', 'a.ktp_kelurahan_kode', '=', 'ktp_kelurahan.kelurahan_kode')
                ->select(
                    'a.nama_lengkap',
                    'a.jenis_kelamin',
                    'a.lahir_tanggal',
                    'a.agama',
                    'a.nik',
                    'a.kk',
                    'a.alamat_domisili',
                    'a.rupiah',
                    'a.created_at',
                    'prov.provinsi_nama',
                    'k.kabkota_nama',
                    'mk.kecamatan_nama',
                    'ml.kelurahan_nama',
                    
                    'a.ktp_alamat',
                    'ktp_provinsi.provinsi_nama as ktp_provinsi_nama',
                    'ktp_kabkota.kabkota_nama as ktp_kabkota_nama',
                    'ktp_kecamatan.kecamatan_nama as ktp_kecamatan_nama',
                    'ktp_kelurahan.kelurahan_nama as ktp_kelurahan_nama',
                    'p.program_nama',
                    't.laz_nama',
                    DB::raw("CASE WHEN t.skala = 1 THEN 'Nasional' WHEN t.skala = 2 THEN 'Provinsi' WHEN t.skala = 3 THEN 'Kabupaten/Kota' END AS skala"),
                    DB::raw('LAG(a.nama_lengkap) OVER (ORDER BY a.created_at) AS prev_nama_lengkap'),
                    DB::raw('LAG(a.jenis_kelamin) OVER (ORDER BY a.created_at) AS prev_jenis_kelamin'),
                    DB::raw('LAG(t.laz_nama) OVER (ORDER BY a.created_at) AS prev_laz_nama'),
                    DB::raw('LAG(a.agama) OVER (ORDER BY a.created_at) AS prev_agama'),
                    DB::raw('LAG(a.nik) OVER (ORDER BY a.created_at) AS prev_nik')
                )
                ->where(DB::raw('MD5(a.nik)'), '=', $id)
                ->orderByDesc('a.created_at')
                ->get();

            $results = $data->map(function ($item) {
                $item->nama_lengkap = ($item->prev_nama_lengkap === $item->nama_lengkap) ? null : $item->nama_lengkap;
                $item->jenis_kelamin = ($item->prev_jenis_kelamin === $item->jenis_kelamin && $item->prev_laz_nama === $item->laz_nama) ? null : $item->jenis_kelamin;
                $item->agama = ($item->prev_agama === $item->agama) ? null : $item->agama;
                $item->nik = ($item->prev_nik === $item->nik) ? null : $item->nik;
                /* ---------- format birth‑date --------------------------------- */
                if ($item->lahir_tanggal) {
                    // `Carbon` is already bundled with Laravel; use the fully‑qualified name
                    $item->lahir_tanggal = \Carbon\Carbon::parse($item->lahir_tanggal)
                        ->locale('id')                 // Indonesian locale
                        ->isoFormat('DD MMMM YYYY');   // e.g. 02 Januari 1990
                }
                /* -------------------------------------------------------
             *  Convert the gender code to human‑readable text
             * ------------------------------------------------------- */
                if ($item->jenis_kelamin !== null) {
                    switch ($item->jenis_kelamin) {
                        case 'F':
                            $item->jenis_kelamin = 'Perempuan';
                            break;
                        case 'M':
                            $item->jenis_kelamin = 'Laki - Laki';
                            break;
                        default:
                            // keep the original value if it’s something else
                            break;
                    }
                }

                // Remove temporary columns
                unset($item->prev_nama_lengkap);
                unset($item->prev_jenis_kelamin);
                unset($item->prev_agama);
                unset($item->prev_nik);

                return $item;
            });

            return $results;

        } catch (\Exception $e) {
            \Log::error('Error fetching detail mustahik: '.$e->getMessage());

            return null;  // Handle errors gracefully
        }
    }
    public static function getReallyDetaiMustahikNotHashed($id)
    {
        try {

            $data = DB::table('t_mustahik as a')
                ->leftJoin('t_laz as t', 'a.laz_kode', '=', 't.laz_kode')
                ->leftJoin('t_program as p', 'a.program_kode', '=', 'p.program_kode')
                ->leftJoin('m_provinsi as prov', 'a.provinsi_kode', '=', 'prov.provinsi_kode')
                ->leftJoin('m_kabkota as k', 'a.kabkota_kode', '=', 'k.kabkota_kode')
                ->leftJoin('m_kecamatan as mk', 'a.kecamatan_kode', '=', 'mk.kecamatan_kode')
                ->leftJoin('m_kelurahan as ml', 'a.kelurahan_kode', '=', 'ml.kelurahan_kode')
                ->leftJoin('m_provinsi as ktp_provinsi', 'a.ktp_provinsi_kode', '=', 'ktp_provinsi.provinsi_kode')
                ->leftJoin('m_kabkota as ktp_kabkota', 'a.ktp_kabkota_kode', '=', 'ktp_kabkota.kabkota_kode')
                ->leftJoin('m_kecamatan as ktp_kecamatan', 'a.ktp_kecamatan_kode', '=', 'ktp_kecamatan.kecamatan_kode')
                ->leftJoin('m_kelurahan as ktp_kelurahan', 'a.ktp_kelurahan_kode', '=', 'ktp_kelurahan.kelurahan_kode')
                ->select(
                    'a.nama_lengkap',
                    'a.jenis_kelamin',
                    'a.lahir_tanggal',
                    'a.agama',
                    'a.nik',
                    'a.kk',
                    'a.alamat_domisili',
                    'a.rupiah',
                    'a.created_at',
                    'prov.provinsi_nama',
                    'k.kabkota_nama',
                    'mk.kecamatan_nama',
                    'ml.kelurahan_nama',
                    
                    'a.ktp_alamat',
                    'ktp_provinsi.provinsi_nama as ktp_provinsi_nama',
                    'ktp_kabkota.kabkota_nama as ktp_kabkota_nama',
                    'ktp_kecamatan.kecamatan_nama as ktp_kecamatan_nama',
                    'ktp_kelurahan.kelurahan_nama as ktp_kelurahan_nama',
                    'p.program_nama',
                    't.laz_nama',
                    DB::raw("CASE WHEN t.skala = 1 THEN 'Nasional' WHEN t.skala = 2 THEN 'Provinsi' WHEN t.skala = 3 THEN 'Kabupaten/Kota' END AS skala"),
                    DB::raw('LAG(a.nama_lengkap) OVER (ORDER BY a.created_at) AS prev_nama_lengkap'),
                    DB::raw('LAG(a.jenis_kelamin) OVER (ORDER BY a.created_at) AS prev_jenis_kelamin'),
                    DB::raw('LAG(t.laz_nama) OVER (ORDER BY a.created_at) AS prev_laz_nama'),
                    DB::raw('LAG(a.agama) OVER (ORDER BY a.created_at) AS prev_agama'),
                    DB::raw('LAG(a.nik) OVER (ORDER BY a.created_at) AS prev_nik')
                )
                ->where(DB::raw('a.nik'), '=', $id)
                ->orderByDesc('a.created_at')
                ->get();

            $results = $data->map(function ($item) {
                $item->nama_lengkap = ($item->prev_nama_lengkap === $item->nama_lengkap) ? null : $item->nama_lengkap;
                $item->jenis_kelamin = ($item->prev_jenis_kelamin === $item->jenis_kelamin && $item->prev_laz_nama === $item->laz_nama) ? null : $item->jenis_kelamin;
                $item->agama = ($item->prev_agama === $item->agama) ? null : $item->agama;
                $item->nik = ($item->prev_nik === $item->nik) ? null : $item->nik;
                /* ---------- format birth‑date --------------------------------- */
                if ($item->lahir_tanggal) {
                    // `Carbon` is already bundled with Laravel; use the fully‑qualified name
                    $item->lahir_tanggal = \Carbon\Carbon::parse($item->lahir_tanggal)
                        ->locale('id')                 // Indonesian locale
                        ->isoFormat('DD MMMM YYYY');   // e.g. 02 Januari 1990
                }
                /* -------------------------------------------------------
             *  Convert the gender code to human‑readable text
             * ------------------------------------------------------- */
                if ($item->jenis_kelamin !== null) {
                    switch ($item->jenis_kelamin) {
                        case 'F':
                            $item->jenis_kelamin = 'Perempuan';
                            break;
                        case 'M':
                            $item->jenis_kelamin = 'Laki - Laki';
                            break;
                        default:
                            // keep the original value if it’s something else
                            break;
                    }
                }

                // Remove temporary columns
                unset($item->prev_nama_lengkap);
                unset($item->prev_jenis_kelamin);
                unset($item->prev_agama);
                unset($item->prev_nik);

                return $item;
            });

            return $results;

        } catch (\Exception $e) {
            \Log::error('Error fetching detail mustahik: '.$e->getMessage());

            return null;  // Handle errors gracefully
        }
    }

}
