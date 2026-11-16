from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib, json, re, struct, sys, zlib

ROOT = Path(__file__).resolve().parents[1]
errors = []
seen_images = {}
EXPECTED_IDS = {"deepseek","qwen","kimi","glm","gpt","claude","gemini","grok"}
IGNORED_DIRS = {".git",".venv","__pycache__","dist",".local"}

def require(condition, message):
    if not condition:
        errors.append(message)

def inside(path):
    target = (ROOT/path).resolve()
    require(target.is_relative_to(ROOT), f"Path escapes project: {path}")
    require(target.exists(), f"Missing file or directory: {path}")
    return target

def png_record(record):
    p = inside(record["path"])
    if not p.is_file():
        return
    raw = p.read_bytes()
    require(raw[:8] == b"\x89PNG\r\n\x1a\n", f"Not PNG: {p.relative_to(ROOT)}")
    if len(raw) < 33 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        return
    width, height = struct.unpack(">II", raw[16:24])
    require([width,height] == [record["width"],record["height"]], f"Dimension mismatch: {record['path']}")
    require(len(raw) == record["bytes"], f"Byte-size mismatch: {record['path']}")
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == record["sha256"], f"Hash mismatch: {record['path']}")
    pos = 8
    ended = False
    while pos + 12 <= len(raw):
        length = struct.unpack(">I", raw[pos:pos+4])[0]
        kind = raw[pos+4:pos+8]
        end = pos + 12 + length
        if end > len(raw):
            errors.append(f"Truncated PNG: {record['path']}")
            break
        payload = raw[pos+8:pos+8+length]
        crc = struct.unpack(">I", raw[pos+8+length:end])[0]
        require(zlib.crc32(kind+payload) & 0xffffffff == crc, f"PNG CRC mismatch: {record['path']} {kind!r}")
        pos = end
        if kind == b"IEND":
            ended = True
            break
    require(ended and pos == len(raw), f"Invalid PNG ending: {record['path']}")
    seen_images[record["path"]] = digest

def local_link(source, href):
    href = href.strip().strip("<>")
    if not href or href.startswith(("#","mailto:","data:")):
        return
    if urlsplit(href).scheme:
        return
    target = unquote(href.split("#",1)[0].split("?",1)[0])
    if not target:
        return
    path = (source.parent/target).resolve()
    require(path.is_relative_to(ROOT), f"Link escapes project: {source.relative_to(ROOT)} -> {href}")
    require(path.exists(), f"Broken local link: {source.relative_to(ROOT)} -> {href}")

