#import os, sys
#sys.path.insert(0, "..")
import numpy as np
import dbdreader

'''
As seen via dbd2asc (Slocum binaries)

$ bin/dbd2asc -c ~/src/dbdreader/data/cac ~/src/dbdreader/data/amadeus-2014-204-05-000.dbd | bin/dba_sensor_filter m_present_time m_time_til_wpt
dbd_label: DBD_ASC(dinkum_binary_data_ascii)file
encoding_ver: 2
num_ascii_tags: 14
all_sensors: 0
filename: amadeus-2014-204-5-0-sf
the8x3_filename: 07160000
filename_extension: dbd
filename_label: amadeus-2014-204-5-0-dbd(07160000)
mission_name: MICRO.MI
fileopen_time: Thu_Jul_24_17:03:02_2014
sensors_per_cycle: 2
num_label_lines: 3
num_segments: 1
segment_filename_0: amadeus-2014-204-5-0
m_present_time m_time_til_wpt 
timestamp s 
8 4 
1406221416.56702 0 
1406221444.0452 NaN 
1406221448.99835 NaN 
1406221453.9433 NaN 
1406221462.78418 NaN 
1406221467.7373 NaN 
1406221472.7084 NaN 
1406221477.66046 NaN 
1406221482.61267 NaN 
1406221487.82343 93665.8 
1406221492.99747 51991 
1406221497.87772 37061.5 
1406221502.74731 inf 
1406221507.86731 91327.3 
1406221513.19812 209718 
1406221518.0636 52789.6 
1406221522.92633 inf 
1406221527.80518 inf 
1406221532.69302 115338 
1406221537.30292 367537 
1406221541.79474 194995 
1406221546.28998 65410.9 
1406221550.77869 47719.9 
1406221555.27179 61500.2 
'''


s='''1406221416.56702 0 
1406221444.0452 NaN 
1406221448.99835 NaN 
1406221453.9433 NaN 
1406221462.78418 NaN 
1406221467.7373 NaN 
1406221472.7084 NaN 
1406221477.66046 NaN 
1406221482.61267 NaN 
1406221487.82343 93665.8 
1406221492.99747 51991 
1406221497.87772 37061.5 
1406221502.74731 inf 
1406221507.86731 91327.3 
1406221513.19812 209718 
1406221518.0636 52789.6 
1406221522.92633 inf 
1406221527.80518 inf 
1406221532.69302 115338 
1406221537.30292 367537 
1406221541.79474 194995 
1406221546.28998 65410.9 
1406221550.77869 47719.9 
1406221555.27179 61500.2'''.split("\n")
# Read using dbdreader

dbdFp = dbdreader.DBD("../data/amadeus-2014-204-05-000.dbd",
                      cacheDir="../data/cac")

t, v = dbdFp.get("m_time_til_wpt", return_nans =True)
t = t[:24]
v = v[:24]
s_dbd2asc='''1406221416.56702 0 
1406221444.0452 NaN 
1406221448.99835 NaN 
1406221453.9433 NaN 
1406221462.78418 NaN 
1406221467.7373 NaN 
1406221472.7084 NaN 
1406221477.66046 NaN 
1406221482.61267 NaN 
1406221487.82343 93665.8 
1406221492.99747 51991 
1406221497.87772 37061.5 
1406221502.74731 inf 
1406221507.86731 91327.3 
1406221513.19812 209718 
1406221518.0636 52789.6 
1406221522.92633 inf 
1406221527.80518 inf 
1406221532.69302 115338 
1406221537.30292 367537 
1406221541.79474 194995 
1406221546.28998 65410.9 
1406221550.77869 47719.9 
1406221555.27179 61500.2'''

tp = []
vp = []
for line in s_dbd2asc.splitlines():
    _x, _y = line.split()
    tp.append(float(_x))
    vp.append(float(_y))
tp = np.array(tp)
vp = np.array(vp)

            
for x, y in zip(v, vp):
    print(f"{x:16f}, {y:16f}")
    
Q
#x = dbdFp.get("m_present_time")
#x = dbdFp.get("m_depth", "m_present_time")
#x = dbdFp.get("m_time_til_wpt", "m_present_time")
#x = dbdFp.get("m_depth")


# Read all fields

dbdData = dbdFp.get(*dbdFp.parameterNames, return_nans=True)

# Show first 24 rows of m_present_time m_time_til_wpt

tIndex = dbdFp.parameterNames.index('m_present_time')
fIndex = dbdFp.parameterNames.index('m_time_til_wpt')

t, f = dbdFp.get("m_time_til_wpt", return_nans=True)

print("m_present_time m_time_til_wpt")
for r in range(24):
    x, y = (float(i) for i in s[r].split())
#    print("{:15f} {:10f} {:15f} {:10f} {:15f} {:10f} {:15f} {:10f}".format(x,y,
#                                                                           dbdData[tIndex][1][r], dbdData[fIndex][1][r],
#                                                                           dbdData[fIndex][0][r], dbdData[fIndex][1][r],
#                                                                           t[r], f[r]))
    print("{:15f} {:15f} {:15f} {:15f}".format(x,
                                               dbdData[tIndex][1][r],
                                               dbdData[fIndex][0][r],
                                               t[r]))
    print("{:15f} {:15f} {:15f} {:15f}".format(y,
                                               dbdData[fIndex][1][r],
                                               dbdData[fIndex][1][r],
                                               f[r]))
    print()
    
#    print("%f %f" % (dbdData[tIndex][1][r], dbdData[fIndex][1][r]))
#    print("%f %f" % (dbdData[fIndex][0][r], dbdData[fIndex][1][r]))
#    print("%f %f" % (t[r], f[r]))
#    print()



x = dbdFp.get("m_time_til_wpt", "m_depth")

p = [i for i in dbdFp.parameterNames if not i.startswith("m_present_time")]
x = dbdFp.get(*p)
dbdFp.close()

t, f = dbdFp.get("m_time_til_wpt")
