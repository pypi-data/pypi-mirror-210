import json
from ctypes import *
from ctypes import wintypes

import os ,sys
r=os.path.abspath(os.path.dirname(__file__))
rootpath=os.path.split(r)[0]
sys.path.append(rootpath)
from vcarhilclient.kunyi_util import *
from vcarhilclient.Enums import *
from vcarhilclient.mrt_strunctures import *
import pathlib
import time

import platform
system = platform.system()
if system == "Windows":
    dll_path = os.path.join(pathlib.Path(__file__).parent, "mrt.dll")
    mrt_lib = WinDLL(dll_path)
else:
    dll_path = os.path.join(pathlib.Path(__file__).parent, "libmrt.so")
    mrt_lib = CDLL(dll_path)


class mrt_client():
    dispatch_progress = 0

    def __init__(self, host, managerment_port=8888, push_port=8889, subscription_port=8890):
        self.host = host
        self.mgr_port = managerment_port
        self.push_port = push_port
        self.subs_port = subscription_port
        self.envs = []
        self.record_env = ''
        self.context = None
        self.daqs = {}
        self.log_writter = None
        self.log_reader = None
        self.data_listTemp = []
        self.recodeStatus = 0
        self.writeNo = 1
        self.fileNum = 1
        self.temp_size = 1024*1024*10
        self.isrecord = False
        self.record_start = False
        self.isTrigger = False
        self.trigger_start = ()
        self.trigger_stop = ()

    def connet(self):

        error_code = mrt_status_t()
        p_ec = pointer(error_code)
        con_str = "tcp://%s:%s" % (self.host, self.mgr_port)

        bs = con_str.encode('utf-8')
        con_str_pointer = c_char_p(bs)

        mrt_lib.mrt_create_context.restype = c_void_p
        self.context = mrt_lib.mrt_create_context(POINTER(c_char)(),con_str_pointer, p_ec)

        return error_code

    def disconnect(self):
        if self.log_writter != None:
            self.close_log_writter()
        if self.log_reader != None:
            self.close_log_reader()
        if self.context == None:
            return 0
        mrt_lib.mrt_destroy_context.argtypes = [c_void_p]
        mrt_lib.mrt_destroy_context.restype = mrt_status_t
        error_code = mrt_lib.mrt_destroy_context(self.context)
        if error_code == 0:
            self.context = None
        return error_code

    def create_test_env(self, env_name):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_create_enviroment.argtypes = [c_void_p, c_char_p]
        mrt_lib.mrt_create_enviroment.restype = mrt_status_t
        error_code = mrt_lib.mrt_create_enviroment(self.context, name_pointer)
        if error_code.value == 0:
            self.envs.append(env_name)
        return error_code

    def delete_test_env(self, env_name):
        # if env_name not in self.envs:
        #    return mrt_status_t.MRT_ERR_OBJECT_NOT_EXIST
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_destroy_enviroment.argtypes = [c_void_p, c_char_p]
        mrt_lib.mrt_destroy_enviroment.restype = mrt_status_t
        error_code = mrt_lib.mrt_destroy_enviroment(self.context, name_pointer)
        if error_code.value == 0:
            try:
                self.envs.remove(env_name)
            except:
                pass
        return error_code

    def load_test_resources_to_env(self, env_name, fileid):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_load_enviroment.argtypes = [c_void_p, c_char_p, POINTER(c_uint64)]
        mrt_lib.mrt_load_enviroment.restype = mrt_status_t
        error_code = mrt_lib.mrt_load_enviroment(self.context, name_pointer, byref(c_uint64(fileid)))
        return error_code

    def unload_test_resources_to_env(self, env_name, fileid):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_unload_enviroment.argtypes = [c_void_p, c_char_p, POINTER(c_uint64)]
        mrt_lib.mrt_unload_enviroment.restype = mrt_status_t
        error_code = mrt_lib.mrt_unload_enviroment(self.context, name_pointer, byref(c_uint64(fileid)))
        return error_code

    def load_enviroment_interface_mapping(self, env_name, mapping_id):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_load_enviroment_interface_mapping.argtypes = [c_void_p, c_char_p, POINTER(c_uint64)]
        mrt_lib.mrt_load_enviroment_interface_mapping.restype = mrt_status_t
        error_code = mrt_lib.mrt_load_enviroment_interface_mapping(self.context, name_pointer, byref(c_uint64(mapping_id)))
        return error_code

    def unload_enviroment_interface_mapping(self, env_name, mapping_id):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_unload_enviroment_interface_mapping.argtypes = [c_void_p, c_char_p, POINTER(c_uint64)]
        mrt_lib.mrt_unload_enviroment_interface_mapping.restype = mrt_status_t
        error_code = mrt_lib.mrt_unload_enviroment_interface_mapping(self.context, name_pointer, byref(c_uint64(mapping_id)))
        return error_code

    def start_test(self, env_name):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_start_enviroment.argtypes = [c_void_p, c_char_p]
        mrt_lib.mrt_start_enviroment.restype = mrt_status_t
        error_code = mrt_lib.mrt_start_enviroment(self.context, name_pointer)

        return error_code

    def stop_test(self, env_name):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_stop_enviroment.argtypes = [c_void_p, c_char_p]
        mrt_lib.mrt_stop_enviroment.restype = mrt_status_t
        error_code = mrt_lib.mrt_stop_enviroment(self.context, name_pointer)
        return error_code

    def get_env_number(self):
        num_pointer = pointer(c_int())
        mrt_lib.mrt_get_enviroment_number.argtypes = [c_void_p, c_void_p]
        mrt_lib.mrt_get_enviroment_number.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_enviroment_number(self.context, num_pointer)
        return error_code, num_pointer.contents.value

    def is_env_exists(self, env_name):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        mrt_lib.mrt_is_enviroment_exist.argtypes = [c_void_p, c_char_p]
        mrt_lib.mrt_is_enviroment_exist.restype = c_int32
        existance = mrt_lib.mrt_is_enviroment_exist(self.context, name_pointer)
        return bool(existance)


    def _rebuild_self_env_dict(self, real_env_num):
        for i in range(real_env_num):
            pass

    def get_env_info(self, env_name):
        bs = env_name.encode('utf-8')
        name_pointer = c_char_p(bs)
        info = mrt_enviroment_info_t()
        ei_p = pointer(info)
        mrt_lib.mrt_get_enviroment_info.argtypes = [c_void_p, c_char_p, POINTER(mrt_enviroment_info_t)]
        mrt_lib.mrt_get_enviroment_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_enviroment_info(self.context, name_pointer, byref(info))
        return error_code, ei_p

    def get_env_name_by_idx(self, idx):
        ec, num = self.get_env_number()
        if ec.value != 0:
            return None
        # if idx >= num:
        #    return None

        arr = bytearray(512)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)
        size_pointer = pointer(c_int32(512))
        mrt_lib.mrt_get_enviroment_name.argtypes = [c_void_p, c_uint32, c_char_p, POINTER(c_int32)]
        mrt_lib.mrt_get_enviroment_name.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_enviroment_name(self.context, idx, buf_c, size_pointer)
        return error_code, buf_c.value.decode('utf-8')

    @staticmethod
    def call_back(error_code, current_process, total_process):
        if error_code.value != 0:
            mrt_client.dispatch_progress = 100
        if float(total_process) != 0:
            mrt_client.dispatch_progress = float(current_process) / float(total_process)

    def download_file(self, file_path):
        bs = file_path.encode('utf-8')
        path_pointer = c_char_p(bs)
        file_id_pointer = pointer(c_uint64())
        CALLBACK = CFUNCTYPE(None, mrt_status_t, c_int, c_int)
        mrt_lib.mrt_download_file.argtypes = [c_void_p, c_char_p, CALLBACK, POINTER(c_uint64)]
        mrt_lib.mrt_download_file.restype = mrt_status_t
        my_callback = CALLBACK(mrt_client.call_back)
        error_code = mrt_lib.mrt_download_file(self.context, path_pointer, my_callback, file_id_pointer)
        return error_code, file_id_pointer.contents.value


    def get_input_port_value(self, env_name, instance_name, port_name, signal_data_type, item_count, struct_detail=None, **sub_struct_detail):
        return self.get_port_value(env_name, instance_name, port_name,
                                   mrt_port_type_t.MRT_INPUT_PORT, signal_data_type, item_count, struct_detail, **sub_struct_detail)

    def get_output_port_value(self, env_name, instance_name, port_name, signal_data_type, item_count, struct_detail=None, **sub_struct_detail):
        return self.get_port_value(env_name, instance_name, port_name,
                                   mrt_port_type_t.MRT_OUTPUT_PORT, signal_data_type, item_count, struct_detail, **sub_struct_detail)

    def get_measurement_value(self, env_name, instance_name, port_name, signal_data_type, item_count, struct_detail=None, **sub_struct_detail):
        return self.get_port_value(env_name, instance_name, port_name,
                                    mrt_port_type_t.MRT_MEASUREMENT, signal_data_type, item_count, struct_detail, **sub_struct_detail)

    def get_port_value(self, env_name, instance_name, port_name, port_type, signal_data_type,  item_count, struct_detail, **sub_struct_detail):
        en_bs = env_name.encode('utf-8')
        en_pointer = c_char_p(en_bs)
        in_bs = instance_name.encode('utf-8')
        in_pointer = c_char_p(in_bs)
        pn_bs = port_name.encode('utf-8')
        pn_pointer = c_char_p(pn_bs)

        buf_size = kunyi_util.get_signal_bytes_length(signal_data_type, item_count, struct_detail, **sub_struct_detail)
        if buf_size == None:
            return mrt_status_t.MRT_ERR_INVALID_ARG, None

        arr = bytearray(buf_size)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        mrt_lib.mrt_model_read_port.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p,
                                                c_int32, c_int32, c_int32, c_void_p]
        mrt_lib.mrt_model_read_port.restype = c_int32
        return_bytes = mrt_lib.mrt_model_read_port(self.context, en_pointer, in_pointer, pn_pointer,
                                                 port_type[0], 0, buf_size, buf_c)
        port_value = kunyi_util.bytes_to_data(signal_data_type, arr, item_count, struct_detail, **sub_struct_detail)
        return return_bytes, port_value

    def set_input_port_value(self, env_name, instance_name, port_name, signal_type, signal_value,
                             item_count, struct_detail, **sub_struct_detail):
        return self.set_port_value(env_name, instance_name, port_name,
                                   signal_type, signal_value, mrt_port_type_t.MRT_INPUT_PORT,
                                   item_count, struct_detail, **sub_struct_detail)

    def set_port_value(self, env_name, instance_name, port_name, signal_type, signal_value,
                       port_type, item_count, struct_detail, **sub_struct_detail):
        en_bs = env_name.encode('utf-8')
        en_pointer = c_char_p(en_bs)
        in_bs = instance_name.encode('utf-8')
        in_pointer = c_char_p(in_bs)
        pn_bs = port_name.encode('utf-8')
        pn_pointer = c_char_p(pn_bs)

        python_bytes = kunyi_util.data_to_bytes(signal_type, signal_value, item_count,
                                                struct_detail, **sub_struct_detail)
        arr = bytearray.fromhex(python_bytes.hex())
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        buf_size = kunyi_util.get_signal_bytes_length(signal_type, item_count,
                                                      struct_detail, **sub_struct_detail)
        if buf_size == None:
            return mrt_status_t.MRT_ERR_INVALID_ARG, None

        mrt_lib.mrt_model_write_port.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p,
                                                 c_int32, c_int32, c_int32, c_void_p]
        mrt_lib.mrt_model_write_port.restype = c_int32
        rc = mrt_lib.mrt_model_write_port(self.context, en_pointer, in_pointer, pn_pointer,
                                          port_type[0], 0, buf_size, buf_c)
        return rc

    def get_calibration(self, env_name, instance_name, cal_name,
                        cal_datatype, xlength=0, ylength=0, funlength=1,
                        xidx=0, yidx=0, funidx=0):

        rc, rvz = self.get_calibration_value(env_name, instance_name, cal_name, 0, funidx,
                              funlength, cal_datatype)
        cal_v = []
        if (xlength == 0) and (ylength == 0):
            return rvz
        else:
            cal_v.append(rvz)
            if xlength != 0:
                rc, rvx = self.get_calibration_value(env_name, instance_name, cal_name, 1, xidx,
                                                    xlength, cal_datatype)

                cal_v.append(rvx)
            if ylength != 0:
                rc, rvy = self.get_calibration_value(env_name, instance_name, cal_name, 2, yidx,
                                                    ylength, cal_datatype)
                cal_v.append(rvy)

            return cal_v

    def get_calibration_value(self, env_name, instance_name, cal_name, axis_idx, data_idx,
                              array_size, cal_datatype):
        en_bs = env_name.encode('utf-8')
        en_pointer = c_char_p(en_bs)
        in_bs = instance_name.encode('utf-8')
        in_pointer = c_char_p(in_bs)
        cn_bs = cal_name.encode('utf-8')
        cn_pointer = c_char_p(cn_bs)

        signal_buf_size = kunyi_util.get_signal_bytes_length(cal_datatype)
        buf_size = array_size * signal_buf_size
        arr = bytearray(buf_size)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)
        mrt_lib.mrt_model_cal_read.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p,
                                                c_int32, c_int32, c_int32, c_void_p]
        mrt_lib.mrt_model_cal_read.restype = c_int32

        error_code = mrt_lib.mrt_model_cal_read(self.context, en_pointer, in_pointer, cn_pointer,
                                                axis_idx, data_idx, buf_size, buf_c)

        if array_size == 1:
            cal_value = kunyi_util.bytes_to_data(cal_datatype, arr)
        else:
            cal_value = kunyi_util.bytes_array_to_data_array(cal_datatype, arr, array_size)
        return error_code, cal_value

    def set_calibration(self, env_name, instance_name, cal_name,
                        cal_datatype, xlength=0, ylength=0, funlength=1,
                        xidx=0, yidx=0, funidx=0, cal_value_array=[]):
        if len(cal_value_array) < 1:
            return "-999"

        rc = self.set_calibration_value(env_name, instance_name, cal_name,
                                        0, funidx, funlength, cal_datatype, cal_value_array[0])
        if (ylength == 0) and (xlength == 0):
            return str(rc)
        else:
            rc_all = str(rc)
            if xlength != 0:
                rcx = self.set_calibration_value(env_name, instance_name, cal_name,
                                                1, xidx, xlength, cal_datatype, cal_value_array[1])
                rc_all = rc_all + ':' + str(rcx)

            if ylength != 0:
                rcy = self.set_calibration_value(env_name, instance_name, cal_name,
                                                 2, yidx, ylength, cal_datatype, cal_value_array[2])
                rc_all = rc_all + ':' + str(rcy)

            return rc_all



    def set_calibration_value(self, env_name, instance_name, cal_name, axis_idx, data_idx,
                              array_size, cal_datatype, cal_value):
        en_bs = env_name.encode('utf-8')
        en_pointer = c_char_p(en_bs)
        in_bs = instance_name.encode('utf-8')
        in_pointer = c_char_p(in_bs)
        pn_bs = cal_name.encode('utf-8')
        pn_pointer = c_char_p(pn_bs)

        python_bytes = kunyi_util.data_to_bytes(cal_datatype, cal_value, array_size)
        arr = bytearray.fromhex(python_bytes.hex())
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        buf_size = kunyi_util.get_signal_bytes_length(cal_datatype, array_size)
        if buf_size == None:
            return mrt_status_t.MRT_ERR_INVALID_ARG, None

        mrt_lib.mrt_model_cal_write.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p,
                                                 c_int32, c_int32, c_int32, c_void_p]
        mrt_lib.mrt_model_cal_write.restype = c_int32
        rc = mrt_lib.mrt_model_cal_write(self.context, en_pointer, in_pointer, pn_pointer,
                                          axis_idx, data_idx, buf_size, buf_c)
        return rc

    def create_daq(self, env_name, port_number, is_queue):
        if is_queue == 1:
            if port_number > 1:
                raise Exception("One daq can only contain one queue port")

        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        daq_handle = pointer(c_uint64())
        mrt_lib.mrt_create_daq.argtypes = [c_void_p, c_char_p, c_int32, POINTER(c_uint64), c_int]
        mrt_lib.mrt_create_daq.restype = mrt_status_t
        error_code = mrt_lib.mrt_create_daq(self.context, en_pointer, port_number, daq_handle, is_queue)
        if error_code.value == 0:
            self.daqs[(daq_handle.contents.value,env_name)] = [None] * port_number
            with open("./daqinfo.txt","w") as f:
                f.write(str(daq_handle.contents.value))
        return error_code, daq_handle.contents.value

    def destroy_daq(self, env_name, daq_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_destroy_daq.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_destroy_daq.restype = mrt_status_t
        error_code = mrt_lib.mrt_destroy_daq(self.context, en_pointer, c_uint64(daq_handle))
        if error_code.value == 0:
            try:
                del(self.daqs[(daq_handle,env_name)])
            except:
                pass
        return error_code

    def get_daq_info(self, env_name, daq_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        daq_info = mrt_daq_info_t()
        info_p = pointer(daq_info)
        mrt_lib.mrt_get_daq_info.argtypes = [c_void_p, c_char_p, c_uint64, POINTER(mrt_daq_info_t)]
        mrt_lib.mrt_get_daq_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_daq_info(self.context, en_pointer, c_uint64(daq_handle), byref(daq_info))
        return error_code, daq_info

    def get_port_info(self, env_name, daq_handle, port_index):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        port_info = mrt_daq_port_info_t()
        info_p = pointer(port_info)
        mrt_lib.mrt_get_port_info.argtypes = [c_void_p, c_char_p, c_uint64,c_uint32,POINTER(mrt_daq_port_info_t)]
        mrt_lib.mrt_get_port_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_port_info(self.context,en_pointer,c_uint64(daq_handle),
                                               c_uint32(port_index), info_p)
        return error_code, port_info


    def daq_set_trigger_period(self, env_name, daq_handle, period_ms, offset_ms):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_daq_set_trigger_period.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32, c_uint32]
        mrt_lib.mrt_daq_set_trigger_period.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_set_trigger_period(self.context, en_pointer, c_uint64(daq_handle),
                                                        period_ms, offset_ms)
        return error_code

    def daq_set_port(self, env_name, daq_handle, port_index, model_instance_name, port_name, port_type, port_datatype):

        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        modelName = model_instance_name.encode('utf-8')
        mn_pointer = c_char_p(modelName)
        portName = port_name.encode('utf-8')
        pn_pointer = c_char_p(portName)
        mrt_lib.mrt_daq_set_port.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32, c_char_p, c_char_p, c_int32]
        mrt_lib.mrt_daq_set_port.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_set_port(self.context, en_pointer, c_uint64(daq_handle), c_uint32(port_index),
                                              mn_pointer, pn_pointer, port_type[0])
        if error_code.value == 0:
            self.daqs[(daq_handle,env_name)][port_index] = (model_instance_name, port_name, port_type[0], port_datatype)
        return error_code

    def daq_set_multiple_ports(self, env_name, daq_handle, port_index, port_info_list, port_num):

        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        tt = (mrt_daq_port_cfg_t*port_num)()
        for i in range(port_num):
            tt[i].port_type = port_info_list[i]['port_type'][0]
            model_name = port_info_list[i]["model_instance_name"].encode('utf-8')
            tt[i].model_instance_name = c_char_p(model_name)
            port_name = port_info_list[i]["port_name"].encode('utf-8')
            tt[i].port_name = c_char_p(port_name)


        # model_name = port_info_list[0]["model_instance_name"].encode('utf-8')
        # tt.model_instance_name = c_char_p(model_name)
        # port_name = port_info_list[0]["port_name"].encode('utf-8')
        # tt.port_name = c_char_p(port_name)

        p_a = cast(pointer(tt), c_void_p)
        p_b = cast(p_a, POINTER(mrt_daq_port_cfg_t))
        mrt_lib.mrt_daq_set_multi_ports.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32,
                                                   POINTER(mrt_daq_port_cfg_t), c_uint32]
        mrt_lib.mrt_daq_set_multi_ports.restype = c_int32
        c_p = cast(self.context, c_void_p)
        error_code = mrt_lib.mrt_daq_set_multi_ports(c_p, en_pointer, c_uint64(daq_handle),
                                                     c_uint32(port_index), p_b, port_num)

        return error_code

    def daq_clear_port(self, env_name, daq_handle, port_index):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_daq_clear_port.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32]
        mrt_lib.mrt_daq_clear_port.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_clear_port(self.context, en_pointer, c_uint64(daq_handle), c_uint32(port_index))
        if error_code == 0:
            self.daqs[(daq_handle,env_name)][port_index] = None
        return error_code

    def daq_clear_all_ports(self, env_name, daq_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_daq_clear_all_ports.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_daq_clear_all_ports.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_clear_all_ports(self.context, en_pointer, c_uint64(daq_handle))
        if error_code == 0:
            for i in range(len(self.daqs[(daq_handle,env_name)])):
                self.daqs[(daq_handle,env_name)][i] = None
        return error_code

    def daq_append_trigger_event(self, env_name, daq_handle, model_instance_name, event_name):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        modelName = model_instance_name.encode('utf-8')
        mn_pointer = c_char_p(modelName)
        eventName = event_name.encode('utf-8')
        eventn_pointer = c_char_p(eventName)
        mrt_lib.mrt_daq_append_trigger_event.argtypes = [c_void_p, c_char_p, c_uint64, c_char_p, c_char_p]
        mrt_lib.mrt_daq_append_trigger_event.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_append_trigger_event(self.context, en_pointer, c_uint64(daq_handle),
                                                          mn_pointer, eventn_pointer)
        return error_code

    def daq_remove_trigger_event(self, env_name, daq_handle, model_instance_name, event_name):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        modelName = model_instance_name.encode('utf-8')
        mn_pointer = c_char_p(modelName)
        eventName = event_name.encode('utf-8')
        eventn_pointer = c_char_p(eventName)
        mrt_lib.mrt_daq_remove_trigger_event.argtypes = [c_void_p, c_char_p, c_uint64, c_char_p, c_char_p]
        mrt_lib.mrt_daq_remove_trigger_event.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_remove_trigger_event(self.context, en_pointer, c_uint64(daq_handle),
                                                          mn_pointer, eventn_pointer)
        return error_code

    def daq_clear_trigger_events(self, env_name, daq_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_daq_clear_trigger_events.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_daq_clear_trigger_events.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_clear_trigger_events(self.context, en_pointer, c_uint64(daq_handle))
        return error_code

    def daq_get_trigger_event(self, env_name, daq_handle, event_index, model_instance_name, event_name):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        modelName = model_instance_name.encode('utf-8')
        # mn_pointer = c_char(modelName)
        eventName = event_name.encode('utf-8')
        # eventn_pointer = c_char(eventName)
        evinfo = mrt_daq_trigger_event_info_t(modelName, eventName)
        evinfo_p = pointer(evinfo)
        mrt_lib.mrt_daq_get_trigger_event.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32,
                                                      POINTER(mrt_daq_trigger_event_info_t)]
        mrt_lib.mrt_daq_get_trigger_event.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_get_trigger_event(self.context, en_pointer, c_uint64(daq_handle),
                                                       c_uint32(event_index), byref(evinfo))
        return error_code, evinfo_p

    def start_daq(self, env_name, daq_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_start_daq.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_start_daq.restype = mrt_status_t
        error_code = mrt_lib.mrt_start_daq(self.context, en_pointer, c_uint64(daq_handle))
        return error_code


    def open_log_reader(self):
        addr = "tcp://" + self.host + ":" + str(self.subs_port)
        addr_bs = addr.encode('utf-8')
        addr_pointer = c_char_p(addr_bs)

        mrt_lib.mrt_log_reader_open.argtypes = [c_char_p]
        mrt_lib.mrt_log_reader_open.restype = c_void_p
        self.log_reader = mrt_lib.mrt_log_reader_open(addr_pointer)
        return self.log_reader

    def open_log_writter(self):
        addr = "tcp://" + self.host + ":" + str(self.push_port)
        addr_bs = addr.encode('utf-8')
        addr_pointer = c_char_p(addr_bs)

        mrt_lib.mrt_log_writer_open.argtypes = [c_char_p]
        mrt_lib.mrt_log_writer_open.restype = c_void_p
        self.log_writter = mrt_lib.mrt_log_writer_open(addr_pointer)
        return self.log_writter

    def log_write(self, level, own, log_text):
        if self.log_writter == None:
            self.open_log_writter()
        own2 = "pymrt:"+own
        bs = own2.encode('utf-8')
        fmtbs = log_text.encode('utf-8')
        logtext_pointer = c_char_p(bs)
        fmtbs_pointer = c_char_p(fmtbs)
        c_void = self.open_log_writter()
        time.sleep(0.1)
        mrt_lib.mrt_log_write.argtypes = [c_void_p,c_int32,c_char_p,c_char_p]
        mrt_lib.mrt_log_write.restype = c_int32
        self.log = mrt_lib.mrt_log_write(c_void,c_int32(level),logtext_pointer,fmtbs_pointer)
        time.sleep(0.1)
        self.close_log_writter()
        return self.log


    def close_log_reader(self):

        mrt_lib.mrt_log_reader_close.argtypes = [c_void_p]
        mrt_lib.mrt_log_reader_close.restype = mrt_status_t
        ec = mrt_lib.mrt_log_reader_close(self.log_reader)
        if ec.value == 0:
            self.log_reader = None
        return ec

    def log_read(self,buf_size):
        arr = bytearray(buf_size)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)
        mrt_lib.mrt_log_read.argtypes = [c_void_p, c_char_p,c_int32,c_int32,]
        mrt_lib.mrt_log_read.restype = c_int32
        c_void = self.open_log_reader()
        time.sleep(0.2)
        self.logr = mrt_lib.mrt_log_read(c_void, buf_c,buf_size,5)
        log = kunyi_util.bytes_to_data("UTF8", arr[:buf_size],item_count=1,struct_detail=None)
        return log

    def close_log_writter(self):

        mrt_lib.mrt_log_writer_close.argtypes = [c_void_p]
        mrt_lib.mrt_log_writer_close.restype = mrt_status_t
        ec = mrt_lib.mrt_log_writer_close(self.log_writter)
        if ec.value == 0:
            self.log_writter = None
        return ec

    def fetch_log(self, buf_size):
        if self.log_reader == None:
            self.open_log_reader()
        arr = bytearray(buf_size)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        mrt_lib.mrt_log_read.argtypes = [c_void_p, c_char_p, c_int32, c_int32]
        mrt_lib.mrt_log_read.restype = c_int32
        size = mrt_lib.mrt_log_read(self.log_reader, buf_c, buf_size, 5)
        log_data = kunyi_util.bytes_to_data("UTF8", arr[:size])
        return log_data

    def stop_daq(self, env_name, daq_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_stop_daq.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_stop_daq.restype = mrt_status_t
        error_code = mrt_lib.mrt_stop_daq(self.context, en_pointer, c_uint64(daq_handle))
        return error_code

    def daq_read(self, env_name, daq_handle, item_count, sub_struct_detail):
        info_dir = r'./record_infoFile'
        if not os.path.exists(info_dir):
            os.mkdir(info_dir)
        with open(f"{info_dir}/PortConfig.json", "w") as f:
            f.write(str(self.daqs))
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        msg_pp = pointer(c_void_p())
        is_release = False
        msg_list = []
        try:
            mrt_lib.mrt_daq_read.argtypes = [c_void_p, c_char_p, c_uint64, POINTER(POINTER(None))]
            mrt_lib.mrt_daq_read.restype = c_int32
            buf_size = mrt_lib.mrt_daq_read(self.context, en_pointer, c_uint64(daq_handle), msg_pp)
            if buf_size == 0:
                print(f"The experimental environment({env_name}) Is Starting:{buf_size}")
                return msg_list
            elif buf_size == -6:
                with open("./readErro.erro", "a") as f:
                    try:
                        self.log_write(3,f"{env_name}",f"{time.strftime('%m%d_%H:%M:%S')}:daqhandle>>{daq_handle},"
                                                 f"{env_name}>>MRT_ERR_RPC_CALL_FAIL -6\n")
                    except:
                        pass
                    f.write(f"{time.strftime('%m%d_%H:%M:%S')}:daqhandle>>{daq_handle},{env_name}>>MRT_ERR_RPC_CALL_FAIL -6\n")
                    f.flush()
                raise Exception("MRT_ERR_RPC_CALL_FAIL -6")
            elif buf_size < 0:
                with open("./readErro.erro", "a") as f:
                    try:
                        self.log_write(3, f"{env_name}",f"Experiment environment:daqhandle>>{daq_handle},{env_name} "
                                                  f">>error code:{buf_size}\n")
                    except:
                        pass
                    f.write(f"Experiment environment:daqhandle>>{daq_handle},{env_name} >>error code:{buf_size}\n")
                    f.flush()
                raise Exception(f"Experiment environment error code:{buf_size}")
            mrt_msg_array = mrt_daq_msg_t * buf_size
            msg_arr_obj = mrt_msg_array.from_address(msg_pp.contents.value)
            if msg_arr_obj:
                is_release = True

            ports = self.daqs[(daq_handle,env_name)]
            for msg in msg_arr_obj:
                data_buf = c_char * msg.data_size
                data_byte_arr = data_buf.from_address(msg.data)
                data_pba = bytearray(data_byte_arr)
                p_idx = 0
                buf_read_idx = 0
                data_list = []
                for item in ports:
                    if item is None:
                        continue
                    item_size = kunyi_util.get_signal_bytes_length(item[3],item_count,sub_struct_detail)
                    item_data_buf = data_pba[buf_read_idx: buf_read_idx+item_size]
                    item_data_value = kunyi_util.bytes_to_data(item[3], item_data_buf,item_count,sub_struct_detail)
                    data_list.append((item[0], item[1], item[2], item_data_value, msg.time_stamp_us))
                    buf_read_idx = buf_read_idx + item_size
                    p_idx = p_idx + 1
                self.data_listTemp = data_list
                t = msg.time_stamp_us
                t_bytes = kunyi_util.data_to_bytes("UInt64", t, 1, struct_detail=None)
                if self.isrecord:
                    self.record_env = env_name
                    self.record(env_name,self.isTrigger,t_bytes,data_pba,self.trigger_start,self.trigger_stop)
                msg_list.append(data_list)
            return msg_list
        except Exception as ex:
            raise ex
        finally:
            if is_release:
                releaseInfo = self.daq_msg_release(msg_arr_obj[0])
                if releaseInfo.value != 0:
                    raise Exception("rtcp error after read daq data")


    def daq_msg_release(self, msg):

        mrt_lib.mrt_daq_msg_release.argtypes = [c_void_p, POINTER(mrt_daq_msg_t)]
        mrt_lib.mrt_daq_msg_release.restype = mrt_status_t
        error_code = mrt_lib.mrt_daq_msg_release(self.context, msg)
        return error_code


    def load_device_mapping(self, fileid):

        mrt_lib.mrt_load_device_mapping.argtypes = [c_void_p, POINTER(c_uint64)]
        mrt_lib.mrt_load_device_mapping.restype = mrt_status_t
        error_code = mrt_lib.mrt_load_device_mapping(self.context, byref(c_uint64(fileid)))
        return error_code

    def load_channel_setting(self, fileid):

        mrt_lib.mrt_load_channel_setting.argtypes = [c_void_p, POINTER(c_uint64)]
        mrt_lib.mrt_load_channel_setting.restype = mrt_status_t
        error_code = mrt_lib.mrt_load_channel_setting(self.context, byref(c_uint64(fileid)))
        return error_code

    def get_device_number(self):
        num_pointer = pointer(c_uint32())
        mrt_lib.mrt_get_device_number.argtypes = [c_void_p, POINTER(c_uint32)]
        mrt_lib.mrt_get_device_number.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_device_number(self.context, num_pointer)
        return error_code, num_pointer.contents.value

    def get_mapped_device_number(self):
        num_pointer = pointer(c_uint32())
        mrt_lib.mrt_get_mapped_device_number.argtypes = [c_void_p, POINTER(c_uint32)]
        mrt_lib.mrt_get_mapped_device_number.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_mapped_device_number(self.context, num_pointer)
        return error_code, num_pointer.contents.value

    def get_device_info(self, dev_idx):
        dev_info = mrt_device_info_t()
        info_p = pointer(dev_info)
        mrt_lib.mrt_get_device_info.argtypes = [c_void_p, c_uint32, POINTER(mrt_device_info_t)]
        mrt_lib.mrt_get_device_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_device_info(self.context, dev_idx, byref(dev_info))
        return error_code, dev_info

    def get_mapped_device_info(self, dev_idx):
        dev_info = mrt_device_info_t()
        info_p = pointer(dev_info)
        mrt_lib.mrt_get_mapped_device_info.argtypes = [c_void_p, c_uint32, POINTER(mrt_device_info_t)]
        mrt_lib.mrt_get_mapped_device_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_mapped_device_info(self.context, dev_idx, byref(dev_info))
        return error_code, dev_info

    def get_device_channel_info(self, dev_idx, channel_idx):
        channel_info = mrt_channel_info_t()
        info_p = pointer(channel_info)
        mrt_lib.mrt_get_device_channel_info.argtypes = [c_void_p, c_uint32, c_uint32, POINTER(mrt_channel_info_t)]
        mrt_lib.mrt_get_device_channel_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_device_channel_info(self.context, dev_idx, channel_idx, byref(channel_info))
        return error_code, channel_info

    def get_mapped_device_channel_info(self, dev_idx, channel_idx):
        channel_info = mrt_channel_info_t()
        info_p = pointer(channel_info)
        mrt_lib.mrt_get_mapped_device_channel_info.argtypes = [c_void_p, c_uint32, c_uint32, POINTER(mrt_channel_info_t)]
        mrt_lib.mrt_get_mapped_device_channel_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_mapped_device_channel_info(self.context, dev_idx, channel_idx, byref(channel_info))
        return error_code, channel_info

    def create_gen(self,env_name,port_number):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        gen_handle = pointer(c_uint64())

        mrt_lib.mrt_create_gen.argtypes = [c_void_p, c_char_p, c_uint32, POINTER(c_uint64)]
        mrt_lib.mrt_create_gen.restype = mrt_status_t
        error_code = mrt_lib.mrt_create_gen(self.context, en_pointer, c_uint32(port_number), gen_handle)
        return error_code,gen_handle.contents.value

    def destroy_gen(self,env_name,gen_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)

        mrt_lib.mrt_destroy_gen.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_destroy_gen.restype = mrt_status_t
        error_code = mrt_lib.mrt_destroy_gen(self.context, en_pointer, c_uint64(gen_handle))
        return error_code

    def get_gen_number(self,env_name):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        gen_num = pointer(c_uint64())

        mrt_lib.mrt_get_gen_number.argtypes = [c_void_p, c_char_p, POINTER(c_uint64)]
        mrt_lib.mrt_get_gen_number.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_gen_number(self.context, en_pointer, gen_num)
        return error_code,gen_num.contents.value

    def get_gen_handle(self,env_name,idx):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        gen_handle = pointer(c_uint64())

        mrt_lib.mrt_get_gen_handle.argtypes = [c_void_p, c_char_p,c_uint32, POINTER(c_uint64)]
        mrt_lib.mrt_get_gen_handle.restype = mrt_status_t
        error_code = mrt_lib.mrt_get_gen_handle(self.context, en_pointer,c_uint32(idx), gen_handle)
        return error_code,gen_handle.contents.value

    def gen_set_port(self, env_name, gen_handle, port_index, model_instance_name, port_name):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        modelName = model_instance_name.encode('utf-8')
        mn_pointer = c_char_p(modelName)
        portName = port_name.encode('utf-8')
        pn_pointer = c_char_p(portName)
        mrt_lib.mrt_gen_set_port.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32, c_char_p, c_char_p]
        mrt_lib.mrt_gen_set_port.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_set_port(self.context, en_pointer, c_uint64(gen_handle), c_uint32(port_index),
                                              mn_pointer, pn_pointer)
        return error_code

    def gen_get_port_num(self,env_name,gen_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        port_num = pointer(c_uint32())

        mrt_lib.mrt_gen_get_port_num.argtypes = [c_void_p, c_char_p,c_uint64, POINTER(c_uint32)]
        mrt_lib.mrt_gen_get_port_num.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_get_port_num(self.context, en_pointer, c_uint64(gen_handle), port_num)
        return error_code, port_num.contents.value

    def gen_get_port_info(self, env_name, gen_handle, port_idx):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        port_info = mrt_gen_port_info_t()
        port_info_p = pointer(port_info)


        mrt_lib.mrt_gen_get_port_info.argtypes = [c_void_p, c_char_p,c_uint64,c_uint32, POINTER(mrt_gen_port_info_t)]
        mrt_lib.mrt_gen_get_port_info.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_get_port_info(self.context, en_pointer,c_uint64(gen_handle), c_uint32(port_idx), byref(port_info))
        return error_code,port_info_p

    def gen_set_port_event(self, env_name, gen_handle, port_index, model_instance_name, event_name):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        modelName = model_instance_name.encode('utf-8')
        mn_pointer = c_char_p(modelName)
        portName = event_name.encode('utf-8')
        pn_pointer = c_char_p(portName)
        mrt_lib.mrt_gen_set_port_event.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32, c_char_p, c_char_p]
        mrt_lib.mrt_gen_set_port_event.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_set_port_event(self.context, en_pointer, c_uint64(gen_handle), c_uint32(port_index),
                                              mn_pointer, pn_pointer )
        return error_code

    def gen_set_port_period(self, env_name, gen_handle, port_index, period_ms,offset_ms):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_gen_set_port_period.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32, c_uint32, c_uint32]
        mrt_lib.mrt_gen_set_port_period.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_set_port_period(self.context, en_pointer, c_uint64(gen_handle), c_uint32(port_index),
                                              c_uint32(period_ms), c_uint32(offset_ms) )
        return error_code

    def gen_clr_port_event(self, env_name, gen_handle, port_index):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_gen_clr_port_event.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32]
        mrt_lib.mrt_gen_clr_port_event.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_clr_port_event(self.context, en_pointer, c_uint64(gen_handle), c_uint32(port_index))
        return error_code

    def gen_write_port(self, env_name, gen_handle, port_index, data, data_type, time_interval_ms):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        python_bytes = kunyi_util.data_to_bytes(data_type, data, len(data))
        arr = bytearray.fromhex(python_bytes.hex())
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        mrt_lib.mrt_gen_write_port.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32,c_void_p,c_uint32,c_uint32]
        mrt_lib.mrt_gen_write_port.restype = c_int32
        res = mrt_lib.mrt_gen_write_port(self.context, en_pointer, c_uint64(gen_handle), c_uint32(port_index)
                                                    ,buf_c, len(arr), c_uint32(time_interval_ms))
        return res

    def gen_write_queue(self, env_name, gen_handle, port_index, data):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        python_bytes = b''
        for i in range(len(data)):
            python_bytes = python_bytes + kunyi_util.data_to_bytes("UInt32", data[i]["interval"], 1)
            python_bytes = python_bytes + kunyi_util.data_to_bytes(data[i]["data_type"], data[i]["data_value"], 1)

        arr = bytearray.fromhex(python_bytes.hex())
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)

        mrt_lib.mrt_gen_write_queue.argtypes = [c_void_p, c_char_p, c_uint64, c_uint32, c_void_p, c_uint32, c_uint32]
        mrt_lib.mrt_gen_write_queue.restype = c_int32
        res = mrt_lib.mrt_gen_write_queue(self.context, en_pointer, c_uint64(gen_handle), c_uint32(port_index)
                                         , buf_c, 8, c_uint32(len(data)))
        return res

    def gen_start(self, env_name, gen_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_gen_start.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_gen_start.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_start(self.context, en_pointer, c_uint64(gen_handle))
        return error_code

    def gen_stop(self, env_name, gen_handle):
        bs = env_name.encode('utf-8')
        en_pointer = c_char_p(bs)
        mrt_lib.mrt_gen_stop.argtypes = [c_void_p, c_char_p, c_uint64]
        mrt_lib.mrt_gen_stop.restype = mrt_status_t
        error_code = mrt_lib.mrt_gen_stop(self.context, en_pointer, c_uint64(gen_handle))
        return error_code


    def record(self,env,isTrigger,t_bytes,data_pba,trigger_start=None,trigger_stop=None):
        temp_dir = "./dataRecordTemp"
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        with open(f"{temp_dir}/dataRecord_{env}_{self.fileNum}.tmp", "ab") as f:
            if isTrigger:
                if trigger_start is None:
                    tri_start = True
                else:
                    tri_start = self.record_trigger_start(*trigger_start)
                if trigger_stop is None:
                    tri_stop = False
                else:
                    tri_stop = self.record_trigger_stop(*trigger_stop)
                if tri_start and not tri_stop:
                    if self.recodeStatus < 0:
                        self.recodeStatus = 0
                    self.recodeStatus += 1
                    self.record_start = True
                elif tri_stop:
                        if self.recodeStatus > 0:
                            self.recodeStatus = 0
                        if self.recodeStatus == 0:
                            self.record_start = False
                            self.log_write(1, f"{env}", "stop-record!")
                            print("\nstop-record!")
                            self.recodeStatus -= 1
                if self.record_start:
                    if self.recodeStatus == 1:
                        self.log_write(1,f"{env}","Start the trigger!")
                        print("\nStart the trigger!")
                    f.write(t_bytes + data_pba)
                    print(f"\rWrite to record successful No:{self.writeNo}!", end='')
                    self.writeNo += 1
            else:
                f.write(t_bytes + data_pba)
                print(f"\rWrite to record successful No:{self.writeNo}!", end='')
                self.writeNo += 1
            f.flush()
            statinfo = os.stat(f"{temp_dir}/dataRecord_{env}_{self.fileNum}.tmp")
            if statinfo.st_size >= self.temp_size:  # 10M
                self.fileNum += 1

    def record_trigger(self,envN,instance_name, port_name, trigger_mode,signal_value,signal_value2=None):
        for portData in self.data_listTemp:
            if envN == self.record_env and portData[0]== instance_name and portData[1]==port_name:
                if trigger_mode == "=" and portData[3]== signal_value:
                    return True
                if trigger_mode == "!=" and portData[3] != signal_value:
                    return True
                if trigger_mode == ">" and portData[3] >signal_value:
                    return True
                if trigger_mode == "<" and portData[3] <signal_value:
                    return True
                if trigger_mode == ">=" and portData[3] >= signal_value:
                    return True
                if trigger_mode == "<=" and portData[3] <= signal_value:
                    return True
                if trigger_mode == "between" and signal_value <= portData[3] <= signal_value2:
                    return True
                else:
                    continue

    def record_trigger_start(self,envN,instance_name, port_name, trigger_mode,signal_value,signal_value2=None):
        if self.record_trigger(envN,instance_name, port_name, trigger_mode,signal_value,signal_value2):
            return True

    def record_trigger_stop(self,envN,instance_name, port_name, trigger_mode,signal_value,signal_value2=None):
        if self.record_trigger(envN,instance_name, port_name, trigger_mode, signal_value, signal_value2):
            return True

    def mrt_version(self):
        arr = bytearray(512)
        char_array = c_char * len(arr)
        buf_c = char_array.from_buffer(arr)
        mrt_lib.mrt_version.argtypes = [c_void_p]
        mrt_lib.mrt_version.restype = c_char_p
        version = mrt_lib.mrt_version(buf_c)
        return version.decode('utf-8')

    def mrtd_version(self):

        mrt_lib.mrtd_verison.argtypes = [c_void_p]
        mrt_lib.mrtd_verison.restype = c_char_p
        version = mrt_lib.mrtd_verison(self.context)
        return version.decode('utf-8')
