# Variety × system cards

Five classes, not one crop. Hours 0-7.2 C, UF 32-45 F, and Dynamic Model portions run in parallel. Do not convert them linearly.

Source of truth: [`packages/analogue/blueberry_analogue/data/variety_cards.yaml`](../../packages/analogue/blueberry_analogue/data/variety_cards.yaml)

| Class | Hours | Portions | Notes |
|---|---|---|---|
| NHB | 800-1200 | 55-90 | Duke heat-sensitive. Inland MI can kill Legacy/Draper fruit buds. |
| Low-chill SHB | 100-250 | 18-40 | Snowchaser bloom is a freeze magnet. O'Neal flower 400 h vs leaf 700 h. |
| High-chill SHB | 350-700 | 35-65 | Star fails south of Ocala. Legacy heat-sensitive (González-Villagra 2024). |
| Rabbiteye | 300-700 | 30-60 | Second RE for pollen. Brightwell cracks if wet at maturity. |
| Evergreen / zero-chill | 0-80 | 0-15 | Prune date sets harvest. Winter DLI leads. Chill is nearly irrelevant. |

System is required: `open_soil | pine_bark | substrate` × `open | tunnel | greenhouse` × `none | net | woven | ldpe` × `deciduous | evergreen`.

Substrate drops soil pH weight to 0. Tunnels cut freeze water about 10× and need Bombus. Covers do not restore chill.
