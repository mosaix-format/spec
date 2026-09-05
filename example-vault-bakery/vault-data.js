// Mosaix example vault — Forno Vialetto, a fictional artisan bakery.
// Source of truth for export_vault.py (which writes the .md files).
// Every note: path, title, type, tags, updated, summary (120–240), keywords (6–8), entities, relations, links, rev, status, body.
window.MOSAIX_VAULT = [
/* ---------- MOC ---------- */
{path:"Home.md",title:"Home",type:"moc",tags:["moc"],updated:"2026-09-05",
 summary:"Map of content of the Forno Vialetto vault: three partners, five products, three suppliers, the local market, daily operations, key decisions, one synthesis and one composed document.",
 keywords:["home","map of content","index","where to start","forno vialetto vault","bakery vault","entry point"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Forno Vialetto in one page","Elsa Nordgren","Marco Trevisan","Layla Beshir","Ciabatta Vialetto","Rye country loaf","Almond croissant","Hazelnut and honey tart","Hazelnut tart (old recipe)","Mulino Cerrina","Latteria Voss","Biolievito Kraus","Viale Giardini neighbourhood","Café Lindström","Panificio Reale","Saturday market at Piazza Solari","Baking shifts","The wood-fired oven","Unsold bread policy","No delivery policy","Closed on Mondays","Organic certification","Open questions","Opening the second shop — brief","Conventions"],rev:"0a1b2c3d4e5f",status:"sourced",
 body:"Start with [[Forno Vialetto in one page]]. Then the notes by area.\n\nPeople: [[Elsa Nordgren]], [[Marco Trevisan]], [[Layla Beshir]] — the three partners who opened the bakery in 2019.\n\nProducts: [[Ciabatta Vialetto]], [[Rye country loaf]], [[Almond croissant]], [[Hazelnut and honey tart]]. Old recipe kept: [[Hazelnut tart (old recipe)]].\n\nSuppliers: [[Mulino Cerrina]], [[Latteria Voss]], [[Biolievito Kraus]].\n\nMarket: [[Viale Giardini neighbourhood]], [[Café Lindström]], [[Panificio Reale]], [[Saturday market at Piazza Solari]].\n\nOperations: [[Baking shifts]], [[The wood-fired oven]], [[Unsold bread policy]].\n\nDecisions: [[No delivery policy]], [[Closed on Mondays]], [[Organic certification]].\n\nGovernance: [[Open questions]], [[Conventions]]. Composed document: [[Opening the second shop — brief]]."},

/* ---------- meta ---------- */
{path:"_meta/Conventions.md",title:"Conventions",type:"meta",tags:["moc","meta","ledger","synthesis","people","product","bread","pastry","seasonal","supplier","market","neighbourhood","competitor","event","operations","equipment","policy","decision","composed-document"],updated:"2026-09-05",
 summary:"Meta note of the Forno Vialetto vault: folder contract, reliability convention (status key), declared tags, domain keys (season, channel), entity type recipe, and closed relation vocabulary.",
 keywords:["conventions","meta note","folder contract","reliability convention","declared tags","bakery taxonomy","domain keys","maintainer"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Open questions","Home"],rev:"1a2b3c4d5e6f",status:"sourced",
 body:"mosaix: \"1.0\". Folders: `01-People/` who the partners are, `02-Products/` what the bakery sells, `03-Suppliers/` who provides the ingredients, `04-Market/` where they sell and who competes, `05-Operations/` how the bakery runs, `06-Decisions/` choices that shape the business. Reserved: `_meta/`, `_synthesis/`, `_docs/`.\n\nReliability: frontmatter key `status` with values sourced · to-confirm · superseded. Domain keys: `season` (spring, summer, autumn, winter), `channel` (shop, market, wholesale). Entity type added: `recipe`. Relation types: supplies, owns, sells at, competes with, depends on.\n\nTags declared: the `tags` list of this note is the taxonomy. Maintainers: E. Nordgren (products), M. Trevisan (operations). Map of content: [[Home]]. Ledger: [[Open questions]]."},

{path:"_meta/Open questions.md",title:"Open questions",type:"ledger",tags:["meta","ledger"],updated:"2026-09-05",
 summary:"Ledger of what is not decided: flour price discrepancy between two quotes, Saturday market pitch fee in two contracts, and the sourdough starter age claimed by two sources.",
 keywords:["open questions","contradictions","flour price","pitch fee","sourdough age","unresolved","both versions","competing sources"],
 entities:[{name:"Mulino Cerrina",type:"company"},{name:"Biolievito Kraus",type:"company"}],relations:[],links:["Mulino Cerrina","Saturday market at Piazza Solari","Biolievito Kraus","Layla Beshir"],rev:"2b3c4d5e6f7a",status:"sourced",
 body:"## #1 · Flour price from Mulino Cerrina\n\n- Version A — March 2025, source: quote MC-2025-03. €0.85/kg for type-1 flour.\n- Version B — June 2025, source: invoice MC-2025-06-014. €0.92/kg for the same flour.\n\nConsequence: the ciabatta cost model changes by €0.04 per loaf; margin drops below 60 % if B is the new baseline.\nOwner: [[Mulino Cerrina]] contact · status: open.\n\n## #2 · Saturday market pitch fee\n\n- Version A — 2024, source: verbal agreement with market manager. €120/month.\n- Version B — January 2025, source: new contract draft. €150/month.\n\nConsequence: annual market cost rises by €360; changes the break-even from 18 to 22 loaves per Saturday.\nOwner: Marco Trevisan · see [[Saturday market at Piazza Solari]] · status: open.\n\n## #3 · Age of the sourdough starter\n\n- Version A — [[Biolievito Kraus]] website, accessed 2025-04. Claims the starter culture is 40 years old.\n- Version B — [[Layla Beshir]]'s tasting notes, 2024-11. Records 35 years, told by the founder in person.\n\nConsequence: marketing materials and the shop sign say \"40-year starter\"; if B is correct, the claim is overstated.\nOwner: Layla Beshir · status: open."},

/* ---------- synthesis ---------- */
{path:"_synthesis/Forno Vialetto in one page.md",title:"Forno Vialetto in one page",type:"synthesis",tags:["synthesis"],updated:"2026-09-05",
 summary:"One-page synthesis of Forno Vialetto: an artisan bakery opened in 2019 by three partners, selling bread and pastries at the shop and the Saturday market, with a wood-fired oven and no delivery.",
 keywords:["one page overview","artisan bakery summary","forno vialetto summary","three partners","quick read","stand-alone context","bakery at a glance"],
 entities:[{name:"Forno Vialetto",type:"company"},{name:"Elsa Nordgren",type:"person"},{name:"Marco Trevisan",type:"person"},{name:"Layla Beshir",type:"person"}],relations:[{from:"Elsa Nordgren",type:"owns",to:"Forno Vialetto"},{from:"Marco Trevisan",type:"owns",to:"Forno Vialetto"},{from:"Layla Beshir",type:"owns",to:"Forno Vialetto"}],links:["Elsa Nordgren","Marco Trevisan","Layla Beshir","Ciabatta Vialetto","The wood-fired oven","Saturday market at Piazza Solari","No delivery policy","Closed on Mondays"],rev:"3c4d5e6f7a8b",status:"sourced",
 body:"Forno Vialetto is an artisan bakery in the Viale Giardini neighbourhood, opened in 2019 by [[Elsa Nordgren]] (business and products), [[Marco Trevisan]] (operations and oven) and [[Layla Beshir]] (sourcing and flavour development). The bakery bakes in a restored wood-fired oven ([[The wood-fired oven]]) and sells five products, led by the [[Ciabatta Vialetto]], the house bread.\n\nTwo channels: the shop (Tuesday to Saturday) and the [[Saturday market at Piazza Solari]]. The bakery does not deliver ([[No delivery policy]]) and is closed on Mondays ([[Closed on Mondays]]). Three suppliers provide the core ingredients: a regional mill, a small dairy and a sourdough-starter producer. Revenue in 2024 was approximately €210,000, split 70 % shop and 30 % market."},

/* ---------- 01-People ---------- */
{path:"01-People/Elsa Nordgren.md",title:"Elsa Nordgren",type:"person",tags:["people"],updated:"2026-09-05",
 summary:"Co-founder responsible for business development and the product range; trained at a culinary school in Lyon, runs the customer side of the shop and sets the seasonal menu each quarter.",
 keywords:["elsa nordgren","co-founder","product range","lyon training","seasonal menu","business development","customer relations"],
 entities:[{name:"Elsa Nordgren",type:"person"},{name:"Forno Vialetto",type:"company"}],relations:[{from:"Elsa Nordgren",type:"owns",to:"Forno Vialetto"}],links:["Marco Trevisan","Layla Beshir","Ciabatta Vialetto"],rev:"4d5e6f7a8b9c",status:"sourced",
 body:"Elsa Nordgren (born 1986) trained in pastry at a culinary school in Lyon, then worked in two bakeries before co-founding Forno Vialetto in 2019 with [[Marco Trevisan]] and [[Layla Beshir]]. She sets the product range each quarter and runs the customer-facing side of the shop. ✅ sourced (partnership agreement, 2019-03).\n\nThe house bread, [[Ciabatta Vialetto]], is her recipe. She holds a 40 % share of the business."},

{path:"01-People/Marco Trevisan.md",title:"Marco Trevisan",type:"person",tags:["people"],updated:"2026-09-05",
 summary:"Co-founder responsible for operations, the baking schedule and oven maintenance; rebuilt the wood-fired oven in 2020 and manages the 3:30 a.m. shift five days a week.",
 keywords:["marco trevisan","co-founder","operations manager","oven maintenance","baking schedule","early shift","wood-fired oven rebuild"],
 entities:[{name:"Marco Trevisan",type:"person"},{name:"Forno Vialetto",type:"company"}],relations:[{from:"Marco Trevisan",type:"owns",to:"Forno Vialetto"}],links:["Elsa Nordgren","Layla Beshir","The wood-fired oven","Baking shifts"],rev:"5e6f7a8b9c0d",status:"sourced",
 body:"Marco Trevisan (born 1983) is a former construction worker who moved into baking after apprenticing at a village oven in the mountains. He co-founded Forno Vialetto in 2019 with [[Elsa Nordgren]] and [[Layla Beshir]]. He rebuilt [[The wood-fired oven]] in summer 2020 and runs [[Baking shifts]] starting at 3:30 a.m., Tuesday to Saturday. ✅ sourced (partnership agreement, 2019-03).\n\nHe holds a 30 % share of the business."},

{path:"01-People/Layla Beshir.md",title:"Layla Beshir",type:"person",tags:["people"],updated:"2026-09-05",
 summary:"Co-founder responsible for ingredient sourcing and flavour development; manages supplier relationships with Mulino Cerrina, Latteria Voss and Biolievito Kraus, and develops new recipes.",
 keywords:["layla beshir","co-founder","ingredient sourcing","flavour development","supplier relationships","new recipes","tasting notes"],
 entities:[{name:"Layla Beshir",type:"person"},{name:"Forno Vialetto",type:"company"}],relations:[{from:"Layla Beshir",type:"owns",to:"Forno Vialetto"}],links:["Mulino Cerrina","Latteria Voss","Biolievito Kraus","Elsa Nordgren","Marco Trevisan"],rev:"6f7a8b9c0d1e",status:"sourced",
 body:"Layla Beshir (born 1991) studied food science before joining the bakery as the third partner in 2019. She manages the relationships with all three suppliers: [[Mulino Cerrina]], [[Latteria Voss]] and [[Biolievito Kraus]]. She develops new recipes and keeps tasting notes on every batch. ✅ sourced (partnership agreement, 2019-03).\n\nShe holds a 30 % share of the business and leads sourcing decisions together with [[Elsa Nordgren]] and [[Marco Trevisan]]."},

/* ---------- 02-Products ---------- */
{path:"02-Products/Ciabatta Vialetto.md",title:"Ciabatta Vialetto",type:"product",tags:["product","bread"],updated:"2026-09-05",
 summary:"The house bread and best seller: a high-hydration ciabatta with a thin crust and open crumb, baked twice a day in the wood-fired oven, accounting for 35 % of daily revenue.",
 keywords:["ciabatta","house bread","high hydration","open crumb","best seller","twice a day","wood-fired"],
 entities:[{name:"Ciabatta Vialetto",type:"product"},{name:"Ciabatta Vialetto recipe",type:"recipe"}],relations:[{from:"Ciabatta Vialetto",type:"depends on",to:"Mulino Cerrina"}],links:["Mulino Cerrina","The wood-fired oven","Elsa Nordgren"],rev:"7a8b9c0d1e2f",status:"sourced",
 body:"High-hydration ciabatta (78 % hydration) with a thin, crackling crust and an open, irregular crumb. Developed by [[Elsa Nordgren]] in 2019 using type-1 flour from [[Mulino Cerrina]]. Baked twice daily in [[The wood-fired oven]], first batch at 5:30 a.m., second at 11:00 a.m. ✅ sourced (recipe log, 2019-06).\n\nRetail price: €3.80 per 500 g loaf. Accounts for about 35 % of daily revenue. The flour costs approximately €0.85–0.92/kg depending on the current quote."},

{path:"02-Products/Rye country loaf.md",title:"Rye country loaf",type:"product",tags:["product","bread"],updated:"2026-09-05",
 summary:"A dense, slow-fermented loaf of 70 % rye and 30 % wheat, proofed for 18 hours and baked once daily; the second best seller after the ciabatta, popular at the Saturday market.",
 keywords:["rye bread","country loaf","slow fermentation","18-hour proof","dense crumb","saturday market seller","rye flour"],
 entities:[{name:"Rye country loaf",type:"product"},{name:"Rye country loaf recipe",type:"recipe"}],relations:[{from:"Rye country loaf",type:"depends on",to:"Mulino Cerrina"}],links:["Mulino Cerrina","Saturday market at Piazza Solari","Biolievito Kraus"],rev:"8b9c0d1e2f3a",status:"sourced",
 body:"A 70/30 rye-wheat loaf, proofed for 18 hours with the sourdough starter from [[Biolievito Kraus]] and baked once daily at 6:00 a.m. Dense, moist crumb with a thick flour-dusted crust. Rye flour from [[Mulino Cerrina]], milled to order every two weeks. ✅ sourced (recipe log, 2020-01).\n\nRetail price: €5.20 per 750 g loaf. Sells best at [[Saturday market at Piazza Solari]], where it accounts for about 40 % of market-day revenue."},

{path:"02-Products/Almond croissant.md",title:"Almond croissant",type:"product",tags:["product","pastry"],updated:"2026-09-05",
 summary:"Laminated croissant filled with almond cream and topped with flaked almonds, baked fresh each morning; the bakery's only viennoiserie, made with butter from Latteria Voss.",
 keywords:["almond croissant","viennoiserie","laminated dough","almond cream","flaked almonds","morning pastry","butter croissant"],
 entities:[{name:"Almond croissant",type:"product"},{name:"Almond croissant recipe",type:"recipe"}],relations:[{from:"Almond croissant",type:"depends on",to:"Latteria Voss"}],links:["Latteria Voss","Elsa Nordgren"],rev:"9c0d1e2f3a4b",status:"sourced",
 body:"Laminated croissant with almond frangipane filling and flaked-almond topping, baked fresh each morning. The only viennoiserie on the menu, introduced by [[Elsa Nordgren]] in 2020. Uses high-fat butter (84 %) from [[Latteria Voss]], which gives the dough its colour and flake. ✅ sourced (recipe log, 2020-04).\n\nRetail price: €3.20 each. Batch size: 40 pieces. Usually sells out by 10:00 a.m."},

{path:"02-Products/Hazelnut tart (old recipe).md",title:"Hazelnut tart (old recipe)",type:"product",tags:["product","pastry"],updated:"2026-09-05",
 summary:"Original hazelnut tart recipe using blanched hazelnuts and cane sugar, produced from 2019 to 2024; superseded by the hazelnut and honey version after customer feedback on sweetness.",
 keywords:["hazelnut tart","old recipe","blanched hazelnuts","cane sugar","superseded product","too sweet","original version"],
 entities:[{name:"Hazelnut tart (old recipe)",type:"product"},{name:"Hazelnut tart recipe v1",type:"recipe"}],relations:[],links:["Hazelnut and honey tart"],rev:"0d1e2f3a4b5c",status:"superseded",
 body:"Hazelnut tart made with blanched hazelnuts, cane sugar and a shortcrust base. Produced from the bakery's opening in 2019 until January 2024. Customers reported the filling as too sweet for a morning pastry. ✅ sourced (customer feedback log, 2023-09 to 2023-12).\n\nSuperseded by [[Hazelnut and honey tart]], which replaces cane sugar with chestnut honey. This note is kept in place per R7."},

{path:"02-Products/Hazelnut and honey tart.md",title:"Hazelnut and honey tart",type:"product",tags:["product","pastry","seasonal"],updated:"2026-09-05",
 summary:"Revised hazelnut tart replacing cane sugar with chestnut honey and adding a pinch of sea salt; introduced January 2024 after the original was judged too sweet by regular customers.",
 keywords:["hazelnut honey tart","revised recipe","chestnut honey","sea salt","less sweet","replaced version","customer feedback"],
 entities:[{name:"Hazelnut and honey tart",type:"product"},{name:"Hazelnut and honey tart recipe",type:"recipe"}],relations:[],links:["Hazelnut tart (old recipe)","Layla Beshir"],rev:"1e2f3a4b5c6d",status:"sourced",
 body:"Revised version of the [[Hazelnut tart (old recipe)]], introduced in January 2024. Replaces cane sugar with chestnut honey (from a local apiary) and adds a pinch of sea salt to balance the sweetness. Developed by [[Layla Beshir]] after three months of customer feedback. ✅ sourced (recipe log, 2024-01).\n\nRetail price: €4.50 per slice. Available autumn and winter only (honey supply is seasonal). Sells about 15 slices per day in season."},

/* ---------- 03-Suppliers ---------- */
{path:"03-Suppliers/Mulino Cerrina.md",title:"Mulino Cerrina",type:"supplier",tags:["supplier"],updated:"2026-09-05",
 summary:"Regional stone mill supplying type-1 wheat flour and rye flour to the bakery since 2019; deliveries every two weeks, current price under discussion after a recent invoice increase.",
 keywords:["mulino cerrina","stone mill","flour supplier","type-1 flour","rye flour","biweekly delivery","regional mill"],
 entities:[{name:"Mulino Cerrina",type:"company"}],relations:[{from:"Mulino Cerrina",type:"supplies",to:"Forno Vialetto"}],links:["Ciabatta Vialetto","Rye country loaf","Open questions"],rev:"2f3a4b5c6d7e",status:"sourced",
 body:"Mulino Cerrina is a family-owned stone mill about 90 km from the bakery, operating since 1957. Supplies type-1 wheat flour and stone-ground rye flour, delivered every two weeks. ✅ sourced (supply contract MC-2019-08, renewed annually).\n\nCurrent quoted price: €0.85/kg for type-1 (March 2025 quote), but the June 2025 invoice charged €0.92/kg — see [[Open questions]] #1. The flour is the base of [[Ciabatta Vialetto]] and [[Rye country loaf]]."},

{path:"03-Suppliers/Latteria Voss.md",title:"Latteria Voss",type:"supplier",tags:["supplier"],updated:"2026-09-05",
 summary:"Small dairy supplying high-fat butter (84 %) and fresh cream to the bakery since 2020; weekly delivery every Monday, single-origin milk from a herd of 120 Braunvieh cows.",
 keywords:["latteria voss","dairy supplier","high-fat butter","fresh cream","braunvieh cows","weekly delivery","single origin"],
 entities:[{name:"Latteria Voss",type:"company"}],relations:[{from:"Latteria Voss",type:"supplies",to:"Forno Vialetto"}],links:["Almond croissant"],rev:"3a4b5c6d7e8f",status:"sourced",
 body:"Latteria Voss is a small dairy about 45 km north, running a herd of 120 Braunvieh cows. Supplies 84 % butter and fresh cream, delivered every Monday morning. ✅ sourced (supply agreement LV-2020-03).\n\nThe butter goes into the [[Almond croissant]] lamination and the tart bases. Price: €8.60/kg for butter, stable since 2023. Minimum order: 10 kg per week."},

{path:"03-Suppliers/Biolievito Kraus.md",title:"Biolievito Kraus",type:"supplier",tags:["supplier"],updated:"2026-09-05",
 summary:"Artisan producer supplying the bakery's sourdough starter culture since opening day in 2019; the starter is claimed to be 35 to 40 years old depending on the source consulted.",
 keywords:["biolievito kraus","sourdough starter","mother dough","artisan producer","starter culture","natural leavening","long fermentation"],
 entities:[{name:"Biolievito Kraus",type:"company"}],relations:[{from:"Biolievito Kraus",type:"supplies",to:"Forno Vialetto"}],links:["Rye country loaf","Open questions"],rev:"4b5c6d7e8f9a",status:"sourced",
 body:"Biolievito Kraus is a one-person operation that maintains and distributes sourdough starter cultures. The bakery has used the same culture since opening day in 2019; it is refreshed in-house three times a week. ✅ sourced (purchase receipt BK-2019-04).\n\nThe culture's age is disputed: 40 years per the producer's website, 35 years per Layla's notes from a conversation with the founder — see [[Open questions]] #3. The starter is the base of the [[Rye country loaf]] and adds flavour to the ciabatta pre-ferment."},

/* ---------- 04-Market ---------- */
{path:"04-Market/Viale Giardini neighbourhood.md",title:"Viale Giardini neighbourhood",type:"place",tags:["market","neighbourhood"],updated:"2026-09-05",
 summary:"The neighbourhood where the bakery is located: a residential area of about 8,000 people with a tree-lined avenue, a park, two schools and a weekly farmers market at its central square.",
 keywords:["viale giardini","residential area","bakery location","8000 residents","tree-lined avenue","local catchment","where the bakery is"],
 entities:[{name:"Viale Giardini",type:"place"}],relations:[],links:["Café Lindström","Panificio Reale","Saturday market at Piazza Solari"],rev:"5c6d7e8f9a0b",status:"sourced",
 body:"Viale Giardini is a residential neighbourhood of roughly 8,000 people centred on a tree-lined avenue with a park, two primary schools and a handful of independent shops. The bakery sits at number 14, between a bookshop and a florist. ✅ sourced (municipal register, 2024).\n\nTwo competitors operate in the same catchment: [[Café Lindström]] (200 m east) and [[Panificio Reale]] (600 m south). The [[Saturday market at Piazza Solari]] is held in the central square, 150 m from the shop."},

{path:"04-Market/Café Lindström.md",title:"Café Lindström",type:"competitor",tags:["market","competitor"],updated:"2026-09-05",
 summary:"A café 200 metres east of the bakery selling industrial pastries and sandwiches; competes on morning traffic and coffee but not on bread quality, with lower prices and longer opening hours.",
 keywords:["café lindström","rival café","industrial pastries","morning traffic","lower prices","longer hours","coffee and sandwich"],
 entities:[{name:"Café Lindström",type:"company"}],relations:[{from:"Café Lindström",type:"competes with",to:"Forno Vialetto"}],links:["Viale Giardini neighbourhood","No delivery policy"],rev:"6d7e8f9a0b1c",status:"sourced",
 body:"Café Lindström opened in 2017, two years before Forno Vialetto. It serves espresso, industrial croissants and sandwiches, open 6:30 a.m. to 8:00 p.m., seven days a week. Located on the same avenue, about 200 m east. ✅ sourced (observation, 2025-02).\n\nCompetes for the morning walk-in crowd. Lower prices (croissant €1.80 vs. our €3.20) but no artisan bread. The overlap is limited to the first hour of trading. See [[Viale Giardini neighbourhood]]. The café offers delivery, unlike Forno Vialetto ([[No delivery policy]])."},

{path:"04-Market/Panificio Reale.md",title:"Panificio Reale",type:"competitor",tags:["market","competitor"],updated:"2026-09-05",
 summary:"A traditional bakery 600 metres south, open since 1998, with a wider bread range and wholesale accounts; the main competitor on bread, competing on variety and established reputation.",
 keywords:["panificio reale","traditional bakery","wider range","wholesale accounts","established reputation","bread rival","older bakery nearby"],
 entities:[{name:"Panificio Reale",type:"company"}],relations:[{from:"Panificio Reale",type:"competes with",to:"Forno Vialetto"}],links:["Viale Giardini neighbourhood"],rev:"7e8f9a0b1c2d",status:"sourced",
 body:"Panificio Reale has been in the neighbourhood since 1998. It sells 12 types of bread (vs. our two), focaccia, pizza al taglio and a small range of biscuits. Open Tuesday to Sunday, 7:00 a.m. to 1:00 p.m. and 4:00 to 7:30 p.m. ✅ sourced (observation, 2025-02).\n\nThree wholesale accounts with local restaurants, a channel Forno Vialetto has not entered. See [[Viale Giardini neighbourhood]]. The owner has been there for 27 years; local trust is high."},

{path:"04-Market/Saturday market at Piazza Solari.md",title:"Saturday market at Piazza Solari",type:"event",tags:["market","event"],updated:"2026-09-05",
 summary:"Weekly farmers market held every Saturday from 7:00 a.m. to 1:00 p.m. in Piazza Solari; the bakery's second sales channel, contributing about 30 % of weekly revenue with a dedicated stall.",
 keywords:["saturday market","piazza solari","farmers market","weekly stall","second channel","30 percent revenue","outdoor selling"],
 entities:[{name:"Saturday market at Piazza Solari",type:"event"},{name:"Piazza Solari",type:"place"}],relations:[{from:"Forno Vialetto",type:"sells at",to:"Saturday market at Piazza Solari"}],links:["Rye country loaf","Viale Giardini neighbourhood","Open questions"],rev:"8f9a0b1c2d3e",status:"sourced",
 body:"Farmers market held every Saturday, 7:00 a.m. to 1:00 p.m., in Piazza Solari, 150 m from the shop. The bakery has had a regular stall since April 2020, selling bread, tarts and croissants. ✅ sourced (market licence FV-2020-04).\n\nBest seller at the market: [[Rye country loaf]] (40 % of market-day revenue). The pitch fee is under discussion — see [[Open questions]] #2. The square is at the centre of [[Viale Giardini neighbourhood]]. Saturdays average €580 in revenue (2024 figures)."},

/* ---------- 05-Operations ---------- */
{path:"05-Operations/Baking shifts.md",title:"Baking shifts",type:"operations",tags:["operations"],updated:"2026-09-05",
 summary:"The daily schedule runs from 3:30 a.m. (oven pre-heat) to 1:00 p.m. (cleanup), with two baking windows and one prep window; Marco leads the morning, Elsa joins at 7:00 for the shop opening.",
 keywords:["baking shifts","daily schedule","3:30 am start","two baking windows","prep window","morning shift","shop opening"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Marco Trevisan","Elsa Nordgren","The wood-fired oven"],rev:"9a0b1c2d3e4f",status:"sourced",
 body:"[[Marco Trevisan]] arrives at 3:30 a.m. to pre-heat [[The wood-fired oven]] (takes 90 minutes to reach 280 °C). First bake (ciabatta, rye loaf): 5:00–6:30 a.m. Pastry prep: 6:30–8:00 a.m. Second bake (croissants, tarts): 8:00–9:00 a.m. ✅ sourced (shift log, 2024).\n\n[[Elsa Nordgren]] opens the shop at 7:00 a.m. Cleanup finishes by 1:00 p.m. One part-time assistant (hired 2023) covers the shop on Saturdays while both partners are at the market."},

{path:"05-Operations/The wood-fired oven.md",title:"The wood-fired oven",type:"tool",tags:["operations","equipment"],updated:"2026-09-05",
 summary:"A brick wood-fired oven rebuilt by Marco Trevisan in 2020 from a 1960s base; holds 28 loaves per load, reaches 280 °C in 90 minutes, and consumes about 15 kg of beechwood per day.",
 keywords:["wood-fired oven","brick oven","rebuilt 2020","28 loaves capacity","280 degrees","beechwood fuel","1960s base"],
 entities:[{name:"The wood-fired oven",type:"tool"}],relations:[],links:["Marco Trevisan","Ciabatta Vialetto"],rev:"0b1c2d3e4f5a",status:"sourced",
 body:"Brick oven built on a 1960s base that was part of the premises when the bakery moved in. [[Marco Trevisan]] rebuilt the dome and the flue in summer 2020, keeping the original hearth slab. Capacity: 28 loaves per load. ✅ sourced (renovation invoice, 2020-08).\n\nFuel: seasoned beechwood, about 15 kg per baking day, sourced from a local firewood dealer at €180 per tonne. The oven is central to the flavour of the [[Ciabatta Vialetto]] — the crust character does not replicate in an electric oven (tested in 2021)."},

{path:"05-Operations/Unsold bread policy.md",title:"Unsold bread policy",type:"policy",tags:["operations","policy"],updated:"2026-09-05",
 summary:"Bread unsold by closing time is donated to a neighbourhood food bank every evening; the policy has been in place since 2019 and covers roughly 8 % of daily production on average.",
 keywords:["unsold bread","food bank donation","waste policy","daily surplus","evening collection","8 percent waste","neighbourhood food bank"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Closed on Mondays"],rev:"1c2d3e4f5a6b",status:"sourced",
 body:"All unsold bread and pastries are collected by a neighbourhood food bank at 1:30 p.m. each closing day. The arrangement has been in place since the bakery opened in 2019. ✅ sourced (food bank agreement, 2019-05).\n\nAverage daily surplus: about 8 % of production (2024 figures). The surplus is higher on rainy days and lower on Saturdays (market absorbs the extra). The policy aligns with the bakery's decision to stay [[Closed on Mondays]] — no stale bread carried over."},

/* ---------- 06-Decisions ---------- */
{path:"06-Decisions/No delivery policy.md",title:"No delivery policy",type:"decision",tags:["decision"],updated:"2026-09-05",
 summary:"Decided in 2021 after a three-month trial: the bakery does not deliver because delivery costs exceeded the margin on a €3.80 loaf and quality suffered from transit time of over 40 minutes.",
 keywords:["no delivery","policy decision","delivery trial","margin too low","quality loss","transit time","shop and market only"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Café Lindström","Saturday market at Piazza Solari"],rev:"2d3e4f5a6b7c",status:"sourced",
 body:"The bakery trialled delivery from March to May 2021 using a third-party courier. Delivery cost per order: €4.20 (minimum), against an average order of €9.50. Bread quality dropped noticeably after 40 minutes in a paper bag. ✅ sourced (trial report, 2021-06).\n\nDecision: no delivery. Customers buy at the shop or at [[Saturday market at Piazza Solari]]. [[Café Lindström]] delivers, but only sandwiches and coffee, not bread. Revisited annually; last review: January 2025 — decision stands."},

{path:"06-Decisions/Closed on Mondays.md",title:"Closed on Mondays",type:"decision",tags:["decision"],updated:"2026-09-05",
 summary:"Decided at opening in 2019: the bakery is closed every Monday for rest, oven maintenance and dough preparation; Monday is also the day Latteria Voss delivers butter for the week.",
 keywords:["closed monday","rest day","oven maintenance","dough preparation","weekly rhythm","butter delivery day","work-life balance"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Marco Trevisan","Latteria Voss","The wood-fired oven"],rev:"3e4f5a6b7c8d",status:"sourced",
 body:"Monday has been the rest day since opening in 2019. [[Marco Trevisan]] uses it for oven maintenance and ash removal from [[The wood-fired oven]]. Long-fermentation doughs (rye, ciabatta) are mixed on Monday evening for Tuesday's first bake. ✅ sourced (operating plan, 2019-03).\n\n[[Latteria Voss]] delivers butter on Monday morning, fitting the rest-day schedule. The partners considered opening seven days a week in 2022 but decided the quality risk was not worth the extra revenue."},

{path:"06-Decisions/Organic certification.md",title:"Organic certification",type:"decision",tags:["decision"],updated:"2026-09-05",
 summary:"Under discussion since early 2025: whether to pursue organic certification for the bakery, which would raise ingredient costs by an estimated 15 % but could justify a price increase and attract new customers.",
 keywords:["organic certification","bio label","cost increase","price premium","certification process","ingredient sourcing","undecided"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Mulino Cerrina","Latteria Voss","Biolievito Kraus","Elsa Nordgren"],rev:"4f5a6b7c8d9e",status:"to-confirm",
 body:"Elsa Nordgren raised the idea in February 2025. [[Mulino Cerrina]] already offers organic-certified flour at a 12 % premium. [[Latteria Voss]] could certify within six months. [[Biolievito Kraus]] is already organic. ⚠ to confirm (internal discussion, 2025-02).\n\nEstimated cost increase: 15 % on ingredients, or about €0.35 per loaf. The partners have not decided; [[Elsa Nordgren]] favours it, Marco is cautious about the paperwork. A decision is expected by September 2025."},

/* ---------- composed document ---------- */
{path:"_docs/Opening the second shop — brief.md",title:"Opening the second shop — brief",type:"document",tags:["composed-document"],updated:"2026-09-05",
 summary:"Composed document for the partners to review before deciding on a second shop: the neighbourhood, the Saturday market, delivery policy, Monday closure and organic certification, with two notes excluded.",
 keywords:["second shop","expansion brief","composed document","partner decision","five fragments","neighbourhood analysis","growth plan"],
 entities:[{name:"Forno Vialetto",type:"company"}],relations:[],links:["Viale Giardini neighbourhood","Saturday market at Piazza Solari","No delivery policy","Closed on Mondays","Organic certification"],rev:"5a6b7c8d9e0f",status:"sourced",
 fragments:["Viale Giardini neighbourhood","Saturday market at Piazza Solari","No delivery policy","Closed on Mondays","Organic certification"],
 pool:["Café Lindström","Panificio Reale"],
 layout:{cover:{title:"Opening the second shop",subtitle:"Partners' reading",date:"2026-09-05"},page:"A4",sections:[{title:"Context",fragments:["Viale Giardini neighbourhood","Saturday market at Piazza Solari"]},{title:"Constraints",fragments:["No delivery policy","Closed on Mondays"]},{title:"Open question",fragments:["Organic certification"]}],show:["summary","status"]},
 body:"Read the five fragments in order. This document assembles what the partners need to review before deciding on a second location.\n\n![[Viale Giardini neighbourhood]]\n![[Saturday market at Piazza Solari]]\n![[No delivery policy]]\n![[Closed on Mondays]]\n![[Organic certification]]\n\nNot included: Café Lindström and Panificio Reale (competitor profiles, in the pool for reference)."}
];
