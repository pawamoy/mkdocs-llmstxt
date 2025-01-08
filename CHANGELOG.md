# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [2.0.1](https://github.com/pawamoy/mkdocs-manpage/releases/tag/2.0.1) - 2024-11-25

<small>[Compare with 2.0.0](https://github.com/pawamoy/mkdocs-manpage/compare/2.0.0...2.0.1)</small>

### Build

- Drop support for Python 3.8 ([ff2b8bb](https://github.com/pawamoy/mkdocs-manpage/commit/ff2b8bb3573c3c8d2691aac13b9c8bdaf5639ff1) by Timothée Mazzucotelli).

### Bug Fixes

- Fix usual encoding error on the annoying operating system ([3204f71](https://github.com/pawamoy/mkdocs-manpage/commit/3204f7111111ad78bb119fd1ae7ca20af13a08c7) by Timothée Mazzucotelli). [Issue-1](https://github.com/pawamoy/mkdocs-manpage/issues/1)

## [2.0.0](https://github.com/pawamoy/mkdocs-manpage/releases/tag/2.0.0) - 2024-03-31

<small>[Compare with 1.0.0](https://github.com/pawamoy/mkdocs-manpage/compare/1.0.0...2.0.0)</small>

### Features

- Support multiple outputs, glob pattern for inputs, custom title and header ([b45a81e](https://github.com/pawamoy/mkdocs-manpage/commit/b45a81ee927d50aa038a183e5a39e92721dcc88b) by Timothée Mazzucotelli). Breaking changes: configuration format in `mkdocs.yml` and public API changed.

## [1.0.0](https://github.com/pawamoy/mkdocs-manpage/releases/tag/1.0.0) - 2024-01-06

<small>[Compare with first commit](https://github.com/pawamoy/mkdocs-manpage/compare/39a85476b514404f465011c18c3c13823734908f...1.0.0)</small>

### Features

- Implement HTML pre-processing option ([170199e](https://github.com/pawamoy/mkdocs-manpage/commit/170199e93874849b9a8fcc94d8ab46f7cc6b7c2e) by Timothée Mazzucotelli).
- Implement manpage generation ([a9f8c9a](https://github.com/pawamoy/mkdocs-manpage/commit/a9f8c9ac06a2affc7e23a64400f4e2052b36e186) by Timothée Mazzucotelli).
- Generate project using copier-pdm template ([a018851](https://github.com/pawamoy/mkdocs-manpage/commit/a0188519373bfa02d27122e3b7294dd1ae4ac3d7) by Timothée Mazzucotelli).
