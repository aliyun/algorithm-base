import hashlib
from itertools import cycle
from datetime import timedelta, datetime


# only enc
def step1(input_line):
    sout = [chr(ord(a) ^ ord(b)) for (a, b) in
            zip(input_line, cycle("your-key"))]
    return "".join(sout)


# enc + md5
def step2(input_line):
    m = hashlib.md5()
    m.update(step1(input_line).encode('utf-8'))
    return m.hexdigest()


def license_create(path, days):
    """
    许可证明文格式
    ===== license start =====
    to:2022-06-19
    inode filename1
    inode filename2
    inode filename3
    inode filename4
    inode filename5
    inode filename6
    inode filename7
    ===== license end =====
    :param path:
    :return:
    """

    result = ""
    with open("license.ab", 'w') as of:
        # start
        l = "===== license start =====\n"
        of.write(l)
        result = result + l

        # enddate
        enddate = datetime.strftime(datetime.today() + timedelta(days=int(days)), '%Y-%m-%d')
        t = "to:{}".format(enddate)
        l = step1(t)
        l = l + "\n"
        of.write(l)
        result = result + l

        with open(path) as f:
            for num, line in enumerate(f, 1):
                # only need if the num from [2,8], total 7 lines
                if 2 <= num <= 8:
                    if "---" not in line:
                        license_string = step2(line.strip())
                        of.write(license_string)
                        of.write("\n")

                        result = result + license_string + "\n"
                    else:
                        raise RuntimeError("errors in license format")

        l = "===== license end ====="
        of.write(l)
        result = result + l
    print(result)


import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise RuntimeError("请依次输入2个参数 预检结果文件 和 许可证有效天数（如果永久许可，请输入99999)")
    filename = sys.argv[1]
    license_days = sys.argv[2]

    license_create(filename, license_days)
