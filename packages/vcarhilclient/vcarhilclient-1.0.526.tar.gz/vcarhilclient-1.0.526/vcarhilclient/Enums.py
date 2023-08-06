from ctypes import *
from enum import Enum

class enum_base (c_int):
    def get_name(self):
        members= dir(self)
        for m in members:
            v = getattr(self, m)
            if ("MRT_" in m) and (v[0] == self.value):
                return m

class mrt_status_t(enum_base):
    MRT_STS_OK = 0,
    MRT_ERR_INVALID_ARG = -1,
    MRT_ERR_OBJECT_ALREADY_EXIST = -2,
    MRT_ERR_OBJECT_NOT_EXIST = -3,
    MRT_ERR_OBJECT_CREATE_FAIL = -4,
    MRT_ERR_CONNECT_FAIL = -5,
    MRT_ERR_RPC_CALL_FAIL = -6,
    MRT_ERR_RPC_SERVICE_NOT_AVAILABLE = -7,
    MRT_ERR_FILE_ID_NOT_MATCH = -8,
    MRT_ERR_RPC_CALL_TIMEOUT = -9,
    MRT_ERR_INVALID_NAME = -10,
    MRT_ERR_DAQ_DATA_OBJ_INVALID = -11,
    MRT_ERR_SVC_EXEC_ERROR = -12,
    MRT_ERR_NOT_IMPLEMENT = -13,
    MRT_ERR_INVALID_RPC_RESP_SIZE = -14,
    MRT_ERR_SVC_ROUTE_FAIL = -1024,
    MRT_VRPC_ERR_SVC_NOT_IMPLEMENTED = -1023,
    MRT_VRPC_ERR_SVC_MALLOC_FAIL = -1022,
    MRT_VRPC_ERR_SVC_IN_PROGRESS = -1021,
    MRT_VRPC_ERR_RESP_BUF_SIZE_INVALID = -1020,
    MRT_VRPC_ERR_TIMEOUT = -1019,
    MRT_VRPC_ERR_GENERIC_ERROR = -1018,
    MRT_VRPC_ERR_SVC_SIGNATURE_INVALID = -1017,
    MRT_VRPC_ERR_INVALID_ARG = -1016,
    MRT_VRPC_ERR_CLI_ENV_NAME_INVALID = -1015,
    MRT_VRPC_ERR_CLI_SOCK_INVALID = -1014,
    MRT_VRPC_ERR_CLI_INVALID_DATA_SIZE = -1013,
    MRT_VRPC_ERR_CLI_INVALID_FN_ID = -1012,
    MRT_VRPC_ERR_CLI_INVALID_SN = -1011,
    MRT_VRPC_ERR_CLI_INVALID_RESP = -1010,
    MRT_VRPC_ERR_CLI_RECV_FAIL = -1009,
    MRT_VRPC_ERR_CLI_SEND_FAIL = -1008,
    MRT_VRPC_ERR_CLI_MSG_INIT_FAIL = -1007,
    MRT_VRPC_ERR_CLI_ARG_INVALID = -1006,
    MRT_VRPC_ERR_SVC_ARG_INVALID = -1005,
    MRT_VRPC_ERR_MSG_DATA_INVALID = -1004,
    MRT_VRPC_ERR_MSG_INIT_FAIL = -1003,
    MRT_VRPC_ERR_DATA_SIZE_INVALID = -1002,
    MRT_VRPC_ERR_FN_ID_INVALID = -1001,
    NO_USE = -99


class mrt_port_type_t(enum_base):
    MRT_INPUT_PORT = 0,
    MRT_OUTPUT_PORT = 1,
    MRT_MEASUREMENT = 2,
    MRT_UNKNOWN_PORT = 3
    NO_USE = -99



class mrt_port_data_type_t(enum_base):
    MRT_DATA_TYPE_UINT8 = 0,
    MRT_DATA_TYPE_UINT16 = 1,
    MRT_DATA_TYPE_UINT32 = 2,
    MRT_DATA_TYPE_UINT64 = 3,
    MRT_DATA_TYPE_INT8 = 4,
    MRT_DATA_TYPE_INT16 = 5,
    MRT_DATA_TYPE_INT32 = 6,
    MRT_DATA_TYPE_INT64 = 7,
    MRT_DATA_TYPE_FLOAT32 = 8,
    MRT_DATA_TYPE_FLOAT64 = 9,
    MRT_DATA_TYPE_STRUCT = 10,
    NO_USE = -99


