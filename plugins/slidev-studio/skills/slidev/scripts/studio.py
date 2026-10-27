#!/usr/bin/env python3
"""Slidev Studio: local template selection, project settings, and reversible styling."""

import argparse
import base64
import copy
import datetime as dt
import hashlib
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
from urllib.parse import urlparse
import webbrowser

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets" / "studio"
CONFIG = "slidev-studio.json"
STYLE = "styles/index.css"
BEGIN = "/* slidev-studio:begin */"
END = "/* slidev-studio:end */"
LEGACY_TEMPLATE_IDS = {"ics-course": "cyan-classroom"}
FONTS = {
    "sans": '"Avenir Next", "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif',
    "serif": '"Iowan Old Style", "Noto Serif CJK SC", "Songti SC", "SimSun", Georgia, serif',
}


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def inside(root, relative):
    path = root / relative
    # A project may itself be a symlink, but a managed path cannot escape it.
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Managed path escapes project: {relative}")
    return path


def catalog(project=None):
    items = json.loads((ASSETS / "templates.json").read_text(encoding="utf-8"))
    if project and project.exists():
        folder = inside(project, "slidev-templates")
        if folder.exists():
            for path in sorted(folder.glob("*.json")):
                item = json.loads(path.read_text(encoding="utf-8"))
                if not re.fullmatch(r"[a-z][a-z0-9-]{0,48}", item.get("id", "")):
                    raise ValueError(f"Invalid template id in {path.name}")
                if item["id"] in LEGACY_TEMPLATE_IDS or any(x["id"] == item["id"] for x in items):
                    raise ValueError(f"Duplicate template id: {item['id']}")
                if not isinstance(item.get("name"), str) or not item["name"].strip():
                    raise ValueError(f"Template name missing: {path.name}")
                # Validate custom defaults as data; no scripts or arbitrary CSS.
                cfg = {"template": items[0]["id"], "title": "Preview", "settings": item["defaults"]}
                normalized=validate_config(cfg, items)
                items.append({**item,"defaults":normalized["settings"]})
    return items


def validate_config(config, items):
    if not isinstance(config, dict) or set(config) - {"version", "template", "title", "settings"}:
        raise ValueError("Unsupported configuration fields")
    if config.get("version", 1) != 1:
        raise ValueError("Unsupported configuration version")
    requested = config.get("template")
    identifier = LEGACY_TEMPLATE_IDS.get(requested, requested) if isinstance(requested, str) else None
    template = next((i for i in items if i["id"] == identifier), None)
    if not template:
        raise ValueError("Unknown template")
    title = config.get("title", "Slidev Presentation")
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 240 or any(ord(c) < 32 for c in title):
        raise ValueError("Title must be 1–240 characters on one line")
    supplied = config.get("settings", {})
    if not isinstance(supplied, dict) or set(supplied) - set(template["defaults"]):
        raise ValueError("Unknown setting")
    settings = {**template["defaults"], **supplied}
    for key in ["accent", "accentEnd", "background", "foreground", "muted"]:
        if not isinstance(settings[key], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", settings[key]):
            raise ValueError(f"{key}: expected a six-digit hex color")
    for key, low, high in [("titleSize", 28, 60), ("bodySize", 18, 32), ("codeSize", 14, 26), ("spacing", 28, 72)]:
        value = settings[key]
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"{key}: expected an integer between {low} and {high}")
    for key, choices in {"font": FONTS, "aspectRatio": ["16/9", "4/3", "16/10"],
                         "transition": ["fade", "slide-left", "slide-up", "none"],
                         "coverStyle": ["light", "dark"], "colorSchema": ["light", "dark"],
                         "composition": ["classic", "briefing", "editorial", "blueprint", "poster"]}.items():
        if settings[key] not in choices:
            raise ValueError(f"Invalid {key}")
    for key in ["gradientTitle", "pageNumbers"]:
        if type(settings[key]) is not bool:
            raise ValueError(f"{key}: expected true or false")
    image = settings["coverImage"]
    if not isinstance(image, str) or (image and not re.fullmatch(r"/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|webp|svg)", image, re.I)) or ".." in image or "//" in image:
        raise ValueError("Cover must be a local /path/image.png, jpg, webp or svg asset")
    return {"version": 1, "template": template["id"], "title": title.strip(), "settings": settings}


def default_config(project=None, template="cyan-classroom", title="让机制看得见"):
    return validate_config({"template": template, "title": title}, catalog(project))


