# Presence Rx Webapp

This is the marketer-facing dashboard for Presence Rx.

It turns generated Presence Rx artifacts into an interactive workflow:

- action brief
- conversation blocks
- claims and simulator
- charts
- future-direction previews
- export tools

## Run Locally

```bash
npm install
npm run dev
```

Open the local URL printed by Next.js.

## Verify

```bash
npm run build
npm run lint
```

## Data

The app reads static case-study data from:

```text
public/data/
```

Those files are generated from the Python pipeline and copied into the webapp for the demo surface.

