# Applies twist 1 to Pope's integrated culture decisions: studying a foreign
# tree only needs one pop of a culture in that tree's culture group.
import re, sys
src, dst = sys.argv[1], sys.argv[2]
raw = open(src, 'rb').read()
t = raw.decode('utf-8-sig')
nl = '\r\n' if '\r\n' in t else '\n'
t = t.replace('\r\n', '\n')
allow_re = re.compile(r'''scope:target_culture = \{\s*custom_tooltip = \{\s*text = tradition_unlock_requirement_\w+\s*is_integrated = yes\s*num_pops_same_group_mil_trads >= percent_size_culture_group_comparison\s*(is_\w+_culture_group_trigger) = yes\s*\}\s*\}''')
t, n1 = allow_re.subn(lambda m: (
    "custom_tooltip = {\n"
    "\t\t\t\ttext = mlft_tradition_unlock_one_pop_tt\n"
    "\t\t\t\tany_country_culture = {\n"
    f"\t\t\t\t\t{m.group(1)} = yes\n"
    "\t\t\t\t\tcountry_culture_pop_count >= 1\n"
    "\t\t\t\t}\n"
    "\t\t\t}"), t)
pot_re = re.compile(r'(scope:target_culture = \{\n)\t\t\t\tis_integrated = yes\n(\t\t\t\tis_\w+_culture_group_trigger\s*= yes)')
t, n2 = pot_re.subn(r'\1\2', t)
print(f"allow blocks patched: {n1}, potential blocks patched: {n2}")
assert n1 == 13 and n2 == 13, "unexpected structure - check the source file"
assert t.count('{') == t.count('}'), f"brace mismatch {t.count('{')} vs {t.count('}')}"
open(dst, 'wb').write(b'\xef\xbb\xbf' + t.replace('\n', nl).encode('utf-8'))
