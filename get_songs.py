# -*- coding: utf-8 -*-
"""扫描桌面 music 文件夹里的所有 .mp3 文件并打印文件名。

文件夹不存在时会自动创建。
"""

import os
import sys

# Windows 控制台默认不是 UTF-8，文件名里的中文/日文会乱码，这里强制用 UTF-8 输出
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

MUSIC_DIR = r"C:\Users\wendy\Desktop\music"


def main():
    # 文件夹不存在则创建
    os.makedirs(MUSIC_DIR, exist_ok=True)

    mp3_files = []
    for name in os.listdir(MUSIC_DIR):
        full_path = os.path.join(MUSIC_DIR, name)
        if os.path.isfile(full_path) and name.lower().endswith(".mp3"):
            mp3_files.append(name)

    mp3_files.sort()

    print(f"文件夹：{MUSIC_DIR}")
    print(f"共找到 {len(mp3_files)} 个 .mp3 文件：")
    for idx, name in enumerate(mp3_files, 1):
        print(f"{idx:>4}. {name}")


if __name__ == "__main__":
    main()
