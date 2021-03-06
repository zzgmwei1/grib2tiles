import sys
import os
import datetime
import logging

import grib2tiles
from lfm import LFM

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lfm_to_tiles(file):
    lfm = LFM(file)
    files = []

    lfm.parse_section0()
    sec1 = lfm.parse_section1()
    sec3, grid = lfm.parse_section3()

    ref_time = datetime.datetime(
        sec1['year'][0],        
        sec1['month'][0],        
        sec1['day'][0],
        sec1['hour'][0],
        sec1['minute'][0],
        sec1['second'][0]
    )
    ref_time_str = ref_time.strftime('%Y%m%d%H%M')
    bitmap = ''

    while not lfm.is_end_section():
        sec4, pdt = lfm.parse_section4()
        sec5, drt, bin_RED = lfm.parse_section5(True)
        sec6, bitmap_iter = lfm.parse_section6(return_bitmap=True)
        sec7, data = lfm.parse_section7()

        if sec6['bitmap_indicator'] == 0:
            bitmap = bitmap_iter

        level = lfm.level(
            pdt['first_fixed_surface_type'],
            pdt['first_fixed_surface_scale_factor'],
            pdt['first_fixed_surface_scale_value'])
        element = lfm.parameter(
            pdt['parameter_category'],
            pdt['parameter_number'])

        ft = pdt['forecast_time'][0]
        if element == 'APCP':
            ft += 60
        valid_time = ref_time + datetime.timedelta(minutes=int(ft))
        valid_time_str = valid_time.strftime('%Y%m%d%H%M')

        directory = '' + '/'.join(['tiles', ref_time_str, valid_time_str, level, element])

        if level == 'surface':
            files.extend(grib2tiles.to_tile(directory, data, bin_RED, ni=1201, nj=1261, level=2, bitmap=bitmap))
            files.extend(grib2tiles.to_tile(directory, data, bin_RED, ni=1201, nj=1261, level=1, thinout=1, bitmap=bitmap))
            files.extend(grib2tiles.to_tile(directory, data, bin_RED, ni=1201, nj=1261, level=0, thinout=2, bitmap=bitmap))

        else:
            files.extend(grib2tiles.to_tile(directory, data, bin_RED, ni=601, nj=631, level=1, bitmap=bitmap))
            files.extend(grib2tiles.to_tile(directory, data, bin_RED, ni=601, nj=631, level=0, thinout=1, bitmap=bitmap))

        logger.info(directory)

    return files



def main(grib):
    logging.info("start processing: " + grib)
    files = lfm_to_tiles(grib)


if __name__ == '__main__':
    grib = sys.argv[1]
    main(grib)

