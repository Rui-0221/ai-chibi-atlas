# 上传 GitHub 与展示

本目录是独立的作品项目，图片使用仓库相对路径。无需访问本机原始工作目录，也无需 API Key。

## 网页上传

在 GitHub 创建空仓库，将本目录的项目文件上传到仓库根目录。根目录应直接看到 `README.md`、`catalog.json`、`characters/` 与 `index.html`。不要把 ZIP 文件本身当作整个仓库上传。

## 使用 Git

在项目根目录执行：

```bash
git init -b main
git add .
git commit -m "Add AI Chibi Atlas collection"
git remote add origin <你的仓库地址>
git push -u origin main
```

如果目录已经初始化为 Git 仓库，沿用现有分支和远程配置即可，不必重复初始化。

## GitHub Pages（可选）

仓库的 Settings → Pages 选择从分支部署，目录选择仓库根目录。展示入口是 `index.html`，不依赖构建服务、框架、外部字体或后端。也可以在本地直接双击此文件，或运行：

```bash
python -m http.server 8000
```

然后打开 `http://localhost:8000`。浏览页支持角色切换、版本切换、与初版并排对照，以及查看共同参考图。

独立动作关键帧入口为 `keyframes/index.html`，可切换八位角色、逐帧放大与下载 PNG；GitHub 中也可通过 [动作目录](../keyframes/README.md) 查看每帧及制作记录。

## 上传前检查

```bash
python scripts/build_gallery.py
python scripts/verify.py
```

项目附带 GitHub Actions 检查，但不会自动发布或替你创建仓库。公开说明应保留作者署名和许可状态，尤其是 DeepSeek 的非商业要求与 GPT 变体尚未核实的来源授权。详见 [图片许可](../ASSET-LICENSES.md)。
