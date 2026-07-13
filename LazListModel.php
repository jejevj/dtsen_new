<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Log;

class LazListModel extends Model
{
    //
     protected $table = 't_mustahik';

    public static function getSummary()
    {
        try {

            return self::selectRaw('select laz_kode,laz_parent_kode,laz_nama')->first();
        } catch (\Exception $e) {

            Log::error('Error fetching report summary: '.$e->getMessage());

            return [
                'error' => 'Summary gagal diproses. Hubungi pengembang.',
            ];
        }
    }
}
