# Point — From Number Theory to Algebraic Geometry and Logic
### نقطه: از نظریه اعداد تا هندسه جبری و منطق

A self-contained, year-long course (**64 meetings**: P1–P3 + S1–S61) that traces one unifying
concept — **the point** — from primes and valuations, through schemes and Class Field Theory,
to topoi and Deligne's theorem. Every main theorem is proved; all prerequisites are built
inside the course, just in time.

یک دوره‌ی یک‌ساله‌ی خودکفا (۶۴ جلسه) که یک مفهوم واحد — **نقطه** — را از اعداد اول و ارزش‌گذاری‌ها،
از میان اسکیم‌ها و نظریه‌ی میدان‌های طبقاتی، تا توپوس‌ها و قضیه‌ی دلین پی می‌گیرد.
همه‌ی قضایای اصلی با اثبات‌اند و همه‌ی پیش‌نیازها داخل خود دوره ساخته می‌شوند.

## What's in this repository / چه چیزی این‌جاست

| Path | What it is |
|---|---|
| [`index.html`](index.html) | Interactive syllabus (acts, sessions, proofs listed, references). Best via GitHub Pages. |
| [`dependencies.html`](dependencies.html) | Interactive dependency DAG: shortest track & critical chain per session. |
| [`syllabus/syllabus.tex`](syllabus/syllabus.tex) / [`syllabus/syllabus.pdf`](syllabus/syllabus.pdf) | Printable detailed syllabus. |
| [`lectures/`](lectures/) | Full lecture notes, one LaTeX (+PDF) file per session. |
| [`tools/sessions.json`](tools/sessions.json) | Manifest of all 64 sessions (id, act, title, slug). |
| [`tools/update_readme.py`](tools/update_readme.py) | Regenerates the sessions table below from the manifest + files on disk. |

Online (GitHub Pages): <https://masoudmz.github.io/point-course/> — syllabus at `/`, dependency diagram at `/dependencies.html`.

## Course map & sessions / نقشه‌ی دوره و جلسات

<!-- SESSIONS:START -->

> **Progress:** 4/64 sessions have compiled lecture notes.


