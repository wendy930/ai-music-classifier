# -*- coding: utf-8 -*-
"""扫描桌面 music 文件夹里的所有 .mp3 文件，读取 ID3 标签提取歌名和歌手。

- 文件夹不存在时会自动创建。
- 只扫描后缀为 .mp3 的文件（含子文件夹）。
- 每首歌返回一个字典：
    file_path（完整绝对文件路径）、file_name（磁盘文件名）、title（歌名）、artist（歌手）。
- 当 mp3 没有 ID3 标签、文件损坏或读取标签失败时，title 和 artist 为 None
  （json.dumps 后自动变成 null）。
"""

import os
import sys
import json

from mutagen.id3 import ID3

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

MUSIC_DIR = r"C:\Users\wendy\Desktop\music"


def _frame_text(tags, key):
    """取出 ID3 文本帧（如 TIT2 歌名、TPE1 歌手）的第一个文本值，取不到返回 None。"""
    frame = tags.get(key)
    if frame is None:
        return None
    text = getattr(frame, "text", None)
    if not text:
        return None
    if isinstance(text, (list, tuple)):
        return str(text[0]).strip()
    return str(text).strip()


def _read_tags(file_path):
    """读取单个 mp3 的 (title, artist)；无 ID3 标签、文件损坏或读取失败返回 (None, None)。"""
    try:
        tags = ID3(file_path)
        return _frame_text(tags, "TIT2"), _frame_text(tags, "TPE1")
    except Exception:
        return None, None


def get_songs(music_dir=MUSIC_DIR):
    """扫描文件夹里的所有 .mp3 文件，返回 [{file_path, file_name, title, artist}, ...]。"""
    # 文件夹不存在则创建
    os.makedirs(music_dir, exist_ok=True)

    songs = []
    for root, _dirs, files in os.walk(music_dir):
        for name in files:
            if not name.lower().endswith(".mp3"):
                continue
            full_path = os.path.join(root, name)
            title, artist = _read_tags(full_path)
            songs.append({
                "file_path": full_path,
                "file_name": name,
                "title": title,
                "artist": artist,
            })

    songs.sort(key=lambda s: s["file_path"].lower())
    return songs


def get_mp3_files(music_dir=MUSIC_DIR):
    """兼容旧调用：只返回排序后的磁盘文件名列表。"""
    return [s["file_name"] for s in get_songs(music_dir)]


def main():
    songs = get_songs()

    print(f"文件夹：{MUSIC_DIR}")
    print(f"共找到 {len(songs)} 个 .mp3 文件：")
    print(json.dumps(songs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
