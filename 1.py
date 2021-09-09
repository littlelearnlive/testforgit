# --*-- coding: utf-8 --*--
"""Get the syscall data of the container's process.

Usage: 
    python get_data.py -c <containerID>

References:
    Docker SDK for Python:
        https://docker-py.readthedocs.io/en/stable/
    python-ptrace:
        https://python-ptrace.readthedocs.io/en/latest/
"""

import os
import sys
import subprocess
import shutil
import logging
import argparse
import time
from multiprocessing import Process


def init_logger(logger_name, logger_file):
    """
    init a logger
    :param logger_name ：日志名称
    :param logger_file ：日志文件路径
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(name)-12s : %(levelname)-8s : %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S')
    # logging to file
    fileHandler = logging.FileHandler(logger_file)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    # logging to streamHandler
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.info("> "*5 + f"Initial the Logger {logger_name}" + " <"*5)
    return logger


def directory_check(path):
    """
    检查路径是否标准
    :param path:dir path
    """
    return path + '/' if path[-1] != '/' else path


def strace_capture(cid):
    '''
    use strace to caputre data
    :param cid: container id
    '''
    start_time = time.time()
    """trace_data = './trace_data/'
    logger_file = './tracer.log'
    main_logger = init_logger(sys._getframe().f_code.co_name, logger_file)

    file_path = directory_check(trace_data)
    if os.path.exists(file_path):
        shutil.rmtree(file_path)  # delete path and file recursively
        os.makedirs(file_path)
    else:
        os.makedirs(file_path)"""
    #获取ppid和pid


    ppidc = "docker top %s | awk 'NR==2 {print $3}'" % (cid)
    pptop = os.popen(ppidc, "r")
    for ppid in pptop:
        ppid = ppid.strip('\n')
    pidc = "docker top %s | awk 'NR==2,NR==0 {print $2}'" % (cid)
    ptop = os.popen(pidc, "r")
    popen_objs = []
    for pnum, pid in enumerate(ptop, 1):
        pid = pid.strip('\n')

    try:
        strace_str = "strace -e trace=all -f -t -y -qq -o {0} -p {1},{2}".format(file_path + cid, pid, ppid)
        popen_objs.append(subprocess.Popen(strace_str, shell=True))
        while 1 :
            time.sleep(10)
            print('logging')
    except KeyboardInterrupt:
        for p_obj in popen_objs:
            p_obj.terminate()
            main_logger.critical(f"Terminate {p_obj}")
        main_logger.critical("Interrupt manually.")
    finally:
        for p_obj in popen_objs:
            p_obj.terminate()
            main_logger.critical(f"Terminate {p_obj}")
        end_time = time.time()
        main_logger.info(f"Total time: {end_time-start_time:.5f}s\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get the syscall data of the \
        container's process")
    parser.add_argument('-i', '--id', help="The ID of the Docker container",
        metavar="ID")
    args = parser.parse_args()
    trace_data = './trace_data/'
    logger_file = './tracer.log'
    main_logger = init_logger(sys._getframe().f_code.co_name, logger_file)

    file_path = directory_check(trace_data)
    """if os.path.exists(file_path):
        shutil.rmtree(file_path)  # delete path and file recursively
        os.makedirs(file_path)
    else:
        os.makedirs(file_path)"""
    containers_list = []
    if args.id is not None:
        container_id_list = [i[:-2] for i in list(args.id.split(','))]
        # 容器在 shell 中显示的 id，比 short_id 得到的多了两个字符
        containers_list += container_id_list
    print(containers_list)
    for id in containers_list:
        p=Process(target=strace_capture,args=(id,))
        p.start()

        #strace_capture(id)

    #strace_capture(args.id)

