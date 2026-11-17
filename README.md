# huge_multiplayer_overhaul_invictus

Bridges the gap between Invictus and the multiplayer features and balance from HMO.

Published on Steam as **Molon Labe Invictus SubMod – Foreign Traditions** ([Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3830831474)).

A submod for **Imperator: Invictus** that rebalances the military and reshapes the map. Foreign military traditions are easier and cheaper to reach but much weaker than your own, so borrowing from your neighbours becomes a flavour choice rather than the best build. Military tech no longer inflates morale. Every nation starts independent, with at most one province and without legions, and a new mission tree lets each people fight to unite its homeland.

**Current version: 1.9**

Built on the **Molon Labe Invictus SubMod by Pope**, which is included, so you don't need to run both.

## Features
- **Study foreign ways of war with a single pop.** The "Study … Ways of War" culture decisions no longer need the culture to be integrated or a large pop share. Owning at least one pop of a culture in that tradition's culture group is enough. The cost is halved: −13 stability, −90 military experience and −100 political influence (you need 90 military experience to take it). You still need 10 territories and more than 40 stability.
- **Foreign traditions work at 25% strength.** Every tradition that is not from your primary culture's own tree gets a counter-modifier worth −75% of its values. A foreign +10% discipline gives you +2.5%. Each penalty appears in your country modifiers as "Foreign Tradition: <name>".
- **Follows your primary culture.** If you change primary culture, your old tree's traditions take the penalty and the new tree's traditions return to full strength automatically.
- **No morale from military tech.** Advancing military technology no longer adds land or naval morale (the base game gave +0.075 per level).
- **One Province Nations.** Every nation starts with at most one province. Each nation keeps the province its capital is in, and every other province it held becomes a new independent nation, about 1,500 nations in total. New nations take their culture and religion from their pops and their government and tech from their old owner, and they are named after their capital.
- **No subjects at start.** All starting feudatories, satrapies, tributaries, client states, vassal tribes and temple states begin as independent nations.
- **No legions at start.** No nation starts with a legion or with a military law that allows recruiting one. The Diadochi kingdoms now start on "Recruit from Nobles" instead of "Work for the Best", so everyone has to change military law before raising legions. Mission rewards that used to hand out a free legion (Parthian satrapy, Argyraspides, Hamilcar, Magas of Cyrene) now give manpower instead, about 1,000 men for every cohort the legion would have had.
- **Unify Your Home Lands.** A new mission tree, suggested by Nabber, for every independent nation whose people still live in territories it does not own. When you start it, every territory of your capital's region where the culture of your capital holds the majority becomes your homeland, so a Macedonian Bactria unites Bactria and Carthage unites its corner of Africa rather than the whole Hellenistic or Punic world. If your capital's people have nothing left to unite in the region, your primary culture is used instead. Claim it all, conquer it step by step (25%, 50%, 75%, 90%), win over any nation as ally or subject and build up your capital. Finishing it grants a permanent *Homeland United* bonus. The AI uses it too, but historical mission trees are preferred wherever they are available. Almost every nation has at least one mission at start; the few exceptions already rule every territory of their people.
- **No Wars of the Diadochi event.** The Invictus start event "The Wars of the Diadochi" no longer fires for the Antigonids, Macedon, Thrace, Egypt or the Seleukids. That removes its scripted war chain (Egypt, the Seleukids and Thrace declaring war on the Antigonids, the Macedonian war choice and the ultimatums), the Legacy of Alexander claims it handed out, and the Diadochi province-flipping that depended on it. The Diadochi now fight only the wars their players or the AI choose.
- **No Threaten War.** The "Threaten War" diplomatic action is gone from the diplomacy window in every game language, so territory changes hands only through real wars. As a safety net the AI also always refuses it.
- **Independent Cyrene.** Cyrene's first Magas mission ("A Governor for Cyrenaica") no longer makes Cyrene a feudatory of Egypt. Magas still arrives from the Ptolemaic court and takes the throne, but Cyrene stays independent and gains +10 stability and +15 legitimacy instead.
- **15-year truces.** Every peace deal now gives a flat 15-year truce, whatever the warscore (vanilla: 3 years plus up to 5 more for a decisive peace).
- **Open granaries for allies.** Ported from **HMO: Huge Multiplayer Overhaul**. While you are at war, player armies of your allies, subjects and overlord standing in your provinces are fed from your province food stores every month: unit size ÷ 5 + 5 food, as long as the province has that much and at least 10 food. AI armies don't take your food.
- **Vegetables move tribesmen too.** Ported from **HMO: Huge Multiplayer Overhaul**. A vegetables surplus now makes moving tribesmen 25% cheaper as well as slaves (Invictus: slaves only).
- **Less commerce for large empires.** Late-game money inflation comes from commerce, not tax, so large empires lose commerce income: Major Powers −15% commerce, Great Powers −25% commerce and −5% tax. Ported from **HMO: Huge Multiplayer Overhaul**: recruiting mercenaries costs +200% for Major and +300% for Great Powers. Regional Powers are untouched, since by mid-game almost every nation is one. Every other rank bonus is unchanged.
- **Levy experience.** Ported from **HMO: Huge Multiplayer Overhaul** (by x8). A levy remembers its experience when it is raised. Disband it with a governorship's disband button or the *Disband All Levies* button and you get military experience for what it gained since: 7.5% of the gain in experience points, up to 10 per levy. Only levies led by a governor or the ruler pay out. The game itself decides which armies are levies, so armies granted by missions or events are never disbanded. The vanilla flat disband experience is gone.
- **Levy veterans.** While your military law does not allow legions, experience decay drops from 4.5% to about 0.5% a month, so starting experience sticks and levies are much stronger. The trade-off: since only experience gained above the starting value counts, these levies give less military experience when disbanded. Enacting a legion law removes the bonus.
- **Faster auto-trade.** Once a month, every state of a player that has automated trading switched on fills its free trade routes with goods it does not have yet. Foreign imports earn commerce and trading with yourself does not, so it buys abroad first, from the AI nations that like you best: allies, subjects and your overlord, then nations with great relations (opinion 80+), then good relations (40+), then anyone who does not dislike you, nearest region first. Only if no foreign seller is found does it import from your own states. It never sells away the surplus your capital needs for its capital bonus, never imports from other players (they decide their own exports) and never from AI nations at war with you or that dislike you. AI nations keep the normal game behaviour.
- **Molon Labe changes by Pope:** his reworked integrated-culture decisions.

