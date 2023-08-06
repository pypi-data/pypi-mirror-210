import os,zipfile
import json
import codecs
r=os.path.abspath(os.path.dirname(__file__))
rootpath= os.path.split(r)[0]
sys.path.append(rootpath)
from vcarhilclient.Enums import mrt_port_type_t
from vcarhilclient.kunyi_util import kunyi_util


class instance_detail():
    def __init__(self):
        self.xpaths = {
            "instances": "",
        }
        self.name = ""
        self.input_ports = {}
        self.output_ports = {}
        self.calibrations = {}
        self.measurements = {}


class hil_project():

    def __init__(self, ipr_path):
        if not os.path.isfile(ipr_path):
            raise Exception("Invalid ipr path")
        with open(ipr_path,encoding='utf-8') as ipr_file:
            try:
                ipr_json = json.load(ipr_file)
            except Exception as ex:
                raise Exception("ipr is not a valid json file")
        self.project_name = ipr_json["ProjectName"]
        self.version = ipr_json["Version"]
        self.hil_json_path = os.path.join(os.path.dirname(ipr_path), ipr_json["HILSystemFilePath"])
        self.project_root_dir = os.path.dirname(ipr_path)
        if not os.path.isfile(self.hil_json_path):
            raise Exception("Invalid hil system file path")

        try:
            self.hil_json = json.load(codecs.open(self.hil_json_path, 'r', 'utf-8-sig'))
            self.system_id = self.hil_json["SystemID"]

            self.instances_orig = self.hil_json["Instances"]
            self.instances = {}
            for item in self.instances_orig:
                self.instances[item["InstanceName"]] = item
            self.model_meta_files_orig = self.hil_json["ModelMetaFiles"]
            self.model_meta_files = {}
            self.modelPath = {}
            for item in self.model_meta_files_orig:
                self.model_meta_files[item["ModelMetaFile"]] = item
                self.modelPath[item["ModelMetaFile"]] = os.path.join(os.path.dirname(ipr_path),item["File"]["Path"])
            pass

        except Exception as ex:
            raise Exception("hil file content is not correct")

    def get_Calibrations(self, instance, signal_type, cal_type, signal_name):
        instance_is_found = False
        signal_name_is_found = False
        cal_type_is_found = False
        st, stid = self.get_signalType(signal_type)
        for k, v in self.modelPath.items():
            if instance == k:
                instance_is_found = True
                with open(v) as f:
                    try:
                        instance_json = json.load(f)
                    except Exception as ex:
                        raise Exception(f"{v} is not a valid json file")
                    for cal_t, cal_v in instance_json[st].items():
                        if cal_t.lower() == cal_type.lower():
                            cal_type_is_found = True
                            for cal in cal_v:
                                if signal_name == cal["Name"]:
                                    signal_name_is_found = True
                                    if cal_type.lower() in ["curve", "map"]:
                                        data_type = cal["FunValue"]["DataType"]
                                    elif cal_type.lower() in ["scalar"]:
                                        data_type = cal["Value"]["DataType"]
                                    elif cal_type.lower() in ["vector"]:
                                        data_type = cal["Values"]["DataType"]
                                    return signal_name, stid, data_type
        if not instance_is_found:
            raise Exception(f"not found {instance},Please check the json parameters'var_instance'")
        if not cal_type_is_found:
            raise Exception(f"not found {cal_type},Please check the json parameters'var_cal_type'")
        if not signal_name_is_found:
            raise Exception(f"not found {signal_name},Please check the json parameters'var_signal_name'")

    def get_dataType_itemcount(self,instance,signal_type,signal_name):
        instance_is_found = False
        signal_name_is_found =False
        st,stid = self.get_signalType(signal_type)
        for k , v in self.modelPath.items():
            if instance == k:
                instance_is_found = True
                with open(v) as f:
                    try:
                        instance_json = json.load(f)
                    except Exception as ex:
                        raise Exception(f"{v} is not a valid json file")
                    for s in instance_json[st]:
                        if s["Name"] == signal_name:
                            signal_name_is_found = True
                            return s["Type"] , s["ItemCount"],stid
        if not instance_is_found:
            raise Exception(f"not found {instance},Please check the json parameters'var_instance'")
        if not signal_name_is_found:
            raise Exception(f"not found {signal_name},Please check the json parameters'var_signal_name'")

    def get_signalType(self,signal_type):
        st = signal_type.lower()
        if st == "inputport" or st == "inputports":
            return "InputPorts",(0,)
        if st == "outputport" or st == "outputports":
            return "OutputPorts",(1,)
        if st == "measurement" or st == "measurements" :
            return "Measurements",(2,)
        if st == "calibration" or st == "calibrations" :
            return "Calibrations",(3,)

        else:
            raise Exception(f"signal type error! ,Please check the json parameters'var_type'")




    def get_packageName(self,packageName):
        package_path = os.path.join(self.project_root_dir, "Packages", packageName)
        packagefileList = os.listdir(package_path)
        # self.model_json_path = os.path.join(self.project_root_dir, "Packages", packageName, "*.json")
        return package_path,packagefileList

    def build_zip(self):
        temp_dir = r'c:\zip_dir'
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        td =os.path.join(temp_dir, "build")
        zipPath = kunyi_util.file_compress(self.project_root_dir, td)
        return zipPath


    def get_instance_items(self, instance_name, item_type):
        if instance_name not in self.instances:
            return None
        meta_file_name = self.instances[instance_name]["ModelMetaFile"]
        model_json_path = os.path.join(self.project_root_dir,
                                       self.model_meta_files[meta_file_name]["File"]["Path"])
        try:
            model_json = json.load(codecs.open(model_json_path, 'r', 'utf-8-sig'))
            all_items = {}
            item_tys = item_type.split(".")
            if len(item_tys) == 1:
                json_parts = model_json[item_tys[0]]
            elif len(item_tys) == 2:
                if item_tys[1] in model_json[item_tys[0]]:
                    json_parts = model_json[item_tys[0]][item_tys[1]]
            else:
                raise Exception("item_type input is incorrect")
            for item in json_parts:
                all_items[item["Name"]] = item
            return all_items
        except:
            raise Exception("Invalid model file for instance %s" %(instance_name))

    def get_instance_item(self, instance_name, item_name, item_type):
        if instance_name not in self.instances:
            return None
        meta_file_name = self.instances[instance_name]["ModelMetaFile"]
        model_json_path = os.path.join(self.project_root_dir,
                                       self.model_meta_files[meta_file_name]["File"]["Path"])
        try:
            model_json = json.load(codecs.open(model_json_path, 'r', 'utf-8-sig'))
            item_tys = item_type.split(".")
            if len(item_tys) == 1:
                json_parts = model_json[item_tys[0]]
            elif len(item_tys) == 2:
                json_parts = model_json[item_tys[0]][item_tys[1]]
            else:
                raise Exception("item_type input is incorrect")
            for item in json_parts:
                if item["Name"] == item_name:
                    return item
            return None

        except:
            raise Exception("Invalid model file for instance %s" %(instance_name))

    def get_instance_detail(self, instance_name):
        if instance_name not in self.instances:
            return None
        return self.instances[instance_name]

    def get_ports(self, instanceName, packageName = "stdmdl"):
        filename = "unknow"
        inputPortsList = []
        outputPortsList = []
        package_path,pack_list = self.get_packageName(packageName=packageName)
        for file in pack_list:
            if file.split(".")[-1] == "json" and file.split(".")[0] == instanceName:
                filename = file
                break
        package_json_path = os.path.join(package_path,filename)
        with open(package_json_path,'r',encoding="utf-8-sig") as package_file:
            try:
                package_json = json.load(package_file)
            except Exception:
                raise Exception("package_file is not a valid json file")

        for inputport in package_json["InputPorts"]:
            portName = inputport["Name"]
            portType = inputport["Type"]
            portIdentify = (instanceName, portName, mrt_port_type_t.MRT_INPUT_PORT, portType)
            inputPortsList.append(portIdentify)

        for outputport in package_json["OutputPorts"]:
            portName = outputport["Name"]
            portType = outputport["Type"]
            portIdentify = (instanceName, portName, mrt_port_type_t.MRT_OUTPUT_PORT, portType)
            outputPortsList.append(portIdentify)
        return inputPortsList ,outputPortsList

    def instance_computemethod_initialize(self, json_dir, instance_name):
        """
        Modify the JSON of the instance according to the JSON file of the custom ComputeMethod
        :param json_dir: Custom ComputeMethod JSON file path
        :param instance_name: The name of the concrete instance
        """
        if instance_name not in self.instances:
            return None
        meta_file_name = self.instances[instance_name]["ModelMetaFile"]
        model_json_path = os.path.join(self.project_root_dir,
                                       self.model_meta_files[meta_file_name]["File"]["Path"])
        COMPU_TABs = []
        COMPU_VTAB_RANGEs = []
        COMPU_VTABs = []
        COMPU_TAB_BLENDs = []
        ComputeMethods = []
        try:
            with open(json_dir, "r", encoding="gbk") as f:
                m_json = json.load(f)
                ct = m_json['COMPU_TABs']
                cvr = m_json['COMPU_VTAB_RANGEs']
                cv = m_json['COMPU_VTABs']
                ctb = m_json['COMPU_TAB_BLENDs']
                cm = m_json['ComputeMethods']
                for item in ct:
                    COMPU_TABs.append(item)
                for item in cvr:
                    COMPU_VTAB_RANGEs.append(item)
                for item in cv:
                    COMPU_VTABs.append(item)
                for item in ctb:
                    COMPU_TAB_BLENDs.append(item)
                for item in cm:
                    ComputeMethods.append(item)
        except:
            raise Exception("Invalid json file, please check whether the file exists")
        try:
            with open(model_json_path, "r", encoding="utf-8-sig") as f:
                data_json = json.load(f)
                data_json['COMPU_TABs'] = COMPU_TABs
                data_json['COMPU_VTAB_RANGEs'] = COMPU_VTAB_RANGEs
                data_json['COMPU_VTABs'] = COMPU_VTABs
                data_json['COMPU_TAB_BLENDs'] = COMPU_TAB_BLENDs
                data_json['ComputeMethods'] = ComputeMethods
                with open(model_json_path, "w", encoding="utf-8-sig") as w:
                    json.dump(data_json, w)
        except:
            raise Exception("Invalid model file for instance %s" % instance_name)

    def add_instance_computemethod(self, instance_name, **port_method):
        """
        ComputeMethod binding of the specific instance port based on the passed parameters
        :param instance_name: The name of the concrete instance
        :param port_method: This is a dictionary of port types, names of specific ports, and ComputeMethod names; eg: {
        "InputPorts": {"port_name": "ComputeMethod_name"......}, "OutputPorts": {"port_name": "ComputeMethod_name"......}}
        """
        if instance_name not in self.instances:
            return None
        meta_file_name = self.instances[instance_name]["ModelMetaFile"]
        model_json_path = os.path.join(self.project_root_dir,
                                       self.model_meta_files[meta_file_name]["File"]["Path"])
        ports = []
        input_ports = []
        output_ports = []
        for item in port_method.items():
            ports.append(item)

        test0 = ports[0][0]
        for i in ports[0][1].items():
            input_ports.append(i)

        test1 = ports[1][0]
        for j in ports[1][1].items():
            output_ports.append(j)

        try:
            with open(model_json_path, "r", encoding="utf-8-sig") as r:
                model_json = json.load(r)
                input_parts = model_json[test0]
                output_parts = model_json[test1]
                for i in range(0, len(input_ports)):
                    for item_in in input_parts:
                        if item_in["Name"] == input_ports[i][0]:
                            item_in["RefComputeMethod"] = input_ports[i][1]
                            break
                for j in range(0, len(output_ports)):
                    for item_out in output_parts:
                        if item_out["Name"] == output_ports[j][0]:
                            item_out["RefComputeMethod"] = output_ports[j][1]
                            break
                with open(model_json_path, "w", encoding="utf-8-sig") as a:
                    json.dump(model_json, a)
        except:
            raise Exception("Invalid model file for instance %s" % instance_name)

    def get_model_detail(self, model_meta_file, key):
        if model_meta_file not in self.model_meta_files:
            raise Exception("Wrong model metafile name pass in")
        model_meta_full_path = os.path.join(self.project_root_dir, model_meta_file)
        with open(model_meta_full_path) as mmf:
            mmf_json = json.load(mmf)
        if key not in mmf_json:
            return None
        return mmf_json[key]

    def get_struct_detail(self, model_meta_file, struct_name):
        if model_meta_file not in self.model_meta_files:
            raise Exception("Wrong model metafile name pass in")
        all_struct = self.get_model_detail(model_meta_file, "Structs")
        the_struct = None
        for struct in all_struct:
            if struct["Name"] == struct_name:
                the_struct = struct
        return the_struct