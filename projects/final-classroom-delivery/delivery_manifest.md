# Final Classroom Delivery Manifest

Generated: 2026-06-24

## Delivery Status

The classroom delivery has been rebuilt around a deeper evidence map and a cleaner narrative:

- HTML manuscript source: `index.qmd`
- Slide source: `slides.qmd`
- Speaker notes: `speaker_notes.md`
- Static HTML manuscript: `classroom_report.html`
- Static slide webpage: `classroom_slides.html`
- PowerPoint backup deck: `final_classroom_delivery.pptx`

Quarto rendering was attempted, but this desktop sandbox could not open Quarto's global Sass/Deno cache database. The escalation request to render with application-cache access was rejected by the runtime usage limit. A local fallback renderer was therefore used to generate `classroom_report.html`, `classroom_slides.html`, and `final_classroom_delivery.pptx` without touching files outside the workspace.

## Evidence Summary

- Raw robustness rows: 126, including duplicate recovery sources.
- Deduplicated representative robustness rows: 84 in the current normalized table.
- DeepSeek exploration package: `mvp_cn/outputs/research_documentation/`.
- Project inventory: `project_timeline_inventory.md`.
- Chapter evidence map: `deep_revision_evidence_map.md`.
- Core evidence tables:
  - `assets/tables/deep_key_version_comparison.csv`
  - `assets/tables/deep_final_robustness_unique.csv`
  - `assets/tables/deep_excess_over_benchmark_metrics.csv`
  - `assets/tables/deep_halfyear_wall_sensitivity.csv`
  - `assets/tables/deep_chapter_evidence_map.csv`

## Main Figures Added Or Rebuilt

- `assets/figures/deep_key_version_comparison.png`
- `assets/figures/deep_excess_over_benchmark.png`
- `assets/figures/deep_final_90_spec_summary.png`
- `assets/figures/deep_not_more_triptych.png`
- `assets/figures/deep_algorithm_equal_weight_surprise.png`
- `assets/figures/deep_wall_scheme_heatmap.png`
- `assets/figures/deep_component_decomposition.png`
- `assets/figures/deep_halfyear_wall_sensitivity.png`
- `assets/figures/deep_market_regime_comparison.png`
- `assets/figures/deep_training_window_diagram.png`

## Labeling Standard

Formal charts avoid internal file or experiment labels. Factors are named by economic meaning, ETF universes are named by portfolio role, and validation walls are shown as "2019年后验证", "2021年后验证", or "2023年后验证".

## Remaining Cleanup

This phase does not delete redundant scripts or intermediate files. Cleanup is tracked separately in `cleanup_backlog.md`.
