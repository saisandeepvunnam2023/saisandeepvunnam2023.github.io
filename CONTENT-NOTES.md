# Content notes — read this before you send the link to anyone

Everything on the site came from your own résumé files, your old live site, your
GitHub, or your direct statement about what you built. Nothing was invented.

But there are conflicts you need to resolve, and one of them is serious enough
that it is first.

---

## 0. The Rakesh portfolio overlap — deal with this

`rakesh0710.github.io/Rakesh_Portfolio` is live, public and indexed under the
name **Rakesh Reddy Yeduru**. It currently shares the following with your site:

| | |
|---|---|
| **Phone number** | +1 (940) 843-8351 — the number on your own résumé |
| **Employers** | University of Dayton, Unity Technologies |
| **Metric** | "175+" |
| **Education** | M.S. Computer Science, University of Dayton |
| **Projects** | NFL Season Hub, CNR Car Zone — now on both sites |

A recruiter who searches your phone number, or the phrase "175+ digital
initiatives", finds both portfolios. Two names, one work history. That does not
read as a coincidence to a hiring manager — it reads as one of you having taken
the other's history, and neither of you gets the benefit of the doubt.

**This is not a design problem and I cannot fix it in code.** Options, in order
of how well they work:

1. **Take the overlapping material off the other site.** If that site is yours to
   edit, this is the clean fix — at minimum remove your phone number from it.
2. **Split the projects.** If NFL Season Hub and CNR Car Zone are genuinely yours,
   they should appear on one portfolio, not two.
3. **Leave it and accept the risk.** Understand what the risk is: it is not a
   missed interview, it is a withdrawn offer after a background check.

I did **not** copy `LTIMindtree (Jan 2020 – May 2023)` across, because it
contradicts the KIMS and BSCPL roles you asked me to keep for those same years.
Both cannot be true and you did not claim it.

---

## 1. Must fix before sending the link

| What | Where |
|---|---|
| **LinkedIn URL** | `content/site.json` → `links.linkedin`. Shows as a TODO chip in the hero and contact. |
| **Résumé PDF** | `static/files/Sai-Sandeep-Vunnam-Resume.pdf`, then set `"showResume": true` in `content/site.json`. Every résumé button is hidden until you do — a recruiter currently has no way to get your CV. |
| **Unity location** | `content/experience.json` — TODO. |
| **Undergraduate degree** | `content/experience.json` → education — TODO. VNR VJIET is named in your résumés but no degree or dates appear anywhere. |
| **CNR Car Zone outcome** | `content/projects.json` — TODO. One honest sentence about what changed for the business. |
| **NFL case study: Approach + Reflection** | `content/projects.json` → `caseStudySections`. See §3. |

---

## 2. Conflicts between your own sources

### Unity dates — **check this one first**

- Your résumé (`SaiSandeepVunnam.docx`): **Jan 2026 – May 2026**
- The Rakesh portfolio: **Nov 2025 – Jul 2026**

I used **your own résumé**, because inventing a longer tenure is exactly the kind
of thing that fails a reference check. Flagged `verify` on the page. If the real
dates are the longer ones, fix the résumé too so they match.

### University of Dayton dates

Four versions exist across your files: `Nov 2023 – Present`, `Nov 2024 – Present`,
`Nov 2025 – Present`, and `Nov 2023 – Dec 2025`. I used **Nov 2023 – Dec 2025**,
the only one with an end date and the only one consistent with Unity starting
Jan 2026.

### 175+ versus 75+

- Live site + Rakesh site: **175+**
- `Resume_Sai_Sandeep_Vunnam.docx`: **75+**
- `cherry/VunnamSaiSandeep.docx`: says **75+** in the body and **175+** in the
  same document's Training section

I used **175+**, matching your published claim, and project 03 is built around
it. Three of your own files say 75. If 175 counts pages and 75 counts sites you
owned, say 75 — it is still a lot and it survives an interview.

