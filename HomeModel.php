<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

class HomeModel extends Model
{
    public static function getAgregatPenerimaan()
    {

        $lastYear = Carbon::now()->subYear()->year;
        $thisYear = Carbon::now()->year;

        $sql = <<<'SQL'
            SELECT
                a.provinsi_nama,
                COALESCE(SUM(tp.penerimaan_nominal), 0)          AS total_nominal_numeric,
                IFNULL(SUM(tp.penerimaan_nominal), 'Tidak Ada Data') AS total_nominal_text,
                CASE
                    WHEN SUM(tp.penerimaan_nominal) IS NULL
                        THEN 'Tidak Ada Data'
                    ELSE SUM(tp.penerimaan_nominal)
                END AS total_nominal_case
            FROM
                m_provinsi   AS a
            LEFT JOIN
                t_laz        AS tl ON a.provinsi_kode = tl.provinsi_kode
            LEFT JOIN
                t_penerimaan AS tp
                    ON tp.laz_kode = tl.laz_kode
                    AND tp.penerimaan_tahun = ?
            GROUP BY
                a.provinsi_nama
            ORDER BY
                a.provinsi_nama
        SQL;

        return DB::select($sql, [$lastYear]);
    }

    public static function getDataLaz()
    {
        // Query from v_laz_usulan_kma with active KMA only
        $data = DB::table('v_laz_usulan_kma')
            ->whereNotNull('kma_berkas')
            ->where('kma_kadaluarsa', '>=', DB::raw('CURRENT_DATE'))
            ->selectRaw('
                SUM(CASE WHEN kma_skala = 1 THEN 1 ELSE 0 END) AS nasional,
                SUM(CASE WHEN kma_skala = 2 THEN 1 ELSE 0 END) AS provinsi,
                SUM(CASE WHEN kma_skala = 3 THEN 1 ELSE 0 END) AS kabkota
            ')
            ->first();

        return $data;
    }

    public static function getAgregatSummary()
    {
        return DB::table('t_mustahik as tm')
            ->leftJoin('t_laz as tl', 'tm.laz_kode', '=', 'tl.laz_kode')
            ->selectRaw('
                SUM(rupiah) AS total_penyaluran,
                SUM(CASE WHEN skala = 1 THEN 1 ELSE 0 END) AS nasional,
                SUM(CASE WHEN skala = 2 THEN 1 ELSE 0 END) AS provinsi,
                SUM(CASE WHEN skala = 3 THEN 1 ELSE 0 END) AS kabkota
            ')
            ->first();
    }

    public static function getMapData($params = '1')
    {

        $thisYear = (int) date('Y');
        $lastYear = $thisYear - 1;
        $year = ($params === '1' || $params === '3') ? $thisYear : $lastYear;

        $startOfYear = Carbon::createFromDate($year, 1, 1)->startOfDay();

        if ($params == '1' || $params == '2') {

            return DB::table('m_provinsi as a')
                ->leftJoin('t_laz as tl', 'a.provinsi_kode', '=', 'tl.provinsi_kode')
                ->leftJoin('t_mustahik as tm', function ($join) use ($startOfYear) {
                    $join->on('tm.laz_kode', '=', 'tl.laz_kode')
                        ->where('tm.created_at', '>=', $startOfYear);
                })
                ->select(
                    'a.provinsi_nama',
                    DB::raw('COALESCE(SUM(tm.rupiah), 0) AS total_penyaluran_numeric'),
                    DB::raw("IFNULL(SUM(tm.rupiah), 'Tidak Ada Data') AS total_penyaluran_text"),
                    DB::raw("
                    CASE
                        WHEN SUM(tm.rupiah) IS NULL
                            THEN 'Tidak Ada Data'
                        ELSE SUM(tm.rupiah)
                    END AS total_penyaluran_case
                ")
                )
                ->groupBy('a.provinsi_nama')
                ->orderBy('a.provinsi_nama')
                ->get();
        } else {
            return DB::table('m_provinsi AS a')
                ->leftJoin('t_laz AS tl', 'a.provinsi_kode', '=', 'tl.provinsi_kode')
                ->leftJoin('t_mustahik as tm', function ($join) use ($startOfYear) {
                    $join->on('tm.laz_kode', '=', 'tl.laz_kode')
                        ->where('tm.created_at', '>=', $startOfYear);
                })
                ->select(
                    'a.provinsi_nama',
                    DB::raw('COUNT(DISTINCT tm.nik) AS total_penyaluran_numeric'),
                    DB::raw('IFNULL(COUNT(DISTINCT tm.nik), "Tidak Ada Data") AS total_penyaluran_text'),
                    DB::raw('CASE WHEN COUNT(DISTINCT tm.nik) IS NULL THEN "Tidak Ada Data" ELSE COUNT(DISTINCT tm.nik) END AS total_penyaluran_case')
                )
                ->groupBy('a.provinsi_nama')
                ->orderBy('a.provinsi_nama')
                ->get();
        }
    }
}
