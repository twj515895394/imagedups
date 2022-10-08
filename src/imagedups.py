#!python
import multiprocessing as mp
import os
import shutil

import imagehash
import progressbar
from PIL import Image


def dupes(path, method="ahash"):
    subdirs = []
    paths = [path]
    for root, dirs, _ in os.walk(path):
        for name in dirs:
            subdirs.append(os.path.join(root, name))
    paths += subdirs
    files = []
    for path in paths:
        fs = os.listdir(path)
        for f in fs:
            fpath = os.path.join(path, f)
            if os.path.isdir(fpath):
                continue
            files.append(fpath)

    num_cores = int(mp.cpu_count())
    pool = mp.Pool(num_cores)
    manager = mp.Manager()
    managed_locker = manager.Lock()
    managed_dict = manager.dict()
    results = [pool.apply_async(async_hash, args=(fpath, managed_dict, managed_locker, method)) for fpath in files]

    pbar = progressbar.ProgressBar(max_value=len(files))
    for i, p in enumerate(results):
        p.get()
        pbar.update(i)
    pbar.finish()
    for k, v in managed_dict.items():
        if len(v) == 1:
            continue
        for idx, fpath in enumerate(v):
            if idx == 0:
                print("[保留]", fpath, os.path.getsize(fpath))
            else:
                print("[移除]", fpath, os.path.getsize(fpath))

                # 做移动而不是删除
                new_path = os.path.dirname(os.path.abspath(fpath)) + "/delete"
                # print(new_path)
                if not os.path.exists(new_path):
                    os.mkdir(new_path)
                (absp, file_name) = os.path.split(fpath)
                # print("file_name:" + file_name)
                shutil.move(fpath, os.path.join(new_path, file_name))
        print()


def async_hash(fpath, result_dict, result_lock, method):
    try:
        h = imagehash.average_hash(Image.open(fpath))
        if method == 'dhash':
            h = imagehash.dhash(Image.open(fpath))
        h = "%s" % h
        sims = result_dict.get(h, [])
        sims.append(fpath)
        with result_lock:
            result_dict[h] = sims
    except Exception as e:
        pass


def input_path():
    ipath = input("请输入图片所在文件夹路径:  ")
    if os.path.isdir(ipath) is False:
        return input("输入的不是文件路径，请输入图片所在文件夹路径")
    return ipath


def get_model():
    # 选择模式
    method = input("请选择识别模式:1.懒散模式 2.精细模式:  ")
    while method not in ["1", "2"]:
        method = input("输入格式有误， 请输入1或2:")
    return method


if __name__ == '__main__':

    ###说明###
    print('\033[0;32;40m ============================\033[0m')
    print('\033[0;30;46m  图片去重工具v.1.0.1 by 刺猬粑粑 \033[0m')
    print('\033[0;30;43m dfldata.xyz【论坛专用】\033[0m')
    print(r'''     _  __ _     _       _                         
        | |/ _| |   | |     | |                        
      __| | |_| | __| | __ _| |_ __ _  __  ___   _ ____
     / _` |  _| |/ _` |/ _` | __/ _` | \ \/ / | | |_  /
    | (_| | | | | (_| | (_| | || (_| |_ >  <| |_| |/ / 
     \__,_|_| |_|\__,_|\__,_|\__\__,_(_)_/\_\\__, /___|
                                              __/ |    
                                             |___/     ''')
    print('\033[0;32;40m ============================\033[0m')
    print('\033[0;33;40m 本工具作用：该工具主要用于src图片去重\033[0m')
    print('\033[0;33;40m 切src头像图片后，因为每帧可能会切好几张，导致重复图片过多，过多重复图片会给训练增加负担\033[0m')
    print('\033[0;33;40m 注意事项：只适用于处理src重复图片的筛选移除\033[0m')
    print('\033[0;32;40m ============================\033[0m')
    print('\033[0;32;40m 使用说明：\033[0m')
    print('\033[0;32;40m 1.输入人脸图片的路径，如D:/人脸图片路径 \033[0m')
    print('\033[0;32;40m 2.选择模式，1 懒散模式(推荐)，2 精细模式。\033[0m')
    print('\033[0;32;40m 3.比如a,b图片90%一样，但是可能有些细节，比如眼神看的方向是不一样的 \033[0m')
    print(
        '\033[0;32;40m   精细模式会认为这是两张不同图片选择保留，而懒散模式会认为这两张图片相同，会选择删除后一张图片 \033[0m')
    print('\033[0;32;40m 4.被移除的图片会保存在上面输入的目录下的delete文件夹中。\033[0m')
    print('\033[0;32;40m ============================\033[0m')

    npath = input_path()
    model = get_model()

    if model == "2":
        dupes(path=npath, method="dhash")
    else:
        dupes(path=npath)
