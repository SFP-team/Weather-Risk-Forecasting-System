# Research package, 11 October 2026: Astra review and source expansion

Start with the [master plan](source_expansion_and_improvement_plan.md). It has the bottom line, the review of Astra's work, the cross-region findings, a summary for each region, the ingestion design summary, the improvement roadmap, the decisions needed and the verification notes.

## Contents

| Folder or file | Contents |
|---|---|
| [source_expansion_and_improvement_plan.md](source_expansion_and_improvement_plan.md) | Master plan |
| [source_catalog.json](source_catalog.json) | Compact merged index: 824 unique sources and 174 extraction jobs, with statistics |
| [review/](review/) | Reviews of Astra's work: [science](review/astra_science_review.md), [IBO evidence layer](review/astra_ibo_evidence_review.md), [engineering](review/astra_engineering_review.md) |
| [architecture/](architecture/) | [Ingestion and retrieval design](architecture/rag_ingestion_architecture.md) |
| [regions/](regions/) | Ten regional reports, each with a Markdown report and a `.sources.json` list: [US Southeast](regions/us-southeast.md), [US North and West plus Canada](regions/us-north-west-canada.md), [Peru and Mexico](regions/peru-mexico.md), [Chile, Argentina and Uruguay](regions/chile-argentina-uruguay.md), [Brazil, Colombia and Ecuador](regions/brazil-colombia-ecuador.md), [Spain, Portugal and Morocco](regions/iberia-morocco.md), [Central, Northern and Eastern Europe](regions/europe-central-north-east.md), [Africa](regions/africa.md), [China, Japan, Korea and India](regions/china-east-asia-india.md), [Australia and New Zealand](regions/australia-new-zealand.md) |
| [global/](global/) | Cross-region reports: [trade, market and industry](global/market-trade-industry.md), [phenology, weather, land use and literature](global/phenology-weather-landuse-literature.md), [losses, extremes and validation design](global/losses-extremes-validation.md) |

## How it was produced

- **Who did the work.** A coordinating agent ran 17 research agents in parallel: three reviewers, one architect, ten regional researchers and three global researchers. All used Claude Opus 5.5.
- **Output format.** Each research agent followed one contract: verify every URL, record its access and terms, and describe the top sources from real samples. Each wrote a Markdown report and a JSON source list.
- **Coordinator checks.** The coordinator re-checked the high-impact claims (master plan, section 2.5) and corrected one figure. It also removed packages the agents had installed in the repository `.venv` and temporary files they left in local `/tmp`.
- **Scope.** This is research only. Apart from documentation fixes, no application, model or server behaviour changed.

## Source JSON format

Each `*.sources.json` file has `sources` and `rag_jobs`.

- **Source fields:** identity; publisher; countries and subnational scope; categories; blueberry specificity; URLs; format; language; coverage; update frequency; access; licence or terms; extractable fields; app uses; model families; extraction mode; verification status and note; quality caveats; priority; estimated effort.
- **Job fields:** output, extraction method, fields mapped, cadence, review needs, licensing gate, effort, priority and app value.
