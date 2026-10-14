# -*- coding: utf-8 -*-
"""把 music 文件夹里的歌曲按音乐流派分类，调用通义千问 API。

把去掉 .mp3 后缀的原始文件名直接发给 AI，由 AI 自己清理干扰信息、
判断歌名和歌手，并按音乐流派（Genre）分类，不按国家/语言分，开启联网搜索。
返回 JSON：{"流派名": [{"song": "纯歌名", "artist": "纯歌手名"}, ...], ...}
"""

import sys
import json

from openai import OpenAI

import config
from get_songs import get_mp3_files

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen3.7-plus"


def strip_mp3_ext(name):
    """去掉 .mp3 后缀，返回原始文件名主体。"""
    if name.lower().endswith(".mp3"):
        return name[:-4]
    return name


def classify_songs(stems):
    """stems: 去掉 .mp3 后的原始文件名列表，返回 {流派: [{song, artist}, ...]}。"""
    client = OpenAI(api_key=config.QWEN_API_KEY, base_url=BASE_URL)

    system_prompt = (
        "你是一名专业的音乐分类助手。用户会给你一个歌曲文件名列表（已去掉 .mp3 后缀）。"
        "你必须严格按「音乐流派（Genre）」分类，只分析歌曲本身的流派，绝不要按国家或语言分类。"
        "参考流派包括但不限于：摇滚、爵士、说唱、纯音乐/器乐、电子、民谣、流行等，"
        "可以根据歌曲实际情况自行增减类别。"
        "如果一首歌跨越多个流派，只归入其中最主要的那个流派。"
        "不要预先限制类别数量，类别的多少完全由歌曲的实际流派决定。"
        "把每首歌恰好分到其中一个最合适的类别里。"
        "文件名可能包含干扰信息（如末尾的 -1、(1)、[官方版]、专辑名等）。"
        "请你先清理这些干扰信息，再判断哪个是歌名、哪个是歌手。"
        "返回 JSON 时，song 只写清理后的纯歌名，artist 只写纯歌手名，不要保留任何干扰字符。"
        "只输出一个 JSON 对象，不要输出任何解释、markdown 代码块或多余文字。"
        "JSON 的 key 是流派类别名（用简洁的中文），value 是该类别下歌曲的数组。"
        "数组里每一项是一个对象，必须同时包含 song（歌名）和 artist（歌手）两个字段。"
    )
    user_prompt = "请分类以下歌曲（文件名列表）：\n" + "\n".join(stems)

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        extra_body={"enable_search": True},
    )

    content = completion.choices[0].message.content
    print("=== AI 原始返回 ===")
    print(content)
    return json.loads(content)


def main():
    filenames = get_mp3_files()
    if not filenames:
        print("没有找到任何 .mp3 文件")
        return

    stems = [strip_mp3_ext(name) for name in filenames]
    print(f"共 {len(stems)} 首歌，正在让通义千问分类…")

    result = classify_songs(stems)

    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
