# Figma Design System Rules

## Scope

These rules apply whenever a Figma design is implemented, refined, reviewed, or translated into this repository.

This project is a uni-app / Vue mini program for high-school chemistry teachers. Figma output must be treated as design intent, not as copy-paste application code.

## Required Figma MCP Flow

1. Run `create_design_system_rules(clientLanguages="javascript", clientFrameworks="vue")` when refreshing these rules.
2. For implementation work, run `get_design_context` for the exact Figma node before editing code.
3. If the response is too large or truncated, run `get_metadata`, identify the exact child node, then fetch that child with `get_design_context`.
4. Run `get_screenshot` for the exact node or variant and keep it as the visual reference.
5. Only start implementation after both structured context and screenshot are available.
6. Download or reuse any Figma-provided assets before replacing them with local alternatives.
7. Validate the finished mini program page against the screenshot for hierarchy, spacing, color, typography, and interaction states.

If Figma MCP tools are not exposed in the current agent session, do not pretend the visual context was fetched. State the limitation, use the existing project rules below, and continue only with tasks that do not require direct Figma node inspection.

## Project Structure

- Pages live in `frontend/src/pages/`.
- Shared frontend utilities live in `frontend/src/utils/`.
- Static assets live in `frontend/src/static/`.
- Add reusable UI components under `frontend/src/components/` only when there are at least two real call sites or a clear near-term reuse path.
- Preserve the current single-file Vue page style: `<template>`, `<script>`, and `<style lang="scss" scoped>`.
- Use `uni.*` APIs and existing utility wrappers instead of adding browser-only dependencies.
- API calls should go through `frontend/src/utils/api.js` or a closely related existing utility.

## Styling Rules

- Reuse SCSS tokens from `frontend/src/uni.scss` for core colors, semantic colors, radius, shadows, difficulty colors, and question-type colors.
- Prefer existing page-local visual patterns before adding new tokens.
- Avoid new arbitrary hex colors. If a new color is truly needed, add a named token to `frontend/src/uni.scss` and use it consistently.
- Use `rpx` for mini program layout sizing unless the surrounding code uses another unit for a specific reason.
- Keep touch targets large enough for phone use; primary buttons, chips, and list rows should be easy to tap quickly.
- Preserve existing patterns for navigation bars, search bars, filter chips, cards, modals, empty states, loading states, and bottom action bars.
- Avoid adding a third-party UI library or icon package unless the user explicitly approves it.

## Product UI Conventions

- The UI is a teacher productivity tool, not a landing page.
- Prioritize scanability, dense but readable information, explicit actions, and low learning cost.
- Keep high-frequency actions visible. Do not rely on hidden gestures, long press, or placeholder-only instructions for core workflows.
- Favor calm, utilitarian layouts over decorative hero sections, oversized cards, or marketing-style composition.
- Chemistry content may include LaTeX-like formulas, subscripts, superscripts, OCR text, and attached figures; layouts must not clip or obscure long question content.

## Domain Semantics

- `question_type` and `difficulty` are structural attributes; use explicit segmented, chip, picker, or modal selection controls.
- `book`, `knowledge`, and similar taxonomy values are classification tags; do not mix them into the same chooser as structural attributes.
- `source` is freeform reference text unless a managed source taxonomy is intentionally added.
- Question type and difficulty colors should come from `QUESTION_TYPES`, tag-derived configs, or the SCSS token layer.
- OCR result pages should make review, correction, original-image preview, attached figures, and save actions obvious.

## Assets

- If Figma MCP returns a localhost or file asset URL, use that asset directly or download it into the project as instructed by the MCP output.
- Store approved new assets under `frontend/src/static/`.
- Do not replace real Figma assets with placeholders.
- Do not introduce a new icon package just to mimic Figma icons. Use existing assets, text symbols already used by the project, or Figma-provided assets.

## Implementation Rules

- Translate Figma React/Tailwind examples into this project's uni-app / Vue conventions.
- Do not paste Tailwind classes into Vue files unless Tailwind already exists in the project and is configured for the target platform.
- Keep edits scoped to the target page or component and the smallest necessary supporting utilities.
- Reuse existing helpers such as `frontend/src/utils/util.js`, `frontend/src/utils/type-config.js`, `frontend/src/utils/difficulty.js`, and `frontend/src/utils/time.js` when applicable.
- For display-mapping logic, prefer utility functions over duplicating maps inside pages.
- Preserve safe-area handling for fixed bottom actions.
- Avoid broad refactors while implementing a Figma screen.

## Validation

- For any significant UI implementation, compile the mini program or run the relevant existing build command.
- When WeChat DevTools automation is available, verify the target page visually and check tap behavior.
- At minimum, inspect the changed Vue file for template/style consistency and obvious text overflow or fixed-position overlap.
- Add focused tests only when the change affects shared display logic, data mapping, or nontrivial state transitions.

