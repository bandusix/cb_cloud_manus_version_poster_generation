# Poster Generator v5

[🇨🇳 中文文档 (Chinese)](docs/README_zh.md)

Poster Generator is a programmatic poster generation script based on Python (Pillow). It automatically synthesizes user-provided text, brand ICONs, and multiple poster images into a beautiful 1200×630px (1.91:1 ratio) collage-style poster.

## Core Features

- **Adaptive Typography**: Title text and CTA button text automatically wrap and scale based on length, ensuring they never overflow or obscure the right-side posters.
- **Multi-Language Support**: Automatically detects CJK (Chinese, Japanese, Korean) characters and intelligently switches to the Noto Sans CJK font to prevent mojibake (garbled text).
- **Random Color Theme System**: Built-in 6 exquisite gradient color themes (Pink, Blue, Green, Yellow, Purple, Gray), supporting specific selection or random generation.
- **Lossless Collage Synthesis**: The right-side poster collage supports random rotation and staggered arrangement. White borders are precisely controlled at 2px, and the background after rotation is completely transparent with no black artifacts.
- **Flexible Integration**: Supports direct invocation via Python API, making it ideal for integration with backend services (e.g., FastAPI / Flask) for automated batch generation.

---

## Color Themes Showcase

The script provides 6 built-in gradient themes. You can specify them using the `theme` parameter:

| `theme="pink"` (Default) | `theme="blue"` |
|:---:|:---:|
| ![Pink Theme](docs/images/theme_pink.jpg) | ![Blue Theme](docs/images/theme_blue.jpg) |

| `theme="green"` | `theme="yellow"` |
|:---:|:---:|
| ![Green Theme](docs/images/theme_green.jpg) | ![Yellow Theme](docs/images/theme_yellow.jpg) |

| `theme="purple"` | `theme="gray"` |
|:---:|:---:|
| ![Purple Theme](docs/images/theme_purple.jpg) | ![Gray Theme](docs/images/theme_gray.jpg) |

---

## Environment Requirements

Running this script requires Python 3.7+ and the following dependencies:

```bash
pip install pillow requests
```

Additionally, the system needs the following fonts installed (Ubuntu/Debian environment):
```bash
sudo apt-get install fonts-noto fonts-noto-cjk
```

---

## Quick Start (API Invocation)

The recommended way to use this script is as a module in other Python code. You can fetch asset URLs and text via API requests and pass them directly to the `generate_poster` function.

### 1. Basic Invocation Example

```python
from generate_poster import generate_poster

# Prepare asset data (usually from your API request or database)
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
    "theme": "random"  # Random color theme
}

# Execute generation
output_path = generate_poster(**poster_data)
print(f"Poster generated and saved to: {output_path}")
```

### 2. Parameter Details

The `generate_poster` function accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `icon_url` | `str` | No | URL of the brand ICON in the top left corner. If `None` or empty, it will not be displayed. |
| `brand_name` | `str` | Yes | Brand name text displayed next to the ICON (e.g., `capybaba.io`). |
| `title_text` | `str` | Yes | Large title text on the left. Supports manual line breaks using `\n`. The script automatically calculates the font size to ensure it stays within the safe zone. |
| `cta_text` | `str` | Yes | Text next to the play button in the bottom left (e.g., `WATCH NOW`). Supports multi-language and auto-scaling to prevent overlapping. |
| `poster_urls` | `list` | Yes | List of poster image URLs for the right-side collage area. Recommended to pass 9~10 images for the best visual effect. |
| `output_filename` | `str` | No | Output filename (default `poster_output.jpg`). Files are saved in the `output/` directory alongside the script. |
| `theme` | `str` | No | Background gradient color theme. Options: `pink`, `blue`, `green`, `yellow`, `purple`, `gray`, `random`. Default is `random`. |
| `collage_seed` | `int` | No | Random seed for the collage layout (default `42`). Passing the same value ensures the rotation angles and positions are identical every time. |

---

## FAQ

**Q: How do I replace the play button icon in the bottom left?**  
A: The play button is a local static image. Simply replace the `play_button.png` file in the same directory as the script. The script will automatically remove its white background and adjust the size.

**Q: Will long title text be truncated?**  
A: No. The script has a built-in adaptive typography algorithm. When the title is too long, it first tries to wrap the text automatically; if the height exceeds the safe zone after wrapping, it gradually reduces the font size (from 58px down to 24px) to ensure the text is fully displayed without obscuring the right-side posters.

**Q: Why is the right-side collage layout the same every time?**  
A: To ensure stability in the generated results, the default `collage_seed` parameter is fixed at `42`. If you want a different layout (rotation angles, staggered positions) each time, you can pass a random seed when calling the function, e.g., `collage_seed=random.randint(1, 10000)`.

**Q: How do I use this in a Web framework (like FastAPI)?**  
A: It's very simple. In your route handler, receive the JSON data from the frontend, extract the corresponding URLs and text, pass them directly to the `generate_poster` function, and then return the generated image path or image stream to the frontend.
