import ab
import os
import subprocess
import re
from ab.utils import oss_util, sae_util
from ab.utils.ab_config import config as ac
from ab.utils.abt_config import config as abt
from ab.utils import abt_logger as logger


def cli(args):
    operate = args.operate
    if operate == "clean":
        clean(args)
    elif operate == "deploy":
        deploy(build_params(args))
    elif operate == "undeploy":
        undeploy(build_params(args))
    else:
        exec_command(operate, build_params(args))


def file(args):
    operate = args.operate
    if operate == "upload":
        upload()
    else:
        download()


def get(args):
    operate = args.operate
    if operate == "logs":
        logs(args)
    else:
        deploy_info(args)


def clean(args):
    params = {}
    if args.name is not None:
        params[" -n "] = args.name
    if args.version is not None:
        params[" -v "] = args.version
    logger.info("abt clean, the args is [{}]".format(params))
    exec_command("clean", params)


def upload():
    oss = []
    sae_util.get_oss_data_mount(oss)
    import os
    curr_path = os.path.abspath(os.curdir)
    for mount in oss:
        oss_util.upload(
            mount.get_bucket_name(),
            mount.get_mount_path().replace("/root/app", curr_path),
            mount.get_bucket_path(),
            True,
            True)


def download():
    oss = []
    sae_util.get_oss_data_mount(oss)
    import os
    curr_path = os.path.abspath(os.curdir)
    for mount in oss:
        oss_util.download(
            mount.get_bucket_name(),
            mount.get_mount_path().replace("/root/app", curr_path),
            mount.get_bucket_path(),
            True,
            True)


def deploy(args):
    if args.get(" -o ") == "false":
        exec_command("push", args)
        exec_result = os.path.exists("/tmp/abt.log_tmp")
        if exec_result:
            logger.error("ABT deploy failed.")
            os.system("rm -rf /tmp/abt.log_tmp")
            return
    if sae_util.deploy(args):
        logger.info("The application has been successfully deployed to the Serverless")
    else:
        logger.error("ABT deploy failed.")


def undeploy(args):
    app_name = args.name if args.name is not None else ac.get_value("app_name")
    sl_namespace = args.namespace if args.namespace is not None else sae_util.get_sl_namespace()
    sae_util.undeploy(app_name, sl_namespace)


def exec_command(operate, args):
    command = get_command(operate, args)
    subprocess.run(command, shell=True)


def get_command(operate, args):
    abt_path = ab.__path__[0] + "/abt.sh "
    command = ". " + abt_path + " -i " + operate
    for key, value in args.items():
        command = command + key + " " + str(value)
    return command + " | tee -a /tmp/abt.log"


def logs(args):
    app_name = args.name if args.name is not None else ac.get_value("app_name")
    sl_namespace = args.namespace if args.namespace is not None else sae_util.get_sl_namespace()
    if args.file_name is None:
        app_slb = get_app_slb_info(app_name, sl_namespace)
        if app_slb is None:
            return
        internet = app_slb.get("Internet")
        if internet is not None and len(internet) != 0:
            command = "curl " + "'http://" + app_slb.get("InternetIp") + ":" + str(internet[0].get("Port")) \
                      + "/api/algorithm/sync_logs?path=" + sae_util.get_log_path() + "'"
            os.system(command)
        oss_util.list_file(ac.get_value("oss_bucket"), sae_util.get_oss_log_path(app_name))
    else:
        oss_util.desc_file(args.file_name)


def deploy_info(args):
    app_name = args.name if args.name is not None else ac.get_value("app_name")
    sl_namespace = args.namespace if args.namespace is not None else sae_util.get_sl_namespace()
    app_config, app_slb = sae_util.get_app_deploy_info(app_name, sl_namespace)
    keys = ["AppName", "RegionId", "PackageType", "ImageUrl", "Cpu", "Memory", "Replicas", "VSwitchId", "VpcId",
            "OssMountDescs", "InternetSlbId", "InternetIp", "Internet"]
    info = os.linesep
    for key in keys:
        if app_config is not None and key in app_config:
            info = info + key + ": " + str(app_config.get(key)) + os.linesep
        if app_slb is not None and key in app_slb:
            info = info + key + ": " + str(app_slb.get(key)) + os.linesep
    if info == os.linesep:
        logger.error("Get application deploy info error")
    else:
        logger.info("The application deploy info is: {}".format(info))


def build_params(args):
    params = {}
    if args.name is not None:
        params[" -n "] = args.name
    if args.version is not None:
        params[" -v "] = args.version
    if args.namespace is not None:
        params[" -ns "] = args.namespace
    params[" -s "] = str(args.skiptest).strip().lower()
    params[" -o "] = str(args.only).strip().lower()
    params[" -c "] = str(args.use_cache).strip().lower()
    params[" -f "] = str(args.force).strip().lower()
    params[" -u "] = abt.get_value("docker_registry_username")
    params[" -p "] = abt.get_value("docker_registry_password")
    params[" -l "] = ac.get_value("enable_license") if ac.get_value("enable_license") is not None else "false"
    return params


def get_app_slb_info(app_name, sl_namespace):
    namespace = None
    if sl_namespace != "Default":
        namespace = sae_util.get_sl_namespace_info(sl_namespace, True)
        if namespace is None:
            logger.error("The namespace [{}] does not exist".format(sl_namespace))
            return None
    app = sae_util.get_application(app_name, namespace)
    if app is None:
        logger.error("The application [{}] does not exist".format(app_name))
        return None
    return sae_util.desc_app_slb(sae_util.SaeRequest(), app)


def project(args):
    name = args.name
    if re.match("^[a-z]([-_a-z0-9]{3,63})+$", name) is None:
        logger.error("Failed to create project. The name must start with a lowercase letter and contain 4 to 64 "
                     "lowercase letters, digits, underscores (_), and hyphens (-).")
        return
    ab_path = ab.__path__[0]
    command = "cp -r " + ab_path.replace("/src/ab", "/examples/simple/") + " ./" + name
    subprocess.run(command, shell=True)
    replace(os.getcwd() + "/" + name, "simple", "simple", name)
    logger.info("Project created successfully, You can run 'cd ./" + name + ";pyab' to start the project.")


def replace(file_path, file_name, old, new):
    if os.path.isfile(file_path):
        if file_name == "doc.yaml" or "DS_Store" in file_name or file_name.endswith(".pyc"):
            return
        if file_name == "base.txt":
            subprocess.run("sed -i '' 's/algorithm-base.git/algorithm-base.git@" + get_ab_version() + "/' " + file_path, shell=True)
        subprocess.run("sed -i '' 's/" + old + "/" + new + "/' " + file_path, shell=True)
    else:
        if file_name == "docker":
            return
        for file_name in os.listdir(file_path):
            replace(file_path + "/" + file_name, file_name, old, new)


def get_ab_version():
    import configparser
    config_parser = configparser.RawConfigParser()
    config_parser.read(ab.__path__[0].replace("/src/ab", "/setup.cfg"), "utf-8")
    items = config_parser.items("metadata")
    for item in items:
        if item[0] == "version":
            return item[1]
