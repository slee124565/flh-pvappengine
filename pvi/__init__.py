
from enum import Enum

PVI_TYPE_DELTA_PRI_H5 = 'DELTA_PRI_H5'

class PVIType(Enum):
    Delta_PRI_H5 = 1
    
class PVIQueryInfo(Enum):
    #-> Energy
    Energy_Today = 1
    Energy_This_Month = 2
    Energy_Until_Now = 3
    #-> AC Output
    AC_Output_Voltage = 11
    AC_Output_Current = 12
    AC_Output_Wattage = 13

class PVIEnvConditions(Enum):
    Temperature = 1
    UV_Index = 2
    Visibility = 3    