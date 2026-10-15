# -*- coding: utf-8 -*-
"""一键流水线：扫描 music 文件夹 → AI 联网分类曲风 → 按曲风移动文件。"""

import sys

import get_songs
import classify
import move_files

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def main():
    # 第 1 步：扫描本地 music 文件夹
    print("正在扫描…")
    songs = get_songs.get_songs()
    print(f"  扫描完成，共 {len(songs)} 首。")
    if not songs:
        print("没有找到任何 .mp3 文件，流程结束。")
        return

    # 第 2 步：调用 AI 分类
    print("正在分类…")
    classify.main()

    # 第 3 步：根据分类结果移动文件
    print("正在移动文件…")
    move_files.main()

    print("全部完成。")


if __name__ == "__main__":
    main()
