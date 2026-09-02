#!/usr/bin/env python3
"""
rfmc_newsletter.py - build an email-safe HTML newsletter for the
Ride for Missing Children - Mohawk Valley from a simple Markdown file.

Usage:
    python3 rfmc_newsletter.py content.md -o newsletter.html
    python3 rfmc_newsletter.py content.md            # writes content.html

No third-party packages required. Python 3.8+.

See README.md for the content file format.
"""

import argparse
import html
import os
import re
import sys

# ---------------------------------------------------------------- palette --

THEME = {
    "page_bg": "#f4f6f8",
    "header_bg": "#000000",
    "body_bg": "#ffffff",
    "text": "#000000",
    "eyebrow": "#ef6d9e",
    "headline": "#ffffff",
    "subhead": "#d7e6ff",
    "teal": "#59bfc9",
    "pink": "#ef6d9e",
    "box_bg": "#f7f9fc",
    "box_border": "#e6e8eb",
    "rule": "#e6e8eb",
    "tiny_footer": "#6b7280",
    "link": "#ef6d9e",
    "button_text": "#000000",
}

FONT = "Arial, Helvetica, sans-serif"

DEFAULTS = {
    "title": "Ride for Missing Children - Mohawk Valley",
    "eyebrow": "",
    "headline": "Ride for Missing Children - Mohawk Valley",
    "subhead": "",
    "preheader": "",
    "banner": "https://static.wixstatic.com/media/008655_824eb686e1514882887ed15aaa785fc7~mv2.jpg",
    "banner_alt": "Ride for Missing Children - Mohawk Valley",
    "footer_org": "Ride for Missing Children - Mohawk Valley",
    "footer_address": "",
    "unsubscribe": "{{ unsubscribe_link }}",
    "link_color": THEME["link"],
}


# ------------------------------------------------------------ front matter --

def parse_front_matter(text):
    """Return (meta_dict, body_text). Front matter is a leading --- block."""
    meta = dict(DEFAULTS)
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return meta, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return meta, text
    for raw in lines[1:end]:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace("-", "_")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[key] = value
    return meta, "\n".join(lines[end + 1:])


# ---------------------------------------------------------------- inline ----

BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.S)
ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(\s*([^)\s]+)\s*\)")
BARE_URL_RE = re.compile(r"(?<![\"'=>])\bhttps?://[^\s<>\)]+")
PLACEHOLDER_RE = re.compile(r"\{\{\s*[\w.]+\s*\}\}")


def inline(text, link_color):
    """Escape HTML then apply the small set of inline Markdown we support."""
    out = html.escape(text, quote=False)
    # Un-escape template placeholders such as {{ unsubscribe_link }}.
    out = out.replace("&amp;#", "&#")

    def link_sub(m):
        label = m.group(1)
        url = html.escape(m.group(2), quote=True)
        return (
            '<a href="%s" style="color:%s; text-decoration:underline;">%s</a>'
            % (url, link_color, label)
        )

    out = LINK_RE.sub(link_sub, out)

    # Auto-link bare URLs that are not already inside an anchor tag.
    parts = re.split(r"(<a [^>]*>.*?</a>)", out, flags=re.S)
    for i, part in enumerate(parts):
        if part.startswith("<a "):
            continue
        parts[i] = BARE_URL_RE.sub(
            lambda m: '<a href="%s" style="color:%s; text-decoration:underline;">%s</a>'
            % (m.group(0), link_color, m.group(0)),
            part,
        )
    out = "".join(parts)

    out = BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = ITALIC_RE.sub(r"<em>\1</em>", out)
    out = out.replace("\n", "<br />")
    return out


# ------------------------------------------------------------- tokenizer ----

BOX_OPEN_RE = re.compile(r"^\[BOX(?:\s+(teal|pink|plain))?\]\s*$", re.I)
BOX_CLOSE_RE = re.compile(r"^\[/BOX\]\s*$", re.I)
BUTTON_RE = re.compile(r"^\[BUTTON(?:\s+(teal|pink))?\]\s*(.+?)\s*\|\s*(\S+)\s*$", re.I)
IMAGE_RE = re.compile(r"^\[IMAGE\]\s*(\S+)(?:\s*\|\s*(.*))?$", re.I)
HR_RE = re.compile(r"^(\[HR\]|-{3,}|\*{3,})\s*$", re.I)
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*\S)\s*$")
BULLET_RE = re.compile(r"^\s*[-*+•]\s+(.*)$")


