# How blueberry production structures change weather exposure

Evidence memo for analogue transfer functions. Focus is University of Florida / southern highbush (SHB). Chile, Spain, Portugal, Japan, the Netherlands, Mississippi, and one China rain-shelter trial are included only where they measured something. Mexico and Australia appear in industry reviews; they do not have comparable measured tunnel weather papers here.

**Do not encode any of these as a binary 0/1 multiplier.** Plastic does not delete freeze, rain-crack, chill, heat, or disease. It changes the pathway.

Current encoder conflicts (`packages/analogue/blueberry_analogue/systems.py` + `features/cube.py`) are listed at the end.

Evidence tags: **measured** = same paper recorded the weather variable and a crop response; **expert** = UF/IFAS or review guidance without a paired trial number; **unknown** = no blueberry measurement found.

---

## 1. High tunnels / Haygrove / unheated polyethylene vs open field

### Bloom freeze / Tmin

Unheated plastic is not a frost machine. Night effect depends on film, volume, ventilation, and whether water or heat is added.

| Source | Year | What was measured |
|---|---|---|
| Santos & Salamé-Donoso, *Performance of Southern Highbush Blueberry Cultivars Under High Tunnels in Florida*, HortTechnology 22:700–704. DOI 10.21273/HORTTECH.22.5.700. Also EDIS HS1226. Waldo, FL; Haygrove 18 ft × 25 ft × 600 ft; 6-mil polyethylene, 35% light reduction; sides/roof **removed May–August**; ends closed 12–24 h before forecast freeze; both systems had sprinklers (open ~120 gal/min/acre, tunnel minisprinklers ~60 gal/min/acre), on at 34 °F. | 2012 | HOBO T at 3 ft. Open Tmin **~19 °F** (2009–10) and **~21 °F** (2010–11); tunnel Tmin **~32 °F** and **~33 °F**. Days ≤34 °F: **27 vs 2** then **34 vs 1**. Combined: 61 open near-freeze days vs 3 inside. Freeze-protection water **~1/10** of open (open ~2.5 acre-inch/acre per 8 h). |
| Ogden & van Iersel, *Southern Highbush Blueberry Production in High Tunnels…*, HortScience 44:1850–1856. DOI 10.21273/HORTSCI.44.7.1850. Watkinsville, GA; 6-mil K50 clear; propane heaters on nights expected <0 °C. | 2009 | Daytime Tmax **+3 to +15 °C**. Night Tmin **not raised**; often **1–5 °C below** outdoor. Easter 2007 outdoor fruit 100% lost at −5 °C; heated tunnels survived. 25 Mar 2008: heaters off because forecast was +3 °C; inside reached **−5 °C**; tagged fruit set failed. 3 Jan 2008: **−11 °C** unheated tunnel vs **−9 °C** outdoor. Long-wave-blocking film in south Georgia also failed to protect (Krewer et al. 2009, cited). |
| Ogden et al., *Leaf and bud temperatures of southern highbush blueberries inside high tunnels*, Acta Hortic. 893. DOI 10.17660/ActaHortic.2011.893.155. | 2011 | Daily **minimum leaf and bud temperatures lower** inside tunnels than outdoors. Frost blankets tried on 0 to −1 °C nights. |
| Li & Bi, *Container Production of Southern Highbush Blueberries Using High Tunnels*, HortScience 54:267–274. DOI 10.21273/HORTSCI13639-18. Starkville, MS; 6-mil clear; doors/curtains closed when outdoor <4.4 °C. | 2019 | Monthly Tmax **+3.2 to +10.4 °C**; monthly mean **+0.7 to +4.2 °C**; monthly Tmin **up to +3.0 °C** (not every month). On three Jan 2016 nights outdoor −6.7 to −5.6 °C, tunnel **−3.9 to −3.3 °C**. Jan 2017 outdoor −10.0 °C, tunnel **−7.0 °C**. Bloom/fruit of Emerald, Rebel, Meadowlark still frost-damaged in 2016. |
| Retamal-Salgado et al., *Influence of microclimatic conditions under high tunnels… ‘O’Neal’*, Chil. J. Agric. Res. 75. DOI 10.4067/S0718-58392015000400004. Biobío, Chile; 200 µm LDPE, 85% PAR rating; film 35 d before bloom, opened 60 DAFB. | 2015 | Tmax **+10 to +12 °C**. Tmin **+2 to +5 °C** (mean +2 °C during bloom/set). Open field hit ~0 °C **five times**; tunnel stayed above those events. |
| Williamson & Phillips, EDIS HS216 / HS968 *Protecting Blueberries from Freezes in Florida*. DOI 10.32473/edis-hs216-2004. | 2023 rev. | **Expert.** Tunnels can need **no water, or much less water**, than open field. Freeze protection is **still required** at times in central/south Florida and in tunnels. Pine bark beds can run **as much as 5 °F colder** at flower height on calm, low-dewpoint nights. |

