from enum import Enum
import serial

class RegCol(Enum):
    '''
    Sub-Class of `Enum` class. Define the column name and index in `INPUT_REGISTER` 
    and `HOLDING_REGISTER` dictionary constant:
    - `address`: the value of register address
    - `name`: the name of register
    - `length` : the length (word, 2 bytes) of register
    '''
    address = 0
    name = 1
    length = 2

class MeasurementIndexCodeEnum(Enum):
    """PRI H5 inverter `Measurement Index` value definition"""
    u_grid = 0x00
    u_dc1 = 0x30
    u_dc2 = 0x31
    p_bus = 0x40
    n_bus = 0x41
    
HOLDING_REGISTER = {
    "Measurement Index": [
        "800",
        "Measurement Index",
        1
    ],
    "Event Index" : [
        "801",
        "Event Index",
        1
    ]
}
'''
Constant `HOLDING_REGISTER` directory table. 
Take register name as key and value in `RegCol` format
'''

INPUT_REGISTER = {
    "Delta 5K:Solar 1 RLeakageAvg": [
        "1163",
        "Delta 5K:Solar 1 RLeakageAvg",
        1
    ],
    "Serial number 4,5": [
        "40977",
        "Serial number 4,5",
        1
    ],
    "RTC_Minute": [
        "1037",
        "RTC_Minute",
        1
    ],
    "Event (index+5)": [
        "1094",
        "Event (index+5)",
        1
    ],
    "Delta 5k: Amb Temp": [
        "1080",
        "Delta 5k: Amb Temp",
        1
    ],
    "RTC_Year": [
        "1033",
        "RTC_Year",
        1
    ],
    "Redundant Voltage": [
        "1062",
        "Redundant Voltage",
        1
    ],
    "Current": [
        "1058",
        "Current",
        1
    ],
    "Delta 5k: BoostHs Temp": [
        "1081",
        "Delta 5k: BoostHs Temp",
        1
    ],
    "AC Life Wh": [
        "53252",
        "AC Life Wh",
        2
    ],
    "Reconnected Time": [
        "1049",
        "Reconnected Time",
        1
    ],
    "Delta5k: InvHs Temp": [
        "1082",
        "Delta5k: InvHs Temp",
        1
    ],
    "Adc Wattage": [
        "1070",
        "Adc Wattage",
        1
    ],
    "Adc Redundant Voltage": [
        "1071",
        "Adc Redundant Voltage",
        1
    ],
    "Inverter ID": [
        "1032",
        "Inverter ID",
        1
    ],
    "Event (index+2)": [
        "1091",
        "Event (index+2)",
        1
    ],
    "Wattage": [
        "1059",
        "Wattage",
        1
    ],
    "Event (index+3)": [
        "1092",
        "Event (index+3)",
        1
    ],
    "Event (index+9)": [
        "1098",
        "Event (index+9)",
        1
    ],
    "Event (index+1)": [
        "1090",
        "Event (index+1)",
        1
    ],
    "Serial number 0,1": [
        "40975",
        "Serial number 0,1",
        1
    ],
    "Frequency": [
        "1060",
        "Frequency",
        1
    ],
    "Delta 5K:Solar 1 RLeakage2": [
        "1161",
        "Delta 5K:Solar 1 RLeakage2",
        1
    ],
    "FW2 Revision": [
        "1042",
        "FW2 Revision",
        1
    ],
    "Redundant Frequency": [
        "1063",
        "Redundant Frequency",
        1
    ],
    "Delta 5k:Max BoostHs Temp": [
        "1153",
        "Delta 5k:Max BoostHs Temp",
        1
    ],
    "Serial number 6,7": [
        "40978",
        "Serial number 6,7",
        1
    ],
    "Delta 5K:Adins_adc": [
        "1164",
        "Delta 5K:Adins_adc",
        1
    ],
    "Voltage": [
        "1057",
        "Voltage",
        1
    ],
    "Percentage": [
        "1061",
        "Percentage",
        1
    ],
    "Delta 5K:Solar 1 RLeakage1": [
        "1160",
        "Delta 5K:Solar 1 RLeakage1",
        1
    ],
    "FW1 Date": [
        "1041",
        "FW1 Date",
        1
    ],
    "Inverter Status": [
        "1048",
        "Inverter Status",
        1
    ],
    "FW4 Date": [
        "1047",
        "FW4 Date",
        1
    ],
    "Event (index+4)": [
        "1093",
        "Event (index+4)",
        1
    ],
    "Serial number 10,11": [
        "40980",
        "Serial number 10,11",
        1
    ],
    "Delta 5K:Solar 1 RLeakage3": [
        "1162",
        "Delta 5K:Solar 1 RLeakage3",
        1
    ],
    "Serial number 8,9": [
        "40979",
        "Serial number 8,9",
        1
    ],
    "DC Life Runtime": [
        "1078",
        "DC Life Runtime",
        2
    ],
    "FW4 Revision": [
        "1046",
        "FW4 Revision",
        1
    ],
    "Event (index+7)": [
        "1096",
        "Event (index+7)",
        1
    ],
    "FW3 Revision": [
        "1044",
        "FW3 Revision",
        1
    ],
    "Event (index+6)": [
        "1095",
        "Event (index+6)",
        1
    ],
    "Delta 5k:Max Amb Temp": [
        "1152",
        "Delta 5k:Max Amb Temp",
        1
    ],
    "DC Life Wh": [
        "1076",
        "DC Life Wh",
        2
    ],
    "RTC_Month": [
        "1034",
        "RTC_Month",
        1
    ],
    "RTC_Day": [
        "1035",
        "RTC_Day",
        1
    ],
    "Adc Current": [
        "1069",
        "Adc Current",
        1
    ],
    "RTC_Hour": [
        "1036",
        "RTC_Hour",
        1
    ],
    "RTC_Second": [
        "1038",
        "RTC_Second",
        1
    ],
    "Event (index+0)": [
        "1089",
        "Event (index+0)",
        1
    ],
    "Measurement Index": [
        "1056",
        "Measurement Index",
        1
    ],
    "Event (index+8)": [
        "1097",
        "Event (index+8)",
        1
    ],
    "FW3 Date": [
        "1045",
        "FW3 Date",
        1
    ],
    "FW2 Date": [
        "1043",
        "FW2 Date",
        1
    ],
    "AC Life Runtime": [
        "53254",
        "AC Life Runtime",
        2
    ],
    "Event Index": [
        "1088",
        "Event Index",
        1
    ],
    "FW1 Revision": [
        "1040",
        "FW1 Revision",
        1
    ],
    "Adc Voltage": [
        "1068",
        "Adc Voltage",
        1
    ],
    "Today Wh": [
        "1072",
        "Today Wh",
        2
    ],
    "Serial number 2,3": [
        "40976",
        "Serial number 2,3",
        1
    ],
    "Delta 5k:Max InvHs Temp": [
        "1154",
        "Delta 5k:Max InvHs Temp",
        1
    ],
    "Today Runtime": [
        "1074",
        "Today Runtime",
        2
    ]
}
'''
Constant `INPUT_REGISTER` directory table. 
Take register name as key and value in `RegCol` format
'''
