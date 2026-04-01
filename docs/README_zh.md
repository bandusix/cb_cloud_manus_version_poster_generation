# Poster Generator v5

[🇬🇧 English Document](../README.md)

Poster Generator 是一个基于 Python (Pillow) 的程序化海报生成脚本。它可以将用户提供的文本、品牌 ICON、多张海报图片等素材，自动合成一张 1200×630px (比例 1.91:1) 的精美拼贴风格海报。

## 核心特性

- **自适应排版**：标题文字和 CTA 按钮文字会根据长度自动换行和缩放，确保不越界、不遮挡右侧海报。
- **多语言支持**：自动检测文字中的中日韩 (CJK) 字符，并智能切换至 Noto Sans CJK 字体，避免乱码。
- **随机主色调系统**：内置 6 种精美渐变主色调（粉红、浅蓝、浅绿、浅黄、浅紫、浅灰），支持指定或随机生成。
- **无损拼贴合成**：右侧海报拼贴支持随机旋转、错落排列，白边精确控制为 2px，且旋转后背景完全透明，无黑色底纹。
- **灵活的接入方式**：支持通过 Python API 直接调用，非常适合与后端服务（如 FastAPI / Flask）集成，实现自动化批量生成。

---

## 主色调展示

脚本内置了 6 种精心调配的渐变主色调。你可以通过 `theme` 参数指定：

| `theme="pink"` (默认) | `theme="blue"` |
|:---:|:---:|
| ![粉红主题](images/theme_pink.jpg) | ![浅蓝主题](images/theme_blue.jpg) |

| `theme="green"` | `theme="yellow"` |
|:---:|:---:|
| ![浅绿主题](images/theme_green.jpg) | ![浅黄主题](images/theme_yellow.jpg) |

| `theme="purple"` | `theme="gray"` |
|:---:|:---:|
| ![浅紫主题](images/theme_purple.jpg) | ![浅灰主题](images/theme_gray.jpg) |

---

## 环境依赖

运行本脚本需要 Python 3.7+ 环境，并安装以下依赖库：

```bash
pip install pillow requests
```

此外，系统需要安装以下字体（Ubuntu/Debian 环境）：
```bash
sudo apt-get install fonts-noto fonts-noto-cjk
```

---

## 快速开始 (API 调用方式)

本脚本最推荐的使用方式是作为模块在其他 Python 代码中调用。你可以通过接口请求获取素材 URL 和文本，然后直接传入 `generate_poster` 函数。

### 1. 基础调用示例

```python
from generate_poster import generate_poster

# 准备素材数据（通常来自你的 API 请求或数据库）
poster_data = {
    "icon_url": "https://capybaba.io/favicon-128x128.png",
    "brand_name": "capybaba.io",
    "title_text": "Top 10\nComedy Movies\n& TV Shows",
    "cta_text": "WATCH NOW",
    "poster_urls": [
        "https://media.themoviedb.org/t/p/w220_and_h330_face/7wIBfBl2gejt6xHxNSK0reVIm7E.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/bRBeSHfGHwkEpImlhxPmOcUsaeg.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/7F0jc75HrSkLVcvOXR2FXAIwuEv.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/znTPnXCK3lEQJgqXCvP7e5FUz6f.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/wfuqMlaExcoYiUEvKfVpUTt1v4u.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/buPFnHZ3xQy6vZEHxbHgL1Pc6CR.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/yihdXomYb5kTeSivtFndMy5iDmf.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/jjyuk0edLiW8vOSnlfwWCCLpbh5.jpg",
        "https://media.themoviedb.org/t/p/w220_and_h330_face/mjkS2iAgWj3ik1DTjvI15nHZ7yl.jpg",
    ],
    "output_filename": "example_poster.jpg",
    "theme": "random"  # 随机主色调
}

# 执行生成
output_path = generate_poster(**poster_data)
print(f"海报已生成并保存至: {output_path}")
```

### 2. 参数详细说明

`generate_poster` 函数接受以下参数：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `icon_url` | `str` | 否 | 左上角品牌 ICON 的图片 URL。若传 `None` 或空字符串则不显示。 |
| `brand_name` | `str` | 是 | ICON 旁边显示的品牌名称文字（如 `capybaba.io`）。 |
| `title_text` | `str` | 是 | 左侧大标题文字。支持使用 `\n` 手动换行。脚本会自动计算字号以确保不超出安全区。 |
| `cta_text` | `str` | 是 | 左下角播放按钮旁边的文字（如 `WATCH NOW` 或 `立即观看`）。支持多语言，自动防遮挡。 |
| `poster_urls` | `list` | 是 | 右侧拼贴区域的海报图片 URL 列表。建议传入 9~10 张图片以获得最佳视觉效果。 |
| `output_filename` | `str` | 否 | 输出的文件名（默认 `poster_output.jpg`）。文件将统一保存在脚本同级的 `output/` 目录下。 |
| `theme` | `str` | 否 | 背景渐变主色调。可选值：`pink`, `blue`, `green`, `yellow`, `purple`, `gray`, `random`。默认 `random`。 |
| `collage_seed` | `int` | 否 | 拼贴布局的随机种子（默认 `42`）。传入相同的值可保证每次生成的拼贴旋转角度和位置完全一致。 |

---

## 常见问题 (FAQ)

**Q: 如何替换左下角的播放按钮图标？**  
A: 播放按钮是本地固定图片。只需替换脚本同级目录下的 `play_button.png` 文件即可。脚本会自动去除该图片的白色背景并调整尺寸。

**Q: 标题文字太长会被截断吗？**  
A: 不会。脚本内置了自适应排版算法。当标题过长时，脚本会优先尝试自动换行；如果换行后高度超出安全区，脚本会逐步缩小字号（从 58px 降至 24px），确保文字完整显示且不遮挡右侧海报。

**Q: 为什么生成的海报右侧拼贴每次位置都一样？**  
A: 为了保证生成结果的稳定性，默认的 `collage_seed` 参数固定为 `42`。如果你希望每次生成的拼贴布局（旋转角度、错落位置）都不一样，可以在调用时传入随机种子，例如：`collage_seed=random.randint(1, 10000)`。

**Q: 如何在 Web 框架（如 FastAPI）中使用？**  
A: 非常简单。在你的路由处理函数中接收前端传来的 JSON 数据，提取出对应的 URL 和文本，直接传递给 `generate_poster` 函数，然后将生成的图片路径返回给前端或直接返回图片流即可。
