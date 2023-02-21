import ab
import os
import subprocess
import re
from ab.utils import oss_util
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
    pass


def download():
    pass



def deploy(args):
    pass



def undeploy(args):
    pass


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
    pass



def deploy_info(args):
    pass



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
    pass



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
