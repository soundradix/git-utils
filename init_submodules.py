#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
init_submodules.py

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

'''

import collections
import os
import subprocess
import sys

def command_output(cmd):
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).stdout.read().decode('utf-8')

def list_submodules():
    for line in command_output('git config --file .gitmodules --get-regexp submodule\..*\.url').splitlines():
        [key, value] = line.split(' ', 1)
        name = key.split('.', 1)[1].rsplit('.', 1)[0]
        yield {
            'local': command_output('git config --file .gitmodules submodule.%s.path' % (name, )).strip(),
            'remote': value,
            }

class ChangeDir:
    def __init__(self, target):
        self.target = target
    def __enter__(self):
        self.prev_dir = os.getcwd()
        os.chdir(self.target)
    def __exit__(self, type, value, traceback):
        os.chdir(self.prev_dir)

submodule_sources = {}

# Python 2 compatibility
try:
    input = raw_input
except NameError:
    pass

todos = collections.deque([os.getcwd()])
while todos:
    cur = todos.popleft()
    print('Initializing submodules at %s' % (cur, ))
    os.chdir(cur)
    subs = list(list_submodules())
    for sub in subs:
        source = submodule_sources.get(sub['remote'])
        if source:
            print('Using source %s for submodule %s' % (source, sub['local']))
            subprocess.check_call(['git', 'submodule', 'update', '--reference', source, '--init', sub['local']])
        else:
            print('Initializing new submodule %s' % (sub['local'], ))
            try:
                subprocess.check_call(['git', 'submodule', 'update', '--init', sub['local']])
            except:
                print('Failed initializing submodule %s' % (sub['local'], ))
                sys.stdout.write('Continue (y/n)? ')
                if not input().lower().startswith('y'):
                    sys.exit(1)
                continue
        with ChangeDir(sub['local']):
            cur_dir = os.getcwd()
            submodule_sources[sub['remote']] = os.getcwd()
            todos.append(cur_dir)
