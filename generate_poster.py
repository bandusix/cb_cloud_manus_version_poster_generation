#!/usr/bin/env python3
"""
Poster Generator v5
====================
程序化生成 1200×630px (1.91:1) 风格海报

布局结构:
  ┌─────────────────────────────────────────────────────┐
  │ [ICON] brand_name                                   │
  │                                                     │
  │  Title Text                  ┌──────────────────┐  │
  │  (自适应缩放)                 │  海报拼贴区域     │  │
  │                              │  (9~10张随机旋转) │  │
  │  [▶] CTA Text                │                  │  │
  └─────────────────────────────────────────────────────┘

主色调: 支持 6 种预设 + 随机选取
"""

import os
import sys
import random
import requests
import io
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════
# 路径配置
# ═══════════════════════════════════════════════════════
_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_BOLD    = "/usr/share/fonts/truetype/noto/NotoSans-ExtraBold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FONT_CJK     = "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf"
PLAY_BUTTON_PATH = os.path.join(_DIR, "play_button.png")
OUTPUT_DIR   = os.path.join(_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════
# 画布尺寸
# ═══════════════════════════════════════════════════════
CANVAS_W, CANVAS_H = 1200, 630

# ═══════════════════════════════════════════════════════
# 布局安全区
# ═══════════════════════════════════════════════════════
LEFT_MARGIN      = 36    # 左侧内边距
LEFT_SAFE_WIDTH  = 430   # 左侧文字/CTA 安全区宽度（不遮挡右侧海报）
COLLAGE_START_X  = 480   # 右侧拼贴区起始 x

# ═══════════════════════════════════════════════════════
# 主色调预设
# ═══════════════════════════════════════════════════════
# 每个主题: (theme_name, bg_left_rgb, bg_right_rgb)
# bg_left  = 渐变左侧（较浅）
# bg_right = 渐变右侧（较深）
COLOR_THEMES = {
    "pink":   ("粉红色", (255, 160, 160), (230,  80, 110)),   # 默认粉红
    "blue":   ("浅蓝色", (160, 210, 255), ( 60, 130, 220)),   # 浅蓝
    "green":  ("浅绿色", (160, 230, 180), ( 50, 170,  90)),   # 浅绿
    "yellow": ("浅黄色", (255, 235, 130), (220, 170,  30)),   # 浅黄
    "purple": ("浅紫色", (210, 170, 255), (130,  70, 210)),   # 浅紫
    "gray":   ("浅灰色", (210, 215, 220), (130, 140, 155)),   # 浅灰
}
THEME_KEYS = list(COLOR_THEMES.keys())


def get_theme(theme: str = "random") -> tuple:
    """
    获取主色调配置。

    参数:
        theme: 主题名称，可选值:
               "pink" | "blue" | "green" | "yellow" | "purple" | "gray"
               "random" — 从以上 6 种中随机选取（默认）

    返回:
        (theme_name_cn, bg_left_rgb, bg_right_rgb)
    """
    if theme == "random":
        theme = random.choice(THEME_KEYS)
    theme = theme.lower().strip()
    if theme not in COLOR_THEMES:
        print(f"  [警告] 未知主题 '{theme}'，使用默认粉红色")
        theme = "pink"
    name_cn, left, right = COLOR_THEMES[theme]
    print(f"  主色调: {theme} ({name_cn})")
    return (left, right)


# ═══════════════════════════════════════════════════════
# 图片加载工具
# ═══════════════════════════════════════════════════════

def fetch_image(url: str) -> Image.Image:
    """
    从 URL 下载图片，返回 RGBA PIL Image。
    支持 http/https 链接，失败返回 None。
    """
    if not url:
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content)).convert("RGBA")
    except Exception as e:
        print(f"  [警告] 下载失败 {url[:60]}: {e}")
        return None


def load_local_image(path: str) -> Image.Image:
    """从本地路径加载图片，返回 RGBA PIL Image。"""
    try:
        return Image.open(path).convert("RGBA")
    except Exception as e:
        print(f"  [警告] 本地图片加载失败 {path}: {e}")
        return None


