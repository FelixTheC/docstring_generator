#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 24.08.21
@author: felix
"""
import inspect
from pathlib import Path

if __name__ == '__main__':
    for file in Path().cwd().parent.glob("*/*.py"):
        if file.name != "gen_docs.py":
            data = {}
            exec(file.read_text(), globals(), data)
            if 'foo' in data:
                print(data["foo"].__doc__)
                for idx, line in enumerate(file.read_text().split('\n')):
                    print(f'{idx}: {line}')
