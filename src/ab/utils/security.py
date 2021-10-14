import os
import subprocess
import re
from jinja2 import Environment, PackageLoader
from ab.utils import logger


def gen_cython_setup(root_dir, files):
    """
    加密root_dir文件夹下的files模块组
    :return:
    """
    env = Environment(loader=PackageLoader('ab', 'templates'))
    template = env.get_template('cython_setup.py')
    content = template.render(files=files)
    position = root_dir + "/setup.py"

    file = open(position, "w")
    file.write(content)
    file.close()


def build_c():
    """
    编译
    :return:
    """
    command = "python setup.py build_ext --inplace"
    subprocess.run(command, shell=True)


def clear_files(dir, target_files):
    """
    删除无用文件
    :param dir:
    :param target_files:
    :return:
    """
    # remove python
    for f in target_files:
        command = "rm -rf {}".format(f)
        subprocess.run(command, shell=True)

    # remove .c
    for f in target_files:
        t = f.replace(".py", ".c")
        command = "rm -rf {}".format(t)
        subprocess.run(command, shell=True)


def list_dir(include, exclude):
    """
    列出需要加密的python文件
    :return:
    """
    if exclude is not None:
        excludes = exclude.split(",")

    if include is not None:
        includes = include.split(",")

    def include_name(oname):
        if include is not None:
            for e in includes:
                match = re.search(e, oname)
                if match:
                    return True
        return False

    def exclude_name(oname):
        if exclude is not None:
            for e in excludes:
                match = re.search(e, oname)
                if match:
                    return False
        return True

    dir = os.getcwd()
    target_files = []
    for root, dirs, files in os.walk(dir, topdown=True):
        for name in files:
            if name[-3:] == ".py":
                if include_name(os.path.join(root, name)) and exclude_name(os.path.join(root, name)):
                    target_files.append(os.path.join(root, name))

    l = len(dir)
    target_files = [x[l + 1:] for x in target_files]

    for f in target_files:
        logger.info("will encrypt file : {}".format(f))
    return dir, target_files


def encrypt_impl(args):
    dir, target_files = list_dir(args.include, args.exclude)

    gen_cython_setup(dir, target_files)

    build_c()

    if args.clear:
        clear_files(dir, target_files)
