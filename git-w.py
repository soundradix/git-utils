#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
git-w.py

A tool to normalize line endings to reduce diffs.
It may normalize line endings to either '\n' (unix) or '\r\n' (windows)
depending on which one best reduces the diff size.
'''

import subprocess

def command_output(cmd):
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).stdout.read().decode('utf-8')

def diffs(options = ''):
    for line in command_output('git diff --stat' + (' ' if options else '') + options).splitlines()[:-1]:
        filename, stats = line.split(' | ', 1)
        yield filename.strip(), int(stats.split()[0])

for ((filename, stats), (filename_w, stats_w)) in zip(diffs(), diffs('-w')):
    assert filename == filename_w
    if stats <= stats_w:
        continue
    def check_success(label):
        new_stats_txt = command_output('git diff --stat %s' % filename).strip()
        new_stats = int(new_stats_txt.split(' | ', 1)[1].split()[0]) if new_stats_txt else 0
        if new_stats >= stats:
            return False
        print('%s: Changed to %s line endings, reducing diff by %d lines.' % (filename, label, stats-new_stats))
        return True
    content = open(filename, 'rb').read()
    unix_style = content.replace(b'\r', b'')
    open(filename, 'wb').write(unix_style)
    if check_success('unix'):
        continue
    windows_style = unix_style.replace(b'\n', b'\r\n')
    open(filename, 'wb').write(windows_style)
    if check_success('windows'):
        continue
    open(filename, 'wb').write(content)
    print('%s: No simple fix' % filename)