# ═══════════════════════════════════════════════════════
# 字体工具
# ═══════════════════════════════════════════════════════

def has_cjk(text: str) -> bool:
    """检测文字中是否包含中日韩字符。"""
    for ch in text:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF or
            0x3040 <= cp <= 0x30FF or
            0xAC00 <= cp <= 0xD7AF or
            0x3400 <= cp <= 0x4DBF):
            return True
    return False


def get_font_for_text(text: str, size: int) -> ImageFont.FreeTypeFont:
    """
    根据文字内容自动选择字体：
    - 含 CJK 字符 → NotoSansCJK Bold
    - 纯拉丁/西文  → NotoSans ExtraBold
    """
    font_path = FONT_CJK if has_cjk(text) else FONT_BOLD
    try:
        return ImageFont.truetype(font_path, size)
    except:
        try:
            return ImageFont.truetype(FONT_BOLD, size)
        except:
            return ImageFont.load_default()


def get_text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple:
    """返回文字渲染尺寸 (width, height)。"""
    dummy = Image.new("RGB", (1, 1))
    draw  = ImageDraw.Draw(dummy)
    bbox  = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


# ═══════════════════════════════════════════════════════
# 文字换行
# ═══════════════════════════════════════════════════════

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """
    将文字按最大宽度自动换行，支持手动 \\n。
    返回行字符串列表。
    """
    paragraphs = text.replace("\\n", "\n").split("\n")
    result = []
    dummy = Image.new("RGB", (1, 1))
    draw  = ImageDraw.Draw(dummy)
    for para in paragraphs:
        words = para.split()
        if not words:
            result.append("")
            continue
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    result.append(current)
                current = word
        if current:
            result.append(current)
    return result


# ═══════════════════════════════════════════════════════
# 标题自适应布局计算
# ═══════════════════════════════════════════════════════

def calculate_title_layout(title_text: str, max_width: int, max_height: int) -> tuple:
    """
    自动计算标题最佳字号和换行结果。

    策略: 从 58px 向下每次减 2px，直到所有行都能在
          max_width × max_height 区域内完整显示。

    返回: (font_size, lines_list, line_height)
    """
    for font_size in range(58, 22, -2):
        font  = get_font_for_text(title_text, font_size)
        lines = wrap_text(title_text, font, max_width)
        line_height = font_size + 10
        if len(lines) * line_height <= max_height:
            return (font_size, lines, line_height)
    # 兜底最小字号
    font_size   = 24
    font        = get_font_for_text(title_text, font_size)
    lines       = wrap_text(title_text, font, max_width)
    line_height = font_size + 10
    return (font_size, lines, line_height)


# ═══════════════════════════════════════════════════════
# 图像合成工具
# ═══════════════════════════════════════════════════════

def make_gradient_bg(w: int, h: int, left_color: tuple, right_color: tuple) -> Image.Image:
    """生成左→右线性渐变背景（RGBA）。"""
    bg = Image.new("RGBA", (w, h))
    px = bg.load()
    for x in range(w):
        t = x / (w - 1)
        r = int(left_color[0] + (right_color[0] - left_color[0]) * t)
        g = int(left_color[1] + (right_color[1] - left_color[1]) * t)
        b = int(left_color[2] + (right_color[2] - left_color[2]) * t)
        for y in range(h):
            px[x, y] = (r, g, b, 255)
    return bg


def remove_white_bg(img: Image.Image, threshold: int = 245) -> Image.Image:
    """将接近白色的像素变为透明（去除白底）。"""
    img  = img.convert("RGBA")
    data = img.getdata()
    new  = [(r, g, b, 0) if r > threshold and g > threshold and b > threshold
            else (r, g, b, a) for r, g, b, a in data]
    img.putdata(new)
    return img