class fetch_value_type(enum_base):
    ON_DEMAND = 0,
    DAQ = 1,
    NO_USE = -99


class fetch_value_datatype(enum_base):
    RAW = 0,
    PHY = 1,
    NO_USE = -99

class mrt_log_level_t(enum_base):
    MRT_LOG_DEBUG = 0,
    MRT_LOG_INFO = 1
    MRT_LOG_WARNING = 2,
    MRT_LOG_ERROR = 3,
    MRT_LOG_CRITICAL = 4,
    MRT_LOG_FATAL = 5,
    MRT_LOG_LEVEL_NUM = 6,
    No_USE = -99

class drt_param_id_t(enum_base):
    DRT_PARAM_CH_BASE_ID = 0,
    DRT_PARAM_DIO_BASE_ID = 0x100,
    DRT_PARAM_AIO_BASE_ID = 0x200,
    DRT_PARAM_TIO_BASE_ID = 0x300,
    DRT_PARAM_CAN_BASE_ID = 0x400,
    DRT_PARAM_CAN_MODE_PARAM = 0x400,
    DRT_PARAM_CAN_TIMMING_PARAM = -1,
    DRT_PARAM_CANFD_TIMMING_PARAM = -2,
    NO_USE = -99

class drt_status_t(enum_base):
    DRT_STATUS_OK = 0,
    DRT_ERR_INVALID_TYPE = -1,
    DRT_ERR_INVALID_IDX = -2,
    DRT_ERR_INVALID_PTR = -3,
    DRT_ERR_INVALID_NUM = -4,
    DRT_ERR_INVALID_CTX = -5,
    DRT_ERR_INVALID_MODE = -6,
    DRT_ERR_INVALID_PARAM_ID = -7,
    DRT_ERR_INVALID_PARAM_SIZE = -8,
    DRT_ERR_INVALID_PARAM_VALUE = -9,
    DRT_ERR_INVALID_FD = -10,
    DRT_ERR_WRITE_FAIL = -11,
    DRT_ERR_READ_FAIL = -12,
    DRT_ERR_SETOPT_FAIL = -13,
    DRT_ERR_TIMEOUT = -14,
    DRT_ERR_NOT_SUPPORT = -15,
    DRT_ERR_GENERIC_ERROR = -16,
    DRT_ERR_MALLOC_FAIL = -17,
    DRT_ERR_NOT_IMPLEMENT = -18,
    NO_USE = -99

class drt_dev_channel_t(enum_base):
    DRT_DEV_ANALOG_INPUT_CH = 0,
    DRT_DEV_ANALOG_OUTPUT_CH = 1,
    DRT_DEV_DIGITAL_INPUT_CH = 2,
    DRT_DEV_DIGITAL_OUTPUT_CH = 3,
    DRT_DEV_TIMER_INPUT_CH = 4,
    DRT_DEV_TIMER_OUTPUT_CH = 5,
    DRT_DEV_CAN_CH = 6,
    DRT_DEV_LIN_CH = 7,
    DRT_DEV_ETH_CH = 8,
    DRT_DEV_VOLTAGE_VCH = 9,
    DRT_DEV_DIGITAL_VCH = 10,
    DRT_DEV_TIMER_VCH = 11,
    DRT_DEV_CAN_VCH = 12,
    DRT_DEV_LIN_VCH = 13,
    DRT_DEV_ETH_VCH_SWITCH = 14,
    DRT_DEV_ETH_VCH = 15,
    DRT_DEV_CH_NUM = 16,
    NO_USE = -99