## Good to know
- Unify Your Home Lands claims now count for declaring war straight away. The game has an old bug where claims given by a script show up on the map but the Declare War screen still says "War without Casus Belli" until you queue and cancel a building; the mission now does that refresh for you. Older claims from other missions or events may still need the manual trick.
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
- Also replaces Invictus's *events/dhe/dhe_diadochi.txt* to switch off the Wars of the Diadochi start event. Mods that change the Diadochi events will conflict.
- Also replaces Invictus's *gui/military_view.gui* (adds the levy-experience hooks to the Raise / Disband Levies buttons). UI mods that change the military window will conflict.
- Also replaces Invictus's *gui/diplomatic_view.gui* (hides the Threaten War button) and *common/ai_diplochance/00_default.txt* (AI always refuses Threaten War), and sets the Threaten War title to the same text in all languages. UI mods that change the diplomacy window will conflict.
- Also replaces Invictus's *events/mission_events/me_cyr_magas_events.txt* (Cyrene no longer becomes Egypt's feudatory). Mods that change the Cyrene Magas events will conflict.
- Also overrides the *vegetables* trade good (in *common/trade_goods/zz_mltg_trade_goods.txt*; the rest of Invictus's trade goods file is untouched). Mods that change the vegetables trade good will conflict.
- Also overrides the Major and Great Power rank modifiers (*nation_rank_4/5* in *common/modifiers/zz_mlrk_rank_modifiers.txt*). Mods that change rank modifiers will conflict.
- Does not change any Invictus military tradition file, so tradition overhauls will still load, although their new traditions won't get a penalty until this mod is updated.
- One Province Nations needs a **new game**. The other features are safe to add to an existing save, and tradition penalties appear within the first month.
- With about 1,500 nations and roughly 70% more characters than a normal Invictus start, the early game runs noticeably slower. Speed improves as nations are conquered and merged.

## Credits
Pope for the original Molon Labe Invictus SubMod, Nabber for the Unify Your Home Lands idea, the HMO: Huge Multiplayer Overhaul team for the allied food-sharing system, x8 for the levy experience system, and the Invictus team.

## Repository layout

- The repository root is the mod itself (`descriptor.mod`, `common/`, `events/`, `setup/`, …). Clone or copy it into `Documents/Paradox Interactive/Imperator/mod/` and point a `.mod` file at it to play-test.
- `tools/` holds development scripts and notes that are **not** part of the mod: the generators/patchers (`generate_tradition_malus.py`, `patch_culture_decisions.py`, `patch_mission_legions.py`, `province_split/`), changenotes, the Workshop description, and removed features kept for reference. Exclude it when uploading to the Workshop.