**Encode:** freeze risk **reduced but not zero** unless heat is actually on. Closed Haygrove + water in north Florida can hold Tmin near 32 °F while the field is in the teens. The same class of unheated film in Georgia can be **colder** than the field. Multiplying frost-night counts by 0.1 (current `freeze_water_factor`) confuses **water volume** with **kill probability**.

### Harvest rainfall / fruit split (rain-crack)

Rain on the peel is the main split pathway. Root uptake still splits fruit under a cover.

| Source | Year | What was measured |
|---|---|---|
| Marshall et al., *Water Uptake Threshold of Rabbiteye…*, HortScience 44:2035–. DOI 10.21273/HORTSCI.44.7.2035. Cites Marshall 2001 cover trial. | 2009 | Covering plants so rain did **not** hit fruit did **not** eliminate split. After rain: uncovered **30.40%** split, covered **19.90%**. Residual attributed to **xylem supply from roots**. |
| Wei et al., *Effect of Rain-Shelter Cultivation… Container-Grown Rabbiteye…*, Plants 14:1167. DOI 10.3390/plants14081167. Nanjing; roof-only PE 0.10–0.12 mm, 75% transmittance; sides open; on from coloration to harvest. | 2025 | T and RH **unchanged** (open sides). PAR/UV-A/UV-B down **27 / 32 / 35%** on sunny days. Fruit drop and cracking **significantly lower** all three years; higher in wetter years (2020 718.8 mm, 2021 485.2 mm under film vs 2019 182.4 mm). Paper does **not** print the cracking percentages in text. Pot soil moisture similar (drip). Yield and Brix not significantly different. |
| Santos 2012 | 2012 | Qualitative: tunnels protect against **rain and ice injury** and reduce nonmarketable fruit. **No split counts.** Plastic off May–August, so Florida summer rain is **not** excluded. |

**Encode:** rain-on-fruit **reduced IF** the cover is rain-excluding **and closed**. Residual split is real. Marshall’s residual is about **two-thirds** of open-field split (19.9 / 30.4), not 5%. A roof-only shelter does not change T/RH and only helps while the film is on.

### Chill accumulation (does plastic create or destroy chill?)

No paper in this set logged chill hours or chill portions inside vs outside a blueberry tunnel. The physiology is one-way: closed plastic **warms days** and can **negate** chill. It does not mint missing chill.

| Source | Year | What was actually said / measured |
|---|---|---|
| HS216 | 2023 | Chill hours ~32–45 °F; below freezing **no** accumulation; >70 °F mid-Nov to mid-Feb **negates**. Plants that **keep leaves** “will not accumulate chilling as quickly as defoliated plants.” Dynamic Model needed for warm-spell cancellation. |
| Ogden 2009 | 2009 | Early closure (15 Dec) advanced flowers but vegetative flush stayed aligned across closure dates. Authors state early closure can **prevent chill-hour accumulation** and that high tunnel heat “likely” **negates** chill (citing Lyrene & Williamson). **Not a chill-logger trial.** |
| Fang et al., *A Review for Southern Highbush Blueberry Alternative Production Systems*, Agronomy 10:1531. DOI 10.3390/agronomy10101531. | 2020 | Review: tunnels raise winter heat units. Evergreen under tunnels is freeze **avoidance**, not chill creation. |
| HS1362 *Evergreen Production System…* DOI 10.32473/edis-hs1362-2020. | 2020 | Evergreen used under tunnels in north-central Florida so plants **do not enter dormancy**. Keys: cultivars that hold leaves, **avoid freezes that induce dormancy**. |

**Encode:** `chill: not restored`. For deciduous SHB, a closed winter tunnel is more likely to **destroy** chill than to add it. For evergreen, chill is already nearly irrelevant (HS1362 / variety cards). Do not multiply outdoor chill upward under plastic.

### Heat / berry temperature

