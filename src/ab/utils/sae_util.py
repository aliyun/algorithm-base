import json
import time

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from ab.utils.abt_config import config as ac
from ab.utils.ab_config import config as ab
from ab.utils import abt_logger as logger


class SaeRequest(object):
    def __init__(
            self,
            ak=ac.get_value("ak"),
            sk=ac.get_value("sk"),
            region_id="cn-hangzhou",
            method="GET",
            protocol_type="https",
            version="2019-05-06",
            url=None,
            params=None,
            action=None
    ):
        self._ak = ak
        self._sk = sk
        self._region_id = region_id
        self._method = method
        self._protocol_type = protocol_type
        self._domain = "sae." + region_id + ".aliyuncs.com"
        self._version = version
        self._url = url
        self._params = params
        self._action = action

    def get_ak(self):
        return self._ak

    def get_sk(self):
        return self._sk

    def get_region_id(self):
        return self._region_id

    def get_method(self):
        return self._method

    def get_protocol_type(self):
        return self._protocol_type

    def get_domain(self):
        return self._domain

    def get_version(self):
        return self._version

    def get_url(self):
        return self._url

    def get_params(self):
        return self._params

    def get_action(self):
        return self._action

    def set_ak(self, ak):
        self._ak = ak

    def set_sk(self, sk):
        self._sk = sk

    def set_region_id(self, region_id):
        self._region_id = region_id
        self._domain = "sae." + region_id + ".aliyuncs.com"

    def set_domain(self, domain):
        self._domain = domain

    def set_method(self, method):
        self._method = method

    def set_protocol_type(self, protocol):
        self._protocol_type = protocol

    def set_version(self, version):
        self._version = version

    def set_url(self, url):
        self._url = url

    def set_params(self, params):
        self._params = params

    def set_action(self, action):
        self._action = action

    def clean_params(self):
        self._params = None


class NameSpace(object):
    def __init__(self, name, ns_id, region, vpc_id, vswitch_id):
        self._vpc_id = vpc_id
        self._vswitch_id = vswitch_id
        self._name = name
        self._id = ns_id
        self._region = region

    def __str__(self):
        return json.dumps(self.__dict__)

    def get_name(self):
        return self._name

    def get_ns_id(self):
        return self._id

    def get_region(self):
        return self._region

    def get_vpc_id(self):
        return self._vpc_id

    def get_vswitch_id(self):
        return self._vswitch_id

    def set_vpc_id(self, vpc_id):
        self._vpc_id = vpc_id

    def set_vswitch_id(self, vswitch_id):
        self._vswitch_id = vswitch_id


class Application(object):
    def __init__(self, name, app_id, ns_id, region):
        self._name = name
        self._id = app_id
        self._ns_id = ns_id
        self._region = region

    def __str__(self):
        return json.dumps(self.__dict__)

    def get_name(self):
        return self._name

    def get_ns_id(self):
        return self._ns_id

    def get_region(self):
        return self._region

    def get_app_id(self):
        return self._id


class OssMount(object):
    def __init__(self, mount_path, bucket_path, read_only, bucket_name):
        self._mount_path = mount_path
        self._bucket_path = bucket_path
        self._read_only = str(read_only != "w" and read_only != "W")
        self._bucket_name = bucket_name

    def __repr__(self):
        return repr({"bucketName": self._bucket_name, "mountPath": self._mount_path, "bucketPath": self._bucket_path,
                     "readOnly": self._read_only})

    def __eq__(self, other):
        return self._bucket_name == other.get_bucket_name() and self._bucket_path == other.get_bucket_path()

    def get_bucket_name(self):
        return self._bucket_name

    def get_mount_path(self):
        return self._mount_path

    def get_bucket_path(self):
        return self._bucket_path

    def get_read_only(self):
        return self._read_only


