# mkdocs_llmstxt

mkdocs-llmstxt package.

MkDocs plugin to generate an /llms.txt file.

Classes:

- **`MkdocsLLMsTxtPlugin`** – The MkDocs plugin to generate an llms.txt file.

Functions:

- **`autoclean`** – Auto-clean the soup by removing elements.

## MkdocsLLMsTxtPlugin

Bases: `BasePlugin[_PluginConfig]`

The MkDocs plugin to generate an `llms.txt` file.

This plugin defines the following event hooks:

- `on_page_content`
- `on_post_build`

Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs` for more information about its plugin system.

Methods:

- **`on_config`** – Save the global MkDocs configuration.
- **`on_files`** – Expand inputs for generated files.
- **`on_page_content`** – Convert page content into a Markdown file and save the result to be processed in the on_post_build hook.
- **`on_post_build`** – Create the final llms.txt file and the MD files for all selected pages.

Attributes:

- **`md_pages`** (`dict[str, list[_MDPageInfo]]`) – Dictionary mapping section names to a list of page infos.
- **`mkdocs_config`** (`MkDocsConfig`) – The global MkDocs configuration.

### md_pages

```python
md_pages: dict[str, list[_MDPageInfo]]

```

Dictionary mapping section names to a list of page infos.

### mkdocs_config

```python
mkdocs_config: MkDocsConfig

```

The global MkDocs configuration.

### on_config

```python
on_config(config: MkDocsConfig) -> MkDocsConfig | None

```

Save the global MkDocs configuration.

Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config). In this hook, we save the global MkDocs configuration into an instance variable, to re-use it later.

Parameters:

- **`config`** (`MkDocsConfig`) – The MkDocs config object.

Returns:

- `MkDocsConfig | None` – The same, untouched config.

Source code in `src/mkdocs_llmstxt/_internal/plugin.py`

```python
def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
    """Save the global MkDocs configuration.

    Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
    In this hook, we save the global MkDocs configuration into an instance variable,
    to re-use it later.

    Arguments:
        config: The MkDocs config object.

    Returns:
        The same, untouched config.
    """
    if config.site_url is None:
        raise ValueError("'site_url' must be set in the MkDocs configuration to be used with the 'llmstxt' plugin")
    self.mkdocs_config = config
    # A `defaultdict` could be used, but we need to retain the same order between `config.sections` and `md_pages`
    # (which wouldn't be guaranteed when filling `md_pages` in `on_page_content()`).
    self.md_pages = {section: [] for section in self.config.sections}
    return config

```

### on_files

```python
on_files(
    files: Files, *, config: MkDocsConfig
) -> Files | None

```

Expand inputs for generated files.

Hook for the [`on_files` event](https://www.mkdocs.org/user-guide/plugins/#on_files). In this hook we expand inputs for generated file (glob patterns using `*`).

Parameters:

- **`files`** (`Files`) – The collection of MkDocs files.
- **`config`** (`MkDocsConfig`) – The MkDocs configuration.

Returns:

- `Files | None` – Modified collection or none.

Source code in `src/mkdocs_llmstxt/_internal/plugin.py`

```python
def on_files(self, files: Files, *, config: MkDocsConfig) -> Files | None:  # noqa: ARG002
    """Expand inputs for generated files.

    Hook for the [`on_files` event](https://www.mkdocs.org/user-guide/plugins/#on_files).
    In this hook we expand inputs for generated file (glob patterns using `*`).

    Parameters:
        files: The collection of MkDocs files.
        config: The MkDocs configuration.

    Returns:
        Modified collection or none.
    """
    page_uris = list(files.src_uris)

    for section_name, file_list in list(self.config.sections.items()):
        self.config.sections[section_name] = self._expand_inputs(file_list, page_uris=page_uris)

    return files

```

### on_page_content

```python
on_page_content(
    html: str, *, page: Page, **kwargs: Any
) -> str | None

