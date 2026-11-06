#!/usr/bin/env python3
"""
Generates the foreign-tradition malus files for the
"Molon Labe Invictus Submod - Foreign Traditions" mod.

Usage:
    python3 generate_tradition_malus.py <invictus common/military_traditions dir> <mod root dir> [malus]

Re-run it after every Invictus update that touches military traditions.
Outputs (all overwritten):
    common/modifiers/zz_mlft_tradition_malus_modifiers.txt
    common/scripted_triggers/zz_mlft_native_tree_triggers.txt
    common/scripted_effects/zz_mlft_tradition_malus_effects.txt
    localization/english/zz_mlft_tradition_malus_l_english.yml
"""
import os, re, sys

MALUS = 0.75
NATIVE_TOOLTIPS = {"began_with_tradition_group", "is_cyr.tt"}

# Some Invictus traditions use vanilla script values instead of numbers
# (e.g. global_slaves_output = output_large_svalue). Those values live in the
# base game's common/script_values, which this script cannot see. Fill in the
# numbers here (copy them from the base game) and re-run; any script value not
# listed is left unpenalised and reported at the end.
SVALUES = {
    # "output_large_svalue": 0.0,
    # "happiness_large_svalue": 0.0,
    # "happiness_huge_svalue": 0.0,
    # "wrong_culture_large": 0.0,
    # "wrong_culture_group_large": 0.0,
}

# ---------------------------------------------------------------- parser
TOKEN_RE = re.compile(r'"[^"]*"|[{}]|[<>!=]=|[<>=]|[^\s{}<>=!"]+')

def tokenize(text):
    out = []
    for line in text.splitlines():
        # strip comments (outside quotes)
        res, q = [], False
        for ch in line:
            if ch == '"': q = not q
            if ch == '#' and not q: break
            res.append(ch)
        out.extend(TOKEN_RE.findall(''.join(res)))
    return out

def parse(tokens, i=0):
    """returns (list of (key, op, value), next index); value is str or list"""
    items = []
    while i < len(tokens):
        t = tokens[i]
        if t == '}':
            return items, i + 1
        if t == '{':                       # anonymous block / list
            v, i = parse(tokens, i + 1)
            items.append((None, None, v)); continue
        if i + 1 < len(tokens) and tokens[i + 1] in ('=', '<', '>', '<=', '>=', '!=', '=='):
            op = tokens[i + 1]; i += 2
            if tokens[i] == '{':
                v, i = parse(tokens, i + 1)
            elif i + 1 < len(tokens) and tokens[i + 1] == '{' and tokens[i] in ('hsv', 'rgb', 'hsv360'):
                v, i = parse(tokens, i + 2); v = [('__color__', tokens[i], v)]
            else:
                v = tokens[i]; i += 1
            items.append((t, op, v))
        else:
            items.append((t, None, None)); i += 1
    return items, i

def dump(items, ind=1):
    s = []
    for k, op, v in items:
        pad = '\t' * ind
        if k is None and isinstance(v, list):
            s.append(pad + '{\n' + dump(v, ind + 1) + pad + '}\n')
        elif op is None:
            s.append(pad + k + '\n')
        elif isinstance(v, list):
            s.append(f'{pad}{k} {op} {{\n' + dump(v, ind + 1) + pad + '}\n')
        else:
            s.append(f'{pad}{k} {op} {v}\n')
    return ''.join(s)

def get(items, key):
    for k, op, v in items:
        if k == key: return v
    return None