def send_request(sae_request: SaeRequest):
    credentials = AccessKeyCredential(sae_request.get_ak(), sae_request.get_sk())

    client = AcsClient(region_id=sae_request.get_region_id(), credential=credentials)

    request = CommonRequest()
    request.set_accept_format('json')
    request.add_header('Content-Type', 'application/json')

    request.set_method(sae_request.get_method())
    request.set_protocol_type(sae_request.get_protocol_type())
    request.set_domain(sae_request.get_domain())
    request.set_version(sae_request.get_version())
    if sae_request.get_url() is not None:
        request.set_uri_pattern(sae_request.get_url())
    else:
        request.set_action_name(sae_request.get_action())

    params = sae_request.get_params()

    if params is not None and isinstance(params, dict):
        dict_params = dict(params)
        for key, value in dict_params.items():
            request.add_query_param(key, value)

    body = '''{}'''
    request.set_content(body.encode('utf-8'))
    try:
        response = client.do_action_with_exception(request)
        result = json.loads(str(response, encoding='utf-8'))
        return dict(result)
    except ServerException as e:
        result = {"Message": "error", "Details": "ServerException:{}".format(e)}
        return result
    except ClientException as e:
        result = {"Message": "error", "Details": "ClientException:{}".format(e)}
        return result
    except Exception as e:
        result = {"Message": "error", "Details": "Exception:{}".format(e)}
        return result


def list_namespaces(request: SaeRequest):
    request.set_url("/pop/v1/sam/namespace/describeNamespaceList")
    request.set_method("GET")
    request.set_params({"ContainCustom": "true"})
    result = send_request(request)
    ns_list = []

    if result.get("Message") == "success":
        data_list = result.get("Data")
        if data_list is not None:
            for data in data_list:
                ns_list.append(
                    NameSpace(data.get("NamespaceName"), data.get("NamespaceId"), data.get("RegionId"),
                              data.get("VpcId"), data.get("VSwitchId")))
    else:
        logger.error(result.get("Details"))
    return ns_list


def create_namespace(request: SaeRequest, namespace_name, namespace_id, desc):
    request.set_url("/pop/v1/paas/namespace")
    request.set_method("POST")
    request.set_params({"NamespaceId": namespace_id, "NamespaceName": namespace_name, "NamespaceDescription": desc})
    result = send_request(request)
    if result.get("Message") == "success" and result.get("Code") == 200 and result.get("Success"):
        return True
    else:
        logger.error("create namespace error [{}]".format(result.get("Details")))
        return False


def list_application(request: SaeRequest, app_name, namespace_id):
    request.set_url("/pop/v1/sam/app/listApplications")
    request.set_method("GET")
    params = {"AppName": app_name}
    if namespace_id is not None:
        params["NamespaceId"] = namespace_id

    request.set_params(params)
    result = send_request(request)
    app_list = []

    if result.get("Message") == "success":
        data_list = result.get("Data")
        if data_list is not None:
            ns_data = data_list.get("Applications")
            for data in ns_data:
                app_list.append(
                    Application(data.get("AppName"), data.get("AppId"), data.get("NamespaceId"), data.get("RegionId")))
    else:
        logger.error("get application list error [{}]".format(result.get("Details")))

    return app_list


def create_application(request: SaeRequest, params: dict):
    request.set_url("/pop/v1/sam/app/createApplication")
    request.set_method("POST")
    request.set_params(params)
    result = send_request(request)
    if result.get("Message") == "success" and result.get("Success"):
        return result.get("Data").get("AppId"), result.get("Data").get("ChangeOrderId")
    else:
        logger.error("create an application error [{}]".format(result.get("Details")))
        return None, None


def delete_application(request: SaeRequest, app):
    request.set_url("/pop/v1/sam/app/deleteApplication")
    request.set_method("DELETE")
    request.set_params({"AppId": app.get_app_id()})
    result = send_request(request)
    if result.get("Success"):
        return True, result.get("Data").get("ChangeOrderId")
    else:
        logger.error("delete an application error [{}]".format(result.get("Details")))
        return False, None