| Source | Year | What was measured |
|---|---|---|
| Santos 2012 | 2012 | Sep–Apr **Tmax did not differ** inside vs outside (sides managed; plastic off in summer). |
| Ogden 2009 | 2009 | Winter/spring Tmax **+3 to +15 °C**. After 15 May sidewalls open, air T similar. Summer **soil** in tunnels **2–5 °C cooler** than open (more canopy shade). Open pine-bark soil **30–35 °C** in summer. |
| Li & Bi 2019 | 2019 | Monthly Tmax **+3.2 to +10.4 °C** year-round under film. |
| Retamal-Salgado 2015 | 2015 | Tmax **+10 to +12 °C**; late fruit expansion AGR/RGR **lower** in tunnel (authors blame high T / low min RH / crop load). Final berry weight **not** different. |
| Matamala et al., *Rain Cover and Netting Materials…*, Plants 12:3556. DOI 10.3390/plants12203556. Linares & Traiguén, Chile; Legacy + Top Shelf. | 2023 | **Fruit-air temperature offset:** LDPE **+0.3 °C**, woven **−0.1 °C**, net **−0.3 °C**. GDD site-dependent: Linares LDPE **+17%** GDD vs open; Traiguén net and LDPE **about −11%** GDD. |
| Darnell & Williamson, *Feasibility of blueberry production in warm climates*, Acta Hortic. 446:251–256. | 1997 | Cited by Fang 2020: air **>30 °C** reduces blueberry photosynthetic rate. |
| Spann et al., *Photoperiod and temperature effects…*, JASHS 129:294–298. | 2004 | Flower-bud initiation and whole-plant carbohydrate **reduced at 28 °C vs 21 °C** (Misty / Sharpblue class material). |
| Spiers, *Substrate temperatures influence root and shoot growth…*, HortScience 30:1029–1030. DOI 10.21273/HORTSCI.30.5.1029. | 1995 | Substrate 16 / 27 / 38 °C at 10 cm. Root and shoot growth **best at 16 °C**, linear decline; shoot at 16 °C **>3×** that at 38 °C. |

**Encode:** heat is **often worse** under closed clear film (day), **sometimes similar** if sides are open or film is off, **sometimes slightly cooler fruit** under net. Do not apply a single Tmax offset to all tunnels.

### Humidity / disease (Botrytis, anthracnose)

**No blueberry paper in this set counted Botrytis or anthracnose incidence in tunnel vs open field.**

| Source | Year | What was measured |
|---|---|---|
| Retamal-Salgado 2015 | 2015 | Max RH ~**99%** both systems. **Min RH 10–20 percentage points lower** in the tunnel. Leaf wetness **not** measured. |
| Li & Bi 2019 | 2019 | Tunnel RH **54.6–81.7%** (monthly means). No outdoor RH pair. No disease counts. |
| Wei 2025 | 2025 | Roof-only: RH **unchanged**. |
| Verma / Punja group, *Environmental and host requirements… Colletotrichum acutatum*, Plant Pathol. DOI 10.1111/j.1365-3059.2006.01450.x | 2006 | Anthracnose infection with **≥10 h wetness at 11 °C**. Splash-dispersed. |
| Miles et al. / MSU Blueberry Advisory (from UF strawberry model) | 2013+ | Anthracnose risk high with **≥12 h wetness** at ~68–86 °F. |
| Xiao et al., *Comparison of epidemics of botrytis fruit rot and powdery mildew… tunnel vs field* (strawberry), Plant Dis. 85:901–909. | 2001 | **Strawberry, not blueberry.** Tunnel **reduced rain-driven Botrytis**, **increased** powdery mildew. Use only as a pathway analog. |
| HS216 | 2023 | Overhead freeze irrigation creates wet tissue → **Botrytis** (expert). |
| HS1362 / PP348 | 2020 | Evergreen needs summer–winter **leaf-disease** control (anthracnose, rust, Septoria, target spot). Drip/microjet to shorten wetness. **Expert.** |
| HS1245 | current | Avanti: **Botrytis fruit rot susceptibility** reported. Cultivar, not structure. |
| Fang 2020 | 2020 | High density + restricted airflow → more foliar disease (review). Honey bees forage poorly in warm closed tunnels. |

**Encode:** rain-splash anthracnose **should fall** when film is closed (mechanism). Condensation, still air, and freeze-water nights can **raise** Botrytis. Current `botrytis_multiplier = 1.6` for every tunnel is **expert**, not measured, and is wrong for a dry, well-vented rain roof.

### PAR / radiation / DLI / fruit quality (Brix)

