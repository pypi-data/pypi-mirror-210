# pymrt_client Package
# kunyi automatic test mrt client；

# Example:

# 1.Create a connection:
from pymrt_client.kunyi_mrt import *

my_mrt = mrt_client("192.168.5.43", "8888", "8889", "8890")

ec = my_mrt.connet()

assert ec.value == 0

# 2.Create experiment
ec = my_mrt.create_test_env("envName")

assert ec.value == 0

# 3.Send test package
ec, file_id = my_mrt.download_file(pf_path)

assert ec.value == 0

# 4.Send mapping file
ec, mapping_id = my_mrt.download_file(mapping_path)

assert ec.value == 0

# 5.Load device mapping
ec = my_mrt.load_device_mapping(map_id)
    assert ec.value == 0

# 6.Loading test package
my_mrt.load_test_resources_to_env("envName", file_id)

# 7.Start the experiment
ec = my_mrt.start_test("envName")

assert ec.value == 0

# 8.Enter the inputport send value
rc = my_mrt.set_input_port_value("envName", "expression_1", "x[0]", "Double", 1.1,item_count=1,struct_detail=None)

assert rc == 8

# 9.Get outputport value
rc, value = my_mrt.get_output_port_value("envName", "expression_1", "y[0]", "Double",item_count=1,struct_detail=None)

assert rc == 8

assert value == 1.1

# 10.Create daq
ec, daq_handle = my_mrt.create_daq("envName", 2, 0)

assert ec.value == 0, "resValue:{}".format(ec.value)

# 11.daq set port
ec = my_mrt.daq_set_port("envName", daq_handle, 0, "expression_1", "x[0]",
                             mrt_port_type_t.MRT_INPUT_PORT, "Double")

assert ec.value == 0, "resValue:{}".format(ec.value)

# 12.start daq
ec = my_mrt.start_daq("envName", daq_handle)

assert ec.value == 0, "resValue:{}".format(ec.value)

# 13.Read daq
res_code  = my_mrt.daq_read("envName", daq_handle,item_count=1,sub_struct_detail=None)

# 14.Creation generator
ec , gen_handle = my_mrt.create_gen("envName",2)

assert ec.value ==0

# 15.Stop daq
ec = my_mrt.stop_daq("envName", daq_handle)

assert ec.value == 0

# 16.Destroy daq
ec = my_mrt.destroy_daq("envName", daq_handle)

assert ec.value == 0

# 17.Stop the experiment
ec = my_mrt.stop_test("envName")

assert ec.value == 0

# 18.Delete the experiment
ec = my_mrt.delete_test_env("envName")

assert ec.value == 0

