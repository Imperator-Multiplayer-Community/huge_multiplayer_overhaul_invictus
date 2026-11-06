"""Minimal Paradox-script tokenizer/parser that keeps character offsets."""
import re
TOK = re.compile(r'#[^\n]*|"(?:[^"\\]|\\.)*"|[{}=<>]|[^\s{}=<>#"]+')

def tokens(text):
    for m in TOK.finditer(text):
        t = m.group()
        if t.startswith('#'):
            continue
        yield t, m.start(), m.end()

class Node:
    __slots__ = ('key', 'val', 'start', 'end', 'vstart', 'vend')
    def __init__(s, key, val, start, end, vstart, vend):
        s.key, s.val, s.start, s.end, s.vstart, s.vend = key, val, start, end, vstart, vend
    def get(s, k):
        if isinstance(s.val, list):
            for n in s.val:
                if isinstance(n, Node) and n.key == k:
                    return n
    def all(s, k):
        return [n for n in s.val if isinstance(n, Node) and n.key == k] if isinstance(s.val, list) else []
    def scalars(s):
        return [x for x in s.val if not isinstance(x, Node)] if isinstance(s.val, list) else []

def parse(text):
    toks = list(tokens(text))
    i = 0
    def block():
        nonlocal i
        items = []
        while i < len(toks):
            t, a, b = toks[i]
            if t == '}':
                return items
            if i + 1 < len(toks) and toks[i+1][0] in ('=', '<', '>'):
                key, ks = t, a
                i += 2
                v, va, vb = toks[i]
                if v == '{':
                    i += 1
                    inner = block()
                    ve = toks[i][2]  # closing brace
                    items.append(Node(key, inner, ks, ve, va, ve))
                    i += 1
                else:
                    items.append(Node(key, v.strip('"'), ks, vb, va, vb))
                    i += 1
            elif t == '{':
                i += 1
                inner = block()
                ve = toks[i][2]
                items.append(Node(None, inner, a, ve, a, ve))
                i += 1
            else:
                items.append(t.strip('"'))
                i += 1
        return items
    return Node('root', block(), 0, len(text), 0, len(text))

def read(path):
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        return f.read()
