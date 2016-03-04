
from enum import Enum
import serial

DEFAULT_DB_CONFIG = [
                       {
                        'name': 'H5',
                        'type': 'DELTA_PRI_H5', #-> refer to pvi.PVI_TYPE_LIST
                        'modbus_id': 2, #-> pvi modbus address
                        'serial': {
                                   'port': '/dev/ttyUSB0',
                                   'baudrate': 9600,
                                   'bytesize': 8,
                                   'parity': serial.PARITY_NONE,
                                   'stopbits': 1,
                                   'timeout': 0.1,
                                   }
                        },
                       ]

# constant string for each PVI implemented by this package
PVI_TYPE_DELTA_PRI_H5 = 'DELTA_PRI_H5'
PVI_TYPE_GROWATTA_PRI = 'GROWATTA' # TODO: not yet implement
PVI_TYPE_LIST = [
                 PVI_TYPE_DELTA_PRI_H5,
                 ]

class PVIType(Enum):
    '''
    enum type for each PVI implemented by this package
    and pvi type string mapping function is http_api.get_pvi_type()
    '''
    Delta_PRI_H5 = 1
    

# energy info query return length for each pvi driver to implement
MAX_QUERY_ENERGY_DAILY_LIST_LEN = 45
MAX_QUERY_ENERGY_HOURLY_LIST_LEN = 48

class PVIQueryInfo(Enum):
    '''
    Enum class type
    Define information type list each pvi driver should implement
    in function query_pvi_info()
    '''
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