class drt_env_channel_t(enum_base):
    DRT_ENV_ANALOG_INPUT_CH = 0,
    DRT_ENV_ANALOG_OUTPUT_CH = 1,
    DRT_ENV_DIGITAL_INPUT_CH = 2,
    DRT_ENV_DIGITAL_OUTPUT_CH = 3,
    DRT_ENV_TIMER_INPUT_CH = 4,
    DRT_ENV_TIMER_OUTPUT_CH = 5,
    DRT_ENV_CAN_CH = 6,
    DRT_ENV_LIN_CH = 1,
    DRT_ENV_ETH_CH = 1,
    DRT_ENV_CH_NUM = 1,
    NO_USE = -99

class ma_compute_method_type_t(enum_base):
    MA_CM_IDENTICAL = 0,
    MA_CM_FORM = 1,
    MA_CM_LINEAR = 2,
    MA_CM_RAT_FUNC = 3,
    MA_CM_TAB_INTP = 4,
    MA_CM_TAB_NOINTP = 5,
    MA_CM_TAB_VERB = 6,
    MA_CM_TAB_RANGE_VERB = 7,
    NO_USE = -99

class ma_status_t(enum_base):
    MA_STS_OK = 0,
    MA_ERR_INVALID_ARG = 1,
    MA_ERR_INIT_FAIL = 2,
    MA_ERR_MALLOC_FAIL = 3,
    MA_ERR_EMPTY = 4,
    MA_ERR_FULL = 5,
    MA_ERR_INVALID_DATA_PTR = 6,
    MA_ERR_INVALID_DATA_SIZE = 7,
    MA_ERR_INVALID_TYPE = 8,
    MA_ERR_LIST_IS_NOT_EMPTY = 9,
    MA_ERR_LIST_IS_EMPTY = 10,
    MA_ERR_INVALID_ENV = 11,
    MA_ERR_INVALID_NAME = 12,
    MA_ERR_INVALID_MODEL = 13,
    MA_ERR_INVALID_INSTANCE_PARAM = 14,
    MA_ERR_INVALID_OBJ_TYPE = 15,
    MA_ERR_INVALID_IDX = 16,
    MA_ERR_INVALID_FILE = 17,
    MA_ERR_OBJECT_EXISTED = 18,
    MA_ERR_OBJECT_CREATE_FAIL = 19,
    MA_ERR_GENERIC_WRITE_FAIL = 20,
    MA_ERR_GENERIC_READ_FAIL = 21,
    NO_USE = -99

class ma_port_data_type_t(enum_base):
    MA_DATA_TYPE_UINT8 = 0,
    MA_DATA_TYPE_UINT16 = 1,
    MA_DATA_TYPE_UINT32 = 2,
    MA_DATA_TYPE_UINT64 = 3,
    MA_DATA_TYPE_INT8 = 4,
    MA_DATA_TYPE_INT16 = 5,
    MA_DATA_TYPE_INT32 = 6,
    MA_DATA_TYPE_INT64 = 7,
    MA_DATA_TYPE_FLOAT32 = 8,
    MA_DATA_TYPE_FLOAT64 = 9,
    MA_DATA_TYPE_STRUCT = 10,
    MA_DATA_TYPE_UNKNOWN = 11,
    NO_USE = -99

class ma_data_layout_t(enum_base):
    MA_DATA_LAYOUT_NONE = 0

class ma_log_level_t(enum_base):
    MA_LOG_DEBUG = 0,
    MA_LOG_INFO = 1,
    MA_LOG_WARNING = 2,
    MA_LOG_ERROR = 3,
    MA_LOG_CRITICAL = 4,
    MA_LOG_FATAL = 5,
    MA_LOG_LEVEL_NUM = 6,
    NO_USE = -99

class ma_model_attrib_id_t(enum_base):
    MA_MODEL_ATTRIB_INSTANCE_DATA = 0,
    MA_MODEL_ATTRIB_START_FN = 1,
    MA_MODEL_ATTRIB_STOP_FN = 2,
    MA_MODEL_ATTRIB_DESTROY_FN = 3,
    MA_MODEL_ATTRIB_VERSION = 4,
    MA_MODEL_ATTRIB_DESCRIPTION = 5,
    MA_MODEL_ATTRIB_TYPE = 6,
    MA_MODEL_ATTRIB_ATOMIC_MODE = 7,
    MA_MODEL_ATTRIB_MODEL_NAME = 8,
    NO_USE = -99