def add_white_border(img: Image.Image, border: int = 2) -> Image.Image:
    """
    添加精确 2px 白色边框（底部 4px 模拟照片感）。
    border 参数保留以便外部调用，默认固定 2px。
    """
    bw = img.width  + border * 2
    bh = img.height + border + border * 2  # 底部多一倍
    out = Image.new("RGBA", (bw, bh), (255, 255, 255, 255))
    out.paste(img, (border, border))
    return out


def rotate_transparent(img: Image.Image, angle: float) -> Image.Image:
    """旋转图片，背景保持完全透明（无黑色底纹）。"""
    return img.convert("RGBA").rotate(
        angle, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0)
    )


def alpha_paste(canvas: Image.Image, overlay: Image.Image, pos: tuple) -> Image.Image:
    """
    将带透明通道的 overlay 正确合成到 canvas 上。
    使用 alpha_composite 避免黑色底纹。
    """
    x, y = pos
    tmp  = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ox, oy = max(0, -x), max(0, -y)
    px, py = max(0, x),  max(0, y)
    cw = min(overlay.width  - ox, canvas.width  - px)
    ch = min(overlay.height - oy, canvas.height - py)
    if cw <= 0 or ch <= 0:
        return canvas
    tmp.paste(overlay.crop((ox, oy, ox + cw, oy + ch)), (px, py))
    return Image.alpha_composite(canvas, tmp)


def draw_shadowed_text(draw, pos, text, font, fill=(255,255,255,255),
                       shadow=(0,0,0,45), offset=(2,3)):
    """绘制带轻微投影的文字。"""
    draw.text((pos[0]+offset[0], pos[1]+offset[1]), text, font=font, fill=shadow)
    draw.text(pos, text, font=font, fill=fill)


# ═══════════════════════════════════════════════════════
# 海报拼贴构建
# ═══════════════════════════════════════════════════════

