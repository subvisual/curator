"""Markdown inspection only: no fetching, rendering, or execution of input."""
from __future__ import annotations

import posixpath
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

PARSER = MarkdownIt("commonmark").enable("table")


def diagnostic(category, path, message, line=None):
    return {"category": category, "path": path, "line": line, "message": message}


def snapshot(root: Path):
    if not root.is_dir() or root.is_symlink():
        raise OSError("Content root must be an existing regular directory")
    files, unsafe = {}, set()
    # Path.walk does not follow symlink directories; explicitly classify them too.
    for parent, dirs, names in root.walk(follow_symlinks=False):
        dirs[:] = sorted(d for d in dirs if not (parent == root and d == '.git'))
        for name in sorted(names):
            path = parent / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                unsafe.add(rel)
            elif path.is_file():
                files[rel] = path.read_bytes()
            else:
                raise OSError(f"Cannot inspect non-regular file: {rel}")
    return files, unsafe


def markdown_paths(files):
    return sorted(p for p in files if p.lower().endswith('.md') and not p.startswith('checks/tests/'))


def local_target(source, destination, *, within=None):
    """Return (normalized repo path, fragment), or None for external URLs."""
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc:
        return None
    raw = unquote(parsed.path)
    if '\\' in raw or '\x00' in raw:
        raise ValueError("Unsupported or unsafe local path")
    if raw:
        path = posixpath.normpath(raw.lstrip('/') if raw.startswith('/')
                                 else posixpath.join(posixpath.dirname(source), raw))
    else:
        path = source
    if path == '..' or path.startswith('../'):
        raise ValueError("Reference escapes the repository")
    if within and not path.startswith(within + '/'):
        raise ValueError("Evidence reference escapes its submission directory")
    return path, unquote(parsed.fragment)


class HTMLReferences(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors, self.links = set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.anchors.add(attrs['id'])
        if tag == 'a' and attrs.get('name'):
            self.anchors.add(attrs['name'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def slug(text):
    # GitHub strips punctuation/symbols, preserves letters/numbers/marks, _ and -.
    text = text.lower()
    return ''.join('-' if c == ' ' else c for c in text
                   if c in ' _-' or unicodedata.category(c)[0] in 'LNM')


def inspect_markdown(text):
    tokens = PARSER.parse(text)
    links, anchors, statuses = [], set(), []
    used = set()
    section_line = None
    html = HTMLReferences()
    for index, token in enumerate(tokens):
        line = token.map[0] + 1 if token.map else None
        if token.type == 'heading_open':
            if token.tag != 'h1' and section_line is None:
                section_line = line
            children = tokens[index + 1].children or []
            visible = ''.join(t.content for t in children if t.type in ('text', 'code_inline', 'image'))
            base = slug(visible)
            anchor, suffix = base, 0
            while anchor in used:
                suffix += 1
                anchor = f'{base}-{suffix}'
            used.add(anchor)
            anchors.add(anchor)
        if token.type == 'html_block':
            html.feed(token.content)
        if token.type != 'inline':
            continue
        # Require a plain visible status line, not text inside code, a link, or HTML.
        visible = ''.join(child.content if child.type == 'text' else
                          '\n' if child.type in {'softbreak', 'hardbreak'} else '\ufffd'
                          for child in token.children or [])
        for offset, raw in enumerate(visible.splitlines()):
            if re.fullmatch(r'Status: [A-Za-z-]+\s*', raw):
                statuses.append((raw.strip().split(': ', 1)[1], (line or 1) + offset))
        for child in token.children or []:
            if child.type == 'link_open':
                links.append((child.attrGet('href'), line))
            elif child.type == 'image':
                links.append((child.attrGet('src'), line))
            elif child.type == 'html_inline':
                html.feed(child.content)
    anchors.update(html.anchors)
    links.extend((dest, None) for dest in html.links)
    return links, anchors, statuses, section_line


def check_status(files, originals):
    errors = []
    for path in markdown_paths(files):
        if path in {'CLAUDE.md', '.github/pull_request_template.md'} or path in originals:
            continue
        _, _, statuses, section = inspect_markdown(files[path].decode('utf-8'))
        allowed = {'evidence'} if path.startswith('evidence/') else {'current', 'superseded', 'template'}
        if (len(statuses) != 1 or statuses[0][0] not in allowed
                or (section is not None and statuses[0][1] >= section)):
            errors.append(diagnostic('document-status', path,
                'Add exactly one early visible Status: ' + '|'.join(sorted(allowed)) + ' line.',
                statuses[0][1] if statuses else None))
    return errors


def check_links(files, unsafe, evidence_links=(), originals=()):
    errors, anchors = [], {}
    references = list(evidence_links)
    directories = {parent.as_posix() for p in files for parent in Path(p).parents}
    for path in markdown_paths(files):
        # Originals may describe their original filesystem, not this repository.
        if path in originals:
            continue
        links, ids, _, _ = inspect_markdown(files[path].decode('utf-8'))
        anchors[path] = ids
        references.extend((path, dest, line, None) for dest, line in links)
    for source, destination, line, within in references:
        try:
            target = local_target(source, destination, within=within)
            if target is None:
                continue
            path, fragment = target
            if within and path not in files:
                raise ValueError('Missing retained evidence file: ' + path)
            if path not in files and path not in directories and path != '.':
                raise ValueError('Missing repository file or directory: ' + path)
            if path in unsafe:
                raise ValueError('Reference uses a symlink: ' + path)
            if fragment and path.lower().endswith('.md') and path in files:
                if path not in anchors:
                    anchors[path] = inspect_markdown(files[path].decode('utf-8'))[1]
                if fragment not in anchors[path]:
                    raise ValueError(f'Missing section #{fragment} in {path}')
        except ValueError as error:
            errors.append(diagnostic('internal-references', source, str(error), line))
    for path in sorted(unsafe):
        errors.append(diagnostic('internal-references', path, 'Symlinks cannot be resolved as repository evidence.'))
    return errors
