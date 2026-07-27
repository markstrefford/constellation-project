# Building the paper

`holding-the-line.md` is the source of truth. Two renders come from it, kept in
lockstep with the source: a theme-aware HTML artifact for on-screen reading
(`holding-the-line.html`, committed here so the build is regenerable), and
`../Holding-the-Line.pdf` - white background, ~11pt paper scale, A4.

Figures live in `figures/` (`galaxy.jpg`, `wealth-kimi-s105.png`) and are
referenced relatively from the markdown; in the rendered HTML they are embedded
as base64 data URIs (the artifact loads no external assets).

## First page (arXiv style)

The first page follows arXiv conventions: centred serif title, centred author
line (`Mark Strefford  Orion`) with affiliation and the Orion research-agent
note beneath it, a centred date, then a centred bold "Abstract" heading over a
narrower justified abstract block with no panel background. A rotated stamp
runs bottom-to-top along the left edge of page one in the arXiv visual grammar,
but carries real provenance, never a fabricated arXiv identifier:

    Reimagined Industries . Constellation . Agentic Economy Playbooks, study one . 27 Jul 2026

In the HTML this is `.arxiv-head`, the restyled `.abstract`, and `.arxiv-stamp`.
On screen the stamp hides below ~62rem viewport width.

## PDF

1. Start from `holding-the-line.html` (screen render, all CSS inlined, figures
   embedded as base64).
2. For print, append the override stylesheet below before `</style>` and wrap
   in a minimal `<!doctype html>...<body>...</body>` document. It forces a
   white background even from a dark-mode OS, scales the document to paper
   size, keeps tables and figures from splitting across page breaks, shrinks
   wide tables to fit A4, and positions the left-edge stamp.
3. Print with headless Chrome.

Override stylesheet:

    :root { --paper:#ffffff; color-scheme: light; }
    @media (prefers-color-scheme: dark){ :root { /* repeat the LIGHT tokens so a dark OS still prints white */ } }
    html { font-size: 87.5%; }                 /* ~11pt body, paper scale */
    html, body { background:#ffffff !important; }
    .wrap { max-width:42rem; animation:none; padding-top:1.2rem; }
    h2, h3 { break-after:avoid; }
    .tablewrap, figure.fig, figure.fig-full, .receipt, table { break-inside:avoid; }
    .tablewrap { overflow:visible; }
    pre.prompt { -webkit-box-decoration-break:clone; box-decoration-break:clone; }
    table { font-size:.72rem; }
    thead th, tbody td { padding:.4rem .45rem; white-space:normal; overflow-wrap:break-word; }
    .rng { white-space:nowrap; font-size:.68rem; }
    .arxiv-stamp { display:block !important; position:absolute; top:28mm; left:0; font-size:.76rem; opacity:.8; }
    @page { size: A4; margin: 16mm 6mm; }

The side margins are 6mm (not 14mm) because headless Chrome clips any
absolutely-positioned content that falls outside the page content box - a
stamp at a negative `left` inside a 14mm margin simply disappears from the
PDF. Instead the printable area extends to 6mm from the paper edge, the text
column keeps its width via `.wrap { max-width:42rem }`, and the stamp sits at
`left:0`, i.e. 6mm in from the edge. The `display:block !important` beats the
screen media query that would otherwise hide the stamp at print viewport width.

Print command:

    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
      --disable-gpu --no-pdf-header-footer \
      --print-to-pdf=../Holding-the-Line.pdf file://print.html

After a rebuild, rasterise the changed pages and check them - a clipped table,
a missing figure, a border lost across a page break, or a vanished margin
stamp is only visible in the rendered output.

## First-page snapshot (for posts)

A share-ready PNG of page one, rasterised from the built PDF:

    python3 -c "
    import fitz
    d = fitz.open('../Holding-the-Line.pdf')
    d[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5)).save('holding-the-line-page1.png')
    "

Keep the snapshot out of this repo (it is marketing collateral, not evidence);
it lives with drafts in the private repo's `sdlc/raw/`.
