# Q-CTRL Sphinx Theme

The Q-CTRL Sphinx Theme is a very opinionated [Sphinx](https://www.sphinx-doc.org/) theme intended for use with public [Q-CTRL Documentation](https://docs.q-ctrl.com/) websites such as the [Q-CTRL Python package](https://docs.q-ctrl.com/boulder-opal/references/qctrl/).

## Installation

```shell
pip install qctrl-sphinx-theme
```

## Usage

1. Add `qctrl-sphinx-theme` as a dev dependency in `pyproject.toml`.
2. Set the `html_theme` config value in `docs/conf.py`.
  ```python
  html_theme = "qctrl_sphinx_theme"
  ```
3. Set the `html_theme_options` config value in `docs/conf.py`.
  ```python
  html_theme_options = {
      "segment_write_key": "<YOUR_SEGMENT_WRITE_KEY>"
  }
  ```
