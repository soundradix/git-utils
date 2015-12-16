# git-utils
Useful scripts for git

## share_submodules.py

For cases where a git submodule is common to several folders/submodules, for example,

* submodule CommonLib appears in submodule A
* submodule CommonLib appears in submodule B
* submodule CommonLib appears in submodule C

Normally a `git submodule update --init --recursive` will download submodule CommonLib several times and duplicate its git repo.

`share_submodule.py` replaces the normal submodule init to use `git worktree` to init the submodule to point to the same shared repo, while each instance still has its own index, HEAD, etc.