def load_config(project):
    path = inside(project, CONFIG)
    if path.exists():
        return validate_config(json.loads(path.read_text(encoding="utf-8")), catalog(project))
    result=default_config(project)
    entry=inside(project,"slides.md")
    if entry.is_file():
        match=re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|$)",entry.read_text(encoding="utf-8"),re.S)
        title=re.search(r"^title:[ \t]*(.+)$",match.group(1),re.M) if match else None
        if title:
            raw=title.group(1).strip()
            try:
                value=json.loads(raw)
            except json.JSONDecodeError:
                value=raw[1:-1].replace("''", "'") if raw.startswith("'") and raw.endswith("'") else raw.split(" #",1)[0]
            if isinstance(value,str) and value and not value.startswith(("|",">")):
                result["title"]=value
    return result


def css(config):
    s = config["settings"]
    title_color = f"background:linear-gradient(110deg,{s['accentEnd']},{s['accent']});background-clip:text;-webkit-background-clip:text;color:transparent" if s["gradientTitle"] else f"color:{s['accent']}"
    image = s["coverImage"] or "/studio/chip-cover.svg"
    cover = f"background-image:linear-gradient(#0007,#0007),url('{image}');background-size:cover;background-position:center;color:#f8fafc" if s["coverStyle"] == "dark" else f"background:{s['background']};color:{s['foreground']}"
    cover_ink = "#f8fafc" if s["coverStyle"] == "dark" else s["foreground"]
    cover_muted = "#d4dce5" if s["coverStyle"] == "dark" else s["muted"]
    composition = s.get("composition", "classic")
    grid_selector = ".slidev-layout,.slidev-layout.starter-cover,.slidev-layout.cover" if s["coverStyle"] == "light" else ".slidev-layout:not(.starter-cover):not(.cover)"
    variants = {
        "classic": "",
        "briefing": f"""
.slidev-layout h1 {{border-bottom:2px solid {s['accent']}55;padding-bottom:16px;line-height:1.2;}}
.slidev-layout.starter-cover,.slidev-layout.cover {{text-align:left;padding-top:82px;border-top:10px solid {s['accent']};}}
.slidev-layout.starter-cover h1,.slidev-layout.cover h1 {{border:0;max-width:820px;margin:44px 0 28px;}}
.slidev-layout.starter-cover :is(p,.caption,.eyebrow,.cover-rule),.slidev-layout.cover :is(p,.caption,.eyebrow) {{margin-left:0;margin-right:0;}}
""",
        "editorial": f"""
.slidev-layout {{border-top:5px solid {s['accent']};}}
.slidev-layout h1 {{line-height:1.18;font-weight:600;letter-spacing:-.025em;}}
.slidev-layout .eyebrow {{letter-spacing:.12em;font-family:{FONTS['sans']};}}
.slidev-layout.starter-cover,.slidev-layout.cover {{text-align:left;padding-top:72px;}}
.slidev-layout.starter-cover h1,.slidev-layout.cover h1 {{max-width:800px;margin:46px 0 30px;}}
.slidev-layout.starter-cover :is(p,.caption,.eyebrow,.cover-rule),.slidev-layout.cover :is(p,.caption,.eyebrow) {{margin-left:0;margin-right:0;}}
""",
        "blueprint": f"""
{grid_selector} {{background-image:linear-gradient({s['accent']}10 1px,transparent 1px),linear-gradient(90deg,{s['accent']}10 1px,transparent 1px)!important;background-size:32px 32px!important;}}
.slidev-layout h1,.slidev-layout .eyebrow {{font-family:ui-monospace,"SFMono-Regular",Consolas,{FONTS['sans']};}}
.slidev-layout h1 {{line-height:1.25;}}
.slidev-layout .eyebrow {{letter-spacing:.1em;}}
.slidev-layout.starter-cover,.slidev-layout.cover {{text-align:left;padding-top:84px;}}
.slidev-layout.starter-cover h1,.slidev-layout.cover h1 {{max-width:820px;margin:42px 0 28px;}}
.slidev-layout.starter-cover :is(p,.caption,.eyebrow,.cover-rule),.slidev-layout.cover :is(p,.caption,.eyebrow) {{margin-left:0;margin-right:0;}}
""",
        "poster": f"""
.slidev-layout h1 {{line-height:1.12;letter-spacing:-.035em;font-weight:800;}}
.slidev-layout.starter-cover,.slidev-layout.cover {{padding-top:58px;border-bottom:14px solid {s['accent']};}}
.slidev-layout.starter-cover h1,.slidev-layout.cover h1 {{max-width:820px;margin:38px auto 28px;font-size:{min(72,s['titleSize']+20)}px;}}
.slidev-layout .eyebrow {{font-weight:700;letter-spacing:.12em;}}
""",
    }
    return f"""{BEGIN}
.slidev-layout {{ --talk-accent:{s['accent']};--talk-ink:{s['foreground']};--talk-muted:{s['muted']};--slidev-code-font-size:{s['codeSize']}px;background:{s['background']};color:{s['foreground']};font-family:{FONTS[s['font']]};font-size:{s['bodySize']}px;padding-left:{s['spacing']}px;padding-right:{s['spacing']}px; }}
.slidev-layout h1 {{font-size:{s['titleSize']}px;{title_color};letter-spacing:normal;}}
.slidev-layout p,.slidev-layout li {{font-size:{s['bodySize']}px;}}
.slidev-layout pre,.slidev-layout code {{font-size:{s['codeSize']}px;}}
.slidev-layout .caption {{color:{s['muted']};font-size:16px;}}
.slidev-layout :is(.eyebrow,.explanation) {{color:{s['accent']};}}
.slidev-layout.starter-cover,.slidev-layout.cover {{ {cover};text-align:center;padding-top:78px; }}
.slidev-layout.starter-cover h1,.slidev-layout.cover h1 {{background:none;color:{cover_ink};font-size:{min(66,s['titleSize']+20)}px;margin:42px auto 26px;}}
.slidev-layout.starter-cover :is(p,.caption,.eyebrow),.slidev-layout.cover :is(p,.caption,.eyebrow) {{color:{cover_muted};opacity:1;margin-left:auto;margin-right:auto;}}
.slidev-layout.starter-cover .cover-rule {{margin-left:auto;margin-right:auto;}}
.slidev-layout.starter-ending h1 {{font-size:{min(52,s['titleSize']+8)}px;}}
.slidev-layout table {{width:100%;border-collapse:collapse;}}
.slidev-layout td,.slidev-layout th {{border-bottom:1px solid {s['muted']}44;padding:12px 10px;text-align:left;}}
.slidev-layout a {{text-decoration:underline;text-underline-offset:4px;text-decoration-style:dashed;}}
.talk-footer {{color:{s['muted']};display:{'flex' if s['pageNumbers'] else 'none'} !important;}}
.slidev-layout .latency-demo {{background:{s['background']};border-color:{s['muted']}66;color:{s['foreground']};}}
.slidev-layout .latency-demo :is(p,.demo-output>span) {{color:{s['muted']};}}
.slidev-layout .latency-demo :is(strong,button) {{color:{s['accent']};}}
.slidev-layout .latency-demo button {{background:{s['background']};border-color:{s['accent']};}}
.slidev-layout .latency-demo .latency-track>div {{background:{s['accent']};}}
{variants[composition]}
{END}
"""


