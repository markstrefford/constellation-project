# Building the paper

`holding-the-line.md` is the source of truth. Two renders come from it, kept in
lockstep with the source: a theme-aware HTML artifact for on-screen reading, and
`../Holding-the-Line.pdf` - white background, ~11pt paper scale, A4.

Figures live in `figures/` (`galaxy.jpg`, `wealth-kimi-s105.png`) and are
referenced relatively from the markdown; in the rendered HTML they are embedded
as base64 data URIs (the artifact loads no external assets).

## PDF

1. Render the markdown to one self-contained HTML file, all CSS inlined and both
   figures embedded as base64. Screen size is comfortable (~17px body).
2. For print, append the override stylesheet below - it forces a white
   background even from a dark-mode OS, scales the whole document to paper size,
   keeps tables and figures from splitting across page breaks, and shrinks wide
   tables to fit A4.
3. Print with headless Chrome.

Override stylesheet (appended before `</style>`):

    :root { --paper:#ffffff; color-scheme: light; }
    @media (prefers-color-scheme: dark){ :root { /* repeat the LIGHT tokens so a dark OS still prints white */ } }
    html { font-size: 87.5%; }                 /* ~11pt body, paper scale */
    html, body { background:#ffffff !important; }
    .wrap { max-width: 42rem; }
    h2, h3 { break-after: avoid; }
    .tablewrap, figure, .receipt, table { break-inside: avoid; }
    pre.prompt { box-decoration-break: clone; -webkit-box-decoration-break: clone; }
    table { font-size:.72rem; }
    thead th, tbody td { padding:.4rem .45rem; white-space:normal; overflow-wrap:break-word; }
    @page { size: A4; margin: 16mm 14mm; }

Print command:

    google-chrome --headless=new --disable-gpu --no-pdf-header-footer \
      --print-to-pdf=../Holding-the-Line.pdf file://print.html

After a rebuild, rasterise the changed pages and check them - a clipped table, a
missing figure, or a border lost across a page break is only visible in the
rendered output.
