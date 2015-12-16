#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Finds remains of old submodules in .git
Useful to clean up .git
'''

import os
from pathlib import Path
import shutil
import sys

if len(sys.argv) > 1:
    assert len(sys.argv) == 2
    mode = sys.argv[1]
    assert mode in ['info', 'list', 'delete']
else:
    mode = 'info'

def try_remove_prefix(s, prefix):
    'Removes prefix or returns None'
    if not s.startswith(prefix):
        return None
    return s[len(prefix):]

dirs_to_delete = []
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
    if mode == 'delete':
        dirs_to_delete.append(module_gitdir)

for dirname in dirs_to_delete:
    assert mode == 'delete'
    print('deleting %s' % dirname)
    shutil.rmtree(str(dirname))
