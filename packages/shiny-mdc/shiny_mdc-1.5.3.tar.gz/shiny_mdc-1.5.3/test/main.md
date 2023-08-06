---
title: "shinymdc-test"
subtitle: Document to Test 'shinymdc' Features and Templates
author:
- name: Author One
  affiliation:
  - 1
  equalcontrib: True
  email: 'author1@institute1.edu'
- name: Author MiddleName Two
  affiliation:
  - 1
  - 2
  equalcontrib: True
  email: 'authortwo@institute1.edu'
- name: Author
  equalcontrib: True
- name: Author Four
  email: 'author4@author4.com'
- name: Author Number Five
  email: 'authornumberfive@institutetwo.edu'
  affiliation:
  - 2
institute:
- id: 1
  name: Institute One
- id: 2
  name: Institute Two at City, State
abstract: _Markdown_ **in** **_abstract_**. $x+2$. @sec:ex1. Reference[@texbook].
bibliography: references.bib
sections:
- sections/main1.md
- sections/main2.md
- sections/empty.md
appendices:
- sections/appendix1.md
- sections/appendix2.md
includes:
- utils/commands.md
---


# Section {#sec:ex1}

Integer at enim eu tellus malesuada scelerisque. Ut sed rhoncus ipsum, at tempor
nisl. Vivamus vitae pulvinar leo, at pharetra massa. Ut lobortis odio non nulla
tincidunt pulvinar. Nunc faucibus pellentesque elit, non ornare risus suscipit
sed. Maecenas vel blandit ex.

Phasellus ultrices mi non nulla hendrerit, at rhoncus augue suscipit. Pellentesque
a lectus eget felis maximus feugiat nec ut ante. Sed eget laoreet lectus. Vestibulum
iaculis enim nec libero sollicitudin, id rhoncus libero consectetur. Integer eget
sem quis urna vulputate aliquet.

<div id="fig:ex0">

![Sub-figure with 'width=2in'](figures/gaussian2d){#fig:ex0a width=2in}

![Sub-figure with 'width=2in'](figures/lines.png){#fig:ex0b width=2in}

![Sub-figure with 'width=2in'](figures/anscombe){#fig:ex0c width=2in}

Sub-figures
</div>

## Subsection 1

In mollis tortor vel ante cursus, ac consectetur nibh commodo. Aenean ultricies
ornare ante ac fermentum. Vestibulum malesuada lectus at pellentesque hendrerit.
Praesent a tempor ex, eget iaculis mauris. Integer turpis nunc, varius ac
posuere consequat, molestie sed felis. Fusce cursus velit eu magna pellentesque
posuere sed eget ex. Vivamus in gravida quam, in volutpat erat.

## Subsection 2 {#sec:ex1.2}

### Subsubsection 1

Suspendisse erat est, imperdiet sed dolor at, sagittis lobortis tortor. Nulla
facilisi. Aliquam pharetra scelerisque auctor. Duis vel auctor ipsum. Nullam
sagittis feugiat mollis. Aliquam at ultrices libero. Nulla facilisi. Fusce sed
est placerat, fringilla augue at, pretium nisl.

### Subsubsection 2

In ut nunc libero. Duis eu elementum purus. Etiam dictum, ipsum nec aliquam
lobortis, magna magna pellentesque ligula, sed ultricies odio ligula vitae orci.
Fusce bibendum maximus ligula, id gravida felis dictum a. In dapibus nulla eget
volutpat vulputate. Quisque congue erat quis nibh molestie, eget varius eros
ultrices.

#### Subsubsubsection

Proin eleifend lorem semper, commodo tellus nec, porta purus. Nullam commodo
lectus nibh, consequat maximus lorem faucibus in. Nam purus eros, rutrum in
sapien et, condimentum lacinia nibh.
