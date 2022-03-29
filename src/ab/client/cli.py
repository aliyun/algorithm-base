import argparse
from ab.utils.security import encrypt_impl
from ab.client.crypto_cli import crypto_impl
from ab.client.crypto_cli import decrypto_impl
from ab.utils import abt
from ab.utils import abt_logger as logger


def cli():
    parser = argparse.ArgumentParser(description="abt 命令行")
    subparsers = parser.add_subparsers()
    add_clean_command(subparsers)
    add_deploy_command(subparsers, "test", "执行test路径下的所有测试用例")
    add_deploy_command(subparsers, "build", "构建docker镜像")
    add_deploy_command(subparsers, "push", "将docker镜像推送到仓库")
    add_deploy_command(subparsers, "deploy", "将应用部署到Serverless应用")
    add_undeploy_command(subparsers)
    add_file_command(subparsers)
    add_get_command(subparsers)
    add_encrypt_command(subparsers)
    add_crypto_command(subparsers)
    add_decrypto_command(subparsers)
    add_license_command(subparsers)
    add_project_command(subparsers)
    args = parser.parse_args()
    logger.info("abt command, the args is [{}]".format(args))
    if not hasattr(args, "func"):
        args = parser.parse_args(["-h"])
    if "operate" in args and args.operate != "create":
        from ab.utils.ab_config import config as ac
        ac.is_load()
    args.func(args)


def add_project_command(parsers):
    project_cmd = parsers.add_parser("project", help="项目命令")
    project_subparsers = project_cmd.add_subparsers()
    logs_cmd = project_subparsers.add_parser("create", help="创建新项目")
    logs_cmd.add_argument("-n", "--name", action="store", nargs="?", help="project name", required=True)
    logs_cmd.add_argument("-v", "--version", action="store", nargs="?", help="the version of algorithm-base to use")
    logs_cmd.set_defaults(func=abt.project, operate="create")


def add_deploy_command(parsers, cmd_name, msg):
    cmd = parsers.add_parser(cmd_name, help=msg)
    cmd.add_argument("-n", "--name", action="store", nargs="?", help="image name")
    cmd.add_argument("-v", "--version", action="store", nargs="?", help="image version")
    cmd.add_argument("-ns", "--namespace", action="store", nargs="?", help="namespace of serverless")
    cmd.add_argument("-s", "--skiptest", action="store", nargs="?", default=False, help="skip test or not")
    cmd.add_argument("-o", "--only", action="store", nargs="?", default=False, help="only the current step")
    cmd.add_argument("-c", "--use-cache", action="store", nargs="?", default=True, help="whether to use cache when "
                                                                                        "docker build")
    cmd.add_argument("-f", "--force", action="store", nargs="?", default=False, help="whether to overwrite deployed "
                                                                                     "applications when abt deploy")
    cmd.set_defaults(func=abt.cli, operate=cmd_name)


def add_clean_command(parsers):
    cmd = parsers.add_parser("clean", help="清理本地环境中的docker实例")
    cmd.add_argument("-n", "--name", action="store", nargs="?", help="image name")
    cmd.add_argument("-v", "--version", action="store", nargs="?", help="image version")
    cmd.set_defaults(func=abt.cli, operate="clean")


def add_undeploy_command(parsers):
    cmd = parsers.add_parser("undeploy", help="删除serverless应用中部署的项目")
    cmd.add_argument("-n", "--name", action="store", nargs="?", help="image name")
    cmd.add_argument("-ns", "--namespace", action="store", nargs="?", help="the namespace of serverless")
    cmd.set_defaults(func=abt.undeploy)


def add_file_command(parsers):
    file_cmd = parsers.add_parser("file", help="文件操作")
    file_subparsers = file_cmd.add_subparsers()
    # abt file download
    download_cmd = file_subparsers.add_parser("download", help="将oss中的文件下载到本地")
    # download_cmd.add_argument("-n", "--file-name", help="file name")
    download_cmd.set_defaults(func=abt.file, operate="download")
    # abt file upload
    upload_cmd = file_subparsers.add_parser("upload", help="将本地文件上传到oss")
    # upload_cmd.add_argument("-n", "--file-name", help="file name")
    upload_cmd.set_defaults(func=abt.file, operate="upload")


def add_get_command(parsers):
    get_cmd = parsers.add_parser("get", help="获取应用的部署信息及日志")
    get_subparsers = get_cmd.add_subparsers()
    # abt get logs
    logs_cmd = get_subparsers.add_parser("logs", help="获取应用的日志")
    logs_cmd.add_argument("-n", "--name", action="store", nargs="?", help="app name")
    logs_cmd.add_argument("-ns", "--namespace", action="store", nargs="?", help="the namespace of serverless")
    logs_cmd.add_argument("-f", "--file-name", action="store", nargs="?", help="file name")
    logs_cmd.set_defaults(func=abt.get, operate="logs")
    # abt get deploy
    deploy_cmd = get_subparsers.add_parser("deploy", help="获取应用的部署信息")
    deploy_cmd.add_argument("-n", "--name", action="store", nargs="?", help="app name")
    deploy_cmd.add_argument("-ns", "--namespace", action="store", nargs="?", help="the namespace of serverless")
    deploy_cmd.set_defaults(func=abt.get, operate="deploy")


def add_license_command(parsers):
    cmd = parsers.add_parser("license", help="许可证服务")
    cmd.add_argument("-v", "--verify", action="store", nargs="?", help="verify the input license file")
    cmd.set_defaults(func=license)


def add_encrypt_command(parsers):
    cmd = parsers.add_parser("encrypt", help="加密python文件")
    cmd.add_argument("-c", "--clear", action="store", default=False, nargs="?", help="clear the generated .c .py files")
    cmd.add_argument("-i", "--include", action="store", nargs="?", default=".*", help="the files will be encrypt, "
                                                                                      "using comma to split. "
                                                                                      "Supporting regex matcher. "
                                                                                      "Default encrypt all")
    cmd.add_argument('-e', '--exclude', action="store", nargs="?",
                     help='the files will NOT be encrypt, using comma to split. Supporting regex matcher')
    cmd.set_defaults(func=encrypt_impl)


def add_crypto_command(parsers):
    cmd = parsers.add_parser("crypto", help="加密数据文件")
    cmd.add_argument("-c", "--clear", action="store", nargs="?", default=False, help="clear the original files")
    cmd.add_argument("-i", "--include", action="store", nargs="?", help="crypto the specific file and "
                                                                        "folders. Supporting regex "
                                                                        "matcher")
    cmd.set_defaults(func=crypto_impl)

def add_decrypto_command(parsers):
    cmd = parsers.add_parser("decrypto", help="解密数据文件")
    cmd.add_argument("-c", "--clear", action="store", nargs="?", default=False, help="clear the original files")
    cmd.add_argument("-i", "--include", action="store", nargs="?", help="decrypto the specific file and "
                                                                    "folders. Supporting regex "
                                                                    "matcher")
    cmd.set_defaults(func=decrypto_impl)

def license(args):
    from ab.keys.crypto import license_impl
    license_impl(args.verify)


if __name__ == "__main__":
    cli()
