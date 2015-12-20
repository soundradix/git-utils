#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
share_submodules.py

Utility to share the git objects of submodules that are common to several repos.

It creates additional git worktrees for the submodule,
and creates worktrees recursively for all the submodules within it.

This disk space as well as
download time during the 'git submodule update --init --recursive'.

Usage: share_submodules.py <src> <dst>
'''

# Compatible with both Python 2 and 3

import os
import subprocess
import sys

def get_git_toplevel(path_in_git):
    os.chdir(path_in_git)
    return subprocess.Popen(
        ['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE
        ).stdout.read().decode('utf-8').strip('\r\n')

def remove_prefix(s, prefix):
    assert s.startswith(prefix)
    return s[len(prefix):]

def get_gitdir(toplevel):
    dotgit_path = os.path.join(toplevel, '.git')
    return remove_prefix(open(dotgit_path).read().strip('\r\n'), 'gitdir: ')

def create_worktree(src_repo, worktree_name):
    worktree_path = os.path.join(src_repo, worktree_name)
    worktree_command = [
        'git', 'worktree', 'add', worktree_name]
    print('Creating worktree at %s\nvia: %s$ %s\n' %
        (worktree_path, src_repo, ' '.join(worktree_command)))
    os.chdir(src_repo)
    subprocess.check_call(worktree_command)
    return worktree_path

def move_worktree(src, dst):
    if os.path.exists(dst):
        print('Deleting old dir %s\n' % dst)
        os.rmdir(dst)
    print('Moving worktree from %s to %s\n' % (src, dst))
    gitdir = get_gitdir(src)
    os.rename(src, dst)
    open(os.path.join(gitdir, 'gitdir'), 'w').write(
        os.path.join(dst, '.git')+'\n')

def create_worktree_at_path(src_repo, dest_path, worktree_name):
    worktree_tmp_path = create_worktree(src_repo, worktree_name)
    move_worktree(worktree_tmp_path, dest_path)

def iter_submodules(repo):
    os.chdir(repo)
    for line in subprocess.Popen(
        ['git', 'submodule'], stdout=subprocess.PIPE
        ).stdout.readlines():
        parts = line.decode('utf-8').split()
        assert len(parts) in [2, 3]
        [hash_info, submodule_path] = parts[:2]
        yield (submodule_path, hash_info)

def get_submodule_hash(submodule_path):
    (parentdir, submodule) = os.path.split(submodule_path)
    for i_submodule, i_hash in iter_submodules(parentdir):
        if i_submodule == submodule:
            return i_hash
    raise IndexError(submodule_path)

def create_worktree_for_submodule(src_repo, dest_submodule_path, worktree_name):
    commit_hash = remove_prefix(get_submodule_hash(dest_submodule_path), '-')

    create_worktree_at_path(src_repo, dest_submodule_path, worktree_name)

    print('checking out commit %s for %s\n' % (commit_hash, dest_submodule_path))
    os.chdir(dest_submodule_path)
    subprocess.check_call(['git', 'checkout', commit_hash])

    os.chdir(src_repo)
    subprocess.check_call(['git', 'branch', '-d', worktree_name])

def create_worktrees_for_submodules(src_repo, dest_submodule_path, worktree_name):
    print('creating worktree for %s\n' % src_repo)
    create_worktree_for_submodule(src_repo, dest_submodule_path, worktree_name)
    for (submodule, _) in iter_submodules(src_repo):
        create_worktrees_for_submodules(
            os.path.join(src_repo, submodule),
            os.path.join(dest_submodule_path, submodule),
            worktree_name)

def get_git_version():
    version_str = subprocess.Popen(
        ['git', '--version'], stdout=subprocess.PIPE
        ).stdout.read().decode('utf-8').strip('\r\n')
    [version_num_str] = [x for x in version_str.split() if '.' in x][:1]
    return [int(x) for x in version_num_str.split('.')]

[src_repo, dest_submodule_path] = [
    os.path.abspath(x.rstrip('/'))
    for x in sys.argv[1:]]

git_version = get_git_version()
if git_version < [2, 5]:
    print('current git version %s does not support worktrees' %
        '.'.join(map(str, git_version)))
    sys.exit(1)

(dest_parent_dir, _) = os.path.split(dest_submodule_path)
dest_parent_repo_path = get_git_toplevel(dest_parent_dir)
(_, dest_parent_repo_name) = os.path.split(dest_parent_repo_path)
worktree_name = 'share_submodules__' + dest_parent_repo_name

create_worktrees_for_submodules(src_repo, dest_submodule_path, worktree_name)