### Overlapping employment

- KIMS Hospitals: **Aug 2020 – May 2023**
- BSCPL Infrastructure: **Jan 2020 – Mar 2021**

You asked to keep both as they are, so both are there, both flagged `verify`.
They overlap for eight months. If either was part-time, freelance or contract,
say so in the role title — it removes the question entirely.

There is also a **VNR VJIET "Website Creator / UI/UX Designer", Jun 2020 – May
2021** role in `cherry/VunnamSaiSandeep.docx` that is on no version of the site.
I left it out: adding a third concurrent role to an already-overlapping pair
makes the timeline harder to defend, not easier.

### Removed

**Indian School of Business** and its Employee of the Month recognition are gone
from the site, at your request.

---

## 3. What I wrote versus what you need to write

The two new projects are on your statement that they are yours. Their **figures
describe the live artefacts and are checkable** — 1,693 games, 273,325 plays,
6.8 KB per game, 100 Lighthouse, 18 document checks, 22 photo categories.

What I did **not** write is the reasoning, because I do not know it:

- **NFL case study, "Approach"** — why precompute rather than serve an API, and
  what you traded away.
- **NFL case study, "Reflection"** — what you would rebuild.
- **CNR outcome** — what actually changed for the business.

Both TODOs sit in the sections an engineer interviewing you will read first.
A case study that explains *what* without *why* is a feature list. Write those
three and this becomes the strongest part of the site.

---

## 4. Skills — what I included and what I left out

`content/skills.json` lists only what is corroborated by your own résumé files or
by the two projects you confirmed.

**Deliberately left out**, because nothing on file supports them: AEM, Sitecore,
Drupal, Contentful, Sanity, Amplitude, Looker, Jenkins, Docker, Java, GraphQL,
Node.js, and the AWS services (Lambda, RDS, DynamoDB, EC2, S3).

Those all appear on the Rakesh portfolio. Add any you can genuinely discuss under
questioning — one object each in `skills.json`. Listing a CMS you have not
configured is the easiest way to lose a technical screen.

---

## 5. Figures, and where each came from

| Figure | Source |
|---|---|
| 7 magazine issues | Your old site's issue list; all seven URLs verified live |
| 175+ sites | Your published claim — see the conflict above |
| ~40% less manual editing | Two of your résumés and your old site |
| 100+ pages audited (Unity) | Rakesh portfolio, via your statement that the role matches |
| NFL: 1,693 games / 273,325 plays / 6.8 KB / Lighthouse 100 | Rakesh portfolio; checkable against the live app |
| CNR: 18 documents / 22 photo categories | Rakesh portfolio, via your statement |

Removed with the old positioning: the **image pipeline** and **archive triage**
case studies. Both were real per your résumés and both survive as bullet points
under the University of Dayton role — they are just no longer headline projects,
because they are not web operations.

---

## 6. Photographs

The photography section now mirrors your own portfolio at
`saisandeepvunnam2023.github.io/sai-sandeep-photography`, using the eight genres
you curated there (Sports, Portrait, Candid, Wildlife, Event, Nature, Street,
Lifestyle) and linking out to the full roll. The seven Desktop photographs that
were here before have been retired.

The photography site lists `vunnamsaisandeep20@gmail.com`; this site lists
`saisandeepvunnam2023@gmail.com`. Both are Sai's, and the difference is
intentional. Not a defect, recorded here so it does not get "fixed" later.

### Sources

Seven photographs from `Desktop/portfolio /` and `Desktop/port/`, chosen for
range. The seven magazine covers in project 02 are the files in `Desktop/port/`,
matching the issue images on your old site.

The four NFL screenshots came from `Desktop/nfl projcts/`, cropped to remove the
browser chrome; the crops are saved at `Desktop/nfl projcts/cropped/`.

Originals are never copied into the repo. `content/media.json` points at them on
your Desktop. **If you move or rename those folders, update `content/media.json`.**
