import time
from threading import Thread
from vcarhilclient.kunyi_util import *


class signal_daq():

    def __init__(self, client, env, init_signal_list=[], max_buffer_len=30, fetch_period=1):
        self.client = client
        self.env = env
        # The key is daq handle and the value is the array of ports in this daq
        self.daqs = {}
        # The key is tuple of instance name, port name and port type, the value is the daq handle this port in
        self.full_signals = {}
        # The key is tuple of instance name, port name and port type, the value is the array buffer of all the values
        # of this port got from daq fetch
        self.full_signal_buffers ={}
        self.unfetch_signal = []
        self.max_buffer_len = max_buffer_len
        self.fetch_period = fetch_period
        self.keep_fetch = False
        if len(init_signal_list) > 0:
            self.add_monitoring_singals(init_signal_list)
        self.daq_handle = None
        self.daq_period = 100
        self.daq_offsiet = 0



    def add_monitoring_singals(self, signal_list):
        this_add_list = []
        for s in signal_list:
            # The s is tuple of instance name, port name, port type and datatype
            if s in self.unfetch_signal:
                self.unfetch_signal.remove(s)
                continue
            if s not in self.full_signals:
                this_add_list.append(s)
        if len(this_add_list) > 0:
            if self.daq_handle is None:
                rc, self.daq_handle = self.client.create_daq(self.env, len(this_add_list), 0)
                if rc.value != 0:
                    raise Exception("Create daq fail")
            rc = 0
            for i in range(len(this_add_list)):
                mrt_port_type = kunyi_util.string_to_mrt_signal_type(this_add_list[i][2])
                set_port_result = self.client.daq_set_port(self.env, self.daq_handle, i, this_add_list[i][0],
                                                   this_add_list[i][1], mrt_port_type, this_add_list[i][3])
                rc = rc + set_port_result.value

            if rc != 0:
                raise Exception("add signal to daq fail")
            self.client.daq_set_trigger_period(self.env, self.daq_handle, self.daq_period, self.daq_offsiet)

            rc = self.client.start_daq(self.env, self.daq_handle)
            if rc.value != 0:
                raise Exception("Start daq fail")
            self.daqs[(self.daq_handle,self.env)] = this_add_list
            for s_added in this_add_list:
                self.full_signals[s_added] = self.daq_handle
        if self.keep_fetch == False:
            self.start_fetch_daq()

    def destroy_daq(self):
        self.keep_fetch = False
        time.sleep(self.fetch_period)
        rc = 0
        for q, v in self.daqs.items():
            rc = rc + self.client.destroy_daq(self.env, q)
        if rc != 0:
            raise Exception("destroy daq fail")

    def remove_monitoring_singals(self, signal_list):
        self.unfetch_signal = self.unfetch_signal + signal_list

    def start_fetch_daq(self):
        if self.keep_fetch:
            return
        self.keep_fetch = True
        t1 = Thread(target=self.do_fetch,  daemon=False)
        t1.start()

    def stop_fetch_daq(self):
        self.keep_fetch = False
        time.sleep(self.fetch_period)
        rc = 0
        for q, v in self.daqs.items():
            rc = rc + self.stop_daq(self.env, q)
        if rc != 0:
            raise Exception("Stop daq fail")

    def do_fetch(self):
        while self.keep_fetch:
            for q, v in self.daqs.items():
                msg_list = self.client.daq_read(self.env, q[0], 1, None)
                for msg in msg_list:
                    for item in msg:
                        # The key is tuple of instance name, port name and port type
                        the_key = (item[0], item[1], item[2])
                        if the_key in self.unfetch_signal:
                            continue
                        if the_key not in self.full_signal_buffers:
                            self.full_signal_buffers[the_key] = []
                        if len(self.full_signal_buffers[the_key]) > self.max_buffer_len:
                            self.pop(the_key)
                        self.full_signal_buffers[the_key].append((item[3], item[4]))
            time.sleep(self.fetch_period)

    def is_signal_monited(self, signal):
        return signal in self.full_signal_buffers

    def pop(self, signal):
        if signal not in self.full_signal_buffers:
            return None
        try:
            if len(self.full_signal_buffers[signal][0]) == 0:
                return None
        except:
            return None

        result = self.full_signal_buffers[signal][0]
        del(self.full_signal_buffers[signal][0])
        return result

    def pop_all(self, signal):
        if signal not in self.full_signal_buffers:
            return None

        result = self.full_signal_buffers[signal]
        self.full_signal_buffers[signal] = []
        return result


    def pop_last(self, signal):
        result = self.pop_all(signal)
        if (result is None) or (len(result)<1):
            return None
        return result[len(result) - 1]