def update_headmatter(text, values):
    # Edit only first headmatter scalar keys. Never split a deck on separators.
    match = re.match(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("Entry needs ordinary YAML headmatter at the beginning; add it before applying a template")
    block = match.group(1)
    for key, value in values.items():
        pattern = re.compile(r"^(?:" + re.escape(key) + r"|'" + re.escape(key) + r"'|\"" + re.escape(key) + r"\"):[^\n]*$", re.M)
        found = list(pattern.finditer(block))
        if len(found) > 1:
            raise ValueError(f"Duplicate headmatter key: {key}")
        replacement = key + ": " + json.dumps(value, ensure_ascii=False)
        if found:
            old = found[0]
            current = old.group().split(":", 1)[1].strip()
            tail = block[old.end():].splitlines()
            next_line = next((line for line in tail if line.strip()), "")
            if not current or current.startswith(("|", ">", "&", "*", "!")) or (next_line and next_line[0].isspace() and not next_line.lstrip().startswith("#")):
                raise ValueError(f"Headmatter {key} is not a simple scalar; edit it manually")
            block = pattern.sub(lambda _: replacement, block, count=1)
        else:
            block += "\n" + replacement
    return "---\n" + block + "\n---\n" + text[match.end():]


def managed_style(original, generated):
    if original.count(BEGIN) != original.count(END) or original.count(BEGIN) > 1:
        raise ValueError("Malformed Studio style markers; repair before applying")
    if BEGIN in original:
        start, end = original.index(BEGIN), original.index(END) + len(END)
        if end < start:
            raise ValueError("Invalid Studio style marker order")
        return original[:start] + generated.rstrip() + original[end:]
    return original.rstrip() + "\n\n" + generated


def snapshot(project, relatives):
    backup = inside(project, ".slidev-studio/backups") / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + secrets.token_hex(2))
    backup.mkdir(parents=True)
    inventory = {}
    for relative in relatives:
        path = inside(project, relative)
        inventory[relative] = path.exists()
        if path.exists():
            target = backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    (backup / "inventory.json").write_text(dump(inventory), encoding="utf-8")
    return backup