def num(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def fmt(x):
    s = f"{x:.5f}".rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

# ---------------------------------------------------------------- main
def main():
    src, mod = sys.argv[1], sys.argv[2]
    malus = float(sys.argv[3]) if len(sys.argv) > 3 else MALUS
    trees = []          # (tree_key, native_conditions, [(trad, {mod: val}, [skipped])])
    seen = {}
    for fn in sorted(os.listdir(src)):
        if not fn.endswith('.txt'): continue
        items, _ = parse(tokenize(open(os.path.join(src, fn), encoding='utf-8-sig').read()))
        for tree_key, _, body in items:
            if not isinstance(body, list): continue
            allow = get(body, 'allow') or []
            native = []
            for bk, _, bv in allow:
                if bk not in ('trigger_if', 'trigger_else_if') or not isinstance(bv, list): continue
                tips = [get(x[2], 'text') for x in bv if x[0] == 'custom_tooltip' and isinstance(x[2], list)]
                tips = [t.strip('"') for t in tips if t]
                if not any(t in NATIVE_TOOLTIPS for t in tips): continue
                cond = [x for x in bv if x[0] not in ('custom_tooltip',)]
                lim = [x for x in cond if x[0] == 'limit']
                rest = [x for x in cond if x[0] != 'limit']
                block = (lim[0][2] if lim else []) + rest
                native.append(block)
            trads = []
            for tk, _, tv in body:
                if tk in ('allow', 'color', 'image') or not isinstance(tv, list): continue
                if get(tv, 'icon') is None and get(tv, 'requires') is None: continue
                mods, skipped = {}, []
                m = get(tv, 'modifier')
                if isinstance(m, list):
                    for mk, mop, mv in m:
                        n = num(mv)
                        if n is None and mv in SVALUES: n = SVALUES[mv]
                        if n is None or mk is None: skipped.append(f"{mk} = {mv}"); continue
                        mods[mk] = mods.get(mk, 0) + n
                if tk in seen:
                    print(f"WARNING: tradition {tk} defined in {seen[tk]} and {fn}")
                seen[tk] = fn
                trads.append((tk, mods, skipped))
            if not native:
                print(f"WARNING: no native branch found for {tree_key} ({fn}) - every owner will be penalised")
            trees.append((tree_key, native, trads))

    def w(rel, text, bom=True):
        p = os.path.join(mod, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='\n') as f: f.write(text)

    hdr = f"# GENERATED by generate_tradition_malus.py - do not edit by hand.\n# Malus = {int(malus*100)}% of each tradition's numeric modifiers.\n\n"

    # modifiers
    out = [hdr]
    n_mod = 0
    for tree, native, trads in trees:
        out.append(f"# ---- {tree}\n")
        for tk, mods, skipped in trads:
            if not mods: continue
            out.append(f"mlft_malus_{tk} = {{\n")
            for mk, v in mods.items():
                out.append(f"\t{mk} = {fmt(-v * malus)}\n")
            out.append("}\n")
            n_mod += 1
    w('common/modifiers/zz_mlft_tradition_malus_modifiers.txt', ''.join(out))

    # native triggers
    out = [hdr, "# Country scope. yes = this tree is the country's own (primary-culture) tree.\n\n"]
    for tree, native, trads in trees:
        out.append(f"mlft_is_native_tree_{tree} = {{\n")
        if native:
            out.append("\tOR = {\n")
            uniq = []
            for blk in native:
                d = []
                for x in blk:
                    if dump([x]) not in [dump([y]) for y in d]: d.append(x)
                txt = dump(d, 2) if len(d) == 1 else "\t\tAND = {\n" + dump(d, 3) + "\t\t}\n"
                if txt not in uniq: uniq.append(txt)
            out.extend(uniq)
            out.append("\t}\n")
        else:
            out.append("\talways = no\n")
        out.append("}\n\n")
    w('common/scripted_triggers/zz_mlft_native_tree_triggers.txt', ''.join(out))

    # effects
    out = [hdr, "# Country scope. Adds/removes one malus modifier per owned non-native tradition.\n",
           "mlft_refresh_tradition_malus_effect = {\n"]
    for tree, native, trads in trees:
        tr = [t for t in trads if t[1]]
        if not tr: continue
        out.append(f"\t# ---- {tree}\n\tif = {{\n\t\tlimit = {{ mlft_is_native_tree_{tree} = yes }}\n")
        for tk, _, _ in tr:
            out.append(f"\t\tif = {{ limit = {{ has_country_modifier = mlft_malus_{tk} }} remove_country_modifier = mlft_malus_{tk} }}\n")
        out.append("\t}\n\telse = {\n")
        for tk, _, _ in tr:
            out.append(
                f"\t\tif = {{\n\t\t\tlimit = {{ has_military_bonus = {tk} NOT = {{ has_country_modifier = mlft_malus_{tk} }} }}\n"
                f"\t\t\tadd_country_modifier = {{ name = mlft_malus_{tk} duration = -1 }}\n\t\t}}\n"
                f"\t\telse_if = {{\n\t\t\tlimit = {{ NOT = {{ has_military_bonus = {tk} }} has_country_modifier = mlft_malus_{tk} }}\n"
                f"\t\t\tremove_country_modifier = mlft_malus_{tk}\n\t\t}}\n")
        out.append("\t}\n")
    out.append("}\n")
    w('common/scripted_effects/zz_mlft_tradition_malus_effects.txt', ''.join(out))

    # localisation (modifier names reuse the tradition's own name)
    out = ["l_english:\n"]
    for tree, native, trads in trees:
        for tk, mods, _ in trads:
            if not mods: continue
            out.append(f' mlft_malus_{tk}:0 "Foreign Tradition: ${tk}$"\n')
            out.append(f' mlft_malus_{tk}_desc:0 "This tradition belongs to a foreign tree, so it only works at {100-int(malus*100)}% strength."\n')
    w('localization/english/zz_mlft_tradition_malus_l_english.yml', ''.join(out))

    print(f"trees={len(trees)} traditions={sum(len(t[2]) for t in trees)} malus_modifiers={n_mod}")
    for tree, native, trads in trees:
        for tk, mods, skipped in trads:
            if skipped: print(f"  non-numeric skipped in {tk}: {skipped}")
            if not mods: print(f"  no numeric modifier (unaffected): {tk}")

if __name__ == '__main__':
    main()
