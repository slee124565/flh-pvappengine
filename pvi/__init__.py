
from enum import Enum

PVI_TYPE_DELTA_PRI_H5 = 'DELTA_PRI_H5'

MAX_QUERY_ENERGY_DAILY_LIST_LEN = 45
MAX_QUERY_ENERGY_HOURLY_LIST_LEN = 48

class PVIType(Enum):
    Delta_PRI_H5 = 1
    
class PVIQueryInfo(Enum):
    #-> Energy
    Energy_Today = 1
    Energy_This_Month = 2
    Energy_Until_Now = 3
    Energy_Hourly_List = 4
    Energy_Daily_List = 5
    #-> AC Output
    AC_Output_Voltage = 11
    AC_Output_Current = 12
    AC_Output_Wattage = 13


