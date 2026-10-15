# -*- coding: utf-8 -*-
"""根据 classify.py 生成的 classification.json，把 music 里的歌曲移动到对应曲风子文件夹。

classification.json 格式：{"<完整 file_path>": ["曲风标签1", "曲风标签2", ...], ...}

- 取曲风数组的第一个标签作为目标文件夹名。
- 自动创建对应风格文件夹，把歌曲剪切移动进去。
- 源路径 == 目标路径时直接跳过；文件不存在或路径错误时打印警告并继续，不中断。
"""

import os
import sys
import json
import re
import shutil

from classify import RESULT_FILE
from get_songs import MUSIC_DIR

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

# Windows 文件夹名里不能出现的字符，统一替换成下划线
ILLEGAL_CHARS = r'[\\/:*?"<>|]'


def safe_folder_name(name):
    """把曲风标签清洗成合法的 Windows 文件夹名。"""
    name = re.sub(ILLEGAL_CHARS, "_", str(name)).strip().strip(".")
    return name or "未分类"


def main():
    if not os.path.exists(RESULT_FILE):
        print(f"未找到分类结果文件：{RESULT_FILE}")
        print("请先运行：python classify.py")
        return

    with open(RESULT_FILE, encoding="utf-8") as f:
        result = json.load(f)

    if not result:
        print("分类结果为空，没有可移动的文件")
        return

    moved = 0
    skipped = 0
    for file_path, genres in result.items():
        # 取曲风数组第一个标签作为目标文件夹名
        if isinstance(genres, list) and genres:
            folder = safe_folder_name(genres[0])
        elif isinstance(genres, str) and genres.strip():
            folder = safe_folder_name(genres)
        else:
            print(f"[警告] 曲风为空，跳过：{file_path}")
            skipped += 1
            continue

        src = os.path.normpath(file_path)
        dst_dir = os.path.join(MUSIC_DIR, folder)
        dst = os.path.join(dst_dir, os.path.basename(src))

        print(f"{file_path} -> {folder}/")

        if os.path.normcase(src) == os.path.normcase(dst):
            print("  已在目标文件夹，跳过")
            skipped += 1
            continue

        try:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.move(src, dst)
            print(f"  移动：{src} -> {dst}")
            moved += 1
        except Exception as e:
            print(f"[警告] 移动失败：{file_path}（{e}）")
            skipped += 1

    print(f"\n完成，共移动 {moved} 首，跳过 {skipped} 首。")


if __name__ == "__main__":
    main()