def slb_info(request: SaeRequest, slb_id):
    request.set_url(None)
    request.set_action("DescribeLoadBalancerAttribute")
    request.set_method("POST")
    request.set_version("2014-05-15")
    request.set_domain("slb.aliyuncs.com")
    request.set_params({"LoadBalancerId": slb_id})
    result = send_request(request)
    if result.get("Message") != "error":
        listener_ports = result.get("ListenerPorts")
        if listener_ports is None:
            return None
        else:
            return listener_ports.get("ListenerPort")
    else:
        logger.error("get slb list error [{}]".format(result.get("Details")))
        return None


def get_change_status(request: SaeRequest, change_id):
    request.set_url("/pop/v1/sam/changeorder/DescribeChangeOrder")
    request.set_method("GET")
    request.set_params({"ChangeOrderId": change_id})
    result = send_request(request)
    if result.get("Success") and result.get("Code") == 200:
        return result.get("Data").get("Status")
    logger.error("get change status error [{}]".format(result.get("Details")))
    return None


def get_app_name(args: dict):
    app_name = args.get(" -n ")
    if app_name is None:
        app_name = ab.get_value("app_name")
    return app_name


def get_app_version(args: dict):
    app_version = args.get(" -v ")
    if app_version is None:
        app_version = ab.get_value("app_version")
    return app_version


def get_sl_namespace():
    sl_namespace = ab.get_value("sl_namespace")
    if sl_namespace is None:
        sl_namespace = "Default"
    return sl_namespace


def get_region_id():
    region_id = ab.get_value("sl_region_id")
    if region_id is None:
        region_id = "cn-hangzhou"
    return region_id


def get_replicas():
    replicas = ab.get_value("sl_replicas")
    if replicas is None or not isinstance(replicas, int):
        return 1
    if int(replicas) > 10:
        return 10
    else:
        return int(replicas)


def get_sl_namespace_info(sl_namespace, get):
    if sl_namespace == "Default":
        return None

    request = SaeRequest()
    request.set_region_id(get_region_id())
    ns_list = list_namespaces(request)
    namespace = None
    if ns_list is not None:
        for ns in ns_list:
            if ns.get_name() == sl_namespace:
                namespace = ns
                break
    if namespace is not None:
        if namespace.get_vswitch_id() is None:
            namespace.set_vswitch_id(ab.get_value("vsw"))
        if namespace.get_vpc_id() is None:
            namespace.set_vpc_id(ab.get_value("vpc"))
        return namespace
    if get:
        return None

    logger.info("The namespace [{}] does not exist, create it now, Please wait...".format(sl_namespace))
    namespace_id = get_region_id() + ":abt" + str(int(time.time()))
    if create_namespace(request, sl_namespace, namespace_id, "Abt auto created."):
        logger.info("The namespace [{}] is created successfully".format(sl_namespace))
        return NameSpace(
            sl_namespace, namespace_id, get_region_id(), ab.get_value("vpc"), ab.get_value("vsw"))
    else:
        logger.error("Failed to create the namespace [{}].".format(sl_namespace))
        return None


def bind_slb_to_application(request: SaeRequest, app_id, slb_id, node_port, port):
    request.set_url("/pop/v1/sam/app/slb")
    request.set_method("POST")
    internet = json.dumps([{"port": node_port, "targetPort": port, "protocol": "HTTP"}])
    request.set_params({"AppId": app_id, "InternetSlbId": slb_id, "Internet": internet})
    result = send_request(request)
    if result.get("Message") != "error":
        return result.get("Data").get("ChangeOrderId")
    else:
        logger.error("bin slb error [{}]".format(result.get("Details")))
        return None


def get_application(app_name, namespace):
    request = SaeRequest()
    request.set_region_id(get_region_id())
    namespace_id = None
    if namespace is not None:
        namespace_id = namespace.get_ns_id()
    app_list = list_application(request, app_name, namespace_id)
    if app_list is not None:
        for app in app_list:
            if app.get_name() == app_name:
                return app

    return None