| Source | Year | What was measured |
|---|---|---|
| Santos 2012 | 2012 | Film specified **35% light reduction**. No Brix. |
| Ogden 2009 | 2009 | PPF line-sensor for canopy interception, not film transmission. Tunnel fruit Brix **11–13** (Emerald 12.8, Jewel 11.5). **No outdoor Brix** (outdoor crop freeze-killed). Anthocyanin rose through harvest. Closure date did not change Brix. |
| Li & Bi 2019 | 2019 | Noon PAR in tunnel **477–1411 µmol m⁻² s⁻¹**. Brix **9.6–14.2**; Sweetcrisp 14.1–14.2. **No outdoor Brix pair.** |
| Retamal-Salgado 2015 | 2015 | PAR total **−25%**; PAR diffuse **+150%** (sunny). gs **+42 to +99%**, related to diffuse PAR (r² = 0.69). Berry weight ns. |
| Matamala 2023 | 2023 | Spectrophotometric transmission: UV **53 / 42 / 10%** (net / woven / LDPE); PAR **83 / 81 / 86%**; NIR **83 / 91 / 96%**. Canopy PPFD cut more than film rating (often **20–47%** depending on cultivar/site). Firmness: net **highest**, LDPE **lowest** (LDPE **−6 to −9%** vs open; net **+3.6 to +4%**). Brix: **small and site-dependent** (Linares LDPE +1.4% relative; Traiguén all covers **−2.3 to −3.7%**). |
| Tamada & Ozeki / Tamada 2012, *Evaluation of blueberry types… unheated plastic house*, Int. J. Fruit Sci. 12:83–91. DOI 10.1080/15538362.2011.619123. | 2011–12 | Unheated house: SSC and citric acid of **all types lower** than open culture (qualitative across cultivars; they measured SSC and acid). |
| Wei 2025 | 2025 | Brix ns. Polyphenols/anthocyanins **lower under roof in the dry year only**. |

**Encode:** PAR usually **−15 to −35%** under clear PE; quality (Brix) is **not a stable tunnel bonus**. Sometimes lower SSC (Japan), sometimes unchanged (China roof; Ogden no pair), sometimes ± a few tenths (Chile). Do not encode “tunnels raise Brix.”

### Harvest timing (days earlier?)

Measured advances are **7–40 days** for unheated plastic, **~2 months** for **heated** greenhouse. The comparison baseline matters.

| Source | Setting | Advance actually measured |
|---|---|---|
| Santos 2012 | FL Haygrove vs open SHB | Early fruit **~4 weeks** (esp. Snow Chaser). Open early yield near zero first year. |
| Ogden 2009 | GA tunnels vs open | Flower initiation **+38 d Emerald, +39 d Jewel** (15 Dec close). Ripe fruit only in tunnels 2007 (outdoor freeze-killed). |
| Li & Bi 2019 | MS tunnel pots | First harvest first week of April; authors call this **4–5 weeks** earlier than **Mississippi rabbiteye field**, not vs SHB field. |
| Retamal-Salgado 2015 | Chile O’Neal | Harvest start **14 d** earlier; yield **+44%**. |
| Baptista et al., *Early ripening… mild winter*, Acta Hortic. 715:191–196. DOI 10.17660/ActaHortic.2006.715.27. SW Portugal; film early January after chill met, off end of April. | 2006 | Harvest peaks **3–16 May**, “nearly a month before” usual S. Europe early crop. O’Neal earliest. |
| Tamada 2012 | Japan unheated house; pots walked in 10 Feb | Flowering **26–40 d** earlier; ripening **7–40 d** earlier. Fruit-development interval **longer** under plastic. |
| Bal, *Blueberry culture in greenhouses, tunnels, and under raincovers*, Acta Hortic. 446:327–332. | 1996 | **Heated greenhouse: ~2 months** before field. **Unheated tunnels: 5–6 weeks**. Plastic rain covers put on at color-change: harvest **delayed 2–3 weeks**. |
| Ciordia et al. 2002 / 2006 | N. Spain pots + Italian tunnels | Cited by Ogden/Santos as **1 week to 1 month**. Ciordia 2006 used for 80–105 d flower-to-ripe comparison. |

**Encode:** unheated tunnel **+14 to +40 days** is the honest band, cultivar- and closure-date-specific. Heated glass is a different object. Rain covers at veraison can **delay**, not advance (Bal).

---

## 2. Cover materials: what each actually solves vs worsens

Sources: Matamala 2023 (measured UV/PAR/NIR, fruit T, GDD, yield, firmness, Brix); Wei 2025 (rain roof only); Santos 2012 (Haygrove PE); Ogden 2009 (clear greenhouse PE); Lobos et al. 2012 / Retamales nets (Chile shade; yield/quality, not rain); commercial insect-net guides (not blueberry weather trials).

