from pathlib import Path
import html, json

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/"catalog.json").read_text(encoding="utf-8"))
payload = json.dumps(data, ensure_ascii=False, separators=(",",":")).replace("<", "\\u003c")
template = (ROOT/"web/index.template.html").read_text(encoding="utf-8")
assert template.count("__CATALOG__") == 1
(ROOT/"index.html").write_text(template.replace("__CATALOG__", payload), encoding="utf-8", newline="\n")

thumbs = []
for c in data["characters"]:
    v = next(v for v in c["variants"] if v["id"] == c["featured_variant"])
    thumbs.append('<td align="center"><a href="characters/{id}/"><img src="{path}" width="480" alt="{name}参考图匹配版三视图"></a><br><b>{name}</b> · {count} 个版本<br><a href="characters/{id}/">角色档案</a> · <a href="{path}">完整 PNG</a></td>'.format(id=c["id"], path=v["image"]["path"], name=html.escape(c["name"]), count=len(c["variants"])))
grid = "<table>\n" + "\n".join("<tr>" + "".join(thumbs[i:i+2]) + "</tr>" for i in range(0,len(thumbs),2)) + "\n</table>"
readme = """# AI Chibi Atlas · AI 娘三视图图鉴

8 位女性 Q 版 AI 拟人角色，17 套三视图。每位角色独立归档，保留多个衣装／表情版本；当前主系列根据同一张八人参考图制作。

*A multi-version fan character turnaround collection: 8 AI characters, 17 sheets, front / left side / back.*

[角色图鉴](#角色图鉴) · [制作记录](docs/WORKFLOW.md) · [来源署名](ATTRIBUTION.md) · [图片许可](ASSET-LICENSES.md) · [上传与展示](docs/PUBLISHING.md)

<img src="references/dance-reference-board.png" width="1100" alt="八位角色共同正面参考图">

## 本次主系列

`v2-dance` 对应上方参考图的发型、服装与闭嘴小表情，每位角色均有匹配的正面、左侧面和背面。新系列统一为 **1536 × 1024 PNG**，共八套；此前九套图以历史版本保留。豆包／Seed 未收录。

图片为同人设计参考与 AI 衍生补全，隐藏结构包含推定。许可按来源分别记录，不能把整套图片理解为 MIT 可商用素材。

## 角色图鉴

点击图片进入该角色文件夹，可浏览全部版本。

{grid}

## 版本与目录

- `v1-initial`：八位角色的初版。保留原始文件字节。
- `v1-natural-smile`：GPT 初版的自然微笑修订。
- `v2-dance`：八位角色按共同参考图制作的新系列，默认展示。

```text
characters/
  deepseek/
    README.md
    provenance.json
    references/author-video-frame.png
    variants/
      v1-initial/sheet.png
      v2-dance/
        sheet.png
        prompt.txt
        generation.json
  qwen/  kimi/  glm/  gpt/  claude/  gemini/  grok/
references/dance-reference-board.png
catalog.json
index.html
scripts/
docs/
```

每张图在 `catalog.json` 中登记尺寸、字节数、SHA-256、版本和来源。新图的完整提示词与修正记录随各版本保存；具体模型版本未由内置工具提供，因此未猜测填写。

## 浏览与检查

下载后双击 [index.html](index.html)，可切换角色、版本，与初版并排对照，并查看共同参考图。页面支持离线使用，也可放到 GitHub Pages；见 [发布说明](docs/PUBLISHING.md)。

```bash
python scripts/build_gallery.py
python scripts/verify.py
```

<img src="docs/gallery-preview.jpg" width="1100" alt="作品集浏览页实际预览">

自动检查图像完整性、元数据与本地链接；美术一致性检查记录在 [QUALITY.md](docs/QUALITY.md)。GitHub Actions 会运行同样的校验。

## 来源与许可

角色设计主要参考 ZipZipPipe 系列，DeepSeek 原型另需署名上善无形。社区三视图、AI 衍生版本与作者视频截帧分别记录，均不是厂商官方角色。

- [ai-girls](https://github.com/shuaizenge/ai-girls)：角色画面参考与 DeepSeek 社区三视图。
- [ai-chan-sheets](https://github.com/lmy414/ai-chan-sheets)：GPT 白紫龙娘社区三视图。
- [蓝色大肥鱼角色百科](https://xn--pssy23gqgbz2d718b.com/characters.html)：角色与作品来源交叉核对。
- [疚刃《若不是你突然闯进我生活》](https://www.bilibili.com/video/BV16Vap6yEGP/)：基础神态与舞蹈表现方向参考。

DeepSeek 设计含非商业与相同方式共享要求；GPT 变体的原作者与授权未明；其余条目保留上游的分享／再创作说明，不擅自补成统一标准许可证。详情见 [署名](ATTRIBUTION.md)、[图片许可](ASSET-LICENSES.md) 和逐角色 provenance.json。代码的 MIT 许可不涵盖图片或角色权利。
""".format(grid=grid)
(ROOT/"README.md").write_text(readme, encoding="utf-8", newline="\n")