class Links(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.source = source
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href","src") and value:
                local_link(self.source,value)

data = json.loads((ROOT/"catalog.json").read_text(encoding="utf-8"))
chars = data["characters"]
require(len(chars)==data["character_count"]==8, "Character count mismatch")
require({c["id"] for c in chars} == EXPECTED_IDS, "Unexpected/missing/duplicate character IDs")
require(len({c["id"] for c in chars}) == len(chars), "Duplicate character")
require(not (EXPECTED_IDS & set(data["excluded_character_ids"])), "Excluded character registered")
png_record(data["reference_board"])
variant_count = 0
current_count = 0
keyframe_count = 0
keyframe_series = data.get("keyframe_series")
if keyframe_series:
    frames = keyframe_series["frames"]
    require([f["id"] for f in frames] == [f"K{i}" for i in range(1,8)], "Expected seven ordered keyframes")
    require([f["seconds"] for f in frames] == [0.0,1.0,1.8,2.2,3.5,4.6,5.8], "Unexpected keyframe timing")
    require(keyframe_series["loop_seconds"] == 6.9, "Unexpected loop timing")
for c in chars:
    require((ROOT/"characters"/c["id"]/"README.md").is_file(), f"Missing character README: {c['id']}")
    provenance = inside(c["provenance"])
    if provenance.is_file():
        p = json.loads(provenance.read_text(encoding="utf-8"))
        require(p["character"] == c["id"], f"Wrong provenance character: {c['id']}")
        require(bool(p.get("license_status")), f"Missing license record: {c['id']}")
    png_record(c["reference"])
    ids = [v["id"] for v in c["variants"]]
    require(len(ids)==len(set(ids)), f"Duplicate variant: {c['id']}")
    require(c["featured_variant"] in ids, f"Missing featured variant: {c['id']}")
    require("v1-initial" in ids and "v2-dance" in ids, f"Missing preserved/current set: {c['id']}")
    for v in c["variants"]:
        variant_count += 1
        expected = f"characters/{c['id']}/variants/{v['id']}/sheet.png"
        require(v["image"]["path"] == expected, f"Nonstandard image path: {c['id']} {v['id']}")
        png_record(v["image"])
        inside(f"characters/{c['id']}/variants/{v['id']}/README.md")
        for key in ("prompt","refinement_prompt","layout_reference","generation"):
            if key in v:
                inside(v[key])
        if v["id"] == "v2-dance":
            current_count += 1
            require([v["image"]["width"],v["image"]["height"]] == [1536,1024], f"Current sheet size mismatch: {c['id']}")
            require("prompt" in v and "generation" in v, f"Missing current prompt/record: {c['id']}")
            if "generation" in v:
                record = json.loads((ROOT/v["generation"]).read_text(encoding="utf-8"))
                require(record["output"] == v["image"], f"Generation metadata mismatch: {c['id']}")
                require(record["view_order"] == ["front","left-side","back"], f"View order mismatch: {c['id']}")
    if keyframe_series:
        collections = c.get("keyframes", [])
        require(len(collections) == 1, f"Expected one individual keyframe series: {c['id']}")
        for collection in collections:
            require(collection["id"] == keyframe_series["id"] == "v4-individual", f"Wrong keyframe series: {c['id']}")
            base = f"characters/{c['id']}/keyframes/{collection['id']}"
            inside(base + "/README.md")
            inside(collection["identity_reference"])
            selected = collection["frames"]
            require([f["id"] for f in selected] == [f"K{i}" for i in range(1,8)], f"Missing/duplicate/out-of-order frame: {c['id']}")
            for frame, timing in zip(selected, keyframe_series["frames"]):
                keyframe_count += 1
                fid = frame["id"]
                require(frame["seconds"] == timing["seconds"], f"Frame timing mismatch: {c['id']}/{fid}")
                require(frame["image"]["path"] == base + "/" + fid + ".png", f"Nonstandard individual frame path: {c['id']}/{fid}")
                png_record(frame["image"])
                require(frame["image"]["width"] > frame["image"]["height"], f"Expected landscape frame: {c['id']}/{fid}")
                generation = inside(frame["generation"])
                record = json.loads(generation.read_text(encoding="utf-8"))
                require(record["character"] == c["id"] and record["frame"] == fid, f"Wrong frame generation identity: {c['id']}/{fid}")
                require(record["output"] == frame["image"] and record["seconds"] == frame["seconds"], f"Frame generation metadata mismatch: {c['id']}/{fid}")
                require(bool(record["review"]["notes"]), f"Missing individual visual review: {c['id']}/{fid}")
                require(bool(frame["prompts"]), f"Missing individual prompt: {c['id']}/{fid}")
                require(frame["prompts"] == [base + "/" + p for p in record["prompts"]], f"Prompt record mismatch: {c['id']}/{fid}")
                for prompt in frame["prompts"]:
                    inside(prompt)
                for key in ("identity_master", "turnaround_reference", "prior_frame_reference"):
                    if key in record:
                        inside(record[key])
require(variant_count==data["variant_count"] and variant_count>=17, "Variant count mismatch or preserved sheets missing")
require(current_count==data["new_series_count"]==8, "Expected 8 new matched sheets")
if keyframe_series:
    require(keyframe_count == keyframe_series["image_count"] == 56, "Expected 56 individual keyframes")
    require(keyframe_series["character_count"] == 8, "Expected 8 keyframe characters")
    inside("keyframes/index.html")
    inside("keyframes/README.md")
art_paths = {p.relative_to(ROOT).as_posix() for folder in ("characters","references") for p in (ROOT/folder).rglob("*.png")}
require(art_paths == set(seen_images), "Artwork files and catalog image records differ")
for name in ("README.md","LICENSE","LICENSE-CODE","ASSET-LICENSES.md","ATTRIBUTION.md","CHANGELOG.md","CONTRIBUTING.md","index.html",".github/workflows/validate.yml"):
    inside(name)
for p in ROOT.rglob("*"):
    if not p.is_file() or any(part in IGNORED_DIRS for part in p.relative_to(ROOT).parts):
        continue
    if p.suffix not in (".md",".html",".css",".js",".py",".json",".yml",".txt"):
        continue
    text = p.read_text(encoding="utf-8")
    require(not re.search(r"[A-Za-z]:[\\/]+Users[\\/]",text), f"Private local path in public text: {p.relative_to(ROOT)}")
    if p.suffix == ".md":
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)",text):
            local_link(p,link)
        Links(p).feed(text)
    elif p.suffix == ".html" and "web" not in p.relative_to(ROOT).parts:
        Links(p).feed(text)
checksums = ROOT/"checksums.sha256"
require(checksums.exists(), "Missing checksums.sha256")
if checksums.exists():
    expected = {}
    for line in checksums.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, path = line.split("  ",1)
            expected[path] = digest
    require(expected == seen_images, "checksums.sha256 and registered images differ")
if errors:
    print("\n".join("ERROR: "+e for e in errors))
    sys.exit(1)
print(f"OK: {len(chars)} characters, {variant_count} turnaround sheets ({current_count} matched), {keyframe_count} individual keyframes, {len(seen_images)} PNG images.")
print("PNG CRC/hash/dimensions, records, local links and public-path hygiene passed.")
