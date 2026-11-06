# huge_multiplayer_overhaul_invictus

Bridges the gap between Invictus and the multiplayer features and balance from HMO.

Published on Steam as **Molon Labe Invictus SubMod – Foreign Traditions** ([Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3830831474)).

A submod for **Imperator: Invictus** that rebalances the military and reshapes the map. Foreign military traditions are easier and cheaper to reach but much weaker than your own, so borrowing from your neighbours becomes a flavour choice rather than the best build. Military tech no longer inflates morale. Every nation starts independent, with at most one province and without legions, and a new mission tree lets each people fight to unite its homeland.

**Current version: 1.2**

Built on the **Molon Labe Invictus SubMod by Pope**, which is included, so you don't need to run both.

## Features
- **Study foreign ways of war with a single pop.** The "Study … Ways of War" culture decisions no longer need the culture to be integrated or a large pop share. Owning at least one pop of a culture in that tradition's culture group is enough. The cost is halved: −13 stability, −90 military experience and −100 political influence (you need 90 military experience to take it). You still need 10 territories and more than 40 stability.
- **Foreign traditions work at 25% strength.** Every tradition that is not from your primary culture's own tree gets a counter-modifier worth −75% of its values. A foreign +10% discipline gives you +2.5%. Each penalty appears in your country modifiers as "Foreign Tradition: <name>".
- **Follows your primary culture.** If you change primary culture, your old tree's traditions take the penalty and the new tree's traditions return to full strength automatically.
- **No morale from military tech.** Advancing military technology no longer adds land or naval morale (the base game gave +0.075 per level).
- **One Province Nations.** Every nation starts with at most one province. Each nation keeps the province its capital is in, and every other province it held becomes a new independent nation, about 1,500 nations in total. New nations take their culture and religion from their pops and their government and tech from their old owner, and they are named after their capital.
- **No subjects at start.** All starting feudatories, satrapies, tributaries, client states, vassal tribes and temple states begin as independent nations.
- **No legions at start.** No nation starts with a legion or with a military law that allows recruiting one. The Diadochi kingdoms now start on "Recruit from Nobles" instead of "Work for the Best", so everyone has to change military law before raising legions. Mission rewards that used to hand out a free legion (Parthian satrapy, Argyraspides, Hamilcar, Magas of Cyrene) now give manpower instead, about 1,000 men for every cohort the legion would have had.
- **Unify Your Home Lands.** A new mission tree, suggested by Nabber, for every independent nation that borders a territory where its primary culture is the majority. When you start it, every territory where your culture holds the majority becomes your homeland. Claim it all, conquer it step by step (25%, 50%, 75%, 90%), win over a kin nation as ally or subject and build up your capital. Finishing it grants a permanent *Homeland United* bonus. The AI uses it too, but historical mission trees are preferred wherever they are available.
- **Open granaries for allies.** Ported from **HMO: Huge Multiplayer Overhaul**. While you are at war, player armies of your allies, subjects and overlord standing in your provinces are fed from your province food stores every month: unit size ÷ 5 + 5 food, as long as the province has that much and at least 10 food. AI armies don't take your food.
- **Molon Labe changes by Pope:** disbanding levies no longer gives military experience, plus his reworked integrated-culture decisions.

## Good to know
- Tradition penalties refresh once a month, so after picking a tradition or changing culture it can take up to 30 days for them to update.
- Only numbers are reduced. Unit unlocks (octeres, mega galleys and so on) and combat tactics from foreign traditions still work in full.
- A tree counts as "your own" under the same rules Invictus uses to give you it at game start, including its special cases (e.g. Carthage, Cyrene, Bosporan heritages). Trees unlocked through missions count as foreign.
- Works with AI countries too.

## Compatibility
- Requires **Imperator: Invictus**. Load this mod **after** Invictus.
- Replaces Invictus's *culture_decisions/integrated_culture_decisions_inv.txt*. Other mods that change that file or the "Study … Ways of War" decisions will conflict.
- Also replaces the base game's *common/technology_tables/0_martial_table.txt*. Mods that change military tech will conflict.
- Also replaces Invictus's *setup/main/00_default.txt* and *setup/countries/countries.txt*, and overrides Invictus's six Diadochi legion setup effects. Other mods that change the 304 BC start (who owns what, subjects, starting legions) will conflict.
- Also replaces Invictus's *decisions/tier_1_formables/form_thessalian_league.txt* and *common/missions/02_tylos_missions.txt* (small error fixes), and empties Invictus's *setup/characters/00_KIO.txt* and *00_STP.txt* (leftover empty files for nations Invictus removed). Mods that change the Thessalian League or the Tylos missions will conflict.
- Also replaces five Invictus event files to swap mission legions for manpower: *events/flavor_egy.txt*, *events/dhe/dhe_carthage.txt*, *me_parthia_satrapy.txt*, *me_diadochi_empire.txt* and *me_carthage_iberian_investments.txt*. Mods that change those events will conflict.
- Does not change any Invictus military tradition file, so tradition overhauls will still load, although their new traditions won't get a penalty until this mod is updated.
- One Province Nations needs a **new game**. The other features are safe to add to an existing save, and tradition penalties appear within the first month.
- With about 1,500 nations at start, the early game will run slower than normal Invictus.

## Credits
Pope for the original Molon Labe Invictus SubMod, Nabber for the Unify Your Home Lands idea, the HMO: Huge Multiplayer Overhaul team for the allied food-sharing system, and the Invictus team.

## Repository layout

- The repository root is the mod itself (`descriptor.mod`, `common/`, `events/`, `setup/`, …). Clone or copy it into `Documents/Paradox Interactive/Imperator/mod/` and point a `.mod` file at it to play-test.
- `tools/` holds development scripts and notes that are **not** part of the mod: the generators/patchers (`generate_tradition_malus.py`, `patch_culture_decisions.py`, `patch_mission_legions.py`, `province_split/`), changenotes, the Workshop description, and removed features kept for reference. Exclude it when uploading to the Workshop.
