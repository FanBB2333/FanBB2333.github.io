from typing import List
from tqdm import tqdm
import os


SOURCE_DIR: str = '/Users/l1ght/Documents/Photo'

TARGET_DIR: str = "/Volumes/Apple/Photo"


def find_missing(recursive: bool = False,
                 dir_only: bool = True
                 ) -> List[str]:
    if not recursive:
        src_dir = os.listdir(SOURCE_DIR)
        target_dir = os.listdir(TARGET_DIR)
    else:
        src_dir = []
        target_dir = []
        for root, dirs, files in os.walk(SOURCE_DIR):
            src_dir.append(dirs)
        for root, dirs, files in os.walk(TARGET_DIR):
            target_dir.append(dirs)
    # find the dirs that are not in target_dir
    missing = []
    for dir in src_dir:
        if dir not in target_dir:
            if dir_only:
                if os.path.isdir(os.path.join(SOURCE_DIR, dir)):
                    missing.append(dir)
            else:
                missing.append(dir)
    return missing

def copy_one(path: str) -> None:
    # copy one file
    os.copy(path, TARGET_DIR)


if __name__ == '__main__':
    copy_files = find_missing()
    print(copy_files)
    
    