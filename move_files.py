# -*- coding: utf-8 -*-
"""根据 classify.py 生成的分类结果，把 music 里的歌曲移动到对应流派子文件夹。

用法：
    1. python classify.py    # 生成 classification.json
    2. python move_files.py          # 实际移动
       python move_files.py --dry-run  # 先预览，不真正移动

每个流派会在 music 文件夹下创建同名子文件夹，并把对应歌曲移动进去。
"""

import os
import sys
import json
import re
import shutil

from classify import RESULT_FILE, strip_mp3_ext
from get_songs import get_mp3_files, MUSIC_DIR

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

# Windows 文件夹名里不能出现的字符，统一替换成下划线
ILLEGAL_CHARS = r'[\\/:*?"<>|]'


def safe_folder_name(name):
    """把类别名清洗成合法的 Windows 文件夹名。"""
    name = re.sub(ILLEGAL_CHARS, "_", name).strip().strip(".")
    return name or "未分类"


def match_files(stems, result):
    """把 {流派: [{song, artist}]} 映射回文件名主干，返回 {主干: 流派}。

    匹配规则：song 必须是文件名主干的子串；artist 非「未知」时也必须是子串。
    无法唯一匹配的条目会打印警告并跳过。
    """
    matched = {}
    for category, entries in result.items():
        for entry in entries:
            song = str(entry.get("song", "")).strip()
            artist = str(entry.get("artist", "")).strip()
            candidates = []
            for stem in stems:
                if stem in matched:
                    continue
                if song and song not in stem:
                    continue
                if artist and artist != "未知" and artist not in stem:
                    continue
                candidates.append(stem)
            if len(candidates) == 1:
                matched[candidates[0]] = category
            else:
                print(f"[警告] 无法唯一匹配：song={song!r}, artist={artist!r}，已跳过")
    return matched


def main():
    dry_run = "--dry-run" in sys.argv

    filenames = get_mp3_files()
    if not filenames:
        print("没有找到任何 .mp3 文件")
        return

    if not os.path.exists(RESULT_FILE):
        print(f"未找到分类结果文件：{RESULT_FILE}")
        print("请先运行：python classify.py")
        return

    with open(RESULT_FILE, encoding="utf-8") as f:
        result = json.load(f)

    stem_to_file = {strip_mp3_ext(f): f for f in filenames}
    matched = match_files(list(stem_to_file.keys()), result)
    if not matched:
        print("没有匹配到任何可移动的文件")
        return

    moved = 0
    for stem, category in matched.items():
        folder = safe_folder_name(category)
        dst_dir = os.path.join(MUSIC_DIR, folder)
        filename = stem_to_file[stem]
        if dry_run:
            print(f"[预览] {filename} -> {folder}/")
        else:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.move(os.path.join(MUSIC_DIR, filename), os.path.join(dst_dir, filename))
            print(f"移动：{filename} -> {folder}/")
        moved += 1

    action = "预览" if dry_run else "移动"
    print(f"\n完成，共{action} {moved} 首歌。")


if __name__ == "__main__":
    main()
