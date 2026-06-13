#!/usr/bin/env python3
"""Synchronize high-drift Herm docs sections from /home/kaio/Dev/herm source.

The script is intentionally dependency-free. It parses the current TypeScript
source conservatively and rewrites only AUTO-GENERATED blocks.
"""
from __future__ import annotations
from pathlib import Path
import ast, os, re

ROOT = Path(__file__).resolve().parents[1]
HERM = Path(os.environ.get("HERM_SOURCE", ROOT.parent / "herm"))

START = "{/* BEGIN AUTO-GENERATED: %s */}"
END = "{/* END AUTO-GENERATED: %s */}"

def replace_block(path: Path, name: str, body: str) -> None:
    text = path.read_text()
    start = START % name
    end = END % name
    block = f"{start}\n{body.rstrip()}\n{end}"
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pat.search(text):
        text = pat.sub(block, text)
    else:
        raise SystemExit(f"missing generated block {name} in {path}")
    path.write_text(text)

def split_top_level_object(src: str) -> list[tuple[str, str, str]]:
    out=[]
    for m in re.finditer(r'"([^"]+)"\s*:\s*def\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)', src):
        out.append((m.group(1), m.group(2), m.group(3)))
    return out

def keybindings() -> str:
    src=(HERM/'src/keys/catalog.ts').read_text()
    rows=split_top_level_object(src)
    scopes={}
    for action,chord,desc in rows:
        # Scope is the fourth capture in the original line; re-match specific line.
        mm=re.search(rf'"{re.escape(action)}"\s*:\s*def\("[^"]*",\s*"[^"]*",\s*"([^"]*)"\)', src)
        scope=mm.group(1) if mm else 'global'
        chord=chord.replace(',', ' / ')
        scopes.setdefault(scope,[]).append((action,chord,desc))
    order=['global','list','dialog','composer','sessions','cron','env','agents','skills','config','eikon']
    labels={s:s.title() for s in order}
    labels.update({'eikon':'Eikon','env':'Env'})
    parts=[]
    for scope in order:
        if scope not in scopes: continue
        parts.append(f"### {labels[scope]}\n")
        parts.append("| Action | Default chord | Description |\n|---|---|---|")
        for a,c,d in scopes[scope]:
            parts.append(f"| `{a}` | `{c}` | {d} |")
        parts.append('')
    return '\n'.join(parts)

def slash_commands() -> str:
    src=(HERM/'src/app/slashCommands.ts').read_text()
    body=src.split('export const LOCAL_COMMANDS',1)[1].split(']\n',1)[0]
    rows=[]
    for obj in re.findall(r'\{\s*name:.*?\}', body, flags=re.S):
        def field(name: str, default: str='') -> str:
            m=re.search(rf'{name}:\s*"([^"]*)"', obj)
            return m.group(1) if m else default
        name=field('name'); desc=field('description'); cat=field('category')
        args=field('argsHint') or 'None'
        m=re.search(r'aliases:\s*\[([^\]]*)\]', obj, flags=re.S)
        aliases=m.group(1) if m else ''
        al=', '.join(f'`{x}`' for x in re.findall(r'"([^"]+)"', aliases)) or 'None'
        if not name or not cat: continue
        rows.append((cat,name,al,args.replace('|','\\|'),desc))
    order=['Client','Session','Info','Exit']
    parts=[]
    for cat in order:
        part=[r for r in rows if r[0]==cat]
        if not part: continue
        parts.append(f"## {cat} commands\n")
        parts.append("| Command | Aliases | Args | Description |\n|---|---|---|---|")
        for _,name,al,args,desc in part:
            parts.append(f"| `/{name}` | {al} | `{args}` | {desc} |")
        parts.append('')
    return '\n'.join(parts)

def themes() -> str:
    src=(HERM/'src/theme/manifest.ts').read_text()
    rows=[]
    for m in re.finditer(r'"([^"]+)": \{ primary: "([^"]+)", accent: "([^"]+)", background: "([^"]+)" \}', src):
        rows.append(m.groups())
    out=["| Theme | Primary | Accent | Background |", "|---|---|---|---|"]
    for name,primary,accent,bg in sorted(rows):
        out.append(f"| `{name}` | `{primary}` | `{accent}` | `{bg}` |")
    return '\n'.join(out)

def env_vars() -> str:
    files=[
        'src/context/gateway-client.ts','src/utils/paths.ts','src/service/hermes-kanban.ts',
        'src/service/eikon.ts','src/service/hermes-home.ts','src/tabs/EikonMarketplace.tsx','src/io/index.ts',
        'src/app/control.ts','src/app/slash.tsx','src/utils/perf.ts','src/utils/editor.ts'
    ]
    names=set()
    for f in files:
        p=HERM/f
        if not p.exists(): continue
        txt=p.read_text()
        names.update(re.findall(r'process\.env\.([A-Z0-9_]+)', txt))
        names.update(re.findall(r'process\.env\["([A-Z0-9_]+)"\]', txt))
    desc={
        'HERMES_HOME':'Hermes data directory. Defaults to `~/.hermes`.',
        'HERMES_AGENT_ROOT':'Hermes Agent source/install tree used to launch the gateway.',
        'HERMES_PYTHON':'Python interpreter used for the gateway subprocess.',
        'HERM_CONFIG_DIR':'Herm TUI preferences directory. Defaults to `$HERMES_HOME/herm`.',
        'HERMES_CWD':'Working directory passed to the gateway session.',
        'HERM_EIKON_MARKETPLACE':'Override the lower-level Eikon catalog loader default. The native Marketplace tab uses `EIKON_URL`.',
        'EIKON_URL':'Override the native Eikon Marketplace catalog URL.',
        'HERMES_KANBAN_HOME':'Pin the kanban data home.',
        'HERMES_KANBAN_BOARD':'Default kanban board filter/selection.',
        'HERMES_KANBAN_BUSY_TIMEOUT_MS':'Kanban busy timeout in milliseconds.',
        'HERMES_KANBAN_ATTACHMENTS_ROOT':'Override where Herm resolves kanban attachment files.',
        'HERM_IO_INLINE':'Inline I/O payload mode for Herm internal I/O.',
        'HERMES_TUI_NO_CONFIRM':'Skip Herm client-side destructive slash confirmations when set to `1`.',
        'CONTROL':'Enable the local control server when set to `1`.',
        'CONTROL_PORT':'Control server port. Defaults to `7777`.',
        'CONTROL_BIND':'Control server bind address. Defaults to `127.0.0.1`.',
        'PERF':'Enable performance logging or verbose performance mode.',
        'VISUAL':'Preferred editor for opening prompt drafts.',
        'EDITOR':'Fallback editor for opening prompt drafts.',
        'VIRTUAL_ENV':'Preferred Python virtualenv when resolving the gateway interpreter.',
        'HERMES_MANAGED':'Marks package-manager-managed Hermes installs.',
    }
    out=["| Variable | Purpose |", "|---|---|"]
    for n in sorted(names):
        if n in {'HOME','USER','TMUX','STY','WAYLAND_DISPLAY','HERM_TEST_PERF'}: continue
        out.append(f"| `{n}` | {desc.get(n,'Internal/development override. Verify source before documenting for end users.')} |")
    return '\n'.join(out)

replace_block(ROOT/'customization/keybindings.mdx','keybindings', keybindings())
replace_block(ROOT/'customization/slash-commands.mdx','local-slash-commands', slash_commands())
replace_block(ROOT/'customization/themes.mdx','themes', themes())
replace_block(ROOT/'configuration.mdx','env-vars', env_vars())
print('synchronized Herm docs generated sections from', HERM)