| Material | Solves (measured or strong mechanism) | Worsens / residual | Evidence |
|---|---|---|---|
| **Clear LDPE / greenhouse PE** | Rain on fruit while closed. Day heat / GDD in cool sites. Some Tmin lift if large, closed, and/or watered (Santos, Li & Bi, Chile O’Neal). Diffuse PAR up (Chile). | Night radiative cooling possible (Ogden). Day heat in warm sites. UV collapse (~10% transmission, Matamala). Firmness down. Chill negation if closed in dormancy. Condensation. Pollination. | Measured |
| **Haygrove 6-mil, 35% shade PE** | Same as LDPE; FL trial held Tmin near 32 °F with less water. | 35% less light. Plastic **off May–Aug** → summer rain, heat, hurricane rain **not** solved. | Measured (Santos) |
| **Woven waterproof rain cover** | Rain. Higher yield than net in Chile (+18 to +31% vs open/net). UV ~42%. | Firmness below open (−3 to −6%). Not a frost wall if sides open. | Measured (Matamala) |
| **Rain-exclusion roof only** (PE, open sides) | Rain-crack / drop down. T and RH **not** changed. | Residual crack (root uptake). PAR/UV down. No freeze help. | Measured (Wei; Marshall residual) |
| **Shade / hail / raschel net** | Hail, some wind, some sunburn. Fruit-air **slightly cooler** (−0.3 °C, Matamala). Firmness **up**. UV still high (~53%). | **Does not stop rain.** Yield **down** ~19–21% in Matamala. Intermediate shade can **delay** harvest (Lobos 2012 Elliott). | Measured |
| **Insect net** | Insects / SWD / birds if mesh is right. | Ventilation down → heat and humidity risk. **No blueberry T/RH/disease trial** in this set. | Expert / other crops |
| **No cover** | Full chill, full PAR, bees. | Full rain-crack, full freeze, full hail. | Baseline |

Matamala PAR film ratings (~81–86%) are **higher** than Haygrove’s 35% shade spec and Wei’s 75% film. Encode a **band**, not one PE number.

---

## 3. Greenhouse vs high tunnel — interchangeable for risk?

**No.**

| | Unheated high tunnel | Greenhouse / heated house |
|---|---|---|
| Heat | Passive solar + vents. Tmax often +3 to +15 °C. Tmin **unreliable**. | Active heat/cool possible. Bal: harvest **~2 months** early vs field; tunnel **5–6 weeks**. |
| Freeze | Not guaranteed. Ogden: crop lost without correct heat. Santos: works with closure + water. | Can be engineered to a setpoint. Fang 2020: most SHB “greenhouse” papers are **physiology**, not commercial yield (exception: Motomura et al. 2016 pot-size in Volcano, HI, **without** climate control). |
| Humidity | Sides often open; RH can be lower or similar. | Closed; humidity and disease are managed as a system. Cho/Aung factory work targets ~40–80% RH (physiology). |
| Light | Single PE; summer film often **removed** (Santos). | Glass/poly + optional lamps. DLI is a design variable, not outdoor climate. |
| Chill | Closing too early can **steal** chill. | Same or worse if heated in winter. |

Fang 2020 treats them as different systems. The analogue `structure` enum should too. Do not copy tunnel freeze-water or rain-exclusion onto “greenhouse” unless the house is specified (heated? pad-fan? retractable?).

---

## 4. Pots / substrate / pine-bark vs in-ground

| Factor | What changes | Evidence |
|---|---|---|
| **Waterlogging** | Pots **can** drain if they have grills and leach 15–25%. They **can** saturate if leach >25%, drains block, or pots sit in flood water. In-ground pine-bark beds exist **because** native Florida sands/flats wet up. | HS1476 (Nunez, Zapien, Phillips 2024): leach **>25%** “saturated conditions can promote Phytophthora or Pythium.” Kingston et al. 2017 HortScience 52:1692: high **bark** fraction dried too fast and cut growth — opposite problem. |
| **Phytophthora** | Drainage and **no standing water** are the control. All FL SHB can get PRR. Pots flooded by surface water after rain: UF says **discard** (nursery/PP347 guidance). Deep sand in-ground may never see it. | PP347 *Phytophthora Root Rot on Southern Highbush Blueberry in Florida* (2024); HS1476. **Expert + disease cycle**, not a pot-vs-field incidence trial. |
| **pH** | Substrate has **no pH buffer**. Target leachate **4.5–5.5**; EC **<2.0 dS m⁻¹**. Alkaline FL water raises pH fast. In-ground pine bark lowers pH vs native sand (Santos site water pH 7.3–7.6; bark used to acidify). | HS1476 **measured method** (pour-through). Fang 2020 / Whidden 2008: commercial FL pots 56–95 L historically; HS1476 says industry moved to **5–7 gal**. |
| **Rain-split** | Fruit still wets in the open. Pots do **not** stop peel uptake. Root-uptake split still happens (Marshall). Wei: pots under a **roof** still need the roof for crack control; pot moisture was managed by drip. | Measured (Marshall, Wei). |
| **Pot / bed heat** | Black pots heat; Wisconsin Extension (home) warns against black containers. HS1476: **no consensus** on pot color/shape for blueberry roots. Pine-bark **beds** run **colder at flowers** (HS216, up to 5 °F) and **hotter at roots** in summer sun (Ogden open soil 30–35 °C). Spiers 1995: roots hate 38 °C. | Mixed: Spiers **measured**; pot-color effect on commercial SHB **unknown**. |
| **Wind / storm** | Small pots blow over; growers trellis or anchor (Fang 2020 Fig. 6; HS1476). Chickadee uproots in storms (HS1362) — cultivar + roots, not only pots. | Expert / observation. |