def write_atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".studio-", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content.encode("utf-8"))
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def apply(project, config):
    project = project.expanduser().resolve()
    config = validate_config(config, catalog(project))
    entry = inside(project, "slides.md")
    if not entry.is_file():
        raise ValueError("No slides.md; create a deck first. This version manages the default entry only")
    # An existing style.ts/js or style.css can take precedence over styles/index.css.
    if any(inside(project, p).exists() for p in ["style.css", "styles/index.ts", "styles/index.js"]):
        raise ValueError("This deck has another style entry. Import a generated Studio stylesheet explicitly instead of replacing it")
    text = entry.read_text(encoding="utf-8")
    s = config["settings"]
    text = update_headmatter(text, {"title":config["title"], "aspectRatio":s["aspectRatio"], "transition":False if s["transition"] == "none" else s["transition"], "colorSchema":s["colorSchema"]})
    style = inside(project, STYLE)
    output = {"slides.md":text, STYLE:managed_style(style.read_text(encoding="utf-8") if style.exists() else "", css(config)), CONFIG:dump(config)}
    if all(inside(project,p).exists() and inside(project,p).read_text(encoding="utf-8")==v for p,v in output.items()):
        return {"project":str(project),"changed":False,"backup":None}
    backup = snapshot(project, output)
    try:
        for relative, content in output.items():
            write_atomic(inside(project,relative), content)
        cover = inside(project, "public/studio/chip-cover.svg")
        if not cover.exists():
            cover.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ASSETS / "chip-cover.svg", cover)
    except Exception:
        restore(project, backup.name, protect=False)
        raise
    return {"project":str(project),"changed":True,"backup":str(backup.relative_to(project))}


def create(project, config):
    project = project.expanduser().absolute()
    validate_config(config, catalog())
    subprocess.run([sys.executable, str(SKILL / "scripts/scaffold.py"), str(project), "--title", config["title"], "--lang", "zh-CN"], check=True, capture_output=True, text=True)
    try:
        return apply(project, config)
    except Exception:
        shutil.rmtree(project)
        raise


def restore(project, name="latest", protect=True):
    parent = inside(project, ".slidev-studio/backups")
    if not parent.is_dir():
        raise ValueError("No backups")
    if name == "latest":
        folders = sorted(p for p in parent.iterdir() if p.is_dir())
        if not folders:
            raise ValueError("No backups")
        backup = inside(project, f".slidev-studio/backups/{folders[-1].name}")
    elif re.fullmatch(r"[A-Za-z0-9-]+", name):
        backup = inside(project, f".slidev-studio/backups/{name}")
    else:
        raise ValueError("Invalid backup id")
    inventory = json.loads(inside(backup,"inventory.json").read_text(encoding="utf-8"))
    if set(inventory) != {"slides.md", STYLE, CONFIG} or any(type(v) is not bool for v in inventory.values()):
        raise ValueError("Invalid backup inventory")
    contents = {p: inside(backup, p).read_text(encoding="utf-8") if exists else None for p,exists in inventory.items()}
    for p in contents:
        inside(project,p)
    if protect:
        snapshot(project,contents)
    for p,content in contents.items():
        target=inside(project,p)
        if content is None:
            target.unlink(missing_ok=True)
        else:
            write_atomic(target,content)
    return {"restored":backup.name,"project":str(project)}


