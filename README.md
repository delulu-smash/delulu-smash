[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

# DeLulu Smash

This is suite of tools, documentation, blog, and packages to help me, [`DeLulu`](https://www.delulu-smash.com/) with Smash Bros.

This follows a monorepo structure with following subcomponents

| Folder                                                              | Description                                                                                                                       |
|---------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| [`docs`](https://github.com/delulu-smash/delulu-smash/tree/main/docs)         | contents for building main site: [delulu-smash.com](https://www.delulu-smash.com/), built with [myst engine](https://mystmd.org/) |
| [`pkgs`](https://github.com/delulu-smash/delulu-smash/tree/main/pkgs)         | contents python packages that aggregates and allows analysis on smash data (general and character specific)                       |
| [`tools`](https://github.com/delulu-smash/delulu-smash/tree/main/tools) | contents for interactive tools, built with [reflex](https://reflex.dev/)                                                          |

## How to run docs locally

Ensure you have ffmpeg installed (per [instructions](https://mystmd.org/guide/figures#videos) for `.mov` conversion).


For Linux
```bash
sudo pacman -S ffmpeg
```

Below command will ensure have proper up to date requirements and run docs locally

```bash
dsu docs run
```

## How to upgrade dependencies

[To update all packages](https://docs.astral.sh/uv/concepts/projects/sync/#syncing-development-dependencies)

```bash
uv lock --upgrade
```

## How to run reflex tools site locally

```bash
uv run --directory=tools/smash reflex run
```