def tokenize(body):
    lines = body.replace("\r\n", "\n").split("\n")
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        m = BOX_OPEN_RE.match(stripped)
        if m:
            accent = (m.group(1) or "plain").lower()
            inner = []
            i += 1
            depth = 1
            while i < n:
                s = lines[i].strip()
                if BOX_OPEN_RE.match(s):
                    depth += 1
                elif BOX_CLOSE_RE.match(s):
                    depth -= 1
                    if depth == 0:
                        break
                inner.append(lines[i])
                i += 1
            i += 1  # consume [/BOX]
            blocks.append({"type": "box", "accent": accent,
                           "blocks": tokenize("\n".join(inner))})
            continue

        m = BUTTON_RE.match(stripped)
        if m:
            blocks.append({
                "type": "button",
                "color": (m.group(1) or "teal").lower(),
                "label": m.group(2),
                "url": m.group(3),
            })
            i += 1
            continue

        m = IMAGE_RE.match(stripped)
        if m:
            blocks.append({"type": "image", "url": m.group(1),
                           "alt": (m.group(2) or "").strip()})
            i += 1
            continue

        if HR_RE.match(stripped):
            blocks.append({"type": "hr"})
            i += 1
            continue

        m = HEADING_RE.match(stripped)
        if m:
            blocks.append({"type": "heading", "level": len(m.group(1)),
                           "text": m.group(2)})
            i += 1
            continue

        if BULLET_RE.match(line):
            items = []
            while i < n and BULLET_RE.match(lines[i]):
                item = BULLET_RE.match(lines[i]).group(1).rstrip()
                i += 1
                # continuation lines: indented, not blank, not a new bullet
                while (i < n and lines[i].strip()
                       and not BULLET_RE.match(lines[i])
                       and lines[i][:1] in (" ", "\t")):
                    item += "\n" + lines[i].strip()
                    i += 1
                items.append(item)
            blocks.append({"type": "list", "items": items})
            continue

        # paragraph: consume until blank line or the start of another block
        para = []
        while i < n and lines[i].strip():
            s = lines[i].strip()
            if (BOX_OPEN_RE.match(s) or BOX_CLOSE_RE.match(s) or BUTTON_RE.match(s)
                    or IMAGE_RE.match(s) or HR_RE.match(s) or HEADING_RE.match(s)
                    or BULLET_RE.match(lines[i])):
                break
            para.append(s)
            i += 1
        if para:
            blocks.append({"type": "para", "text": "\n".join(para)})
    return blocks


# -------------------------------------------------------------- renderer ----

def spacer(px):
    return ('<div style="height:%dpx; line-height:%dpx;">&nbsp;</div>'
            % (px, px))


def gap_between(prev, nxt):
    if prev is None:
        return 0
    p, x = prev["type"], nxt["type"]
    if p == "heading":
        return 0  # headings already carry a 10px bottom margin
    if x == "heading" or x == "hr" or p == "hr":
        return 18
    if p == "para" and x in ("box", "list"):
        return 10
    if p == "para" and x == "button":
        return 12
    if p == "box" and x == "button":
        return 12
    if p == "para" and x == "para":
        return 10
    return 18


def render_para(text, link_color, size=14):
    return ('<div style="color:%s; font-family: %s; font-size:%dpx; '
            'line-height:22px;">%s</div>'
            % (THEME["text"], FONT, size, inline(text, link_color)))


def render_list(items, link_color):
    rows = "<br />\n".join(
        "&bull; %s" % inline(it, link_color) for it in items
    )
    return ('<div style="color:%s; font-family: %s; font-size:14px; '
            'line-height:22px;">%s</div>' % (THEME["text"], FONT, rows))


def render_heading(level, text, link_color):
    size, lh = (20, 28) if level == 1 else (18, 26)
    return ('<div class="h2" style="color:%s; font-family: %s; font-size:%dpx; '
            'line-height:%dpx; font-weight:bold; margin: 0 0 10px;">%s</div>'
            % (THEME["text"], FONT, size, lh, inline(text, link_color)))


def render_button(color, label, url):
    bg = THEME["teal"] if color == "teal" else THEME["pink"]
    return (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn">\n'
        '  <tr>\n'
        '    <td bgcolor="%s" style="border-radius: 10px;">\n'
        '      <a href="%s" style="display:inline-block; padding: 12px 18px; color:%s; '
        'font-family: %s; font-size:14px; font-weight:bold; text-decoration:none; '
        'border-radius:10px;">%s</a>\n'
        '    </td>\n'
        '  </tr>\n'
        '</table>'
        % (bg, html.escape(url, quote=True), THEME["button_text"], FONT,
           html.escape(label, quote=False))
    )


def render_hr():
    return (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%%">\n'
        '  <tr>\n'
        '    <td style="border-top:1px solid %s; font-size:0; line-height:0;">&nbsp;</td>\n'
        '  </tr>\n'
        '</table>' % THEME["rule"]
    )


