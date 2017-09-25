# git-utils
Useful scripts for git

## `git-w.py`
A tool to normalize line endings to reduce diffs.
It may normalize line endings to either '\n' (unix) or '\r\n' (windows)
depending on which one best reduces the diff size.

## `init_submodules.py`
init_submodules is used to initialize submodules after cloning several repositories with shared submodules. It initializes the common submodule with `git submodule update`'s `--reference` option, to avoid downloading each submodule several times as well as sharing their objects to save disk space.

# Useful links/tools
* [git-mediate](https://github.com/Peaker/git-mediate): Tool for resolving merge conflicts correctly and easily

# Useful git configurations
These configuration flags are not default in git but probably should be:
* `git config --global log.decorate auto` - display branch names in `git log`.