### Prelude — Essential Prerequisites

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| P1 | Group Theory: Part I | [site](https://masoudmz.github.io/point-course/#sP1) | [tex](lectures/P1-groups.tex) | [pdf](lectures/P1-groups.pdf) | ✅ done |
| P2 | Topology and Metric Spaces | [site](https://masoudmz.github.io/point-course/#sP2) | [tex](lectures/P2-topology.tex) | [pdf](lectures/P2-topology.pdf) | ✅ done |
| P3 | Algebraic Topology Crash Course | [site](https://masoudmz.github.io/point-course/#sP3) | [tex](lectures/P3-algtop.tex) | [pdf](lectures/P3-algtop.pdf) | ✅ done |

### Act 0 — Foundations

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S1 | Rings, Ideals, Quotients, Prime & Maximal Ideals | [site](https://masoudmz.github.io/point-course/#s1) | [tex](lectures/S1-rings.tex) | [pdf](lectures/S1-rings.pdf) | ✅ done |
| S2 | Modules, Tensor Products, and Exact Sequences | [site](https://masoudmz.github.io/point-course/#s2) | — | — | 🚧 planned |
| S3 | Fields, Extensions, and Algebraic Closure | [site](https://masoudmz.github.io/point-course/#s3) | — | — | 🚧 planned |
| S4 | Category Theory Essentials | [site](https://masoudmz.github.io/point-course/#s4) | — | — | 🚧 planned |

### Act I — The Point as a Prime Number

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S5 | Quadratic Residues and the Legendre Symbol | [site](https://masoudmz.github.io/point-course/#s5) | — | — | 🚧 planned |
| S6 | Quadratic Reciprocity: Statement and First Proof | [site](https://masoudmz.github.io/point-course/#s6) | — | — | 🚧 planned |
| S7 | Quadratic Reciprocity: Geometric Proofs & Generalizations | [site](https://masoudmz.github.io/point-course/#s7) | — | — | 🚧 planned |
| S8 | Reciprocity in the Language of Galois Theory | [site](https://masoudmz.github.io/point-course/#s8) | — | — | 🚧 planned |
| S9 | Cyclotomic Extensions and Frobenius Elements | [site](https://masoudmz.github.io/point-course/#s9) | — | — | 🚧 planned |
| S10 | Summary: From Reciprocity to Galois Theory | [site](https://masoudmz.github.io/point-course/#s10) | — | — | 🚧 planned |

### Act II — Galois Theory and Solvability

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S11 | Solvable Groups, Sₙ, and Aₙ | [site](https://masoudmz.github.io/point-course/#s11) | — | — | 🚧 planned |
| S12 | Galois Extensions, Finite Fields, and Linear Independence | [site](https://masoudmz.github.io/point-course/#s12) | — | — | 🚧 planned |
| S13 | The Fundamental Theorem of Galois Theory | [site](https://masoudmz.github.io/point-course/#s13) | — | — | 🚧 planned |
| S14 | Solvable Groups and Solvability by Radicals | [site](https://masoudmz.github.io/point-course/#s14) | — | — | 🚧 planned |
| S15 | The Insolvability of the Quintic | [site](https://masoudmz.github.io/point-course/#s15) | — | — | 🚧 planned |
| S16 | The Absolute Galois Group | [site](https://masoudmz.github.io/point-course/#s16) | — | — | 🚧 planned |

### Act III — Valuations and p-adic Points

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S17 | Absolute Values, Valuations, and Ostrowski's Theorem | [site](https://masoudmz.github.io/point-course/#s17) | — | — | 🚧 planned |
| S18 | Construction of ℚₚ and ℤₚ | [site](https://masoudmz.github.io/point-course/#s18) | — | — | 🚧 planned |
| S19 | Hensel's Lemma and p-adic Topology | [site](https://masoudmz.github.io/point-course/#s19) | — | — | 🚧 planned |
| S20 | Extension of Valuations: Ramification and Residue Degree | [site](https://masoudmz.github.io/point-course/#s20) | — | — | 🚧 planned |
| S21 | Function Fields and the Geometric Analogy | [site](https://masoudmz.github.io/point-course/#s21) | — | — | 🚧 planned |
| S22 | Adeles, Ideles, and Adelic Compactness | [site](https://masoudmz.github.io/point-course/#s22) | — | — | 🚧 planned |

### Act IV — Algebraic Geometry

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S23 | Commutative Algebra I | [site](https://masoudmz.github.io/point-course/#s23) | — | — | 🚧 planned |
| S24 | Dedekind Domains and Ideal Class Groups | [site](https://masoudmz.github.io/point-course/#s24) | — | — | 🚧 planned |
| S25 | Affine Varieties and Hilbert's Nullstellensatz | [site](https://masoudmz.github.io/point-course/#s25) | — | — | 🚧 planned |
| S26 | Presheaves and Sheaves | [site](https://masoudmz.github.io/point-course/#s26) | — | — | 🚧 planned |
| S27 | Sheafification, Categories of Sheaves, and Étale Spaces | [site](https://masoudmz.github.io/point-course/#s27) | — | — | 🚧 planned |
| S28 | Schemes: Spec(R), the Structure Sheaf, Closed & Generic Points | [site](https://masoudmz.github.io/point-course/#s28) | — | — | 🚧 planned |
| S29 | The Functor of Points and Yoneda's Perspective | [site](https://masoudmz.github.io/point-course/#s29) | — | — | 🚧 planned |
| S30 | Commutative Algebra II: Morphisms, Fiber Products, Étale Maps | [site](https://masoudmz.github.io/point-course/#s30) | — | — | 🚧 planned |
| S31 | Projective Varieties and Points at Infinity | [site](https://masoudmz.github.io/point-course/#s31) | — | — | 🚧 planned |
| S32 | Divisors, the Product Formula, and Riemann–Roch | [site](https://masoudmz.github.io/point-course/#s32) | — | — | 🚧 planned |
| S33 | The Valuative Criterion of Properness | [site](https://masoudmz.github.io/point-course/#s33) | — | — | 🚧 planned |
| S34 | Free Groups and Profinite Groups | [site](https://masoudmz.github.io/point-course/#s34) | — | — | 🚧 planned |
| S35 | Étale Fundamental Group and Grothendieck's Galois Theory | [site](https://masoudmz.github.io/point-course/#s35) | — | — | 🚧 planned |
| S36 | Summary: The Bridge Between Number Theory and Geometry | [site](https://masoudmz.github.io/point-course/#s36) | — | — | 🚧 planned |

### Act V — Curves over ℂ and Elliptic Curves

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S37 | Complex Analysis I: Holomorphic Functions & Cauchy Theory | [site](https://masoudmz.github.io/point-course/#s37) | — | — | 🚧 planned |
| S38 | Complex Analysis II: Riemann Surfaces | [site](https://masoudmz.github.io/point-course/#s38) | — | — | 🚧 planned |
| S39 | Elliptic Curves: Geometry and Group Law | [site](https://masoudmz.github.io/point-course/#s39) | — | — | 🚧 planned |
| S40 | Elliptic Curves: Arithmetic and Modular Forms | [site](https://masoudmz.github.io/point-course/#s40) | — | — | 🚧 planned |
| S41 | Points as Objects: Moduli Spaces and Arithmetic | [site](https://masoudmz.github.io/point-course/#s41) | — | — | 🚧 planned |

### Act VI — Class Field Theory

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S42 | Homological Algebra I | [site](https://masoudmz.github.io/point-course/#s42) | — | — | 🚧 planned |
| S43 | Homological Algebra II | [site](https://masoudmz.github.io/point-course/#s43) | — | — | 🚧 planned |
| S44 | Group Cohomology and Tate Cohomology | [site](https://masoudmz.github.io/point-course/#s44) | — | — | 🚧 planned |
| S45 | Galois Cohomology and the Fundamental Exact Sequence | [site](https://masoudmz.github.io/point-course/#s45) | — | — | 🚧 planned |
| S46 | The Artin Map | [site](https://masoudmz.github.io/point-course/#s46) | — | — | 🚧 planned |
| S47 | Artin Reciprocity | [site](https://masoudmz.github.io/point-course/#s47) | — | — | 🚧 planned |
| S48 | The Existence Theorem | [site](https://masoudmz.github.io/point-course/#s48) | — | — | 🚧 planned |
| S49 | The Idele Formulation and Global CFT | [site](https://masoudmz.github.io/point-course/#s49) | — | — | 🚧 planned |
| S50 | Local Class Field Theory: Lubin–Tate | [site](https://masoudmz.github.io/point-course/#s50) | — | — | 🚧 planned |

### Interlude — Spaces without Points

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S51 | Gelfand–Naimark and Pointless Spaces | [site](https://masoudmz.github.io/point-course/#s51) | — | — | 🚧 planned |

### Act VII — Topos Theory and Logic

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S52 | Sites and Grothendieck Topologies | [site](https://masoudmz.github.io/point-course/#s52) | — | — | 🚧 planned |
| S53 | Sheaves on Sites and Topoi | [site](https://masoudmz.github.io/point-course/#s53) | — | — | 🚧 planned |
| S54 | Geometric Morphisms and Points of a Topos | [site](https://masoudmz.github.io/point-course/#s54) | — | — | 🚧 planned |
| S55 | Enough Points | [site](https://masoudmz.github.io/point-course/#s55) | — | — | 🚧 planned |
| S56 | Classifying Topoi and Geometric Theories | [site](https://masoudmz.github.io/point-course/#s56) | — | — | 🚧 planned |
| S57 | Geometric Model Theory | [site](https://masoudmz.github.io/point-course/#s57) | — | — | 🚧 planned |
| S58 | Deligne's Theorem: Statement and Proof | [site](https://masoudmz.github.io/point-course/#s58) | — | — | 🚧 planned |
| S59 | Deligne's Theorem in Algebraic Geometry | [site](https://masoudmz.github.io/point-course/#s59) | — | — | 🚧 planned |

### Postlude — Synthesis and the Big Picture

| ID | Session | Online | LaTeX | PDF | Status |
|:--:|---|---|:--:|:--:|:--:|
| S60 | The Point: One Concept, Three Worlds | [site](https://masoudmz.github.io/point-course/#s60) | — | — | 🚧 planned |
| S61 | Open Discussion: Points in Physics, Non-commutative Geometry, and Langlands | [site](https://masoudmz.github.io/point-course/#s61) | — | — | 🚧 planned |

<!-- SESSIONS:END -->

## Reading order & prerequisites / ترتیب مطالعه و پیش‌نیازها

The sessions are linearly ordered (P1→…→S61), but the *dependency* structure is a DAG:
open [`dependencies.html`](dependencies.html) to see, for any session, the **shortest track**
(fastest route) and the **critical chain** (longest prerequisite chain = scheduling constraint).
Example: the fastest track to S35 (étale π₁) is P2 → S26 → S27 → S28 → S30 → S35, while its
critical chain also passes through P3 and S34 — which is exactly why P3 cannot move past S35.

## Building the PDFs locally / ساخت PDFها

    latexmk -pdf lectures/P1-groups.tex     # one file
    make                                     # everything (Makefile provided)
    make clean

Or let the GitHub Action (`.github/workflows/build-pdfs.yml`) compile on every push.

## Adding a new lecture / افزودن جزوه‌ی جدید

1. Write `lectures/Sxx-slug.tex` (copy the master preamble from an existing lecture).
2. Compile locally (`latexmk -pdf …`) or push and let CI build the PDF.
3. Run `python tools/update_readme.py` — it rewrites the sessions table above
   (links + ✅/🚧 status) from `tools/sessions.json` and the files on disk.
4. Commit: `git commit -m "lectures: add Sxx (Title)"`.

## License / مجوز

Content: **CC BY-SA 4.0** · Code/workflows: **MIT**. See [`LICENSE`](LICENSE).

## Citation / استناد

*Point: From Number Theory to Algebraic Geometry and Logic*, lecture notes, 2026 — <repo URL>.
Mint a DOI per release via Zenodo if you need a citable version.