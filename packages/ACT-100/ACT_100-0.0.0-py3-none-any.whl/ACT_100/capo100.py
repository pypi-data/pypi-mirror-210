import os
from pathlib import Path
import shutil
from send2trash import send2trash


def creat_100_times(dst, copy_to):
    dst = fr'{dst}\Here'
    copy_to = Path(fr'{copy_to}')
    try:
        send2trash(dst)
    except:
        pass
    os.mkdir(dst)
    for t in range(80):
        dst = f'{dst}\{t}'
        os.mkdir(dst)
    shutil.move(copy_to, f'{dst}/{copy_to.name}')
    print(dst)
