"""Build documents and a static viewer for individually generated keyframes."""
from pathlib import Path
import html, json


def character_frames(root, character):
    title=character['name']
    sections=[]
    for series in character.get('keyframes',[]):
        base='keyframes/'+series['id']
        frames=series['frames']
        sections.append(f'''## 独立动作关键帧

![{title} K1]({base}/K1.png)

每一帧单独生成、对照与修正，共七张。保留小圆手与紧凑手臂；K3／K4 是腰胯转动，K5 双腿不交叉。

[逐帧浏览与制作记录]({base}/README.md) · [独立帧浏览页](../../keyframes/index.html#{character['id']})

''')
        lines=[f'# {title} · 七张独立关键帧','','每次只生成一帧，再与原版对应动作进行视觉对照。使用内置 imagegen，保留各帧提示词、局部修正记录与检查说明。','','| 帧 | 时间 | PNG | 动作重点 |','| --- | --- | --- | --- |']
        for frame in frames:
            focus=next(f['focus'] for f in json.loads((root/'catalog.json').read_text(encoding='utf-8'))['keyframe_series']['frames'] if f['id']==frame['id'])
            lines.append(f"| {frame['id']} | {frame['seconds']:.2f}s | [{frame['id']}.png]({frame['id']}.png) | {focus} |")
        lines+=['','6.90s 回到 K1。沿用原参考至大腿附近的裁切，脚部不在画面内；K3／K4 保持腿向下，以腰胯转动和视角变化表现动作，K5 不抬腿、不交叉。','']
        if character['id']=='deepseek':lines+=['K1 保留用户认可母版的原始字节。其余动作在同一形象基础上分别生成。','']
        if character['id']=='gpt':lines+=['背身帧的单条鳞尾从臀部、后裙摆下方露出，与上背部的小翅膀分开。','']
        if character['id']=='gemini':lines+=['正面为画面左紫红眼、右金眼；K6／K7 的侧向露眼为角色左侧金眼。','']
        for frame in frames:
            fid=frame['id']
            image=frame['image']
            prompts=' · '.join(f'[{Path(p).name}]({Path(p).name})' for p in frame['prompts'])
            lines += [f'## {fid} · {frame["seconds"]:.2f}s','',f'![{title} {fid}]({fid}.png)','',f'{image["width"]} × {image["height"]} PNG · [制作与目视检查记录]({fid}.generation.json)','',prompts,'']
        lines+=['## 来源与使用','','造型沿用本项目既有角色设定；动作依据用户提供的七格参考与 K1 近景附件。动作附件和裁切仅在本地用于比对，不随公开项目分发。每张图均单独生成，不是从整板图裁切。','','视觉比对不等于逐像素复刻或动作捕捉数据。图片许可沿用角色来源记录，代码 MIT 不覆盖图片及角色权利。','','[全部角色关键帧](../../../../keyframes/README.md) · [浏览页](../../../../keyframes/index.html) · [角色档案](../../README.md) · [图片许可](../../../../ASSET-LICENSES.md)','']
        (root/'characters'/character['id']/base/'README.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    return ''.join(sections)


def keyframe_index(root, data):
    series=data['keyframe_series']
    lines=['# 可爱风 · 独立动作关键帧','','**8 位角色 × 7 张 = 56 张独立 PNG**。每张按顺序单独生成、与对应原版姿势比较，必要时局部修正；原有 17 套三视图继续保留。','','[打开逐帧浏览页](index.html) · [返回三视图图鉴](../README.md)','','## 时间与动作','','| 帧 | 时间 | 动作 | 对照重点 |','| --- | --- | --- | --- |']
    lines += [f"| {f['id']} | {f['seconds']:.2f}s | {f['label']} | {f['focus']} |" for f in series['frames']]
    lines+=['| 循环 | 6.90s | 回到 K1 | 同一角色与衣装 |','','K3／K4 双腿保持向下，通过转腰摆胯和视角变化形成动作；K5 不交叉腿。沿用原参考的大腿附近裁切，不额外补画完整脚部。','','## 八位角色','','| 角色 | 独立帧与记录 | K1 |','| --- | --- | --- |']
    nav=[]
    sections=[]
    for i,c in enumerate(data['characters']):
        item=c['keyframes'][0]
        base='../characters/'+c['id']+'/keyframes/'+item['id']
        lines.append(f"| {c['name']} | [K1—K7 与完整提示词]({base}/README.md) | [PNG]({base}/K1.png) |")
        current=' aria-current="true"' if i==0 else ''
        nav.append(f'<a href="#{c["id"]}" data-character-link="{c["id"]}"{current}>{html.escape(c["short_name"])}</a>')
        figures=[]
        for j,f in enumerate(item['frames']):
            img=f['image']
            url='../'+img['path']
            figures.append(f'''<figure><a href="{url}" target="_blank" rel="noopener" aria-label="放大 {html.escape(c['name'])} {f['id']}"><img src="{url}" width="{img['width']}" height="{img['height']}" alt="{html.escape(c['name'])} {f['id']} {html.escape(f['label'])}" loading="{'eager' if i==0 and j==0 else 'lazy'}" decoding="async"></a><figcaption><span><strong>{f['id']}</strong> · {f['seconds']:.2f}s · {html.escape(f['label'])}</span><a href="{url}" download>下载 PNG ↓</a></figcaption></figure>''')
        sections.append(f'''<section id="{c['id']}" data-character{'' if i==0 else ' hidden'} aria-labelledby="title-{c['id']}"><div class="series-heading"><div><p class="eyebrow">{html.escape(c['region'])} / 7 KEYFRAMES</p><h1 id="title-{c['id']}">{html.escape(c['name'])}</h1></div><a class="records" href="{base}/README.md">提示词与制作记录 ↗</a></div><div class="frames">{''.join(figures)}</div></section>''')
    lines+=['','## 制作与许可','','手部采用无分指小圆手，按近远关系调整大小与遮挡。K1 以用户认可的 DeepSeek 独立帧为比例与画风依据，后续逐帧参照对应原动作与本角色 K1；背面另核对本角色三视图。','','GPT 的 K6／K7 尾根位于臀部、后裙摆下方；Gemini 的异色瞳随角色左右眼保持；K7 主要由近侧前臂遮脸。完整修正提示词与逐帧目视检查记录保存在角色目录。','','使用内置 imagegen；具体模型版本未由工具公开。动作参考附件只在本地保留，不随项目分发。视觉比较不代表逐像素复刻；这些文件是关键帧参考图，不含视频、音乐或动作捕捉数据。','','[图片许可](../ASSET-LICENSES.md) · [来源署名](../ATTRIBUTION.md) · [质量检查记录](../docs/QUALITY.md)','']
    target=root/'keyframes'
    target.mkdir(exist_ok=True)
    (target/'README.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    template=(root/'web/keyframes.template.html').read_text(encoding='utf-8')
    for key,value in [('__NAV__',''.join(nav)),('__SECTIONS__',''.join(sections))]:
        assert template.count(key)==1
        template=template.replace(key,value)
    (target/'index.html').write_text(template,encoding='utf-8',newline='\n')