**Encode:** substrate may zero **SoilGrids pH** as a site filter (soilless). It must **not** zero Phytophthora, drought, or pot heat. Current `drainage_weight = 0` under substrate is only honest for **native-soil drainage GIS**, not for “pots cannot waterlog.”

---

## 5. Tunnel + pots: residual risks. Can they “handle extreme rainfall”?

**No. They handle rain on fruit while the roof is on and drains work. They do not handle floods, stalled air, or wind that takes the structure.**

Residual list (all still live under tunnel + pots):

1. **Freeze** if unheated or forecast-wrong (Ogden 2008–09). Even Santos’ “32 °F tunnel” is still bloom-lethal on a worse night.
2. **Heat / VPD** on closed sunny days (Chile Tmax +10–12 °C; Li & Bi Tmax +3–10 °C).
3. **Chill loss** if deciduous plants sit closed in winter (Ogden discussion; HS216 negation).
4. **Rain-crack via roots** (Marshall 19.9% under cover).
5. **Rain on fruit** whenever film is off (Santos May–Aug) or sides are a rain-only roof in wind-driven rain.
6. **Botrytis** from condensation or freeze water (mechanism; not counted).
7. **Anthracnose** if wetness hours persist (splash down, wetness not necessarily zero).
8. **Phytophthora / hypoxia** if leachate >25% or pots stand in water (HS1476).
9. **pH/EC drift** (HS1476).
10. **Pollination failure** without Bombus in a closed house (Ogden fruit set 4% in one tunnel; Fang/Sampson & Spiers 2002).
11. **Blow-over / structure failure** in wind. `wind_failure_kph = 110` in `systems.py` is **not** from a blueberry paper in this set — treat as **unknown**.
12. **Hurricane / extreme rain:** pots can be **moved** if labor exists (Fang). Film and hoops fail. Ground under pots still floods. HS1476: growers **anchor** pots for extreme weather. That is the opposite of “handled.”

---

## 6. Honest effect ranges (and dishonest binaries)

| Factor | Honest range we can encode | Dishonest as 0/1 |
|---|---|---|
| Rain on fruit | **Reduced** if cover is rain-excluding **and closed**. Residual peel wetness from drip/condensate/wind. | `rain_exclusion = 0.97` for every tunnel |
| Rain-crack | Open: full. Closed PE: Marshall residual **~0.65×** open split rate (19.9/30.4), cultivar-specific. Floor is **not** 0. | `rain_crack_multiplier = 0.05` |
| Freeze / Tmin | Closed large Haygrove + water: Tmin lift of **many °F** (field teens → ~32 °F) in **that** trial. Unheated small PE: Tmin **0 to −5 °C vs outdoor**. Heated: can hold. | `frost_nights × 0.1` |
| Freeze water use | Santos: **~0.1×** volume. HS216: sometimes zero, sometimes still needed. | Using water factor as kill factor |
| Chill | Outdoor chill **stands** if film is off in winter. Closed film **does not add** chill; can **negate**. Evergreen: chill weight already ~0. | Raising chill under plastic; or setting deciduous tunnel chill to 0 |
| Heat | Day Tmax **+0 to +15 °C** when closed. Net: fruit **slightly cooler**. Film off: ~open. | One Tmax offset for all structures |
| PAR / DLI | **0.65–0.86** of outdoor under PE (band). Net ~0.80–0.83. | Single 0.62 LDPE |
| Brix | **No consistent direction.** | Tunnel Brix bonus |
| Harvest date | Unheated: **+14 to +40 d**. Heated GH: **~+60 d**. Rain cover at color: **−14 to −21 d** (later). | Flat `+30` for every tunnel |
| Botrytis | Unknown net sign. Rain down, wetness/condensate/freeze-water up. | `×1.6` always |
| Anthracnose splash | Likely down when closed. Wetness hours unknown. | 0 |
| Phytophthora | Pots help **if** drained; worse if sat. | `drainage_weight = 0` meaning no risk |
| Extreme rainfall | Roof helps fruit. **Does not** handle flood, wind, or film-off season. | “Tunnel pots can take extreme rain” |

---

## 7. Decision table