def get_image_url(args: dict):
    app_name = get_app_name(args)
    if app_name is None:
        logger.error("The app_name is None, Please check and try again")
        return None

    app_version = get_app_version(args)
    if app_version is None:
        logger.error("The app_version is None, Please check and try again")
        return None

    acr_address = ab.get_value("acr_address")
    acr_namespaces = ab.get_value("acr_namespace")

    if acr_address is None or acr_namespaces is None:
        logger.error("The acr_address or acr_namespace is None, Please check and try again.")
        return None

    return acr_address + "/" + acr_namespaces + "/" + app_name + ":" + app_version


def get_cpu():
    cpu = ab.get_value("cpu")
    if cpu is None or not isinstance(cpu, int):
        return 2000
    if int(cpu) > 8000:
        return 8000
    elif int(cpu) < 500:
        return 2000
    else:
        return int(cpu)


def get_memory():
    memory = ab.get_value("memory")
    if memory is None or not isinstance(memory, int):
        return 4096
    if int(memory) > 16384:
        return 16384
    elif int(memory) < 1024:
        return 4096


def get_app_params(args, image_url, namespace):
    app_name = get_app_name(args)
    params = {"AppName": app_name,
              "AppDescription": "An application that auto deployed by Abt.", "PackageType": "Image",
              "ImageUrl": image_url, "Cpu": get_cpu(), "Memory": get_memory(), "Replicas": get_replicas(),
              "Deploy": "true", "AutoConfig": "true"}

    if namespace is not None:
        params["NamespaceId"] = namespace.get_ns_id()
        params["AutoConfig"] = "false"
        params["VpcId"] = namespace.get_vpc_id()
        params["VSwitchId"] = namespace.get_vswitch_id()

    oss = []
    get_oss_log_mount(app_name, oss)
    get_oss_data_mount(oss)
    if not oss:
        return params
    params["OssAkId"] = ac.get_value("ak")
    params["OssAkSecret"] = ac.get_value("sk")
    params["OssMountDescs"] = oss
    init_oss_mount_path(oss)
    return params


def init_oss_mount_path(oss_mount):
    if not oss_mount:
        return
    oss = []
    for mount in oss_mount:
        if str(mount.get_bucket_path()).endswith("/"):
            oss.append(mount)
    from ab.utils import oss_util
    oss_util.create_directories(oss)


def get_oss_data_mount(oss_mount: list):
    index = 1
    bucket_name = ab.get_value("oss_bucket")
    while True:
        key = "data[" + str(index) + "]"
        data = ab.get_value(key)
        if data is None:
            break
        if ":" in data:
            file_list = data.split(":")
            oss = OssMount(
                file_list[0].strip(), file_list[1].strip(), "r" if len(file_list) == 2 else file_list[2].strip(),
                bucket_name)
            if oss not in oss_mount:
                oss_mount.append(oss)
        index = index + 1
    return oss_mount


def get_oss_log_mount(app_name, oss_mount):
    oss_mount.append(OssMount(get_log_path(), get_oss_log_path(app_name) + "/", "w", ab.get_value("oss_bucket")))


def get_log_path():
    return ab.get_value("log_path") if ab.get_value("log_path") is not None else "/root/app/logs"


def get_oss_log_path(app_name):
    return app_name + "/logs"


def get_status(change_id):
    import sys
    change_status = None
    for num in range(60):
        sys.stdout.flush()
        time.sleep(5)
        change_status = get_change_status(SaeRequest(), change_id)
        if change_status is None:
            break
        elif change_status != 0 and change_status != 1:
            break
    return change_status


def bind_slb(app_id, slb_id, port):
    list_slb = slb_info(SaeRequest(), slb_id)
    if list_slb is None:
        return False
    node_port = 8001
    n_port = ab.get_value("node_port")
    if n_port is not None:
        node_port = int(n_port)
    else:
        while True:
            if node_port in list_slb:
                node_port = node_port + 1
            else:
                break
    if port is None:
        port = 80
    return bind_slb_to_application(SaeRequest(), app_id, slb_id, node_port, port), node_port


def desc_app_slb(request: SaeRequest, app: Application):
    request.set_url("/pop/v1/sam/app/slb")
    request.set_params({"AppId": app.get_app_id()})
    request.set_method("GET")
    result = send_request(request)
    if result.get("Message") != "error":
        return result.get("Data")
    else:
        logger.error("get application info error [{}]".format(result.get("Details")))
        return None


