
# Tables

* @tbl:ex1
* @tbl:ex2

Col1       Col2     Col3     Col4
------   ------    ------    ------
1             2      3       4
11           22      33      44
111         222     333      444

: Short table {#tbl:ex1}

  Col1      Col2      Col3      Col4     Col5      Col6      Col7      Col8      Col9     Col10
------     -----     -----     -----    -----     -----     -----     -----     -----    ------
     a         1         2         3      123      abcd      1234       444       555       666
     b        11        22        33      456      efgh       567        44        55        66
<!-- -->
**Mid**
     c       111       222       333      789      ijkl        89         4         5         6

: Wide table {#tbl:ex2}


# Figures

![Narrow figure](figures/diamonds){#fig:ex1}

![Wide figure](figures/densities){#fig:ex2 width=5in}

* @fig:ex1
* @fig:ex2
* @fig:ex3, @fig:ex3a, @fig:ex3b

<div id="fig:ex3">

![Figure with 'width=2.5in'](figures/gaussian2d){#fig:ex3a width=2.5in}

![Figure with 'width=3.5in'[^f]](figures/anscombe){#fig:ex3b width=3.5in}

Sub-figures[^g]
</div>

[^f]: Footnote in sub-figure caption.
[^g]: Footnote in figure caption.


# Includes {#sec:includes}

* Commands from metadata include: $\argmin$ $\R$
* Include command in body (there should be text after this):

{% include utils/ext.md %}
