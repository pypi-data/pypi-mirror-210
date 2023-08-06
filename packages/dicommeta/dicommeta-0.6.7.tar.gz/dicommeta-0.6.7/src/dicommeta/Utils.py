from datetime import date, datetime
from enum import Enum #verify, UNIQUE


def calculate_age(birth_str: str) -> int:
    today = date.today()
    birth_date = datetime.strptime(birth_str, '%Y%m%d')

    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def validator_parsable_date(instance, attribute, value):
    try:
        if value is not None:
            if isinstance(value, list):
                datetime.strptime(value[0], '%Y%m%d')
            else:
                datetime.strptime(value, '%Y%m%d')

    except ValueError:
        raise ValueError("Unable to parse value:" + value)


def validator_parsable_time(instance, attribute, value):
    try:
        if value is not None:
            if isinstance(value, list):
                datetime.strptime(value[0], '%H%M%S')
            else:
                datetime.strptime(value, '%H%M%S')
    except ValueError:
        raise ValueError("Unable to parse time:" + value)


def validator_pass(instance, attribute, value):
    pass


# @verify(UNIQUE) needs 3.11
class Mode(Enum):
    AR = "AR"
    AS = "AS"
    ASMT = "ASMT"
    AU = "AU"
    BDUS = "BDUS"
    BI = "BI"
    BMD = "BMD"
    CD = "CD"
    CF = "CF"
    CP = "CP"
    CR = "CR"
    CS = "CS"
    CT = "CT"
    DD = "DD"
    DF = "DF"
    DG = "DG"
    DM = "DM"
    DOC = "DOC"
    DS = "DS"
    DX = "DX"
    EC = "EC"
    ECG = "ECG"
    EPS = "EPS"
    ES = "ES"
    FA = "FA"
    FID = "FID"
    FS = "FS"
    GM = "GM"
    HC = "HC"
    HD = "HD"
    IO = "IO"
    IOL = "IOL"
    IVOCT = "IVOCT"
    IVUS = "IVUS"
    KER = "KER"
    KO = "KO"
    LEN = "LEN"
    LP = "LP"
    LS = "LS"
    MA = "MA"
    MG = "MG"
    MR = "MR"
    MS = "MS"
    NM = "NM"
    OAM = "OAM"
    OCT = "OCT"
    OP = "OP"
    OPM = "OPM"
    OPR = "OPR"
    OPT = "OPT"
    OPV = "OPV"
    OSS = "OSS"
    OT = "OT"
    PLAN = "PLAN"
    PR = "PR"
    PT = "PT"
    PX = "PX"
    REG = "REG"
    RESP = "RESP"
    RF = "RF"
    RG = "RG"
    RTDOSE = "RTDOSE"
    RTIMAGE = "RTIMAGE"
    RTPLAN = "RTPLAN"
    RTRECORD = "RTRECORD"
    RTSTRUCT = "RTSTRUCT"
    RWV = "RWV"
    SEG = "SEG"
    SM = "SM"
    SMR = "SMR"
    SR = "SR"
    SRF = "SRF"
    ST = "ST"
    STAIN = "STAIN"
    TG = "TG"
    US = "US"
    VA = "VA"
    VF = "VF"
    XA = "XA"
    XC = "XC"