def save_template(project, identifier, name, config=None):
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,48}", identifier) or not isinstance(name,str) or not name.strip():
        raise ValueError("Use a lowercase template id and a nonempty name")
    if identifier in LEGACY_TEMPLATE_IDS or any(x["id"] == identifier for x in catalog(project)):
        raise ValueError("Template id already exists; choose another")
    if not inside(project,"slides.md").is_file():
        raise ValueError("Create a deck before saving a project template")
    config = validate_config(config,catalog(project)) if config else load_config(project)
    item = {"id":identifier,"name":name.strip()[:80],"description":"项目自定义模板","defaults":config["settings"]}
    path = inside(project,f"slidev-templates/{identifier}.json")
    write_atomic(path,dump(item))
    return item


def preview(config, view="content"):
    s=config["settings"]
    ratio=[int(x) for x in s["aspectRatio"].split("/")]
    height=980*ratio[1]/ratio[0]
    # srcdoc has no access to project assets; server preview serves local /studio assets.
    generated=css(config).replace("url('/", "url('/project-assets/")
    title=html.escape(config["title"])
    if view == "cover":
        content=f'<div class="slidev-layout starter-cover"><div class="eyebrow">SLIDEV · 课程与技术分享</div><h1>{title}</h1><p>从问题出发，让机制看得见</p><div class="caption">作者 / 机构 · 演示日期</div></div>'
    else:
        content='<div class="slidev-layout"><div class="eyebrow">01 · 从结构到解释</div><h1>用清晰的层级讲透一个概念</h1><p class="caption">让代码、图表和叙述相互配合</p><div class="columns"><div><h2>先给出结论</h2><p>一个页面，只承担一个主要任务。</p><ul><li>突出关键的变化</li><li>保留足够的留白</li><li>用交互验证假设</li></ul></div><pre><code>const cached = cache.get(key)\nif (cached !== undefined)\n  return cached\n\nreturn await fetchValue(key)</code></pre></div></div>'
    return f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>*{{box-sizing:border-box}}body{{margin:0}}.slidev-layout{{width:980px;height:{height}px;padding:44px 52px;line-height:1.5}}h1{{margin:10px 0 20px;font-weight:700}}h2{{font-size:25px}}.eyebrow{{font-size:15px}}.columns{{display:grid;grid-template-columns:1fr 1fr;gap:36px;margin-top:32px}}pre{{padding:24px;background:#12202e;color:#e5f1f5;border-radius:6px;line-height:1.8}}.caption{{font-size:16px}}{generated}</style>{content}</html>'


def serve(project, port=0, open_browser=True):
    token=secrets.token_urlsafe(32)
    project=project.expanduser().absolute()
    mutation_lock=threading.RLock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, code, content, mime="application/json; charset=utf-8"):
            data=content.encode("utf-8") if isinstance(content,str) else content
            self.send_response(code)
            self.send_header("Content-Type",mime)
            self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers()
            self.wfile.write(data)

        def host_ok(self):
            return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}",f"localhost:{self.server.server_port}"}

        def do_GET(self):
            if not self.host_ok():
                return self.send(403,dump({"error":"Invalid host"}))
            path=urlparse(self.path).path
            try:
                if path == "/":
                    page=(ASSETS/"studio.html").read_text(encoding="utf-8").replace("__TOKEN_JSON__",json.dumps(token))
                    return self.send(200,page,"text/html; charset=utf-8")
                if path == "/api/state":
                    return self.send(200,dump({"project":str(project),"exists":(project/"slides.md").is_file(),"templates":catalog(project),"config":load_config(project)}))
                if path.startswith("/project-assets/"):
                    relative=path[len("/project-assets/"):]
                    if not re.fullmatch(r"[A-Za-z0-9_./-]+\.(?:png|jpe?g|webp|svg)",relative,re.I) or ".." in relative:
                        raise ValueError("Invalid asset path")
                    asset=inside(project,"public/"+relative)
                    if relative == "studio/chip-cover.svg" and not asset.exists():
                        asset=ASSETS/"chip-cover.svg"
                    mime={".svg":"image/svg+xml",".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp"}[asset.suffix.lower()]
                    return self.send(200,asset.read_bytes(),mime)
                return self.send(404,dump({"error":"Not found"}))
            except (ValueError,OSError,json.JSONDecodeError) as error:
                return self.send(400,dump({"error":str(error)}))

        def do_POST(self):
            with mutation_lock:
                self.handle_post()

        def handle_post(self):
            origin=self.headers.get("Origin")
            allowed={f"http://127.0.0.1:{self.server.server_port}",f"http://localhost:{self.server.server_port}"}
            if not self.host_ok() or self.headers.get("X-Studio-Token") != token or (origin and origin not in allowed):
                return self.send(403,dump({"error":"Invalid local session"}))
            try:
                length=int(self.headers.get("Content-Length","0"))
                if not 0 < length <= 8_000_000:
                    raise ValueError("Request too large or empty")
                body=json.loads(self.rfile.read(length))
                path=urlparse(self.path).path
                if path in {"/api/preview","/api/apply"}:
                    cfg=validate_config(body["config"],catalog(project))
                    if path == "/api/preview":
                        return self.send(200,preview(cfg,body.get("view","content")),"text/html; charset=utf-8")
                    result=apply(project,cfg) if (project/"slides.md").is_file() else create(project,cfg)
                    return self.send(200,dump(result))
                if path == "/api/save-template":
                    return self.send(200,dump(save_template(project,body["id"],body["name"],body.get("config"))))
                if path == "/api/restore":
                    return self.send(200,dump(restore(project,body.get("backup","latest"))))
                if path == "/api/upload":
                    if not (project/"slides.md").is_file():
                        raise ValueError("Create the deck before importing a cover image")
                    raw=base64.b64decode(body["data"],validate=True)
                    if not 0 < len(raw) <= 5_000_000:
                        raise ValueError("Image must be under 5 MB")
                    ext="png" if raw.startswith(b"\x89PNG\r\n\x1a\n") else "jpg" if raw.startswith(b"\xff\xd8\xff") else "webp" if raw[:4]==b"RIFF" and raw[8:12]==b"WEBP" else None
                    if not ext:
                        raise ValueError("Use a PNG, JPEG or WebP image")
                    relative="studio/"+hashlib.sha256(raw).hexdigest()[:20]+"."+ext
                    target=inside(project,"public/"+relative)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    if not target.exists():
                        target.write_bytes(raw)
                    return self.send(200,dump({"path":"/"+relative}))
                return self.send(404,dump({"error":"Not found"}))
            except (ValueError,KeyError,TypeError,OSError,subprocess.CalledProcessError) as error:
                return self.send(400,dump({"error":str(error)}))

    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    url=f"http://127.0.0.1:{server.server_port}/"
    print(f"Slidev Studio: {url}\nProject: {project}\nStop with Ctrl+C",flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    subs=parser.add_subparsers(dest="command",required=True)
    listing=subs.add_parser("list",help="List bundled and optional project templates")
    listing.add_argument("--project",type=Path)
    for name in ["new","apply"]:
        sub=subs.add_parser(name)
        sub.add_argument("project",type=Path)
        sub.add_argument("--template",default=None)
        sub.add_argument("--title",default=None)
        sub.add_argument("--set",action="append",default=[],metavar="KEY=VALUE")
    sub=subs.add_parser("show");sub.add_argument("project",type=Path)
    sub=subs.add_parser("serve");sub.add_argument("project",type=Path);sub.add_argument("--port",type=int,default=0);sub.add_argument("--no-browser",action="store_true")
    sub=subs.add_parser("save-template");sub.add_argument("project",type=Path);sub.add_argument("--id",required=True);sub.add_argument("--name",required=True)
    sub=subs.add_parser("restore");sub.add_argument("project",type=Path);sub.add_argument("--backup",default="latest")
    args=parser.parse_args()
    try:
        if args.command == "list":
            result=catalog(args.project)
        elif args.command in {"new","apply"}:
            current=load_config(args.project) if args.command=="apply" else default_config()
            if args.template:
                current=default_config(args.project,args.template,current["title"])
            if args.title:
                current["title"]=args.title
            for pair in args.set:
                if "=" not in pair:
                    raise ValueError("--set expects KEY=VALUE")
                key,value=pair.split("=",1)
                try:
                    value=json.loads(value)
                except json.JSONDecodeError:
                    pass
                current["settings"][key]=value
            result=(create if args.command=="new" else apply)(args.project,current)
        elif args.command == "show":
            result=load_config(args.project)
        elif args.command == "save-template":
            result=save_template(args.project,args.id,args.name)
        elif args.command == "restore":
            result=restore(args.project,args.backup)
        elif args.command == "serve":
            serve(args.project,args.port,not args.no_browser)
            return 0
        print(dump(result),end="")
    except (ValueError,OSError,KeyError,TypeError,subprocess.CalledProcessError) as error:
        print(f"Slidev Studio: {error}",file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
