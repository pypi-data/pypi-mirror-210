import dbdreader
from collections import namedtuple

try:
    dbd = dbdreader.DBD("../data/unit_887-2021-321-3-0.sbd")
except dbdreader.DbdError as e:
    data1 = e.data

try: 
    dbd = dbdreader.MultiDBD("../data/unit*")
except dbdreader.DbdError as e:
    data2 = e.data



class DbdError(Exception):
    MissingCacheFileData = namedtuple('MissingCacheFileData', 'missing_cache_files cache_dir')
    def __init__(self,value=9,mesg=None,data=None):
        self.value=value
        self.mesg=mesg
        self.data=data


data = DbdError.MissingCacheFileData('a', 'b')        
