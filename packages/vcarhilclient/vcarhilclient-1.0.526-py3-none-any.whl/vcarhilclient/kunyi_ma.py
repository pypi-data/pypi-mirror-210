from ctypes import *
from ctypes import wintypes
import os
import pathlib

from kunyi_util import *

CDLL(r"D:\work\mrt_test\mrtd\mrtd_w64\bin\jsoncpp.dll")

dll_path = os.path.join(pathlib.Path(__file__).parent, "ma.vcar.dll")
ma_lib = CDLL(dll_path)
from Enums import *


class ma_enviroment():
    def __init__(self):
        self.current_env_p = None
        self.freed = False

    def create(self):
        rc = ma_status_t()
        rc.value = -99
        ma_lib.ma_enviroment_create.argtypes = [POINTER(ma_status_t)]
        ma_lib.ma_enviroment_create.restype = c_void_p
        self.current_env_p = ma_lib.ma_enviroment_create(pointer(rc))
        self.freed = False

        return rc, self.current_env_p

    def free(self):
        if self.current_env_p == None:
            return -99
        ma_lib.ma_enviroment_free.argtypes = [c_void_p]
        ma_lib.ma_enviroment_free.restype = ma_status_t
        rc = ma_lib.ma_enviroment_free(self.current_env_p)
        self.freed = True
        return rc


