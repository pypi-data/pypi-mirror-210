# Brownout / OTA Defines
SEP = "#" * 50
MINUTES_TO_BROWN_OUT = 5
TABLES_SYNC_MINUTES = 70
MINUTES_FOR_LC = 2
LATEST_FW = "1.9.0"
SINGLE_BAT_BO_DICT = {"2.4GhzOutputPower": 2, 'txPeriodMs': 75, 'rxTxPeriodMs': 255, 'energyPattern': 25}
DUAL_BAT_BO_DICT = {"2.4GhzOutputPower": 2, 'txPeriodMs': 75, 'rxTxPeriodMs': 255, 'energyPattern': 50}
LEGACY_BO_DICT = {'energyPattern': 17, 'rxTxPeriodMs': 99}
BO_DICT = {'energyPattern': 36}

# Configuration tool / change Brg/Gw Defines
ATC_GW_CONFIG = {
    'wifi': {'gwDataSrc': 'Bridges only (ch38)',
             'pacerInterval': 60,
             'txPeriodMs': 3,
             'rxTxPeriodMs': 90,
             'energizingPattern': 17,
             "2.4GhzOutputPower": 8},
    'lte': {},
    'mobile': {},
    'unknown': {}}
ATC_REGION_DICT = {
    'IL': {
        'sub1GhzFrequency': 919100,
        'energyPattern': 50
    }
}

energy_patterns = [18, 25, 26]
energy_patterns_db = {17: 50, 18: 51, 25: 56, 26: 57}
gw_rx_channel = {17: "Bridges only (ch39)", 18: "Bridges only (ch38)", 24: "Bridges only (ch39)",
                 25: "Bridges only (ch39)", 26: "Bridges only (ch39)", 51: "Bridges only (ch38)",
                 55: "Bridges only (ch39)", 56: "Bridges only (ch39)", 57: "Bridges only (ch39)",
                 50: "Bridges only (ch39)"}
shifted_brg_energy_patterns = [33, 34, 35, 58, 59, 60]
shifted_gw_energizing_patterns = [33]
lc_output_powers = [14, 17, 20, 23, 26, 29, 32]
fp_duty_cycles = [0.1, 0.15, 0.2, 0.25, 0.3]

# Power Mgmt
EXIT_POWER_MGMT_GW_DICT = {
    'gwDataSrc': gw_rx_channel[17],
    'txPeriodMs': 3,
    'rxTxPeriodMs': 15,
    'energizingPattern': 17,
    'gwMgmtMode': 'active'
}
KEEP_ALIVE_PERIOD = 30  # seconds
KEEP_ALIVE_SCAN_DURATION = 300  # in millisecond
SEC_TO_SEND = 2
BROADCAST_DST_MAC = 'FFFFFFFFFFFF'

colors = ['red', 'blue', 'yellow', 'cyan', 'green', 'brown', 'orange', 'pink', 'purple', 'black']

# Test Tool
WH_OWNER = '832742983939'
INIT_GW_CONFIG = {
    'wifi':{'gwDataSrc': gw_rx_channel[18],
        'txPeriodMs': 3,
        'rxTxPeriodMs': 255,
        'energizingPattern': 17,
        'pacerInterval': 60},
    'lte':{},
    'mobile':{},
    'unknown':{}}
INIT_BRG_CONFIG = {
    "energyPattern": 36,
    "2.4GhzOutputPower": 2,
    "sub1GhzOutputPower": 32,
    "sub1GhzFrequency": 919100,
    "rxTxPeriodMs": 15,
    "txPeriodMs": 5,
    "txProbability": 50,
    "otaUpgradeEnabled": 0,
    "pacerInterval": 15,
    "globalPacingGroup": 0}

BRG_KEYS = ['txPeriodMs', 'rxTxPeriodMs', 'energyPattern', 'pacerInterval', 'txProbability', '2.4GhzOutputPower',
            'otaUpgradeEnabled', 'globalPacingEnabled', 'sub1GhzOutputPower', 'sub1GhzFrequency', 'globalPacingGroup',
            'txRepetition']
GW_KEYS = ['gwDataSrc']
GW_KEYS_THIN = ['dataCoupling', 'useStaticLocation', 'gwMgmtMode']
GW_SHARED_KEYS = ['gw_2.4GhzOutputPower', 'gw_txPeriodMs', 'gw_pacerInterval', 'gw_energizingPattern',
                  'gw_rxTxPeriodMs']
TIME_COLUMNS = ['endTimestamp', 'startTimestamp', 'receivedTestConfigTimestamp']
TEST_CONFIG_COLUMNS = ['testId', 'testTimeMins', 'gatewaysIncluded', 'bridgesIncluded']
