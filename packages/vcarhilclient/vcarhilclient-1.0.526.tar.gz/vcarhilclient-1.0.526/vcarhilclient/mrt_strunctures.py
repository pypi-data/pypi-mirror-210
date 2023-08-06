from ctypes import *
from vcarhilclient.Enums import *
mrt_file_id_t = c_uint64
mrt_daq_handle_t = c_uint64
mrt_name_size = 128
class mrt_enviroment_info_t(Structure):
    _fields_ = [
        ("loaded_file_id", mrt_file_id_t), ("running_status", c_uint32)
    ]

class mrt_daq_info_t(Structure):
    _fields_ = [
        ("port_num", c_uint32), ("trigger_event_num", c_uint32),("period_ms", c_uint32),
        ("offset_ms", c_uint32),("msg_data_size", c_uint32)
    ]

class mrt_daq_port_cfg_t(Structure):
    _fields_ = [
        ("port_type", c_uint32), ("model_instance_name", c_char_p), ("port_name", c_char_p)
    ]

class mrt_daq_trigger_event_info_t(Structure):
    _fields_ = [
        ("model_instance_name", c_char*mrt_name_size), ("event_name",c_char*mrt_name_size)
    ]

class mrt_daq_port_info_t(Structure):
    _fields_ = [
        ("model_instance_name", c_char*mrt_name_size), ("port_name",c_char*mrt_name_size),
        ("port_type_name",c_char*mrt_name_size),
        ("port_type",mrt_port_type_t),("data_type",mrt_port_data_type_t),("data_size",c_uint32),
        ("array_size",c_uint32),("pos_in_daq_data",c_uint32)
    ]

class mrt_daq_msg_t(Structure):
    _fields_ = [("daq",mrt_daq_handle_t),
                ("port_idx",c_uint32),
                ("time_stamp_us",c_uint64),
                ("sn",c_uint32),
                ("data_size",c_uint32),
                ("data", c_void_p)]


class mrt_device_info_t(Structure):
    _fields_ = [("bus_id", c_uint32), ("bus_loc", c_uint32), ("dev_id", c_uint32), ("dev_sn", c_uint32),
                ("name", c_char*mrt_name_size), ("ch_num", c_uint32), ("state", c_int32)]

class mrt_channel_info_t(Structure):
    _fields_ = [("dev_type", c_uint16), ("dev_idx", c_uint16), ("state", c_int32)]

class mrt_gen_port_info_t(Structure):
    _fields_ = [("port_model", c_char*mrt_name_size),
                ("port_name", c_char*mrt_name_size),
                ("event_model", c_char*mrt_name_size),
                ("event_name", c_char*mrt_name_size),
                ("event_type", c_uint32),
                ("period_ms", c_uint32)]