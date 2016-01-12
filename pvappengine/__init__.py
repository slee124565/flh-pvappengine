from enum import Enum

class PVSChartsDataTypeEnum(Enum):
    '''
    define pvstation page chart data type which pvappengine has to provide
    '''
    PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY = 1     # chart for hourly data of energy out and max visibility
    PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY = 2      # chart for daily data of energy out and max visibility
