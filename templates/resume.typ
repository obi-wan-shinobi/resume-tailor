// Resume Template — Shreyas Kalvankar
// Faithful Typst port of the LaTeX resume (sources/resume.tex).
// Static content is hardcoded. Dynamic content is loaded from a JSON data file.
//
// Usage:
//   typst compile templates/resume.typ --input data=examples/sample_tailored.json
//
// Or via the Python renderer which passes sys.inputs.data automatically.

#import "@preview/fontawesome:0.6.2": *

// ── Load Dynamic Data ──
#let data = json("../" + sys.inputs.at("data"))

// ── Page Setup ──
#set page(
  paper: "a4",
  margin: 0.7in,
  header: none,
  footer: none,
)
#set text(size: 10pt, font: "New Computer Modern")
#set par(justify: true, leading: 0.55em, spacing: 0.6em)

// List styling to match LaTeX: leftmargin=1.2em, itemsep=0.2em, topsep=0.15em
#set list(
  indent: 0.2em,
  body-indent: 0.5em,
  spacing: 0.8em,
  marker: sym.bullet,
)

// Link styling — match LaTeX \definecolor{linkblue}{HTML}{1F4E79}
#show link: set text(fill: rgb("#1F4E79"))

// ── Helper Functions ──

// Section heading: \titleformat{\section}{\large\bfseries}{}{0em}{}[\titlerule]
// with \titlespacing*{\section}{0pt}{0.8em}{0.4em}
#let section-heading(title) = {
  v(0.8em)
  text(size: 12pt, weight: "bold", title)
  v(-3pt)
  line(length: 100%, stroke: 0.5pt)
}

// Resume heading macro — matches \resumeheading{company}{dates}{role}{location}
//   \textbf{#1} \hfill #2\\[-0.15em]
//   \textit{#3} \hfill \textit{#4}\\[-1.5em]
#let resume-heading(company, dates, role, location) = {
  grid(
    columns: (1fr, auto),
    align: (left, right),
    text(weight: "bold", company),
    dates,
  )
  v(-0.15em)
  grid(
    columns: (1fr, auto),
    align: (left, right),
    text(style: "italic", role),
    text(style: "italic", location),
  )
  v(0.5em)
}

// Project heading — name bold top-left, kind + URL italic on second line
#let project-heading(name, kind, url) = {
  text(weight: "bold", name)
  v(-0.15em)
  [_#kind --- #link("https://" + url)[#url]_]
  // v(-1.1em)
}


// ════════════════════════════════════════════════════════════════════
// STATIC: Header
// ════════════════════════════════════════════════════════════════════

#align(center)[
  #text(size: 17.28pt, weight: "bold")[Shreyas Kalvankar]
  // #v(0.3em)

  #text(size: 10pt)[
    #fa-icon("phone") +31 616243845
    #h(5pt) | #h(5pt)
    #fa-icon("envelope", solid: true) #link("mailto:shreyaskalvankar@gmail.com")[shreyaskalvankar\@gmail.com]
  ]

  // #v(0.25em)
  #text(size: 10pt)[
    #fa-icon("globe", solid: true) #link("https://obi-wan-shinobi.github.io")[obi-wan-shinobi.github.io]
    #h(5pt) | #h(5pt)
    #fa-icon("linkedin") #link("https://linkedin.com/in/shreyas-kalvankar")[linkedin.com/in/shreyas-kalvankar]
    #h(5pt) | #h(5pt)
    #fa-icon("github") #link("https://github.com/obi-wan-shinobi")[github.com/obi-wan-shinobi]
  ]
  #v(-0.5em)
]

// ════════════════════════════════════════════════════════════════════
// STATIC: Education
// ════════════════════════════════════════════════════════════════════

#section-heading("Education")

#resume-heading(
  "Technische Universiteit Delft",
  "September 2024 – July 2026",
  "MSc Computer Science – Machine Learning Applications Engineering & Algorithmics",
  "Delft, Netherlands",
)
- Master's thesis: Neural network training dynamics and spectral bias \
  Investigated spectral bias and training dynamics of overparameterized neural networks, combining NTK theory, Fourier/operator analysis, and numerical experiments to study how finite width and sampling affect feature learning.

#v(0.3em)

#resume-heading(
  "Savitribai Phule Pune University",
  "August 2017 – May 2021",
  "Bachelor of Engineering in Computer Engineering",
  "Pune, India",
)
- Bachelor's thesis: Astronomical Image Colorization and Super-resolution using GANs

// ════════════════════════════════════════════════════════════════════
// DYNAMIC: Experience
// ════════════════════════════════════════════════════════════════════

#section-heading("Experience")

#for (i, exp) in data.experience.enumerate() {
  resume-heading(exp.company, exp.dates, exp.role, exp.location)
  for bullet in exp.bullets {
    [- #bullet]
  }
  if i < data.experience.len() - 1 {
    v(0.3em)
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
  project-heading(proj.name, proj.kind, proj.url)
  for bullet in proj.bullets {
    [- #bullet]
  }
  if i < data.projects.len() - 1 {
    v(0.3em)
  }
}

// ════════════════════════════════════════════════════════════════════
// STATIC: Publications & Pre-prints
// ════════════════════════════════════════════════════════════════════

#section-heading("Publications & Pre-prints")

- *#link("https://dl.gi.de/items/0ff89330-3adf-49b3-8071-53eb7f176488")[Astronomical Image Colorization and Up-scaling with Conditional Generative Adversarial Networks]*, INFORMATIK 2022
- *#link("https://arxiv.org/abs/2005.11288")[EinsteinPy: A Community Python Package for General Relativity]*, arXiv:2005.11288
- *#link("https://arxiv.org/abs/2008.13611")[Galaxy Morphology Classification using EfficientNet Architectures]*, arXiv:2008.13611

// ════════════════════════════════════════════════════════════════════
// STATIC: Languages
// ════════════════════════════════════════════════════════════════════

#section-heading("Languages")

English (Fluent, IELTS 8.5, CEFR C2), Dutch (Elementary), Japanese (Elementary)
