#!/usr/bin/env python3
import sys, json, os
print('PYTHONPATH env:', os.getenv('PYTHONPATH'))
print('sys.executable:', sys.executable)
print('sys.path (first 10):')
for i, p in enumerate(sys.path[:20]):
    print(i, p)