def render_image(url, alt):
    return ('<img src="%s" width="596" alt="%s" style="display:block; width:100%%; '
            'max-width:596px; height:auto; border-radius:10px;" />'
            % (html.escape(url, quote=True), html.escape(alt, quote=True)))


def render_box(accent, inner_blocks, link_color):
    border = "border:1px solid %s;" % THEME["box_border"]
    if accent == "teal":
        border += " border-left:6px solid %s;" % THEME["teal"]
    elif accent == "pink":
        border += " border-left:6px solid %s;" % THEME["pink"]
    inner = render_blocks(inner_blocks, link_color, indent="      ")
    return (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%%" '
        'style="background-color:%s; %s border-radius:10px;">\n'
        '  <tr>\n'
        '    <td style="padding: 12px 14px;">\n'
        '%s\n'
        '    </td>\n'
        '  </tr>\n'
        '</table>' % (THEME["box_bg"], border, inner)
    )


def render_blocks(blocks, link_color, indent=""):
    out = []
    prev = None
    for b in blocks:
        gap = gap_between(prev, b)
        if gap:
            out.append(spacer(gap))
        t = b["type"]
        if t == "heading":
            out.append(render_heading(b["level"], b["text"], link_color))
        elif t == "para":
            out.append(render_para(b["text"], link_color))
        elif t == "list":
            out.append(render_list(b["items"], link_color))
        elif t == "box":
            out.append(render_box(b["accent"], b["blocks"], link_color))
        elif t == "button":
            out.append(render_button(b["color"], b["label"], b["url"]))
        elif t == "hr":
            out.append(render_hr())
        elif t == "image":
            out.append(render_image(b["url"], b["alt"]))
        prev = b
    body = "\n".join(out)
    if indent:
        body = "\n".join(indent + ln if ln else ln for ln in body.split("\n"))
    return body


# ------------------------------------------------------------- document -----

