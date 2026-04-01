#!/usr/bin/env python3
"""
测试脚本：生成 6 种主色调 + 多语言 CTA + 超长标题 共 8 个版本
"""
import sys
sys.path.insert(0, "/home/ubuntu/poster_generator")
from generate_poster import generate_poster, THEME_KEYS

POSTER_URLS = [
    "https://media.themoviedb.org/t/p/w220_and_h330_face/7wIBfBl2gejt6xHxNSK0reVIm7E.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/bRBeSHfGHwkEpImlhxPmOcUsaeg.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/7F0jc75HrSkLVcvOXR2FXAIwuEv.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/znTPnXCK3lEQJgqXCvP7e5FUz6f.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/wfuqMlaExcoYiUEvKfVpUTt1v4u.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/buPFnHZ3xQy6vZEHxbHgL1Pc6CR.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/yihdXomYb5kTeSivtFndMy5iDmf.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/jjyuk0edLiW8vOSnlfwWCCLpbh5.jpg",
    "https://media.themoviedb.org/t/p/w220_and_h330_face/mjkS2iAgWj3ik1DTjvI15nHZ7yl.jpg",
]

BASE = dict(
    icon_url="https://capybaba.io/favicon-128x128.png",
    brand_name="capybaba.io",
    title_text="Top 10 Comedy Movies & TV Shows",
    cta_text="WATCH NOW",
    poster_urls=POSTER_URLS,
)

# 6 种主色调
for theme in THEME_KEYS:
    generate_poster(**BASE, theme=theme, output_filename=f"theme_{theme}.jpg")

# 超长标题自适应
long_title = {**BASE,
    "title_text": "Top 10 Best Comedy Movies & TV Shows You Must Watch This Year",
    "theme": "blue",
    "output_filename": "test_long_title.jpg"}
generate_poster(**long_title)

# 中文 CTA
zh_cta = {**BASE,
    "cta_text": "立即观看精彩内容",
    "theme": "purple",
    "output_filename": "test_cta_zh.jpg"}
generate_poster(**zh_cta)

print("\n✅ 全部测试版本生成完毕")
