# -*- coding: utf-8 -*-
"""用通义千问多模态接口给 music 文件夹里的歌曲按曲风分类。

逐首联网搜索判断曲风：
- 优先用 title + artist 作为搜索关键词；
- title 为 None（无 ID3 标签）时降级用 file_name；
- 不预设分类、不限制分类数量，由模型根据搜索到的资料自主判断，可输出多个曲风标签。

每首歌返回 {"<完整 file_path>": ["曲风标签", ...]}，失败统一记为 ["未知"]。
"""

import os
import sys
import json
from http import HTTPStatus

import dashscope
from dashscope import MultiModalConversation

import config
from get_songs import get_songs

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

MODEL = "qwen3.7-plus"
RESULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classification.json")
UNKNOWN = ["未知"]


def strip_mp3_ext(name):
    """去掉 .mp3 后缀（兼容 move_files.py 的旧调用）。"""
    if name.lower().endswith(".mp3"):
        return name[:-4]
    return name


def build_keyword(song):
    """构造搜索关键词：优先 title + artist；title 为空时降级用 file_name。

    注意：绝不读取 file_path 里的目录名，目录名不参与曲风判断。
    """
    title = (song.get("title") or "").strip()
    artist = (song.get("artist") or "").strip()
    if title:
        return f"{title} {artist}".strip() if artist else title
    return (song.get("file_name") or "").strip()


def build_prompt(song):
    """为单首歌构造 prompt（多模态 content 用 [{"text": prompt}] 结构）。"""
    keyword = build_keyword(song)
    file_path = song["file_path"]
    return (
        "你是音乐曲风（Genre）分类助手。请联网搜索，判断下面这首歌的曲风。\n\n"
        f"输出 key（file_path）：{file_path}\n"
        f"用于搜索的歌曲信息（title + artist，或文件名）：{keyword}\n\n"
        "要求：\n"
        "1. 只依据「歌曲信息」联网搜索判断曲风，file_path 里的目录名不参与判断，必须忽略。\n"
        "2. 不预设分类、不限制分类数量，由你根据搜索到的资料自主判断，可以输出多个曲风标签。\n"
        "3. 曲风标签使用简短通用的音乐风格名词（如摇滚、爵士、流行、民谣、电子、说唱、纯音乐等）。\n"
        "4. 严格输出一个 JSON 对象：key 是上面的 file_path，value 是曲风标签数组。\n"
        "5. 只输出 JSON，不要任何解释、markdown 代码块或多余文字。\n"
        "6. 输出 JSON 时请正确转义 file_path 里的特殊字符（如反斜杠）。"
    )


def _stream_to_text(responses):
    """循环接收流式分片，拼接全部文本；请求失败时抛出异常。"""
    parts = []
    for resp in responses:
        if resp.status_code != HTTPStatus.OK:
            raise RuntimeError(
                f"API 状态码 {resp.status_code}：{getattr(resp, 'message', '')}"
            )
        try:
            content = resp.output.choices[0].message.content
        except (AttributeError, IndexError, KeyError):
            continue
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, (list, tuple)):
            for part in content:
                if isinstance(part, dict):
                    parts.append(part.get("text", ""))
                else:
                    parts.append(str(part))
    return "".join(parts)


def classify_one(song):
    """对单首歌联网判断曲风，返回拼接后的模型原始文本。"""
    messages = [{"role": "user", "content": [{"text": build_prompt(song)}]}]
    responses = MultiModalConversation.call(
        model=MODEL,
        messages=messages,
        stream=True,
        enable_search=True,
        search_options={"search_strategy": "agent"},
        api_key=config.QWEN_API_KEY,
    )
    return _stream_to_text(responses)


def parse_genres(raw_text, file_path):
    """从模型返回文本解析出该 file_path 的曲风标签数组；非 JSON 时抛出异常。"""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("模型输出不是 JSON 对象")

    genres = data.get(file_path)
    if genres is None:
        genres = next(iter(data.values()), None)

    if isinstance(genres, list):
        result = [str(g).strip() for g in genres if str(g).strip()]
        return result or list(UNKNOWN)
    if isinstance(genres, str) and genres.strip():
        return [genres.strip()]
    raise ValueError("模型输出里没有曲风标签数组")


def main():
    songs = get_songs()
    if not songs:
        print("没有找到任何 .mp3 文件")
        return

    result = {}
    total = len(songs)
    for idx, song in enumerate(songs, 1):
        file_path = song["file_path"]
        try:
            raw = classify_one(song)
            genres = parse_genres(raw, file_path)
        except Exception as e:
            print(f"[警告] {idx}/{total} 分类失败，记为未知：{song['file_name']}（{e}）")
            genres = list(UNKNOWN)
        result[file_path] = genres
        print(f"[{idx}/{total}] {song['file_name']} -> {genres}")

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 分类结果已保存到 {RESULT_FILE}")

    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
