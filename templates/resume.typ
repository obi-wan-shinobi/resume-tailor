// Resume Template — Shreyas Kalvankar
// Static content is hardcoded. Dynamic content is loaded from a JSON data file.
//
// Usage:
//   typst compile templates/resume.typ --input data=examples/sample_tailored.json output.pdf
//
// Or via the Python renderer which passes sys.inputs.data automatically.

// ── Load Dynamic Data ──
#let data = json("../" + sys.inputs.at("data"))

// ── Page Setup ──
#set page(
  paper: "a4",
  margin: (top: 0.35in, bottom: 0.35in, left: 0.45in, right: 0.45in),
)
#set text(size: 10pt, font: "New Computer Modern")
#set par(justify: true, leading: 0.55em)
#set list(indent: 0.3em, body-indent: 0.4em, spacing: 5pt)

// ── Helper Functions ──

// Section heading with a horizontal rule
#let section-heading(title) = {
  v(5pt)
  text(size: 11.5pt, weight: "bold", title)
  v(-6pt)
  line(length: 100%, stroke: 0.6pt)
  v(1pt)
}

// Two-column row: left content, right content
#let header-row(left-content, right-content) = {
  grid(
    columns: (1fr, auto),
    align: (left, right),
    left-content,
    right-content,
  )
}

// ════════════════════════════════════════════════════════════════════
// STATIC: Header
// ════════════════════════════════════════════════════════════════════

#align(center)[
  #text(size: 22pt, weight: "bold")[Shreyas Kalvankar]
  #v(-2pt)
  #text(size: 9.5pt)[
    +31 616243845 #h(4pt) | #h(4pt)
    #link("mailto:shreyaskalvankar@gmail.com")[shreyaskalvankar\@gmail.com] #h(4pt) | #h(4pt)
    #link("https://obi-wan-shinobi.github.io")[obi-wan-shinobi.github.io]
    #linebreak()
    #link("https://linkedin.com/in/shreyas-kalvankar")[linkedin.com/in/shreyas-kalvankar] #h(4pt) | #h(4pt)
    #link("https://github.com/obi-wan-shinobi")[github.com/obi-wan-shinobi]
  ]
]

// ════════════════════════════════════════════════════════════════════
// STATIC: Education
// ════════════════════════════════════════════════════════════════════

#section-heading("Education")

#header-row(
  text(weight: "bold")[Technische Universiteit Delft],
  text(style: "italic")[September 2024 – July 2026],
)
#header-row(
  text(style: "italic")[MSc Computer Science – Machine Learning Applications Engineering & Algorithmics],
  text(style: "italic")[Delft, Netherlands],
)
- Master's thesis: Neural network training dynamics and spectral bias \
  Investigated spectral bias and training dynamics of overparameterized neural networks, combining NTK theory, Fourier/operator analysis, and numerical experiments to study how finite width and sampling affect feature learning.

#v(2pt)

#header-row(
  text(weight: "bold")[Savitribai Phule Pune University],
  text(style: "italic")[August 2017 – May 2021],
)
#header-row(
  text(style: "italic")[Bachelor of Engineering in Computer Engineering],
  text(style: "italic")[Pune, India],
)
- Bachelor's thesis: Astronomical Image Colorization and Super-resolution using GANs

// ════════════════════════════════════════════════════════════════════
// DYNAMIC: Experience
// ════════════════════════════════════════════════════════════════════

#section-heading("Experience")

#for (i, exp) in data.experience.enumerate() {
  header-row(
    text(weight: "bold", exp.company),
    text(style: "italic", exp.dates),
  )
  header-row(
    text(style: "italic", exp.role),
    text(style: "italic", exp.location),
  )
  for bullet in exp.bullets {
    [- #bullet]
  }
  // Add spacing between entries, but not after the last one
  if i < data.experience.len() - 1 {
    v(3pt)
  }
}

// ════════════════════════════════════════════════════════════════════
// DYNAMIC: Technical Skills
// ════════════════════════════════════════════════════════════════════

#section-heading("Technical Skills")

#for (category, items) in data.skills {
  [*#category:* #items.join(", ") \ ]
}

// ════════════════════════════════════════════════════════════════════
// DYNAMIC: Projects
// ════════════════════════════════════════════════════════════════════

#section-heading("Projects")

#for (i, proj) in data.projects.enumerate() {
  header-row(
    [*#proj.name* #h(8pt) #text(style: "italic", proj.kind)],
    text(size: 9pt, link("https://" + proj.url, proj.url)),
  )
  for bullet in proj.bullets {
    [- #bullet]
  }
  if i < data.projects.len() - 1 {
    v(3pt)
  }
}

// ════════════════════════════════════════════════════════════════════
// STATIC: Publications & Pre-prints
// ════════════════════════════════════════════════════════════════════

#section-heading("Publications & Pre-prints")

- Astronomical Image Colorization and Up-scaling with Conditional Generative Adversarial Networks, INFORMATIK 2022
- EinsteinPy: A Community Python Package for General Relativity, arXiv:2005.11288
- Galaxy Morphology Classification using EfficientNet Architectures, arXiv:2008.13611

// ════════════════════════════════════════════════════════════════════
// STATIC: Languages
// ════════════════════════════════════════════════════════════════════

#section-heading("Languages")

English (Fluent, IELTS 8.5, CEFR C2), Dutch (Elementary), Japanese (Elementary)
