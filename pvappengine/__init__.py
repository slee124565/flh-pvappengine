from enum import Enum

class PVSChartsDataTypeEnum(Enum):
    '''
    define pvstation page chart data type which pvappengine has to provide
    '''
    PVS_AMCHARTS_HOURLY_ENERGY_n_VISIBILITY = 1     # chart for hourly data of energy out and max visibility
    PVS_AMCHARTS_DAILY_ENERGY_n_VISIBILITY = 2      # chart for daily data of energy out and max visibility
    PVS_AMCHARTS_HOURLY_ENERGY_VISIBILITY_UV = 3    # chart for hourly data of energy out and max visibility n UV
    
DEFAULT_DB_CONFIG = {
                      'kWh_carbon_save_unit_kg': 0.637,
                      'kWh_income_unit_ntd': 6.8633,
                     }