HEAD = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <style>
      body {{ margin: 0; padding: 0; background-color: {page_bg}; }}
      img {{ border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
      table {{ border-collapse: collapse; }}
      a {{ color: {teal}; }}
      .container {{ max-width: 640px; }}
      @media only screen and (max-width: 680px) {{
        .container {{ width: 100% !important; }}
        .pad {{ padding: 16px !important; }}
        .h1 {{ font-size: 22px !important; line-height: 30px !important; }}
        .h2 {{ font-size: 18px !important; line-height: 26px !important; }}
        .btn a {{ display: block !important; width: 100% !important; box-sizing: border-box !important; }}
      }}
    </style>
  </head>
  <body>
"""


def build(meta, body_html):
    link_color = meta.get("link_color") or THEME["link"]
    parts = [HEAD.format(title=html.escape(meta["title"], quote=False),
                         page_bg=THEME["page_bg"], teal=THEME["teal"])]

    if meta.get("preheader"):
        parts.append(
            '    <div style="display:none; max-height:0; overflow:hidden; '
            'mso-hide:all; font-size:1px; line-height:1px; color:%s;">%s</div>\n'
            % (THEME["page_bg"], html.escape(meta["preheader"], quote=False))
        )

    parts.append(
        '    <table border="0" cellpadding="0" cellspacing="0" height="100%%" width="100%%" '
        'style="background-color:%s;">\n'
        '      <tr>\n'
        '        <td align="center" valign="top" style="padding: 24px 12px;">\n'
        '          <table border="0" cellpadding="0" cellspacing="0" width="640" class="container" '
        'style="width:640px; max-width:640px;">\n' % THEME["page_bg"]
    )

    # Banner
    if meta.get("banner"):
        parts.append(
            '            <!-- Banner image -->\n'
            '            <tr>\n'
            '              <td align="center" valign="top" style="padding:0; background-color:%s; '
            'border-radius: 12px 12px 0 0;">\n'
            '                <img src="%s" width="640" alt="%s" style="display:block; width:100%%; '
            'max-width:640px; height:auto; border-radius: 12px 12px 0 0;" />\n'
            '              </td>\n'
            '            </tr>\n'
            % (THEME["header_bg"], html.escape(meta["banner"], quote=True),
               html.escape(meta["banner_alt"], quote=True))
        )

    # Header bar
    header = ['            <!-- Header bar -->\n'
              '            <tr>\n'
              '              <td align="left" valign="top" class="pad" '
              'style="padding: 18px 22px; background-color:%s;">\n' % THEME["header_bg"]]
    if meta.get("eyebrow"):
        header.append(
            '                <div style="color:%s; font-family: %s; font-size:12px; '
            'letter-spacing:0.4px; text-transform:uppercase;">%s</div>\n'
            % (THEME["eyebrow"], FONT, html.escape(meta["eyebrow"], quote=False))
        )
    header.append(
        '                <div class="h1" style="margin-top:8px; color:%s; font-family: %s; '
        'font-size:26px; line-height:34px; font-weight:bold;">%s</div>\n'
        % (THEME["headline"], FONT, html.escape(meta["headline"], quote=False))
    )
    if meta.get("subhead"):
        header.append(
            '                <div style="margin-top:8px; color:%s; font-family: %s; '
            'font-size:14px; line-height:22px;">%s</div>\n'
            % (THEME["subhead"], FONT, inline(meta["subhead"], link_color))
        )
    header.append('              </td>\n            </tr>\n')
    parts.append("".join(header))

    # Accent strip
    parts.append(
        '            <!-- Accent strip -->\n'
        '            <tr>\n'
        '              <td style="padding:0; background-color:%s;">\n'
        '                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%%">\n'
        '                  <tr>\n'
        '                    <td style="height:6px; line-height:6px; background-color:%s; font-size:0;">&nbsp;</td>\n'
        '                  </tr>\n'
        '                </table>\n'
        '              </td>\n'
        '            </tr>\n' % (THEME["body_bg"], THEME["teal"])
    )

    # Main body
    indented = "\n".join("                " + ln if ln else ln
                         for ln in body_html.split("\n"))
    parts.append(
        '            <!-- Main body -->\n'
        '            <tr>\n'
        '              <td align="left" valign="top" class="pad" '
        'style="padding: 22px; background-color:%s;">\n%s\n'
        % (THEME["body_bg"], indented)
    )

    # Footer / unsubscribe
    footer_lines = ""
    if meta.get("footer_address"):
        footer_lines = ('<div style="color:%s; font-family: %s; font-size:12px; '
                        'line-height:18px; margin-bottom:6px;">%s</div>'
                        % (THEME["text"], FONT,
                           inline(meta["footer_address"], link_color)))
    parts.append(
        '                <div style="height:18px; line-height:18px;">&nbsp;</div>\n'
        '                <!-- Footer / unsubscribe -->\n'
        '                <table role="presentation" border="0" cellpadding="0" cellspacing="0" '
        'width="100%%" style="background-color:%s; border-radius: 10px;">\n'
        '                  <tr>\n'
        '                    <td align="center" style="padding: 14px;">\n'
        '                      %s<div style="color:%s; font-family: %s; font-size: 12px; line-height:18px;">\n'
        '                        <a href="%s" style="color:%s; font-family: %s; font-size: 12px; '
        'text-decoration: underline;">Unsubscribe</a>\n'
        '                      </div>\n'
        '                    </td>\n'
        '                  </tr>\n'
        '                </table>\n'
        '              </td>\n'
        '            </tr>\n'
        % (THEME["page_bg"], footer_lines, THEME["text"], FONT,
           meta["unsubscribe"], THEME["text"], FONT)
    )

    # Bottom rounding + tiny footer
    parts.append(
        '            <!-- Bottom rounding -->\n'
        '            <tr>\n'
        '              <td style="background-color:%s; border-radius: 0 0 12px 12px; height: 12px; '
        'line-height: 12px;">&nbsp;</td>\n'
        '            </tr>\n'
        '            <!-- Tiny footer -->\n'
        '            <tr>\n'
        '              <td align="center" style="padding-top:10px; color:%s; font-family: %s; '
        'font-size: 11px; line-height:16px;">\n'
        '                %s\n'
        '              </td>\n'
        '            </tr>\n'
        '          </table>\n'
        '        </td>\n'
        '      </tr>\n'
        '    </table>\n'
        '  </body>\n'
        '</html>\n'
        % (THEME["body_bg"], THEME["tiny_footer"], FONT,
           html.escape(meta["footer_org"], quote=False))
    )
    return "".join(parts)


def render_markdown_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    meta, body = parse_front_matter(text)
    link_color = meta.get("link_color") or THEME["link"]
    blocks = tokenize(body)
    if not blocks:
        print("warning: no content blocks found in %s" % path, file=sys.stderr)
    return build(meta, render_blocks(blocks, link_color))


def main():
    ap = argparse.ArgumentParser(
        description="Build an RFMC-MV HTML email newsletter from Markdown.")
    ap.add_argument("source", help="Markdown content file")
    ap.add_argument("-o", "--output", help="output HTML file "
                                          "(default: same name with .html)")
    args = ap.parse_args()

    out = args.output or os.path.splitext(args.source)[0] + ".html"
    html_doc = render_markdown_file(args.source)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html_doc)
    print("wrote %s (%d bytes)" % (out, len(html_doc)))


if __name__ == "__main__":
    main()