class ma_model():
    def __init__(self):
        self.model_handel = None
        self.freed = False
        self.ma_json_obj = None

    def new_ma_model_instance(self):
        rc = ma_status_t()
        rc.value = -99
        ma_lib.ma_model_instance_new.argtypes = [POINTER(ma_status_t)]
        ma_lib.ma_model_instance_new.restype = c_void_p
        self.model_handel = ma_lib.ma_model_instance_new(pointer(rc))
        self.freed = False
        return rc, self.model_handel

    def init_ma_model_instance(self, name, input_port_num, output_port_num, measurement_num,
                               calibration_num, event_num, runnable_num):
        bs = name.encode('utf-8')
        mn_pointer = c_char_p(bs)
        ma_lib.ma_model_instance_init.argtypes = [c_void_p, c_char_p, c_uint32, c_uint32, c_uint32, c_uint32,
                                                  c_uint32, c_uint32]
        ma_lib.ma_model_instance_init.restype = ma_status_t
        error_code = ma_lib.ma_model_instance_init(self.model_handel, mn_pointer, input_port_num, output_port_num,
                                                   measurement_num, calibration_num, event_num, runnable_num)
        return error_code

    def create_ma_model_instance(self, name, input_port_num, output_port_num, measurement_num,
                                 calibration_num, event_num, runnable_num):
        bs = name.encode('utf-8')
        mn_pointer = c_char_p(bs)

        rc = ma_status_t()
        rc.value = -99

        ma_lib.ma_model_instance_create.argtypes = [c_char_p, c_uint32, c_uint32, c_uint32, c_uint32,
                                                    c_uint32, c_uint32, POINTER(ma_status_t)]
        ma_lib.ma_model_instance_create.restype = c_void_p
        self.model_handel = ma_lib.ma_model_instance_create(mn_pointer, input_port_num, output_port_num,
                                                            measurement_num, calibration_num, event_num,
                                                            runnable_num, pointer(rc))
        self.freed = False

    def free_ma_model_instance(self):
        ma_lib.ma_model_instance_free.argtypes = [c_void_p]
        ma_lib.ma_model_instance_free.restype = ma_status_t
        error_code = ma_lib.ma_model_instance_free(self.model_handel)
        self.freed = True
        return error_code

    def meta_ma_model_get_input_port(self, idx):
        ma_lib.ma_model_get_input_port_meta.argtypes = [c_void_p, c_uint32]
        ma_lib.ma_model_get_input_port_meta.restype = c_void_p
        input_port_meta = ma_lib.ma_model_get_input_port_meta(self.model_handel, idx)
        return input_port_meta

    def meta_ma_model_get_output_port(self, idx):
        ma_lib.ma_model_get_output_port_meta.argtypes = [c_void_p, c_uint32]
        ma_lib.ma_model_get_output_port_meta.restype = c_void_p
        output_port_meta = ma_lib.ma_model_get_output_port_meta(self.model_handel, idx)
        return output_port_meta

    def meta_ma_model_set_input_port(self, idx):
        ma_lib.ma_model_set_input_port_meta.argtypes = [c_void_p, c_uint32, c_void_p]
        ma_lib.ma_model_set_input_port_meta.restype = ma_status_t
        meta = self.meta_ma_model_get_input_port(idx)
        error_code = ma_lib.ma_model_set_input_port_meta(self.model_handel, idx, meta)
        return error_code

    def meta_ma_model_set_output_port(self, idx):
        ma_lib.ma_model_set_output_port_meta.argtypes = [c_void_p, c_uint32, c_void_p]
        ma_lib.ma_model_set_output_port_meta.restype = ma_status_t
        meta = self.meta_ma_model_get_output_port(idx)
        error_code = ma_lib.ma_model_set_output_port_meta(self.model_handel, idx, meta)
        return error_code

    def meta_ma_model_get_port(self):
        port_handle = c_void_p
        ma_lib.ma_model_get_port_meta.argtypes = [c_void_p]
        ma_lib.ma_model_get_port_meta.restype = c_void_p
        ma_lib.ma_model_get_port_meta(port_handle)
        return port_handle

    def model_get_port_name(self):
        ma_lib.ma_model_get_port_name.argtypes = [c_void_p]
        ma_lib.ma_model_get_port_name.restype = c_char
        port_handle = self.meta_ma_model_get_port()
        port_name = ma_lib.ma_model_get_port_name(port_handle)
        return port_name

    @staticmethod
    def input_port_conn_callback(this_port, peer_port):
        print(this_port, peer_port)

    @staticmethod
    def input_port_disconn_callback(this_port, peer_port):
        print(this_port, peer_port)

    @staticmethod
    def output_port_conn_callback(this_port, peer_port):
        print(this_port, peer_port)

    @staticmethod
    def output_port_disconn_callback(this_port, peer_port):
        print(this_port, peer_port)

    def ma_model_set_input_port_conn_callback(self, idx):
        callback = CFUNCTYPE(None, c_void_p, c_void_p)
        ma_lib.ma_model_set_input_port_conn_callback.argtypes = [c_void_p, c_uint32, callback]
        ma_lib.ma_model_set_input_port_conn_callback.restype = ma_status_t
        my_callback = callback(self.input_port_conn_callback)
        error_code = ma_lib.ma_model_set_input_port_conn_callback(self.model_handel, idx, my_callback)
        return error_code

    def ma_model_set_output_port_conn_callback(self, idx):
        callback = CFUNCTYPE(None, c_void_p, c_void_p)
        ma_lib.ma_model_set_output_port_conn_callback.argtypes = [c_void_p, c_uint32, callback]
        ma_lib.ma_model_set_output_port_conn_callback.restype = ma_status_t
        my_callback = callback(self.output_port_conn_callback)
        error_code = ma_lib.ma_model_set_output_port_conn_callback(self.model_handel, idx, my_callback)
        return error_code

    def ma_model_set_input_port_disconn_callback(self, idx):
        callback = CFUNCTYPE(None, c_void_p, c_void_p)
        ma_lib.ma_model_set_input_port_disconn_callback.argtypes = [c_void_p, c_uint32, callback]
        ma_lib.ma_model_set_input_port_disconn_callback.restype = ma_status_t
        my_callback = callback(self.input_port_disconn_callback)
        error_code = ma_lib.ma_model_set_input_port_disconn_callback(self.model_handel, idx, my_callback)
        return error_code

    def ma_model_set_output_port_disconn_callback(self, idx):
        callback = CFUNCTYPE(None, c_void_p, c_void_p)
        ma_lib.ma_model_set_output_port_disconn_callback.argtypes = [c_void_p, c_uint32, callback]
        ma_lib.ma_model_set_output_port_disconn_callback.restype = ma_status_t
        my_callback = callback(self.output_port_disconn_callback)
        error_code = ma_lib.ma_model_set_output_port_disconn_callback(self.model_handel, idx, my_callback)
        return error_code

    def ma_model_set_input_port(self, idx, name, prt, data_type, unit_size, array_size, queue_size):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        prt_pointer = c_void_p(prt)

        ma_lib.ma_model_set_input_port.argtypes = [c_void_p, c_uint32, c_char_p, c_void_p,
                                                   c_int32, c_uint32, c_uint32, c_uint32]
        ma_lib.ma_model_set_input_port.restype = ma_status_t
        error_code = ma_lib.ma_model_set_input_port(self.model_handel, idx, name_pointer, prt_pointer,
                                                    data_type[0], unit_size, array_size, queue_size)
        return error_code

    def ma_model_set_input_struct_name(self, idx, name):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)

        ma_lib.ma_model_set_input_struct_name.argtypes = [c_void_p, c_uint32, c_char_p]
        ma_lib.ma_model_set_input_struct_name.restype = ma_status_t
        error_code = ma_lib.ma_model_set_input_struct_name(self.model_handel, idx, name_pointer)
        return error_code

    def ma_model_get_input_struct_name(self, idx):
        ma_lib.ma_model_get_input_struct_name.argtypes = [c_void_p, c_uint32]
        ma_lib.ma_model_get_input_struct_name.restype = c_char_p
        input_struct_name = ma_lib.ma_model_get_input_struct_name(self.model_handel, idx)
        return input_struct_name

    def ma_model_set_output_port(self, idx, name, prt, data_type, unit_size, array_size, queue_size):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        prt_pointer = c_void_p(prt)

        ma_lib.ma_model_set_output_port.argtypes = [c_void_p, c_uint32, c_char_p, c_void_p,
                                                    c_int32, c_uint32, c_uint32, c_uint32]
        ma_lib.ma_model_set_output_port.restype = ma_status_t
        error_code = ma_lib.ma_model_set_output_port(self.model_handel, idx, name_pointer, prt_pointer,
                                                     data_type[0], unit_size, array_size, queue_size)
        return error_code

    def ma_model_set_output_struct_name(self, idx, name):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)

        ma_lib.ma_model_set_output_struct_name.argtypes = [c_void_p, c_uint32, c_char_p]
        ma_lib.ma_model_set_output_struct_name.restype = ma_status_t
        error_code = ma_lib.ma_model_set_output_struct_name(self.model_handel, idx, name_pointer)
        return error_code

    def ma_model_get_output_struct_name(self, idx):
        ma_lib.ma_model_get_output_struct_name.argtypes = [c_void_p, c_uint32]
        ma_lib.ma_model_get_output_struct_name.restype = c_char_p
        output_struct_name = ma_lib.ma_model_get_output_struct_name(self.model_handel, idx)
        return output_struct_name

    def ma_model_set_measurement(self, idx, name, prt, data_type, unit_size, array_size):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        prt_pointer = c_void_p(prt)

        ma_lib.ma_model_set_measurement.argtypes = [c_void_p, c_uint32, c_char_p, c_void_p,
                                                    c_int32, c_uint32, c_uint32]
        ma_lib.ma_model_set_measurement.restype = ma_status_t
        error_code = ma_lib.ma_model_set_measurement(self.model_handel, idx, name_pointer, prt_pointer,
                                                     data_type[0], unit_size, array_size)
        return error_code

    def ma_model_set_measurement_struct_name(self, idx, name):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)

        ma_lib.ma_model_set_measurement_struct_name.argtypes = [c_void_p, c_uint32, c_char_p]
        ma_lib.ma_model_set_measurement_struct_name.restype = ma_status_t
        error_code = ma_lib.ma_model_set_measurement_struct_name(self.model_handel, idx, name_pointer)
        return error_code

    def ma_model_get_measurement_struct_name(self, idx):
        ma_lib.ma_model_get_measurement_struct_name.argtypes = [c_void_p, c_uint32]
        ma_lib.ma_model_get_measurement_struct_name.restype = c_char_p
        measurement_struct_name = ma_lib.ma_model_get_measurement_struct_name(self.model_handel, idx)
        return measurement_struct_name

    def ma_model_set_event(self, idx, name):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)

        ma_lib.ma_model_set_event.argtypes = [c_void_p, c_uint32, c_char_p]
        ma_lib.ma_model_set_event.restype = ma_status_t
        error_code = ma_lib.ma_model_set_event(self.model_handel, idx, name_pointer)
        return error_code

    @staticmethod
    def runnable_fn_t(model, param):
        print(model, param)

    def ma_model_set_runnable(self, idx, name, param):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        param_pointer = c_void_p(param)
        callback = CFUNCTYPE(None, c_void_p, c_void_p)

        ma_lib.ma_model_set_event.argtypes = [c_void_p, c_uint32, c_char_p, callback, c_void_p]
        ma_lib.ma_model_set_event.restype = ma_status_t
        my_callback = callback(self.runnable_fn_t)
        error_code = ma_lib.ma_model_set_event(self.model_handel, idx, name_pointer, my_callback, param_pointer)
        return error_code

    def ma_model_set_runnable_active_pattern(self, idx, pattern):
        ma_lib.ma_model_set_runnable_active_pattern.argtypes = [c_void_p, c_uint32, c_uint64]
        ma_lib.ma_model_set_runnable_active_pattern.restype = ma_status_t
        error_code = ma_lib.ma_model_set_runnable_active_pattern(self.model_handel, idx, pattern)
        return error_code

    def ma_model_set_input_listener_runnable(self, input_idx, runnable_idx):
        ma_lib.ma_model_set_input_listener_runnable.argtypes = [c_void_p, c_uint32, c_uint32]
        ma_lib.ma_model_set_input_listener_runnable.restype = ma_status_t
        error_code = ma_lib.ma_model_set_input_listener_runnable(self.model_handel, input_idx, runnable_idx)
        return error_code

    def ma_model_set_input_listener_runnable_with_event_flag(self, input_idx, runnable_idx, evt_flag):
        ma_lib.ma_model_set_input_listener_runnable_with_event_flag.argtypes = [c_void_p, c_uint32, c_uint32, c_uint64]
        ma_lib.ma_model_set_input_listener_runnable_with_event_flag.restype = ma_status_t
        error_code = ma_lib.ma_model_set_input_listener_runnable_with_event_flag(self.model_handel,
                                                                                 input_idx, runnable_idx, evt_flag)
        return error_code

    def ma_model_add_input_port(self, idx, name, prt, data_type, unit_size, array_size, queue_size):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        prt_pointer = c_void_p(prt)

        ma_lib.ma_model_add_input_port.argtypes = [c_void_p, c_uint32, c_char_p, c_void_p,
                                                   c_int32, c_uint32, c_uint32, c_uint32]
        ma_lib.ma_model_add_input_port.restype = ma_status_t
        error_code = ma_lib.ma_model_add_input_port(self.model_handel, idx, name_pointer, prt_pointer,
                                                    data_type[0], unit_size, array_size, queue_size)
        return error_code

    def ma_model_add_output_port(self, idx, name, prt, data_type, unit_size, array_size, queue_size):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        prt_pointer = c_void_p(prt)

        ma_lib.ma_model_add_output_port.argtypes = [c_void_p, c_uint32, c_char_p, c_void_p,
                                                    c_int32, c_uint32, c_uint32, c_uint32]
        ma_lib.ma_model_add_output_port.restype = ma_status_t
        error_code = ma_lib.ma_model_add_output_port(self.model_handel, idx, name_pointer, prt_pointer,
                                                     data_type[0], unit_size, array_size, queue_size)
        return error_code

    def ma_model_add_measurement(self, idx, name, prt, data_type, unit_size, array_size):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        prt_pointer = c_void_p(prt)

        ma_lib.ma_model_add_measurement.argtypes = [c_void_p, c_uint32, c_char_p, c_void_p,
                                                    c_int32, c_uint32, c_uint32]
        ma_lib.ma_model_add_measurement.restype = ma_status_t
        error_code = ma_lib.ma_model_add_measurement(self.model_handel, idx, name_pointer, prt_pointer,
                                                     data_type[0], unit_size, array_size)
        return error_code

    def ma_model_add_event(self, idx, name):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)

        ma_lib.ma_model_add_event.argtypes = [c_void_p, c_uint32, c_char_p]
        ma_lib.ma_model_add_event.restype = ma_status_t
        error_code = ma_lib.ma_model_add_event(self.model_handel, idx, name_pointer)
        return error_code

    @staticmethod
    def runnable_fn_t_add(model, param):
        print(model, param)

    def ma_model_add_runnable(self, idx, name, param):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        param_pointer = c_void_p(param)
        callback = CFUNCTYPE(None, c_void_p, c_void_p)

        ma_lib.ma_model_add_runnable.argtypes = [c_void_p, c_uint32, c_char_p, callback, c_void_p]
        ma_lib.ma_model_add_runnable.restype = ma_status_t
        my_callback = callback(self.runnable_fn_t_add)
        error_code = ma_lib.ma_model_add_runnable(self.model_handel, idx, name_pointer, my_callback, param_pointer)
        return error_code

    def ma_model_set_calibration(self, idx, name, p_value, value_prt_size, value_array_size, axis_num):
        bs = name.encode('utf-8')
        name_pointer = c_char_p(bs)
        value_pointer = c_void_p(p_value)

        ma_lib.ma_model_set_calibration.argtypes = [c_void_p, c_uint32, c_char_p, c_void_p,
                                                    c_int32, c_uint32, c_uint32, c_uint32]
        ma_lib.ma_model_set_calibration.restype = ma_status_t
        error_code = ma_lib.ma_model_set_calibration(self.model_handel, idx, name_pointer, value_pointer
                                                     , value_prt_size, value_array_size, axis_num)
        return error_code

    def ma_model_set_cal_axis(self, cal_idx, axis_idx, p_axis, axis_unit_size, axis_array_size, p_axis_value):
        axis_pointer = c_void_p(p_axis)
        axis_value_pointer = c_void_p(p_axis_value)

        ma_lib.ma_model_set_cal_axis.argtypes = [c_void_p, c_uint32, c_uint32, c_void_p,
                                                 c_int32, c_uint32, c_void_p]
        ma_lib.ma_model_set_cal_axis.restype = ma_status_t
        error_code = ma_lib.ma_model_set_cal_axis(self.model_handel, cal_idx, axis_idx, axis_pointer, axis_unit_size
                                                  , axis_array_size, axis_value_pointer)
        return error_code

    def ma_model_set_attribute(self, attrib_id, data,
                               struct_detail, item_count=1, data_type="UTF8", **sub_struct_detail):
        python_bytes = kunyi_util.data_to_bytes(data_type, data, item_count,
                                                struct_detail, **sub_struct_detail)
        arr = bytearray.fromhex(python_bytes.hex())
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        data_size = kunyi_util.get_signal_bytes_length(data_type, item_count,
                                                       struct_detail, **sub_struct_detail)
        ma_lib.ma_model_set_attribute.argtypes = [c_void_p, c_uint32, c_void_p,
                                                  POINTER(c_int)]
        ma_lib.ma_model_set_attribute.restype = ma_status_t
        error_code = ma_lib.ma_model_set_attribute(self.model_handel, attrib_id[0], buf_c, pointer(data_size))
        return error_code

    def ma_model_get_attribute(self, attrib_id, struct_detail, item_count=1, data_type="UTF8", **sub_struct_detail):
        data_size = kunyi_util.get_signal_bytes_length(data_type, item_count, struct_detail, **sub_struct_detail)

        arr = bytearray(data_size)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        data_size_pointer = pointer(data_size)
        ma_lib.ma_model_set_attribute.argtypes = [c_void_p, c_uint32, c_void_p,
                                                  POINTER(c_int)]
        ma_lib.ma_model_set_attribute.restype = ma_status_t
        error_code = ma_lib.ma_model_set_attribute(self.model_handel, attrib_id[0], buf_c, data_size_pointer)
        attribute_value = kunyi_util.bytes_to_data(data_type, arr, item_count, struct_detail, **sub_struct_detail)
        return error_code, attribute_value

    def ma_model_write_output_ts(self, idx, data, data_type, data_size, array_size, ts_us):
        data_pointer = c_void_p(data)

        ma_lib.ma_model_write_output_ts.argtypes = [c_void_p, c_uint32, c_void_p,
                                                    c_int32, c_uint32, c_uint32, c_uint64]
        ma_lib.ma_model_write_output_ts.restype = ma_status_t
        error_code = ma_lib.ma_model_write_output_ts(self.model_handel, idx, data_pointer,
                                                     data_type[0], data_size, array_size, ts_us)
        return error_code

    def ma_model_write_output(self, idx, data, data_type, data_size, array_size):
        data_pointer = c_void_p(data)

        ma_lib.ma_model_write_output.argtypes = [c_void_p, c_uint32, c_void_p,
                                                 c_int32, c_uint32, c_uint32]
        ma_lib.ma_model_write_output.restype = ma_status_t
        error_code = ma_lib.ma_model_write_output(self.model_handel, idx, data_pointer,
                                                  data_type[0], data_size, array_size)
        return error_code

    def ma_model_read_input_ts(self, idx, data, data_type, data_size, array_size, ts_us):
        data_pointer = c_void_p(data)
        ts_us_data_pointer = c_void_p(ts_us)

        ma_lib.ma_model_read_input_ts.argtypes = [c_void_p, c_uint32, c_void_p,
                                                  c_int32, c_uint32, c_uint32, c_uint64]
        ma_lib.ma_model_read_input_ts.restype = ma_status_t
        error_code = ma_lib.ma_model_read_input_ts(self.model_handel, idx, data_pointer,
                                                   data_type[0], data_size, array_size, ts_us_data_pointer)
        return error_code, data_pointer

    def ma_model_read_input(self, idx, data, data_type, data_size, array_size):
        data_pointer = c_void_p(data)
        ma_lib.ma_model_read_input.argtypes = [c_void_p, c_uint32, c_void_p,
                                               c_int32, c_uint32, c_uint32]
        ma_lib.ma_model_read_input.restype = ma_status_t
        error_code = ma_lib.ma_model_read_input(self.model_handel, idx, data_pointer,
                                                data_type[0], data_size, array_size)
        return error_code, data_pointer

    def ma_model_fire_event(self, idx):
        ma_lib.ma_model_fire_event.argtypes = [c_void_p, c_uint32]
        ma_lib.ma_model_fire_event.restype = ma_status_t
        error_code = ma_lib.ma_model_fire_event(self.model_handel, idx)
        return error_code

    def ma_model_update_output_ports(self):
        ma_lib.ma_model_update_output_ports.argtypes = [c_void_p]
        ma_lib.ma_model_update_output_ports.restype = ma_status_t
        error_code = ma_lib.ma_model_update_output_ports(self.model_handel)
        return error_code

    def ma_checksum_init(self, lib_name):
        lib_name_b = lib_name.encode('utf-8')
        p_lib_name = c_char_p(lib_name_b)
        ma_lib.ma_checksum_init.argtypes = [c_char_p]
        ma_lib.ma_checksum_init.restype = ma_status_t
        error_code = ma_lib.ma_checksum_init(p_lib_name)
        return error_code

    def ma_checksum_deinit(self):
        ma_lib.ma_checksum_deinit.restype = ma_status_t
        error_code = ma_lib.ma_checksum_deinit()
        return error_code

    def ma_checksum_add_crc8_algorithm(self, alg_name, poly, init, final_xor):
        alg_b = alg_name.encode('utf-8')
        p_alg_name = c_char_p(alg_b)
        ma_lib.ma_checksum_add_crc8_algorithm.argtypes = [c_char_p, c_uint8, c_uint8, c_uint8]
        ma_lib.ma_checksum_add_crc8_algorithm.restype = ma_status_t
        error_code = ma_lib.ma_checksum_add_crc8_algorithm(p_alg_name, poly, init, final_xor)
        return error_code

    def ma_checksum_add_crc16_algorithm(self, alg_name, poly, init, final_xor):
        alg_b = alg_name.encode('utf-8')
        p_alg_name = c_char_p(alg_b)
        ma_lib.ma_checksum_add_crc16_algorithm.argtypes = [c_char_p, c_uint16, c_uint16, c_uint16]
        ma_lib.ma_checksum_add_crc16_algorithm.restype = ma_status_t
        error_code = ma_lib.ma_checksum_add_crc16_algorithm(p_alg_name, poly, init, final_xor)
        return error_code

    def ma_checksum_add_crc32_algorithm(self, alg_name, poly, init, final_xor):
        alg_b = alg_name.encode('utf-8')
        p_alg_name = c_char_p(alg_b)
        ma_lib.ma_checksum_add_crc32_algorithm.argtypes = [c_char_p, c_uint32, c_uint32, c_uint32]
        ma_lib.ma_checksum_add_crc32_algorithm.restype = ma_status_t
        error_code = ma_lib.ma_checksum_add_crc32_algorithm(p_alg_name, poly, init, final_xor)
        return error_code

    def ma_checksum_add_crc64_algorithm(self, alg_name, poly, init, final_xor):
        alg_b = alg_name.encode('utf-8')
        p_alg_name = c_char_p(alg_b)
        ma_lib.ma_checksum_add_crc64_algorithm.argtypes = [c_char_p, c_uint64, c_uint64, c_uint64]
        ma_lib.ma_checksum_add_crc64_algorithm.restype = ma_status_t
        error_code = ma_lib.ma_checksum_add_crc64_algorithm(p_alg_name, poly, init, final_xor)
        return error_code

    def ma_checksum_add_custom_algorithm(self, alg_name, result_size):
        alg_b = alg_name.encode('utf-8')
        p_alg_name = c_char_p(alg_b)
        ma_lib.ma_checksum_add_custom_algorithm.argtypes = [c_char_p, c_int]
        ma_lib.ma_checksum_add_custom_algorithm.restype = ma_status_t
        error_code = ma_lib.ma_checksum_add_custom_algorithm(p_alg_name, result_size)
        return error_code

    def ma_checksum_remove_algorithm(self, alg_name):
        alg_b = alg_name.encode('utf-8')
        p_alg_name = c_char_p(alg_b)
        ma_lib.ma_checksum_remove_algorithm.argtypes = [c_char_p]
        ma_lib.ma_checksum_remove_algorithm.restype = ma_status_t
        error_code = ma_lib.ma_checksum_remove_algorithm(p_alg_name)
        return error_code

    def ma_checksum_calc(self, alg_name, data, data_len, result):
        alg_b = alg_name.encode('utf-8')
        p_alg_name = c_char_p(alg_b)
        data_p = c_void_p(data)
        result_p = c_void_p(result)
        ma_lib.ma_checksum_calc.argtypes = [c_char_p, c_void_p, c_int, c_void_p]
        ma_lib.ma_checksum_calc.restype = ma_status_t
        error_code = ma_lib.ma_checksum_calc(p_alg_name, data_p, data_len, result_p)
        return error_code

    def ma_model_import_meta(self, instance_param_str):
        instance_b = instance_param_str.encode('utf-8')
        p_instance_param_str = c_char_p(instance_b)
        ma_json_obj_p = c_void_p(self.ma_json_obj)

        ma_lib.ma_model_import_meta.argtypes = [c_void_p, c_char_p, c_void_p]
        ma_lib.ma_model_import_meta.restype = ma_status_t
        error_code = ma_lib.ma_model_import_meta(self.model_handel, p_instance_param_str, ma_json_obj_p)
        return error_code

    def ma_json_obj_create(self):
        arr = bytearray(512)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)
        ma_lib.ma_json_obj_create.argtypes = [c_void_p]
        ma_lib.ma_json_obj_create.restype = c_void_p
        self.ma_json_obj = ma_lib.ma_json_obj_create(buf_c)
        return self.ma_json_obj

    def ma_json_obj_free(self):
        ma_lib.ma_json_obj_free.argtypes = [c_void_p]
        ma_lib.ma_json_obj_free.restype = ma_status_t
        error_code = ma_lib.ma_json_obj_free(self.ma_json_obj)
        return error_code

    def ma_json_read_file(self, file_name):
        file_name_b = file_name.encode('utf-8')
        p_file_name = c_char_p(file_name_b)
        ma_lib.ma_json_read_file.argtypes = [c_char_p, c_void_p]
        ma_lib.ma_json_read_file.restype = ma_status_t
        error_code = ma_lib.ma_json_read_file(p_file_name, self.ma_json_obj)
        return error_code

    def ma_json_write_file(self, file_name):
        file_name_b = file_name.encode('utf-8')
        p_file_name = c_char_p(file_name_b)
        ma_lib.ma_json_write_file.argtypes = [c_char_p, c_void_p]
        ma_lib.ma_json_write_file.restype = ma_status_t
        error_code = ma_lib.ma_json_write_file(p_file_name, self.ma_json_obj)
        return error_code

    def ma_json_parse_string(self, json_str):
        json_str_b = json_str.encode('utf-8')
        p_json_str = c_char_p(json_str_b)
        ma_lib.ma_json_parse_string.argtypes = [c_char_p, c_void_p]
        ma_lib.ma_json_parse_string.restype = ma_status_t
        error_code = ma_lib.ma_json_parse_string(p_json_str, self.ma_json_obj)
        return error_code

    def ma_json_get_obj(self, name):
        name_b = name.encode('utf-8')
        p_name = c_char_p(name_b)
        p_val = c_void_p()
        ma_lib.ma_json_get_obj.argtypes = [c_void_p, c_char_p, c_void_p]
        ma_lib.ma_json_get_obj.restype = ma_status_t
        error_code = ma_lib.ma_json_get_obj(self.ma_json_obj, p_name, byref(p_val))
        return error_code, p_val

    def ma_json_set_obj(self, name, val):
        name_b = name.encode('utf-8')
        p_name = c_char_p(name_b)
        p_val = c_void_p(val)
        ma_lib.ma_json_set_obj.argtypes = [c_void_p, c_char_p, c_void_p]
        ma_lib.ma_json_set_obj.restype = ma_status_t
        error_code = ma_lib.ma_json_set_obj(self.ma_json_obj, p_name, p_val)
        return error_code, p_val

    def ma_json_append_obj(self, val):
        p_val = c_void_p(val)
        ma_lib.ma_json_append_obj.argtypes = [c_void_p, c_void_p]
        ma_lib.ma_json_append_obj.restype = ma_status_t
        error_code = ma_lib.ma_json_append_obj(self.ma_json_obj, p_val)
        return error_code

    def ma_json_append_bool(self, bool_val):
        c_val = c_bool(bool_val)
        ma_lib.ma_json_append_bool.argtypes = [c_void_p, c_bool]
        ma_lib.ma_json_append_bool.restype = ma_status_t
        error_code = ma_lib.ma_json_append_bool(self.ma_json_obj, c_val)
        return error_code

    def ma_json_append_int(self, int_val):
        c_val = c_int(int_val)
        ma_lib.ma_json_append_int.argtypes = [c_void_p, c_int]
        ma_lib.ma_json_append_int.restype = ma_status_t
        error_code = ma_lib.ma_json_append_int(self.ma_json_obj, c_val)
        return error_code

    def ma_json_append_int64(self, int64_val):
        c_val = c_int64(int64_val)
        ma_lib.ma_json_append_int64.argtypes = [c_void_p, c_int64]
        ma_lib.ma_json_append_int64.restype = ma_status_t
        error_code = ma_lib.ma_json_append_int64(self.ma_json_obj, c_val)
        return error_code

    def ma_json_append_double(self, double_val):
        c_val = c_double(double_val)
        ma_lib.ma_json_append_double.argtypes = [c_void_p, c_double]
        ma_lib.ma_json_append_double.restype = ma_status_t
        error_code = ma_lib.ma_json_append_double(self.ma_json_obj, c_val)
        return error_code

    def ma_json_append_string(self, val_string):
        val_string_b = val_string.encode('utf-8')
        p_string = c_char_p(val_string_b)
        ma_lib.ma_json_append_string.argtypes = [c_void_p, c_char_p]
        ma_lib.ma_json_append_string.restype = ma_status_t
        error_code = ma_lib.ma_json_append_string(self.ma_json_obj, p_string)
        return error_code

    def ma_json_get_obj_in_array(self, idx):
        p_val = c_void_p()
        ma_lib.ma_json_get_obj_in_array.argtypes = [c_void_p, c_int, c_void_p]
        ma_lib.ma_json_get_obj_in_array.restype = ma_status_t
        error_code = ma_lib.ma_json_get_obj_in_array(self.ma_json_obj, idx, byref(p_val))
        return error_code, p_val

    def ma_json_set_value_int(self, int_val):
        c_val = c_int(int_val)
        ma_lib.ma_json_set_value_int.argtypes = [c_void_p, c_int]
        ma_lib.ma_json_set_value_int.restype = ma_status_t
        error_code = ma_lib.ma_json_set_value_int(self.ma_json_obj, c_val)
        return error_code

    def ma_json_set_value_bool(self, bool_val):
        c_val = c_bool(bool_val)
        ma_lib.ma_json_set_value_bool.argtypes = [c_void_p, c_bool]
        ma_lib.ma_json_set_value_bool.restype = ma_status_t
        error_code = ma_lib.ma_json_set_value_bool(self.ma_json_obj, c_val)
        return error_code

    def ma_json_set_value_int64(self, int64_val):
        c_val = c_int64(int64_val)
        ma_lib.ma_json_set_value_int64.argtypes = [c_void_p, c_int64]
        ma_lib.ma_json_set_value_int64.restype = ma_status_t
        error_code = ma_lib.ma_json_set_value_int64(self.ma_json_obj, c_val)
        return error_code

    def ma_json_set_value_double(self, double_val):
        c_val = c_double(double_val)
        ma_lib.ma_json_set_value_double.argtypes = [c_void_p, c_double]
        ma_lib.ma_json_set_value_double.restype = ma_status_t
        error_code = ma_lib.ma_json_set_value_double(self.ma_json_obj, c_val)
        return error_code

    def ma_json_set_value_string(self, val_string):
        val_string_b = val_string.encode('utf-8')
        p_string = c_char_p(val_string_b)
        ma_lib.ma_json_set_value_string.argtypes = [c_void_p, c_char_p]
        ma_lib.ma_json_set_value_string.restype = ma_status_t
        error_code = ma_lib.ma_json_set_value_string(self.ma_json_obj, p_string)
        return error_code

    def ma_json_get_value_int(self, int_val, default_val):
        c_val = pointer(int_val)
        ma_lib.ma_json_get_value_int.argtypes = [c_void_p, POINTER(c_int), c_int]
        ma_lib.ma_json_get_value_int.restype = ma_status_t
        error_code = ma_lib.ma_json_get_value_int(self.ma_json_obj, c_val, default_val)
        return error_code

    def ma_json_get_value_bool(self, bool_val, default_val):
        c_val = pointer(bool_val)
        ma_lib.ma_json_get_value_bool.argtypes = [c_void_p, POINTER(c_bool), c_bool]
        ma_lib.ma_json_get_value_bool.restype = ma_status_t
        error_code = ma_lib.ma_json_get_value_bool(self.ma_json_obj, c_val, default_val)
        return error_code

    def ma_json_get_value_int64(self, int64_val, default_val):
        c_val = pointer(int64_val)
        ma_lib.ma_json_get_value_int64.argtypes = [c_void_p, POINTER(c_int64), c_int64]
        ma_lib.ma_json_get_value_int64.restype = ma_status_t
        error_code = ma_lib.ma_json_get_value_int64(self.ma_json_obj, c_val, default_val)
        return error_code

    def ma_json_get_value_double(self, double_val, default_val):
        c_val = pointer(double_val)
        ma_lib.ma_json_get_value_double.argtypes = [c_void_p, POINTER(c_double), c_double]
        ma_lib.ma_json_get_value_double.restype = ma_status_t
        error_code = ma_lib.ma_json_get_value_double(self.ma_json_obj, c_val, default_val)
        return error_code

    def ma_json_get_value_string(self, string_val, default_val):
        val_string_b = string_val.encode('utf-8')
        default_val_b = default_val.encode('utf-8')
        p_string = c_char_p(val_string_b)
        p_default_val = c_char_p(default_val_b)
        pp_string = pointer(p_string)
        ma_lib.ma_json_get_value_string.argtypes = [c_void_p, POINTER(c_char_p), c_char_p]
        ma_lib.ma_json_get_value_string.restype = ma_status_t
        error_code = ma_lib.ma_json_get_value_string(self.ma_json_obj, pp_string, p_default_val)
        return error_code

    def ma_json_size(self):
        ma_lib.ma_json_size.argtypes = [c_void_p]
        ma_lib.ma_json_size.restype = c_int
        json_size = ma_lib.ma_json_size(self.ma_json_obj)
        return json_size

    def ma_crc8_ctx_create(self, poly, init_val, final_xor):
        ma_lib.ma_crc8_ctx_create.argtypes = [c_uint8, c_uint8, c_uint8]
        ma_lib.ma_crc8_ctx_create.restype = c_void_p
        self.ctx_8 = ma_lib.ma_crc8_ctx_create(poly, init_val, final_xor)
        return self.ctx_8

    def ma_crc8_ctx_free(self):
        ma_lib.ma_crc8_ctx_free.argtypes = [c_void_p]
        val = ma_lib.ma_crc8_ctx_free(self.ctx_8)
        return val

    def ma_crc8(self, data, length):
        data_p = pointer(data)
        ma_lib.ma_crc8.argtypes = [c_void_p, c_uint8, c_int]
        ma_lib.ma_crc8.restype = c_uint8
        re_8 = ma_lib.ma_crc8(self.ctx_8, data_p, length)
        return re_8

    def ma_crc16_ctx_create(self, poly, init_val, final_xor):
        ma_lib.ma_crc16_ctx_create.argtypes = [c_uint16, c_uint16, c_uint16]
        ma_lib.ma_crc16_ctx_create.restype = c_void_p
        self.ctx_16 = ma_lib.ma_crc16_ctx_create(poly, init_val, final_xor)
        return self.ctx_16

    def ma_crc16_ctx_free(self):
        ma_lib.ma_crc16_ctx_free.argtypes = [c_void_p]
        val = ma_lib.ma_crc16_ctx_free(self.ctx_16)
        return val

    def ma_crc16(self, data, length):
        data_p = pointer(data)
        ma_lib.ma_crc16.argtypes = [c_void_p, c_uint16, c_int]
        ma_lib.ma_crc16.restype = c_uint16
        re_16 = ma_lib.ma_crc16(self.ctx_16, data_p, length)
        return re_16

    def ma_crc32_ctx_create(self, poly, init_val, final_xor):
        ma_lib.ma_crc32_ctx_create.argtypes = [c_uint32, c_uint32, c_uint32]
        ma_lib.ma_crc32_ctx_create.restype = c_void_p
        self.ctx_32 = ma_lib.ma_crc32_ctx_create(poly, init_val, final_xor)
        return self.ctx_32

    def ma_crc32_ctx_free(self):
        ma_lib.ma_crc32_ctx_free.argtypes = [c_void_p]
        val = ma_lib.ma_crc32_ctx_free(self.ctx_32)
        return val

    def ma_crc32(self, data, length):
        data_p = pointer(data)
        ma_lib.ma_crc32.argtypes = [c_void_p, c_uint32, c_int]
        ma_lib.ma_crc32.restype = c_uint32
        re_32 = ma_lib.ma_crc32(self.ctx_32, data_p, length)
        return re_32

    def ma_crc64_ctx_create(self, poly, init_val, final_xor):
        ma_lib.ma_crc64_ctx_create.argtypes = [c_uint64, c_uint64, c_uint64]
        ma_lib.ma_crc64_ctx_create.restype = c_void_p
        self.ctx_64 = ma_lib.ma_crc64_ctx_create(poly, init_val, final_xor)
        return self.ctx_64

    def ma_crc64_ctx_free(self):
        ma_lib.ma_crc64_ctx_free.argtypes = [c_void_p]
        val = ma_lib.ma_crc64_ctx_free(self.ctx_64)
        return val

    def ma_crc64(self, data, length):
        data_p = pointer(data)
        ma_lib.ma_crc64.argtypes = [c_void_p, c_uint64, c_int]
        ma_lib.ma_crc64.restype = c_uint64
        re_64 = ma_lib.ma_crc64(self.ctx_64, data_p, length)
        return re_64

    def ma_version(self):
        # arr = bytearray(512)
        # char_array = c_char * len(arr)
        # buf_c = char_array.from_buffer(arr)
        c = c_void_p()
        ma_lib.ma_version.argtypes = [c_void_p]
        ma_lib.ma_version.restype = c_char_p
        version = ma_lib.ma_version(c)
        return version.decode('utf-8')

    def ma_model_modify_meta(self, idx, meta):
        meta_p = pointer(meta)
        ma_lib.ma_model_modify_meta.argtypes = [c_int, c_void_p]
        re = ma_lib.ma_model_modify_meta(idx, meta_p)
        return re

    def ma_model_number(self):
        c = c_void_p()
        ma_lib.ma_model_number.argtypes = [c_void_p]
        ma_lib.ma_model_number.restype = c_int
        model_number = ma_lib.ma_model_number(c)
        return model_number

    def ma_model_get_name(self, idx):
        ma_lib.ma_model_get_name.argtypes = [c_int]
        ma_lib.ma_model_get_name.restype = c_char_p
        name = ma_lib.ma_model_get_name(idx)
        return name.decode('utf-8')

    def ma_model_open(self, model_idx, model_instance_name, init_param_json_string):
        model_instance_name_b = model_instance_name.encode('utf-8')
        init_param_json_string_b = init_param_json_string.encode('utf-8')
        model_instance_name_p = c_char_p(model_instance_name_b)
        init_param_json_string_p = c_char_p(init_param_json_string_b)
        rc = ma_status_t()
        ma_lib.ma_model_open.argtypes = [c_int, c_char_p, c_char_p, POINTER(ma_status_t)]
        ma_lib.ma_model_open.restype = c_void_p
        self.model_handel = ma_lib.ma_model_open(model_idx, model_instance_name_p, init_param_json_string_p,
                                                 pointer(rc))
        return self.model_handel


