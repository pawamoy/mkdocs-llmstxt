# mkdocs-llmstxt

[![ci](https://github.com/pawamoy/mkdocs-llmstxt/workflows/ci/badge.svg)](https://github.com/pawamoy/mkdocs-llmstxt/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://pawamoy.github.io/mkdocs-llmstxt/)
[![pypi version](https://img.shields.io/pypi/v/mkdocs-llmstxt.svg)](https://pypi.org/project/mkdocs-llmstxt/)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#mkdocs-llmstxt:gitter.im)

MkDocs plugin to generate an [/llms.txt file](https://llmstxt.org/).

> /llms.txt - A proposal to standardise on using an /llms.txt file to provide information to help LLMs use a website at inference time. 

See our own dynamically generated [/llms.txt](llms.txt) as a demonstration.

## Installation

```bash
pip install mkdocs-llmstxt
```

## Usage

Enable the plugin in `mkdocs.yml`:

```yaml title="mkdocs.yml"
plugins:
- llmstxt:
    files:
    - output: llms.txt
      inputs:
      - file1.md
      - folder/file2.md
```

You can generate several files, each from its own set of input files.

File globbing is supported:

```yaml title="mkdocs.yml"
plugins:
- llmstxt:
    files:
    - output: llms.txt
      inputs:
      - file1.md
      - reference/*/*.md
```

The plugin will concatenate the rendered HTML of these input pages, clean it up a bit (with [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)), convert it back to Markdown (with [Markdownify](https://pypi.org/project/markdownify)), and format it (with [Mdformat](https://pypi.org/project/mdformat)). By concatenating HTML instead of Markdown, we ensure that dynamically generated contents (API documentation, executed code blocks, snippets from other files, Jinja macros, etc.) are part of the generated text files. Credits to [Petyo Ivanov](https://github.com/petyosi) for the original idea ✨

You can disable auto-cleaning of the HTML:

```yaml title="mkdocs.yml"
plugins:
- llmstxt:
    autoclean: false
```

You can also pre-process the HTML before it is converted back to Markdown:

```yaml title="mkdocs.yml"
plugins:
- llmstxt:
    preprocess: path/to/script.py
```

The specified `script.py` must expose a `preprocess` function that accepts the `soup` and `output` arguments:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

def preprocess(soup: BeautifulSoup, output: str) -> None:
    ...  # modify the soup
```

The `output` argument lets you modify the soup *depending on which file is being generated*.

Have a look at [our own pre-processing function](https://pawamoy.github.io/mkdocs-llmstxt/reference/mkdocs_llmstxt/preprocess/#mkdocs_llmstxt.preprocess.autoclean) to get inspiration.
