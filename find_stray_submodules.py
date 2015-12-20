#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Finds remains of old submodules in .git
Useful to clean up .git

Usage: find_stray_submodules.py <command>
Commands: info, list, delete
'''

import os
from pathlib import Path
import shutil
import sys

def show_help():
    print(__doc__)
    sys.exit(1)

modes = ['info', 'list', 'delete']

if len(sys.argv) == 1:
    mode = 'info'
elif len(sys.argv) > 2 or sys.argv[1] not in modes:
    show_help()
else:
    mode = sys.argv[1]

def try_remove_prefix(s, prefix):
    'Removes prefix or returns None'
    if not s.startswith(prefix):
        return None
    return s[len(prefix):]

dirs_found = []
for config_path in Path('.git').glob('modules/**/config'):
    module_gitdir = config_path.parent
    for config_line in config_path.open('r').readlines():
        worktree_rel = try_remove_prefix(config_line.strip(), 'worktree = ')
        if worktree_rel is not None:
            break
    else:
        raise ValueError('bad config file %s' % config_path)
    worktree = Path(module_gitdir, worktree_rel)
    if not worktree.exists():
        if mode == 'info':
            print('%s\n    references worktree that no longer exists: %s' %
                (module_gitdir, worktree_rel))
    else:
        gitfile_path = Path(worktree, '.git')
        gitfile_data = gitfile_path.open('r').read().strip()
        gitdir = try_remove_prefix(gitfile_data, 'gitdir: ')
        if gitdir is not None and Path(worktree, gitdir).resolve() == module_gitdir.resolve():
            continue
        if mode == 'info':
            print('%s\n    references worktree which does not reference it back' % module_gitdir)
    if mode == 'list':
        print(module_gitdir)
    dirs_found.append(module_gitdir)

if mode == 'delete':
    for dirname in dirs_found[::-1]:
        print('deleting %s' % dirname)
        shutil.rmtree(str(dirname))
    print('Deleted %d stray submodules' % len(dirs_found))
if mode == 'info' and not dirs_found:
    print('No stary submodules found')
