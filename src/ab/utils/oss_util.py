import subprocess
from ab.utils.abt_config import config

ossutil = config.get_value("ossutil")


def download(bucket: str, local_file: str, oss_file: str, update: bool, is_folder: bool):
    command_list = [ossutil, " cp "]
    if is_folder:
        command_list.append(" -r ")
    command_list.append(" oss://")
    command_list.append(bucket)
    command_list.append("/")
    command_list.append(oss_file)
    command_list.append(" ")
    command_list.append(local_file)
    if update:
        command_list.append(" -u")
    subprocess.run("".join(command_list), shell=True)


def upload(bucket: str, local_file: str, oss_file: str, update: bool, is_folder: bool):
    command_list = [ossutil, " cp "]
    if is_folder:
        command_list.append(" -r ")
    command_list.append(local_file)
    command_list.append(" ")
    command_list.append(" oss://")
    command_list.append(bucket)
    command_list.append("/")
    command_list.append(oss_file)
    if update:
        command_list.append(" -u")
    subprocess.run("".join(command_list), shell=True)


def create_directory(bucket_name, dir_name):
    command_list = [ossutil, " mkdir ", " oss://", bucket_name,  "/", dir_name]
    subprocess.run("".join(command_list), shell=True)


def create_directories(oss_mount):
    for oss in oss_mount:
        create_directory(oss.get_bucket_name(), oss.get_bucket_path())


def list_file(bucket_name, dir_name):
    command_list = [ossutil, " ls ", " oss://", bucket_name, "/", dir_name]
    subprocess.run("".join(command_list), shell=True)


def rm_object(bucket_name, dir_name):
    command_list = [ossutil, " rm ", " oss://", bucket_name, "/", dir_name, " -r -f"]
    subprocess.run("".join(command_list), shell=True)


def desc_file(file_name):
    command_list = [ossutil, " cat ", file_name]
    subprocess.run("".join(command_list), shell=True)

