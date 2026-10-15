# AI 音乐自动分类助手

扫描本地音乐文件夹，调用通义千问 API 按音乐流派自动分类，并移动到对应的曲风子文件夹。

## 项目结构

- `get_songs.py` —— 扫描本地 music 文件夹，读取 MP3 的 ID3 标签，提取歌名和歌手。
- `classify.py` —— 调用通义千问多模态接口，联网搜索，按曲风分类每首歌。
- `move_files.py` —— 读取分类结果，把歌曲剪切移动到对应的曲风子文件夹。
- `main.py` —— 整合入口，按「扫描 → 分类 → 移动」顺序一键执行。

## 环境要求

- Python 3.x
- 依赖库：`mutagen`、`dashscope`

## 技术栈

- **编程语言**：Python 3
- **AI 模型**：通义千问（qwen3.7-plus）
- **AI 接口**：DashScope SDK（MultiModalConversation）
- **音频处理**：mutagen（读取 MP3 元数据）
- **版本管理**：Git + GitHub
- **开发工具**：Claude Code,Deepseek（AI 辅助编程）

## 运行方式

安装依赖：

```bash
pip install -r requirements.txt
```

运行项目：

```bash
python main.py
```

## 配置说明

在 `config.py` 中填写你的通义千问 API Key：

```python
QWEN_API_KEY = "你的 API Key"
```

## 注意事项

- `config.py` 已在 `.gitignore` 中忽略，不会提交到仓库，请勿把 API Key 泄露到其他文件。
