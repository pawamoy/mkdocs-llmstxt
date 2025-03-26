# mkdocs-llmstxt

[![ci](https://github.com/pawamoy/mkdocs-llmstxt/workflows/ci/badge.svg)](https://github.com/pawamoy/mkdocs-llmstxt/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://pawamoy.github.io/mkdocs-llmstxt/)
[![pypi version](https://img.shields.io/pypi/v/mkdocs-llmstxt.svg)](https://pypi.org/project/mkdocs-llmstxt/)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#mkdocs-llmstxt:gitter.im)

MkDocs plugin to generate an [/llms.txt file](https://llmstxt.org/).

> /llms.txt - A proposal to standardise on using an /llms.txt file to provide information to help LLMs use a website at inference time.

See our own dynamically generated [/llms.txt](https://pawamoy.github.io/mkdocs-llmstxt/llms.txt) as a demonstration.

## Installation

```bash
pip install mkdocs-llmstxt
```

## Usage

Enable the plugin in `mkdocs.yml`:

```yaml title="mkdocs.yml"
site_name: My project
site_description: Description of my project
site_url: https://myproject.com/  # Required for the llmstxt plugin to work

plugins:
- llmstxt:
    markdown_description: Long description of my project
    sections:
      Usage documentation:
        - file1.md
        - file2.md
```

The resulting `/llms.txt` file will be available at the root of your documentation. With the previous example, it will be accessible at https://myproject.com/llms.txt and will contain the following:

```markdown
# My project

> Description of my project

Long description of my project

## Usage documentation

- [File1 title](https://myproject.com/file1.md)
- [File2 title](https://myproject.com/file2.md)
```

Each source file included in `sections` will have its own markdown file available at the specified URL
in the `/llms.txt`. See [Markdown generation](#markdown-generation) for more details.

File globbing is supported:

```yaml title="mkdocs.yml"
plugins:
- llmstxt:
    sections:
      Usage documentation:
        - index.md
        - usage/*.md
```

## Markdown generation

To generate a markdown page from a source file, the plugin will:

- Cleanup the HTML output (with [BeautifulSoup](https://pypi.org/project/beautifulsoup4/))
- Convert it back to Markdown (with [Markdownify](https://pypi.org/project/markdownify))

Doing so is necessary to ensure that dynamically generated contents (API documentation, executed code blocks,
snippets from other files, Jinja macros, etc.) are part of the generated text files.

Credits to [Petyo Ivanov](https://github.com/petyosi) for the original idea ✨.

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

Have a look at [our own cleaning function](https://pawamoy.github.io/mkdocs-llmstxt/reference/mkdocs_llmstxt/#mkdocs_llmstxt.autoclean) to get inspiration.