Residual risk = what is still live after the system is in place and managed as in the papers (drip, vents, typical FL/SE practice). Not a 0–1 score.

| Weather factor | Open ground (pine-bark bed or soil) | Open pots / substrate | Tunnel ground | Tunnel pots | Evidence |
|---|---|---|---|---|---|
| **Bloom freeze / Tmin** | Full. Overhead water is the FL tool; fails in dry wind (HS216). Bark bed can be **colder** at flowers (up to 5 °F). | Same air freeze. Less soil-heat mass. Pots can be covered/moved (not measured as °C saved). | **Reduced, not zero.** Santos: Tmin ~32–33 °F vs field 19–21 °F **with** water + closed sides. Ogden: unheated tunnel **colder**; crop lost. | Same air as tunnel ground. Bark/pot cooling may be **worse** with no convection (Fang/HS216). | Measured (Santos, Ogden, Li & Bi, Chile Tmin) + expert (HS216) |
| **Harvest rain on fruit** | Full. | Full. Fruit still wets. | **Low while PE is on.** Santos film **off May–Aug** → full summer rain. | Same as tunnel ground. | Measured (Wei rain roof) + Santos management |
| **Rain-crack** | High if ripe + rain (rabbiteye worst; Marshall). | High. Root + peel. | **Lower, not zero** (Marshall 19.9% vs 30.4%). | **Lower, not zero.** Wei: crack down, pot moisture similar. | Measured |
| **Chill (deciduous)** | Outdoor accumulation; leaves slow it (HS216). | Same air chill. Moving pots into a warm house **steals** chill (Japan walked pots in 10 Feb **after** outdoor chill). | **Not restored.** Closed winter film can **negate**. | Same. | Expert + Ogden discussion; no logger trial |
| **Chill (evergreen)** | Almost irrelevant; freeze that strips leaves is the risk (HS1362). | Same. | Tunnel used to **avoid** dormancy-inducing freeze, not to make chill. | Same. | Expert (HS1362) |
| **Day heat / berry T** | Open-sky load; berry can run hotter than air (variety-card offsets are from other heat papers). | Pots/root zone can run **hot** (Spiers 38 °C kills growth). | Often **hotter air** when closed; Santos winter Tmax ~open. | Combined: hot air + hot pot possible. **Unknown** as a paired trial. | Measured air; pot+tunnel heat **unknown** |
| **Botrytis** | Rain + bloom + freeze-water nights (HS216). | Same canopy. | Rain down; condensate / still air / less water but **still wet nights**. Sign **unknown**. | Same. | Unknown (blueberry counts). Expert pathway. |
| **Anthracnose** | Splash + long wetness. | Same. | Splash **down** if closed. Wetness unknown. | Same. | Mechanism strong; incidence **unknown** |
| **PAR / DLI / Brix** | Full sun. | Full sun. | PAR **−15 to −35%**. Brix **no consistent lift**. | Same light. | Measured |
| **Harvest timing** | Baseline for that cultivar/site. | Similar if climate same (Li & Bi have no open SHB control). | **+14 to +40 d** typical unheated. | Same if tunnel climate dominates. | Measured |
| **Waterlogging / Phytophthora** | High on flatwoods / high water table; bark beds are the mitigation. | **Low if drained**; **high if sat or flooded** (discard flooded pots). | Film reduces rain into bed **while on**; summer film-off returns rain. | Best drainage **if** leach 15–25% and no flood. Still residual PRR. | Expert (HS1476, PP347) |
| **pH** | Native soil + S / bark. | **Managed**, no buffer; can crash or climb in days. | Same as open ground. | Same as open pots. | Measured method (HS1476) |
| **Extreme rainfall / flood / wind** | Field floods; fruit splits; canes ice-break in freeze water. | Pots drown or blow over; can be moved. | Roof helps fruit; **structure fails** in wind/hail; flood still under hoops. | **Cannot claim “handles extreme rainfall.”** Move + drain + film integrity are operational, not climate-deleted. | Expert; no extreme-event trial |

---

## 8. Regional literature that is **not** solid enough to encode

| Region | What exists | Why it is not a weather-effect number |
|---|---|---|
| **Mexico** | Bañados 2009 Acta Hortic. 810:439–444 (expansion). Fang 2020: Jalisco prune-timed evergreen; **industry**, not peer-reviewed climate. Insect-net greenhouse guides (other crops). | No tunnel vs open Tmin/PAR/split trial. |
| **Australia** | Wright 1993 Corindi plateau cultivar performance. Evergreen mentioned in reviews. | No measured tunnel weather paper found in this pass. |
| **Spain / Huelva** | Ciordia 2002, 2006; Barrau et al. 2004 Acta Hortic. 649:305–308. | Cited for **1 week–1 month** earliness. Raw T/RH/split tables not retrieved here. |
| **Vendor “50–80% less cracking” reviews** | e.g. trade summaries of mixed countries | Do not use. Marshall and Wei are the split evidence. |