```

Convert page content into a Markdown file and save the result to be processed in the `on_post_build` hook.

Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content).

Parameters:

- **`html`** (`str`) – The rendered HTML.
- **`page`** (`Page`) – The page object.

Source code in `src/mkdocs_llmstxt/_internal/plugin.py`

```python
def on_page_content(self, html: str, *, page: Page, **kwargs: Any) -> str | None:  # noqa: ARG002
    """Convert page content into a Markdown file and save the result to be processed in the `on_post_build` hook.

    Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content).

    Parameters:
        html: The rendered HTML.
        page: The page object.
    """
    for section_name, file_list in self.config.sections.items():
        if page.file.src_uri in file_list:
            path_md = Path(page.file.abs_dest_path).with_suffix(".md")
            page_md = _generate_page_markdown(
                html,
                should_autoclean=self.config.autoclean,
                preprocess=self.config.preprocess,
                path=str(path_md),
            )

            md_url = Path(page.file.dest_uri).with_suffix(".md").as_posix()
            # Apply the same logic as in the `Page.url` property.
            if md_url in (".", "./"):
                md_url = ""

            # Guaranteed to exist as we require `site_url` to be configured.
            base = cast("str", self.mkdocs_config.site_url)
            if not base.endswith("/"):
                base += "/"
            md_url = urljoin(base, md_url)

            self.md_pages[section_name].append(
                _MDPageInfo(
                    title=page.title if page.title is not None else page.file.src_uri,
                    path_md=path_md,
                    md_url=md_url,
                    content=page_md,
                ),
            )

    return html

```

### on_post_build

```python
on_post_build(
    *, config: MkDocsConfig, **kwargs: Any
) -> None

```

Create the final `llms.txt` file and the MD files for all selected pages.

Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).

Parameters:

- **`config`** (`MkDocsConfig`) – MkDocs configuration.

Source code in `src/mkdocs_llmstxt/_internal/plugin.py`

```python
def on_post_build(self, *, config: MkDocsConfig, **kwargs: Any) -> None:  # noqa: ARG002
    """Create the final `llms.txt` file and the MD files for all selected pages.

    Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).

    Parameters:
        config: MkDocs configuration.
    """
    output_file = Path(config.site_dir).joinpath("llms.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    markdown = f"# {config.site_name}\n\n"

    if config.site_description is not None:
        markdown += f"> {config.site_description}\n\n"

    if self.config.markdown_description is not None:
        markdown += f"{self.config.markdown_description}\n\n"

    full_markdown = markdown

    for section_name, file_list in self.md_pages.items():
        markdown += f"## {section_name}\n\n"
        for page_title, path_md, md_url, content in file_list:
            path_md.write_text(content, encoding="utf8")
            _logger.debug(f"Generated MD file to {path_md}")
            markdown += f"- [{page_title}]({md_url})\n"
        markdown += "\n"

    output_file.write_text(markdown, encoding="utf8")
    _logger.debug("Generated file /llms.txt")

    if self.config.full_output is not None:
        full_output_file = Path(config.site_dir).joinpath(self.config.full_output)
        for section_name, file_list in self.md_pages.items():
            list_content = "\n".join(info.content for info in file_list)
            full_markdown += f"# {section_name}\n\n{list_content}"
        full_output_file.write_text(full_markdown, encoding="utf8")
        _logger.debug(f"Generated file /{self.config.full_output}.txt")

```

## autoclean

```python
autoclean(soup: BeautifulSoup) -> None

```

Auto-clean the soup by removing elements.

Parameters:

- **`soup`** (`BeautifulSoup`) – The soup to modify.

Source code in `src/mkdocs_llmstxt/_internal/preprocess.py`

```python
def autoclean(soup: Soup) -> None:
    """Auto-clean the soup by removing elements.

    Parameters:
        soup: The soup to modify.
    """
    # Remove unwanted elements.
    for element in soup.find_all(_to_remove):
        element.decompose()

    # Unwrap autoref elements.
    for element in soup.find_all("autoref"):
        element.replace_with(NavigableString(element.get_text()))

    # Unwrap mkdocstrings div.doc-md-description.
    for element in soup.find_all("div", attrs={"class": "doc-md-description"}):
        element.replace_with(NavigableString(element.get_text().strip()))

    # Remove mkdocstrings labels.
    for element in soup.find_all("span", attrs={"class": "doc-labels"}):
        element.decompose()

    # Remove line numbers from code blocks.
    for element in soup.find_all("table", attrs={"class": "highlighttable"}):
        element.replace_with(Soup(f"<pre>{html.escape(element.find('code').get_text())}</pre>", "html.parser"))  # type: ignore[union-attr]

```
