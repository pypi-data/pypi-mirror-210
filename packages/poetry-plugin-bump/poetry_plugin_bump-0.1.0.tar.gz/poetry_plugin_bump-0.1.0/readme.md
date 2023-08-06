# poetry-plugin-bump

A plugin for poetry to bump version, just like you can in npm.

## Installation

supported version:

| poetry version  | plugin version |
|:---------------:|:--------------:|
| \>=1.2.0,<1.5.0 |     <0.1.0     |
|    \>=1.5.0     |    >=0.1.0     |

Installation requires poetry 1.2.0+. To install this plugin run:

`poetry self add poetry-plugin-bump`

If your poetry is installed with `pipx`:

```
pipx inject poetry poetry-plugin-bump
```

For other methods of installing plugins see
the [poetry documentation](https://python-poetry.org/docs/master/plugins/#the-plugin-add-command).

## Usage

Configuration is optional, but you can define config in `pyproject.toml`

default config:

```toml
[tool.poetry-plugin-bump]
commit_msg = 'bump: v{version}'
tag_name = 'v{version}'
```

this will define bump commit message and tag name.

## License

MIT licensed, inspired by https://github.com/keattang/poetry-exec-plugin
