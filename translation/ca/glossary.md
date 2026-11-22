# Glossari

Terms for the Catalan translation of Metroid Fusion, shared with mzm-cat (Metroid: Zero Mission
en català) wherever the two games name the same thing.

- **APPROVED**: use exactly as written. Every APPROVED term here was approved in mzm-cat
  (its `translation/ca/glossary.md`, or the wording of its shipped text for the save and
  recharge messages) and is reused unchanged.
- **PROPOSED**: new in Fusion. Options in order of preference (1 is the default until
  confirmed), each with a one-line rationale. Every PROPOSED term in use is also listed in
  `notes/translator-notes.md`.

Naming policy, as in mzm-cat: sentence case for item, room and UI names ("Raig de càrrega",
"Sala de navegació"). Proper names and the Galactic Federation keep their capitals. In prose
write "la Samus" and "l'Adam"; no article when someone is addressed ("Samus, ves a…").

`tools/glossary.py import FILE` approves every PROPOSED term that a reference glossary
(mzm-cat's, or AM2R-cat's) already translates, and reports any APPROVED term the reference
translates differently.

Names marked *graphic* are also drawn in a graphic (pause screen, status screen): check their
width there before approving them.

## Characters and factions

| English | Spanish (US ROM) | Catalan | status | notes |
|---|---|---|---|---|
| Samus Aran | Samus Aran | Samus Aran | APPROVED | "la Samus" in prose. |
| Adam Malkovich, Adam | Adam Malkovich | Adam Malkovich, l'Adam | PROPOSED | 1. Unchanged, with the personal article in Samus's prose, like "la Samus". |
| Lady (what Adam called Samus) | señorita | 1. senyoreta<br>2. senyora<br>3. Lady | PROPOSED | 1. Courteous with an edge: "from anyone else it would have sounded sarcastic". As the Spanish.<br>2. More dignified, loses the edge.<br>3. Untranslated nickname. |
| Galactic Federation, the Federation | Federación Galáctica | Federació Galàctica, la Federació | PROPOSED | 1. Only reasonable rendering; still PROPOSED in mzm-cat, where the text never used it. |
| HQ (Galactic Federation HQ) | cuartel general | 1. quarter general<br>2. la central | PROPOSED | 1. Military and literal, as the Spanish.<br>2. Shorter, where a line is tight. |
| CO (commanding officer) | O. J. | 1. comandant<br>2. oficial al comandament | PROPOSED | 1. A rank a reader knows; an abbreviation like the Spanish "O. J." means nothing in Catalan.<br>2. Literal, long. |
| Biologic Space Labs, B.S.L, Biologic | Laboratorios Espaciales Biometrox (B.S.L) | Laboratoris Espacials Biologic (B.S.L), Biologic | PROPOSED | 1. Keeps the company name and the acronym, which is drawn on the station in the cutscenes. The Spanish renamed the company. |
| X parasite(s), the X | parásito X, el X | paràsit(s) X, els X | PROPOSED | 1. "X" is invariable; plural "els X" as in the English ("the X are gathering"). The Spanish uses the singular as a mass noun. |
| SA-X | SA-X | SA-X (l'SA-X) | PROPOSED | 1. Unchanged; apostrophised article because it is read "essa-a-ics". |
| Core-X | X de gran tamaño | 1. nucli X<br>2. X gran | PROPOSED | 1. Names it like the English does; one occurrence.<br>2. Describes it, as the Spanish. |
| Metroid (species) | Metroid | metroide / metroides | APPROVED | Adapted as a common noun, plural with -s. |
| Alpha, Gamma, Zeta, Omega Metroid | Metroides Alfa, Gamma, Zeta, Omega | metroide alfa, gamma, zeta, omega | PROPOSED | 1. Follows "metroide"; the stages as lower-case Greek letter names. |
| infant Metroid, Metroid hatchling | cría de Metroid | cria de metroide | PROPOSED | 1. Literal; the same word for both English terms, which name the same animal. |
| Metroid vaccine | vacuna Metroid | vacuna de metroide | PROPOSED | 1. Made from a metroide cell. |
| Serris | Serris | Serris | PROPOSED | 1. A name. |
| Nightmare | Pesadilla | 1. Malson<br>2. Nightmare | PROPOSED | 1. A nickname the researchers gave it, so it is translated, as the Spanish does.<br>2. Untranslated, as in the series' English material. |
| Etecoons and Dachoras | Etecoones y Dachoras | 1. etecoons i dachores<br>2. Etecoons i Dachoras | PROPOSED | 1. Common nouns with a Catalan plural, like "metroides".<br>2. Untouched. |
| Security Robot, B.O.X. | robot de seguridad, B.O.X. | robot de seguretat, B.O.X. | PROPOSED | 1. Literal; the model name unchanged. |
| crew member | tripulante | tripulant | PROPOSED | 1. Only option. |

## Places

| English | Spanish (US ROM) | Catalan | status | notes |
|---|---|---|---|---|
| SR388 | SR388 | SR388 | PROPOSED | 1. A name. |
| research station, the station | estación de investigación | estació d'investigació, l'estació | PROPOSED | 1. Literal. |
| Main Deck | Cubierta principal | Coberta principal | PROPOSED | 1. Literal. *graphic* (pause screen) |
| Sector 1 (SRX) … Sector 6 (NOC) | Sector 1 -SRX- | Sector 1 (SRX) … Sector 6 (NOC) | PROPOSED | 1. Codes unchanged (they are drawn on the map), with the English parentheses. |
| Reactor Silo | Silo del reactor | Sitja del reactor | PROPOSED | 1. "Sitja" is the Catalan for a silo. |
| Restricted Zone | Zona restringida | Zona restringida | PROPOSED | 1. Literal. |
| Operations Deck | Cubierta de operaciones | Coberta d'operacions | PROPOSED | 1. Literal. |
| Habitation Deck | Cubierta del hábitat | 1. Coberta residencial<br>2. Coberta d'habitatges | PROPOSED | 1. Where the crew lived; short.<br>2. Closer to the English. |
| Docking Bays | Puertos de atraque | 1. Molls d'atracada<br>2. Hangars | PROPOSED | 1. Where ships dock; literal.<br>2. Shorter, less exact. |
| Navigation Room | Sala de navegación | Sala de navegació | PROPOSED | 1. Literal, matches the other "Sala de…" rooms. |
| Data Room | Sala de datos | Sala de dades | PROPOSED | 1. Literal. |
| Security Room | Sala de seguridad | Sala de seguretat | PROPOSED | 1. Literal. |
| Recharge Room | Estación de recarga | Sala de recàrrega | PROPOSED | 1. A room like the others; the Spanish calls it a station. |
| Save Room | Estación de guardado | Sala de guardat | APPROVED | Same verb as the save prompts. |
| Operations Room | Sala de control | Sala d'operacions | PROPOSED | 1. Literal; kept apart from "Sala de control" (Control Room), which the Spanish merges with it. |
| Control Room (Main Boiler) | Sala de control | Sala de control | PROPOSED | 1. Literal. |
| Command Room | sala de mando | sala de comandament | PROPOSED | 1. Literal; one occurrence. |
| Quarantine Bay | Sala de cuarentena | 1. Sala de quarantena<br>2. Zona de quarantena | PROPOSED | 1. "Bay" is a compartment here, not a "badia"; a room like the others, as the Spanish.<br>2. If it should read as bigger than a room. |
| Sub-Zero Containment | Sala de criogenización | 1. Contenció criogènica<br>2. Contenció sota zero | PROPOSED | 1. Says what the room does.<br>2. Literal. |
| Central Reactor Core, Reactor Core | Núcleo del reactor central | Nucli del reactor central, nucli del reactor | PROPOSED | 1. Literal. |
| main silo | silo principal | sitja principal | PROPOSED | 1. Follows "Sitja del reactor". |
| Auxiliary Power Station | Estación de energía auxiliar | Estació d'energia auxiliar | PROPOSED | 1. Literal. |
| Restricted Laboratory, Restricted Lab | Laboratorio de seguridad | Laboratori restringit | PROPOSED | 1. Literal, matches "Zona restringida". |
| Pump Control Unit | Unidad de control de bombeo | Unitat de control de bombament | PROPOSED | 1. Literal. |
| Main Boiler | Caldera principal | Caldera principal | PROPOSED | 1. Literal. |
| Main Boiler Control Room | Sala de control de la caldera | Sala de control de la caldera | PROPOSED | 1. As the Spanish; "principal" doesn't fit the banner. |
| breeding environments | entornos de cría | entorns de cria | PROPOSED | 1. Literal. |
| breeding tank | tanque de cría | tanc de cria | PROPOSED | 1. Literal. |
| Main Elevator, Elevator 1 | ascensor principal, ascensor 1 | ascensor principal, ascensor 1 | PROPOSED | 1. Only option. |
| access shaft | puerto de conexión | pou d'accés | PROPOSED | 1. The vertical shaft the elevators leave from. |
| ship, starship | nave | nau | APPROVED | mzm-cat: "Nau de la Samus". |
| escape pod | vaina de escape | càpsula de salvament | PROPOSED | 1. The usual Catalan term. |

## Equipment and abilities

| English | Spanish (US ROM) | Catalan | status | notes |
|---|---|---|---|---|
| Power Suit | traje | Vestit | APPROVED | Lower case in prose: "el meu vestit". |
| Varia Suit | Traje climático | Vestit climàtic | APPROVED | |
| Gravity Suit | Traje gravitatorio | Vestit gravitatori | APPROVED | |
| Energy Tank | Tanque de energía | Tanc d'energia | APPROVED | |
| Missile | Misil | Míssil | APPROVED | *graphic* |
| Missile Tank | Tanque de misiles | Tanc de míssils | APPROVED | |
| Super Missile | Supermisil | Supermíssil | APPROVED | |
| Ice Missile | (misiles mejorados con hielo) | Míssil de gel | PROPOSED | 1. Parallel to "Raig de gel". |
| Diffusion Missile | (misiles mejorados con difusión) | Míssil de difusió | PROPOSED | 1. Literal. |
| Bomb | Bomba | Bomba | APPROVED | |
| Power Bomb | Bomba de energía | Bomba d'energia | APPROVED | |
| Power Bomb Tank | Tanque de bomba de energía | Tanc de bombes d'energia | APPROVED | |
| Charge Beam | Rayo recarga | Raig de càrrega | APPROVED | |
| Wide Beam | Rayo ancho | Raig ample | PROPOSED | 1. Literal, as the Spanish. |
| Wave Beam | Rayo de ondas | Raig d'ones | APPROVED | |
| Plasma Beam | Rayo de plasma | Raig de plasma | APPROVED | |
| Ice Beam | Rayo de hielo | Raig de gel | APPROVED | |
| Morph Ball | Morfosfera | Morfosfera | APPROVED | |
| Hi-Jump | Supersalto | Supersalt | APPROVED | |
| Jumpball | Rotosalto | 1. Morfosalt<br>2. Salt en morfosfera | PROPOSED | 1. One word built like "Morfosfera": the jump you do as a ball.<br>2. Descriptive, long for the banner. |
| Speed Booster | Aceleración | Acceleració | APPROVED | |
| Space Jump | Salto espacial | Salt espacial | APPROVED | |
| Screw Attack | Salto en barrena | Atac espiral | APPROVED | |
| Shinespark | técnica cometa | 1. salt llampec<br>2. tècnica cometa | PROPOSED | 1. Names the flash and the leap; one occurrence, in a hidden message.<br>2. As the Spanish. |
| Somersault (spin jump) | (salta, arrasa) | tombarella (gir for short) | APPROVED | "en ple gir" where space is short. |
| latent abilities | habilidades latentes | habilitats latents | PROPOSED | 1. Literal. |
| Hatch (door) | puerta | comporta | APPROVED | "comportes blaves", "comportes de nivell 1". |
| security level, Level 1 | nivel 1 de seguridad | nivell de seguretat, nivell 1 | PROPOSED | 1. Literal. |
| security lock | bloqueo | bloqueig de seguretat | PROPOSED | 1. Literal; "desblocar" for "release". |
| Damage (noun) | daño | dany | APPROVED | |

## Mission terms

| English | Spanish (US ROM) | Catalan | status | notes |
|---|---|---|---|---|
| target (map marker and "Proceed to target") | alerta | 1. objectiu<br>2. destinació | PROPOSED | 1. What the mission aims at; also translates "objective", so the pause screen and the briefings agree. *graphic* (TARGET on the map)<br>2. Only a place, wrong for "Target eradicated". |
| Target eradicated. | Alerta desactivada. | Objectiu eliminat. | PROPOSED | 1. Follows "objectiu". |
| objective | misión | objectiu | PROPOSED | 1. Literal. *graphic* (OBJECTIVE on the pause screen) |
| bio-signs | signos de vida | 1. senyals de vida<br>2. biosenyals | PROPOSED | 1. Natural, as the Spanish.<br>2. Closer to the English coinage. |
| atmospheric stabilizer | estabilizador atmosférico | estabilitzador atmosfèric | PROPOSED | 1. Literal. |
| online / offline | en línea / desconectado | en línia / fora de línia | PROPOSED | 1. The standard pair (TERMCAT). |
| cooling unit | unidad de refrigeración | unitat de refrigeració | PROPOSED | 1. Literal. |
| auxiliary power | energía auxiliar | energia auxiliar | PROPOSED | 1. Literal. |
| self-destruct | autodestrucción | autodestrucció | PROPOSED | 1. Only option. |
| support data, weapons data | datos de apoyo, datos de armamento | dades de suport, dades d'armament | PROPOSED | 1. Literal. |
| download (verb, noun) | descargar | 1. baixar, baixada<br>2. descarregar, descàrrega | PROPOSED | 1. TERMCAT and Softcatalà's preferred verb.<br>2. Also correct, and closer to the Spanish. |
| uplink (to Adam) | conectar | connectar, connexió | APPROVED | mzm-cat: "Connectant / connexió". |
| briefing | informe | instruccions | PROPOSED | 1. What Adam gives; "ordres" where he commands. |
| mimic (what the X do) | mimetizar | imitar | PROPOSED | 1. Plain and exact. |
| host (of a parasite) | huésped | hoste | PROPOSED | 1. The biological term. |
| life-form | ser, forma de vida | forma de vida | PROPOSED | 1. Literal. |

## UI terms

| English | Spanish (US ROM) | Catalan | status | notes |
|---|---|---|---|---|
| Save (verb) | Almacenar | Guardar | APPROVED | Matches "Sala de guardat". |
| Save data? | ¿Almacenar datos? | Guardar? | APPROVED | mzm-cat's save prompt. |
| Save complete. | Datos almacenados. | Partida guardada. | APPROVED | |
| Yes / No | Sí / No | Sí / No | APPROVED | |
| Sleep Mode | salvapantallas | Mode repòs | APPROVED | mzm-cat's "Easy Sleep". *graphic* (SLEEP tab) |
| Weapons system resupply | Reabastecimiento del armamento | Reposició de l'armament | APPROVED | mzm-cat's recharge message. |
| acquired (tank) | almacenado | obtingut | APPROVED | mzm-cat: "Tanc d'energia obtingut." |
| capacity increased | capacidad ampliada | capacitat augmentada | APPROVED | |
| recovered / regained / restored (ability) | recuperado | recuperat, recuperada | PROPOSED | 1. One word for the three English verbs, as the Spanish does. |
| absorbed (ability) | asimilada | absorbida | PROPOSED | 1. Literal: Samus absorbs the X that carries it. |
| Button (SELECT, L and R Buttons) | Botón | botó | PROPOSED | 1. Only option. |
