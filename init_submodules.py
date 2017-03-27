#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
init_submodules.py [paths]

A tool to init a git repo of submodules with shared submodules.
For example a repo with structure:

+ Root
|
+-+ Module A
| |
| +-+ Module Lib
|
+-+ Module B
  |
  +-+ Module Lib

Will initialized the submodules recursively so that the shared module "Lib" will only be fetched ones and be initialized using the "reference" flag.

For separate repos with common submodules, one may provide paths in the command line.
So if your repos have this structure

+ Root A
|
+-+ Module Lib

+ Root B
|
+-+ Module Lib

Providing the paths for "Root A" and "Root B" will initialize the submodules so that
"Root B"'s submodule references "Root A"'s submodule.
Note that the order is important and modules in paths provided first will not reference
modules from the paths after them.
This is useful as some repos could be temporary and one would want the temporary repo's
submodule to reference the permanent repo's and not the other way.
'''

import collections
import os
import subprocess
import sys

def command_output(cmd):
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).stdout.read().decode('utf-8')

def strip_end(text, suffix):
    # From http://stackoverflow.com/a/1038999/40916
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]

def list_submodules():
    for line in command_output('git config --file .gitmodules --get-regexp submodule\..*\.url').splitlines():
        [key, value] = line.split(' ', 1)
        name = key.split('.', 1)[1].rsplit('.', 1)[0]
        yield {
            'local': command_output('git config --file .gitmodules submodule.%s.path' % (name, )).strip(),
            'remote': strip_end(value, '.git'),
            }

submodule_sources = {}

def init_submodule(sub):
    source = submodule_sources.get(sub['remote'])
    if source:
        print('Using source %s for submodule %s' % (source, sub['local']))
        subprocess.check_call(['git', 'submodule', 'update', '--reference', source, '--init', sub['local']])
    else:
        print('Initializing new submodule %s' % (sub['local'], ))
        subprocess.check_call(['git', 'submodule', 'update', '--init', sub['local']])
    abs_dir = os.path.abspath(sub['local'])
    if sub['remote'] not in submodule_sources:
        submodule_sources[sub['remote']] = abs_dir

# Python 2 compatibility
try:
    input = raw_input
except NameError:
    pass

def go(path):
    todos = collections.deque([path])
    while todos:
        cur = todos.popleft()
        print('Initializing submodules at %s' % (cur, ))
        os.chdir(cur)
        subs = list(list_submodules())
        for sub in subs:
            try:
                init_submodule(sub)
            except:
                print('Failed initializing submodule %s' % (sub['local'], ))
                sys.stdout.write('Continue (y/n)? ')
                if not input().lower().startswith('y'):
                    sys.exit(1)
            else:
                todos.append(os.path.abspath(sub['local']))

if len(sys.argv) < 2:
    paths = [os.getcwd()]
else:
    paths = [os.path.abspath(x) for x in sys.argv[1:]]

for path in paths:
    go(path)