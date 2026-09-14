# Content notes — read this before you publish

Everything on the site came from your live portfolio, your résumé files, or your
GitHub. Nothing was invented. But your sources **disagree with each other** in
several places, and a recruiter who reads both your site and your résumé will
see the difference. This file lists every one of them.

Anything unresolved renders on the page as a loud orange `TODO` or `verify`
marker, so you cannot ship it by accident.

Sources used:

- `https://saisandeepvunnam.github.io` — the live site (content is inside the JS bundle)
- `Desktop/SaiSandeepVunnam.docx` — newest, IT-support tailored, includes Unity
- `Desktop/Resume Latest/Resume_Sai_Sandeep_Vunnam.docx` — computational-photography framing
- `Desktop/Resume Latest/Vunnam_Sandeep_Resume.docx` — earlier general version
- `github.com/saisandeepvunnam` — 3 repos, one of which is the current site

---

## 1. Must fix before publishing

| What | Where | Why |
|---|---|---|
| **LinkedIn URL** | `content/site.json` → `links.linkedin` | Currently a TODO. It shows as a TODO chip in the hero and the contact section. |
| **Résumé PDF** | `static/files/Sai-Sandeep-Vunnam-Resume.pdf` | A generated placeholder is shipping. Overwrite that file, keep the filename, rebuild. |
| **Unity location** | `content/experience.json` → Unity role | `location` is a TODO. Remote? Which office? |
| **Undergraduate degree** | `content/experience.json` → education | VNR VJIET is referenced in your résumés as where you studied, but no degree or dates appear anywhere. Both fields are TODO. |
| **"Currently" + "Reading" field notes** | `content/story.json` → `notes.items` | Two TODOs. These are the lines that make you a person rather than a CV — worth two real sentences. |

---

## 2. Conflicts between your own sources

I picked the reading noted below in each case. Change any of them if I picked wrong.

### 175+ sites vs 75+ sites — **the one I'd double-check first**

- Live site: *"Built and launched 175+ academic and magazine sites"*
- `Resume_Sai_Sandeep_Vunnam.docx`: *"75+ academic sites"*
- `Vunnam_Sandeep_Resume.docx`: *"over 75 academic websites"*

**Used: 175+**, because it is your own current published claim, and it appears
as the headline number on the whole site (project 02 is built around it).

Two résumés say 75. If 175 counts every page you touched and 75 counts sites you
owned end to end, say the smaller number — it is still a lot and it will survive
an interview. This figure appears in: `site.json` (positioning + meta
description), `projects.json` (project 02), `experience.json` (UD role), and the
generated social card.

### Indian School of Business — which job was it?

- Live site: **Web Content Developer & Campaign Designer**, 40+ WordPress microsites
- `Resume_Sai_Sandeep_Vunnam.docx`: **IT Support Engineer**, CUDA/OpenCL diagnostic scripting

**Used: the web title**, since the site's software-engineering positioning
rests on it, and both sets of duties are listed under it. Flagged `verify`.

### Overlapping employment dates

- KIMS Hospitals: **Aug 2020 – May 2023**
- BSCPL Infrastructure: **Jan 2020 – Mar 2021**
- Indian School of Business: **Sep 2022 – May 2023**

These three overlap heavily, and KIMS and BSCPL appear only on your live site —
not in any résumé. All three are on the site because you confirmed they are real,
and all three are flagged `verify`.

A recruiter reading three concurrent full-time jobs will assume an error. If any
were freelance, part-time or contract, say so in the role title — it removes the
question completely. If a date is simply wrong, fix it in `experience.json`.

### University of Dayton dates

Four different versions exist across your files: `Nov 2023 – Present`,
`Nov 2024 – Present`, `Nov 2025 – Present`, and `Nov 2023 – Dec 2025`.

**Used: Nov 2023 – Dec 2025**, from your newest résumé, which is the only one
with an end date and the only one consistent with Unity starting Jan 2026.

### Convergence hackathon

Live site says *participant*; newest résumé says *Finalist*.
**Used: Finalist** (the newer claim). Only keep it if it is accurate.

### Locations I inferred

`Hyderabad, India` is shown for ISB, KIMS and BSCPL. None of your files state a
city — I inferred it from VNR VJIET being in Hyderabad. Correct it if wrong.

---

## 3. Figures used, and where each came from

Every number on the site traces to one of your own documents. None were estimated.

| Figure | Source |
|---|---|
| 7 magazine issues | The live site's issue list, all seven URLs verified |
| ~40% less manual editing | Two résumés and the live site |
| 2,500+ pages evaluated, 1,600+ retired | `Resume_Sai_Sandeep_Vunnam.docx` and `Vunnam_Sandeep_Resume.docx` |
| ~15% engagement lift | Live site only — *not in any résumé*. Used in `experience.json` only, not as a headline |
| 40+ ISB microsites | Live site only |
| 175+ sites | See the conflict above |

---

## 4. Things I deliberately did not claim

- **No ML/AI job title.** Your verifiable machine-learning work is OpenCV/TensorFlow
  automation, an ONNX→CoreML conversion, and graduate MATLAB coursework. That is
  real and it is all on the site — under *Automate*, *See*, and *Playground* —
  but it does not support "Machine Learning Engineer" as a headline, and a
  recruiter would find that out in the first technical screen.
- **No invented case-study detail.** Where a case study describes a decision
  (the human gate in archive triage, splitting correction from framing in the
  pipeline), it is drawn from what your résumé bullets say the system did.
  If any of it misremembers the real work, edit `projects.json` — those pages
  are what a senior engineer will actually read.
- **No fabricated reflections.** The "what I'd improve" sections are the honest
  next steps implied by each system's design. Read them; they are the part an
  interviewer is most likely to ask you to defend.

---

## 5. Photographs

Seven photographs were selected from `Desktop/portfolio /` and `Desktop/port/`,
chosen for range — weather, motion, quiet detail, people, architecture.

The seven magazine covers in project 01 are the files in `Desktop/port/`, which
match the issue images on the live site. The site states that much of the
photography in those issues is yours. Confirm that is fair to say before publishing.

Originals are never copied into the repo. `content/media.json` points at them on
your Desktop, and `optimize_images.py` writes the web-sized derivatives.
**If you move or rename those folders, update `content/media.json`.**