attribution = ["# 来源与署名", "", "图片权利以原始来源为准。以下记录不把整理者推断成原作者，也不把 AI 衍生当作新增授权。", ""]
for c in data["characters"]:
    provenance = json.loads((ROOT/c["provenance"]).read_text(encoding="utf-8"))
    title = c["name"]
    current = next(v for v in c["variants"] if v["id"]==c["featured_variant"])
    source_url = provenance["source_repository"]
    original_url = provenance["upstream_page"]
    variants = "\n".join(f"| [{v['label']}](variants/{v['id']}/) | {v['image']['width']} × {v['image']['height']} | [{v['id']}](variants/{v['id']}/sheet.png) |" for v in c["variants"])
    character_readme = f"""# {title}

{c['description']}。所属模型／产品：{c['organization']}；社区女性拟人形象。

![{title}当前系列三视图](variants/{c['featured_variant']}/sheet.png)

## 版本

| 版本 | 图像尺寸 | PNG |
| --- | --- | --- |
{variants}

当前默认版本为 **参考图匹配版**，依据 [八人参考图](../../references/dance-reference-board.png) 中的 {c['board_position']}。各版本并列保留；形象、服装与表情可有差异。

## 来源与署名

{provenance['upstream_design_credit']}

[素材来源]({source_url}) · [原始发布／整理来源]({original_url}) · [逐项记录](provenance.json)

许可记录：{provenance['license_record']}

当前系列使用内置 imagegen 参照补全，正／侧／背顺序一致；侧背面不可见结构为推定。图片许可不随代码 MIT 许可变更。详见 [图片许可](../../ASSET-LICENSES.md)。

[返回图鉴](../../README.md) · [在画廊浏览](../../index.html#{c['id']}/{c['featured_variant']})
"""
    (ROOT/"characters"/c["id"]/"README.md").write_text(character_readme,encoding="utf-8", newline="\n")
    for v in c["variants"]:
        parts = [f"# {title} · {v['label']}", "", "![完整三视图](sheet.png)", "", v["notes"], "", f"- 版本 ID：`{v['id']}`", f"- 尺寸：{v['image']['width']} × {v['image']['height']} PNG", f"- 制作类型：`{v['kind']}`", f"- SHA-256：`{v['image']['sha256']}`", ""]
        if "quality_note" in v: parts += [v["quality_note"],""]
        if "prompt" in v: parts += ["[完整提示词](prompt.txt)",""]
        if "refinement_prompt" in v: parts += ["[细节修正提示词](refinement.prompt.txt)",""]
        if "generation" in v: parts += ["[生成与检查记录](generation.json)",""]
        parts += ["[角色版本目录](../../README.md) · [来源记录](../../provenance.json) · [图片许可](../../../../ASSET-LICENSES.md)",""]
        (ROOT/"characters"/c["id"]/"variants"/v["id"]/"README.md").write_text("\n".join(parts),encoding="utf-8", newline="\n")
    attribution += [f"## {title}","",provenance["upstream_design_credit"],"",f"- [素材仓库]({source_url})",f"- [原始发布／整理来源]({original_url})",f"- 许可状态：`{c['license_status']}`",f"- 许可记录：{provenance['license_record']}",f"- [项目中的逐角色记录]({c['provenance']})",""]
attribution += ["## 本项目制作与视频参考","","本项目使用内置 imagegen 制作八人表情参考图与衍生三视图，历史图保持原始字节。v2-dance 的细节修正记录与提示词在各版本目录。","", "[ZipZipPipe · Bilibili](https://space.bilibili.com/4168597) · [上善无形 · Bilibili](https://space.bilibili.com/4456176) · [原视频《大AI和小AI们》](https://www.bilibili.com/video/BV1tE9XBbErS/)","", "神态与舞蹈表现方向参考：[疚刃《若不是你突然闯进我生活》](https://www.bilibili.com/video/BV16Vap6yEGP/)。本项目没有附带该视频文件、音乐或帧截图。","", "[上游原始声明](sources/upstream-ai-girls-NOTICE.md) · [图片许可与边界](ASSET-LICENSES.md)",""]
(ROOT/"ATTRIBUTION.md").write_text("\n".join(attribution),encoding="utf-8", newline="\n")
print("Generated index.html, root/character/variant READMEs and ATTRIBUTION.md.")