---

## 9. Conflicts with the current encoder

These are the places `systems.py` / `cube.py` would be **dishonest** if shipped as physics:

| Code | What it does | Why it is too strong |
|---|---|---|
| `frost_nights_* × freeze_water_factor` (0.1 tunnel, 0.02 GH) | Deletes 90–98% of frost nights | Santos measured **water use**, not kill probability. Ogden lost the crop. |
| `rain_exclusion = 0.97` if structure is tunnel or GH | Almost no harvest rain | False when film is off, sides open, or rain is wind-driven. |
| `rain_crack_multiplier = max(0.05, 1 − rain_exclusion)` | 5% residual crack under any tunnel | Marshall residual ~65% of open split. |
| `botrytis_multiplier = 1.6` tunnel | Always more Botrytis | **Unmeasured** in blueberry. Rain-off can go the other way. |
| `drainage_weight = 0` on substrate | Drops soil drainage from the match | Honest for SoilGrids. Dishonest if read as “no Phytophthora.” |
| Pine-bark note: “does not change bloom freeze” | Comment in `systems.py` | HS216: bark beds **can** be 5 °F colder at flowers. |
| `bloom_advance_days = 30` all tunnels; `40` all GH | Flat | Measured band is 14–40 unheated, ~60 heated. Bal rain-cover can **delay**. |
| `COVER_PAR['ldpe'] = 0.62` | 38% light loss | Matamala LDPE PAR ~86% film; Santos 35% loss; Wei 27% loss. Use a band. |
| Greenhouse copies tunnel rain/freeze logic | Interchangeable | They are not (section 3). |

**Safe comments already in code:** “Covers do not restore chill.” “Closed tunnels without Bombus fail.” Keep those.

---

## 10. Source list (primary)

1. Williamson & Phillips 2023. EDIS HS216. https://ask.ifas.ufl.edu/publication/HS216 — DOI 10.32473/edis-hs216-2004  
2. Phillips, Williamson, Munoz 2020. EDIS HS1362. https://ask.ifas.ufl.edu/publication/HS1362 — DOI 10.32473/edis-hs1362-2020  
3. UF/IFAS HS1245. https://ask.ifas.ufl.edu/publication/HS1245  
4. Santos & Salamé-Donoso 2012. HortTechnology 22:700–704. DOI 10.21273/HORTTECH.22.5.700 (Straughn / Haygrove Waldo). EDIS HS1226.  
5. Ogden & van Iersel 2009. HortScience 44:1850–1856. DOI 10.21273/HORTSCI.44.7.1850  
6. Ogden et al. 2011. Acta Hortic. 893. DOI 10.17660/ActaHortic.2011.893.155  
7. Li & Bi 2019. HortScience 54:267–274. DOI 10.21273/HORTSCI13639-18  
8. Fang, Nunez, da Silva, Phillips, Munoz 2020. Agronomy 10:1531. DOI 10.3390/agronomy10101531  
9. Nunez, Zapien, Phillips 2024. EDIS HS1476. https://ask.ifas.ufl.edu/publication/HS1476  
10. Harmon et al. 2024. EDIS PP347 Phytophthora. DOI 10.32473/edis-pp347-2024  
11. Retamal-Salgado et al. 2015. Chil. J. Agric. Res. DOI 10.4067/S0718-58392015000400004  
12. Matamala et al. 2023. Plants 12:3556. DOI 10.3390/plants12203556  
13. Marshall et al. 2009. HortScience 44:2035. DOI 10.21273/HORTSCI.44.7.2035  
14. Wei et al. 2025. Plants 14:1167. DOI 10.3390/plants14081167  
15. Baptista et al. 2006. Acta Hortic. 715:191–196. DOI 10.17660/ActaHortic.2006.715.27  
16. Tamada 2012. Int. J. Fruit Sci. 12:83–91. DOI 10.1080/15538362.2011.619123  
17. Bal 1996. Acta Hortic. 446:327–332  
18. Ciordia et al. 2002. Acta Hortic. 574:123–127; Ciordia et al. 2006. Acta Hortic. 715:317  
19. Spiers 1995. HortScience 30:1029–1030. DOI 10.21273/HORTSCI.30.5.1029  
20. Kingston et al. 2017. HortScience 52:1692–1699  
21. Darnell & Williamson 1997. Acta Hortic. 446:251–256  
22. Spann et al. 2004. JASHS 129:294–298  
