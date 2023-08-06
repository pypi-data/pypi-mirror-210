# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [1.5.3](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.5.2...v1.5.3) (2023-05-23)


### Bug Fixes

* handle header being absent ([dfc1173](https://github.com/jayanthkoushik/shiny-mdc/commit/dfc1173e2b250c61db50a2815dd8a95760f15745))

### [1.5.2](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.5.1...v1.5.2) (2023-04-26)


### Bug Fixes

* handle metadata being absent ([a2f61a8](https://github.com/jayanthkoushik/shiny-mdc/commit/a2f61a81fc16fe4a1b527fee4a0a971c43c1366a))

### [1.5.1](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.5.0...v1.5.1) (2023-04-20)


### Bug Fixes

* fix spacing for citations, footnotes, and super/sub-scripts ([db84c5d](https://github.com/jayanthkoushik/shiny-mdc/commit/db84c5de40db26594876f6b83293ea6149aad10a))
* prevent output during cleanup when in quiet mode ([d1193f0](https://github.com/jayanthkoushik/shiny-mdc/commit/d1193f06255165db99fd430836a631f7dadd2b12))

## [1.5.0](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.4.1...v1.5.0) (2023-04-20)


### Features

* add appendix labels to footnotes ([8279712](https://github.com/jayanthkoushik/shiny-mdc/commit/8279712031ef4a36cc22720248a63cb22ffc6103))
* add space before superscripts in author lists ([b0db384](https://github.com/jayanthkoushik/shiny-mdc/commit/b0db3843ebca5a68428f275517d3fefce280f45f))
* convert emails into links ([380670c](https://github.com/jayanthkoushik/shiny-mdc/commit/380670c51565789c6ced8c13278cfbd03f79790e))
* in the stylish template, use lining numbers where appropriate ([8b7c643](https://github.com/jayanthkoushik/shiny-mdc/commit/8b7c64339f9b54ae5a6f4168c8ffa73f2c0b5df8))
* make spacing for footnotes and superscripts consistent ([921058f](https://github.com/jayanthkoushik/shiny-mdc/commit/921058fb021805ce4da93151831703cfcbc38fda))
* use `nowidow` for basic/spacious templates ([53fd916](https://github.com/jayanthkoushik/shiny-mdc/commit/53fd9163d8f5f72cd86b311f18d4bdac428a9a9b))
* use small caps for appendix labels in spacious template ([240fa66](https://github.com/jayanthkoushik/shiny-mdc/commit/240fa66fc1f30ddace242a5261c4811ca9302de5))

### [1.4.1](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.4.0...v1.4.1) (2023-04-19)


### Bug Fixes

* fix `hidelinks` argument passed to `hyperref` ([5007034](https://github.com/jayanthkoushik/shiny-mdc/commit/500703429ac92f233caf309f1f6b3f22d88c6ef8))

## [1.4.0](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.3.1...v1.4.0) (2023-04-19)


### Features

* make small tables in stylish template opt-in ([24cdca5](https://github.com/jayanthkoushik/shiny-mdc/commit/24cdca56f336ee69b178a89420c3fe1560be3c94))


### Bug Fixes

* handle additional cases for citations with notes ([1fcce8d](https://github.com/jayanthkoushik/shiny-mdc/commit/1fcce8d9549ebfc0896b46eaadb38f8064f25ace))

### [1.3.1](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.3.0...v1.3.1) (2023-04-18)


### Bug Fixes

* fix handling of notes in citations ([9a272a6](https://github.com/jayanthkoushik/shiny-mdc/commit/9a272a661971a25dc78703a2889dcadf00c429ed))

## [1.3.0](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.2.0...v1.3.0) (2023-04-15)


### Features

* improve clean up of tex files directory ([d5b1822](https://github.com/jayanthkoushik/shiny-mdc/commit/d5b182265fbd3884ebc59ca618bd2302df400647))
* improve command line interface ([58fb232](https://github.com/jayanthkoushik/shiny-mdc/commit/58fb2328e5c59bab3970ee7ff6beea1d4a9af252))

## [1.2.0](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.1.0...v1.2.0) (2023-04-12)


### Features

* use more organized tex folder structure ([4296148](https://github.com/jayanthkoushik/shiny-mdc/commit/4296148d049c41634f80e8aa9535a5710d7d7874))


### Bug Fixes

* fix handling of labels in figures and tables ([0a6fb66](https://github.com/jayanthkoushik/shiny-mdc/commit/0a6fb6669cbc763f22af11dca108a489df60a8d4))
* reset figure counter in appendices ([de0514b](https://github.com/jayanthkoushik/shiny-mdc/commit/de0514be47f1c50be1eb9a551ab82767a0b87fe1))

## [1.1.0](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.0.1...v1.1.0) (2023-04-12)


### Features

* align author list in `authsetup` using fixed size boxes ([ebfa391](https://github.com/jayanthkoushik/shiny-mdc/commit/ebfa3914b635f8609f6c3651ea7455b5649f02e9))
* increase max figure/table width for spacious and basic templates ([773ec2c](https://github.com/jayanthkoushik/shiny-mdc/commit/773ec2c9ddb6843e8eaa3b38c8f1f2c4844db46c))


### Bug Fixes

* wrap figures with empty frames to improve positioning ([7828c0b](https://github.com/jayanthkoushik/shiny-mdc/commit/7828c0b53f09c13e75de34fbb63fd7803ca060c2))

### [1.0.1](https://github.com/jayanthkoushik/shiny-mdc/compare/v1.0.0...v1.0.1) (2023-04-12)


### Bug Fixes

* change resource symlinks to hard links ([0c4ee32](https://github.com/jayanthkoushik/shiny-mdc/commit/0c4ee3290f7171bf6565f3f016444ca4cd955d25))
* fix equal contrib footnote in iclr template ([e1e5292](https://github.com/jayanthkoushik/shiny-mdc/commit/e1e5292090ec644cfd50e2bcea1cb9444f8ae20f))
* make citation space in `citet` non-breaking ([fd1bc73](https://github.com/jayanthkoushik/shiny-mdc/commit/fd1bc73904b3b31cea7bfa1af1dca7913c0414f7))
* remove citation repetition from templates using author-year format ([008c19b](https://github.com/jayanthkoushik/shiny-mdc/commit/008c19b87ca6b252861d37097b81c7cb6bcb202d))
* rewrite template handling ([39b79f4](https://github.com/jayanthkoushik/shiny-mdc/commit/39b79f4c96f275a8b22d955b0d35da8ef9c17a6f))