def desc_app_config(request: SaeRequest, app: Application):
    request.set_url("/pop/v1/sam/app/describeApplicationConfig")
    request.set_params({"AppId": app.get_app_id()})
    request.set_method("GET")
    result = send_request(request)
    if result.get("Message") != "error":
        return result.get("Data")
    else:
        logger.error("get application config error [{}]".format(result.get("Details")))
        return None


def get_app_deploy_info(app_name, sl_namespace):
    namespace = None
    if sl_namespace != "Default":
        namespace = get_sl_namespace_info(sl_namespace, True)
        if namespace is None:
            logger.error("The namespace [{}] does not exist".format(sl_namespace))
            return None, None
    app = get_application(app_name, namespace)
    if app is None:
        logger.error("The application [{}] does not exist".format(app_name))
        return None, None
    request = SaeRequest()
    app_config = desc_app_config(request, app)
    app_slb = desc_app_slb(request, app)
    return app_config, app_slb


def deploy(args: dict) -> bool:
    logger.info("Start deploy, Please wait...")
    image_url = get_image_url(args)
    if image_url is None:
        return False
    else:
        logger.info("The image is: [{}]".format(image_url))

    sl_namespace = get_sl_namespace()

    sl_namespace_info = get_sl_namespace_info(sl_namespace, False)

    if sl_namespace_info is None and sl_namespace != "Default":
        return False
    app_name = get_app_name(args)
    app = get_application(get_app_name(args), sl_namespace_info)
    request = SaeRequest()
    if app is not None:
        usr_input = input("The application [{}] already exists. Do you want to delete the original application and "
                          "deploy the new application? (yes/no)".format(app_name))
        if str(usr_input).strip().lower() == "yes" or str(usr_input).strip().lower() == "y":
            logger.info("Deleting the application, Please wait...")

            result, change_id = delete_application(request, app)
            if not result:
                logger.error("Failed to delete the application.")
                return False
            else:
                from ab.utils import oss_util
                oss_util.rm_object(ab.get_value("oss_bucket"), get_oss_log_path(app_name) + "/")
                change_status = get_status(change_id)
                if change_status == 2:
                    logger.info("Deleting the application succeeded.")
                    logger.info("Creating an new application, Please wait...")
                else:
                    logger.error("Failed to delete the application.")
                    return False
        else:
            logger.warning("You have terminated the deployment operation")
            return False
    else:
        logger.info("Creating the application, Please wait...")

    app_id, change_id = create_application(request, get_app_params(args, image_url, sl_namespace_info))
    if app_id is None or change_id is None:
        return False
    change_status = get_status(change_id)
    if change_status is None or change_status != 2:
        logger.error("Failed to create an application.")
        return False
    else:
        logger.info("Creating an application succeeded.")

    logger.info("The SLB binding starts，Please wait...")
    change_id, node_port = bind_slb(app_id, ab.get_value("slb"), ab.get_value("port"))
    if change_id is None:
        logger.error("Failed to bind SLB.")
        return False
    change_status = get_status(change_id)
    if change_status == 2:
        logger.info("The SLB binding succeeded, Access path: [http://{}:{}].".format(ab.get_value("slb_ip"), node_port))
        return True
    logger.error("Failed to bind SLB.")
    return False


def undeploy(app_name, namespace):
    namespace_info = get_sl_namespace_info(namespace, True)
    if namespace_info is None and namespace != "Default":
        logger.error("The namespace [{}] does not exists".format(namespace))
        return False
    app = get_application(app_name, namespace_info)
    if app is None:
        logger.error("The application [{}] does not exists in namespace [{}]".format(app_name, namespace))
        return False
    result, _ = delete_application(SaeRequest(), app)
    from ab.utils import oss_util
    oss_util.rm_object(ab.get_value("oss_bucket"), get_oss_log_path(app_name) + "/")
    return result