def build_collage(poster_images: list, area_w: int, area_h: int,
                  seed: int = 42) -> Image.Image:
    """
    将多张海报图片拼贴成错落旋转效果。

    参数:
        poster_images : PIL Image 列表（已下载）
        area_w / area_h : 拼贴区域尺寸
        seed          : 随机种子（固定保证布局一致）

    特性:
        - 白边固定 2px
        - 旋转背景完全透明，无黑色底纹
        - 使用 alpha_composite 合成
    """
    pad     = 140
    collage = Image.new("RGBA", (area_w + pad, area_h + pad), (0, 0, 0, 0))
    n       = len(poster_images)
    base_h  = int(area_h * 0.55)
    cols, rows = 3, 4
    cell_w, cell_h = area_w // cols, area_h // rows

    random.seed(seed)
    positions = []
    for i in range(n):
        col, row = i % cols, i // cols
        bx = col * cell_w + cell_w // 2
        by = row * cell_h + cell_h // 2
        ox = random.randint(-cell_w // 4, cell_w // 4)
        oy = random.randint(-cell_h // 5, cell_h // 5)
        positions.append((
            bx + ox + pad // 2,
            by + oy + pad // 2,
            random.uniform(-18, 18),   # 旋转角度
            random.uniform(0.70, 0.95) # 缩放比例
        ))

    order = list(range(n))
    random.shuffle(order)

    for idx in order:
        if idx >= len(poster_images) or poster_images[idx] is None:
            continue
        img = poster_images[idx].convert("RGBA")
        x, y, angle, scale = positions[idx]
        th = int(base_h * scale)
        tw = int(img.width * th / img.height)
        img = img.resize((tw, th), Image.LANCZOS)
        img = add_white_border(img, border=2)
        img = rotate_transparent(img, angle)
        collage = alpha_paste(collage, img, (x - img.width//2, y - img.height//2))

    return collage


# ═══════════════════════════════════════════════════════
# CTA 区域构建
# ═══════════════════════════════════════════════════════

def build_cta(cta_text: str, play_btn: Image.Image, max_width: int) -> Image.Image:
    """
    构建 CTA 区域：[播放按钮图片] + [可变文字]

    参数:
        cta_text  : 按钮旁文字，支持多语言（自动选字体）
        play_btn  : 播放按钮 PIL Image（本地固定图片）
        max_width : 最大宽度（不超过左侧安全区）

    特性:
        - 文字超出时自动缩小字号（36→20px）
        - 背景透明，与渐变背景自然融合
    """
    btn_size = 83  # 播放按钮尺寸（原 64px 放大 30%）
    gap      = 14

    # 自适应字号
    for font_size in range(36, 18, -2):
        font = get_font_for_text(cta_text, font_size)
        tw, th = get_text_size(cta_text, font)
        if btn_size + gap + tw + 20 <= max_width:
            break

    font = get_font_for_text(cta_text, font_size)
    tw, th = get_text_size(cta_text, font)
    total_w = min(btn_size + gap + tw + 20, max_width)
    total_h = max(btn_size, th + 10)

    cta_img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))

    # 粘贴播放按钮
    if play_btn:
        btn = remove_white_bg(play_btn.convert("RGBA"))
        btn = btn.resize((btn_size, btn_size), Image.LANCZOS)
        cta_img = alpha_paste(cta_img, btn, (0, (total_h - btn_size) // 2))

    # 绘制文字
    draw = ImageDraw.Draw(cta_img)
    ty   = (total_h - th) // 2
    draw.text((btn_size + gap + 2, ty + 2), cta_text, font=font, fill=(0, 0, 0, 50))
    draw.text((btn_size + gap,     ty),     cta_text, font=font, fill=(255, 255, 255, 255))

    return cta_img


# ═══════════════════════════════════════════════════════
# 主生成函数（核心 API）
# ═══════════════════════════════════════════════════════

def generate_poster(
    icon_url:        str,
    brand_name:      str,
    title_text:      str,
    cta_text:        str,
    poster_urls:     list,
    output_filename: str   = "poster_output.jpg",
    theme:           str   = "random",
    collage_seed:    int   = 42,
) -> str:
    """
    生成海报并保存到 output/ 目录。

    ┌─────────────────────────────────────────────────────────────┐
    │  参数说明                                                    │
    ├──────────────────┬──────────────────────────────────────────┤
    │ icon_url         │ 右上角品牌 ICON 图片 URL（可为 None）     │
    │ brand_name       │ ICON 旁品牌名称文字                       │
    │ title_text       │ 左侧大标题，支持 \\n 手动换行             │
    │                  │ 自动缩放，不超出左侧安全区                │
    │ cta_text         │ 播放按钮旁文字（多语言自动选字体）        │
    │ poster_urls      │ 右侧拼贴海报 URL 列表（建议 9~10 张）     │
    │ output_filename  │ 输出文件名（保存到 output/ 目录）         │
    │ theme            │ 背景主色调，见下方 COLOR_THEMES           │
    │                  │ "random"（默认）随机选取                  │
    │ collage_seed     │ 拼贴布局随机种子，相同值布局相同          │
    └──────────────────┴──────────────────────────────────────────┘

    返回: 输出文件的绝对路径
    """
    print(f"\n{'='*55}")
    print(f"  🎨 开始生成海报: {output_filename}")
    print(f"{'='*55}")

    # ── 1. 主色调 ──
    bg_left, bg_right = get_theme(theme)

    # ── 2. 渐变背景 ──
    print("[1/6] 创建渐变背景...")
    canvas = make_gradient_bg(CANVAS_W, CANVAS_H, bg_left, bg_right).convert("RGBA")

    # ── 3. 下载 ICON ──
    print("[2/6] 下载 ICON...")
    icon_img = fetch_image(icon_url) if icon_url else None

    # ── 4. 加载播放按钮 ──
    print("[3/6] 加载播放按钮...")
    play_btn = load_local_image(PLAY_BUTTON_PATH)

    # ── 5. 下载海报图片 ──
    print(f"[4/6] 下载海报图片（共 {len(poster_urls)} 张）...")
    poster_images = []
    for i, url in enumerate(poster_urls):
        print(f"  [{i+1:02d}/{len(poster_urls)}] {url[:65]}...")
        poster_images.append(fetch_image(url))

    # ── 6. 构建拼贴 ──
    print("[5/6] 构建海报拼贴...")
    collage = build_collage(poster_images, 760, CANVAS_H + 60, seed=collage_seed)
    canvas  = alpha_paste(canvas, collage, (COLLAGE_START_X, -30))

    # ── 7. 绘制 UI 元素 ──
    print("[6/6] 绘制文字和 UI 元素...")
    draw = ImageDraw.Draw(canvas)

    # ICON + 品牌名
    ix, iy, isz = LEFT_MARGIN, 28, 44
    if icon_img:
        ic = icon_img.convert("RGBA").resize((isz, isz), Image.LANCZOS)
        mask = Image.new("L", (isz, isz), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, isz-1, isz-1], radius=10, fill=255)
        ic.putalpha(mask)
        canvas = alpha_paste(canvas, ic, (ix, iy))
        draw   = ImageDraw.Draw(canvas)
    try:
        font_brand = ImageFont.truetype(FONT_REGULAR, 22)
    except:
        font_brand = ImageFont.load_default()
    draw.text((ix + isz + 10, iy + (isz - 22) // 2), brand_name,
              font=font_brand, fill=(255, 255, 255, 230))

    # 标题（自适应缩放）
    title_start_y  = iy + isz + 40
    title_max_h    = int(CANVAS_H * 0.52)
    fs, lines, lh  = calculate_title_layout(title_text, LEFT_SAFE_WIDTH, title_max_h)
    font_title     = get_font_for_text(title_text, fs)
    for i, line in enumerate(lines):
        draw_shadowed_text(draw, (LEFT_MARGIN, title_start_y + i * lh), line, font_title)

    # CTA（左下角，自适应不遮挡）
    cta_el = build_cta(cta_text, play_btn, LEFT_SAFE_WIDTH)
    canvas = alpha_paste(canvas, cta_el, (LEFT_MARGIN, CANVAS_H - cta_el.height - 44))

    # ── 8. 保存 ──
    out_path = os.path.join(OUTPUT_DIR, output_filename)
    canvas.convert("RGB").save(out_path, "JPEG", quality=95)
    print(f"\n✅ 海报已保存: {out_path}")
    return out_path


# ═══════════════════════════════════════════════════════
# 交互式 CLI 入口
# ═══════════════════════════════════════════════════════

def _cli():
    """交互式命令行，逐步收集用户输入并生成海报。"""
    print("\n🎬 海报生成器 v5  |  1200×630 px")
    print("─" * 50)

    icon_url   = input("\n[1] ICON 图片 URL（回车跳过）: ").strip() or None
    brand_name = input("[2] 品牌名称: ").strip()
    title_text = input("[3] 标题文字（\\n 换行）: ").strip()
    cta_text   = input("[4] CTA 文字（默认 WATCH NOW）: ").strip() or "WATCH NOW"

    print(f"\n[5] 主色调选择: {' | '.join(THEME_KEYS)} | random")
    theme = input("    输入主题（默认 random）: ").strip() or "random"

    print("\n[6] 海报图片 URL（建议 9~10 张，回车结束）")
    poster_urls = []
    for i in range(10):
        url = input(f"  海报 {i+1:02d}: ").strip()
        if url:
            poster_urls.append(url)
        elif i >= 3:
            break

    out_name = input("\n[7] 输出文件名（默认 poster_output.jpg）: ").strip() or "poster_output.jpg"
    if not out_name.lower().endswith((".jpg", ".jpeg", ".png")):
        out_name += ".jpg"

    generate_poster(
        icon_url=icon_url,
        brand_name=brand_name,
        title_text=title_text,
        cta_text=cta_text,
        poster_urls=poster_urls,
        output_filename=out_name,
        theme=theme,
    )


if __name__ == "__main__":
    _cli()
