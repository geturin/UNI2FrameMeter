#!/usr/bin/env python3
"""Build the PE32 data collector and its injection helper."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', default='i686-w64-mingw32-gcc')
    parser.add_argument('--cxx', default='i686-w64-mingw32-g++')
    args = parser.parse_args()
    for compiler in (args.cc, args.cxx):
        machine = subprocess.check_output([compiler, '-dumpmachine'], text=True).strip()
        if machine != 'i686-w64-mingw32':
            raise SystemExit('The collector and helper require the i686-w64-mingw32 compiler.')
    vendor = ROOT / 'vendor/minhook'
    manifest = json.loads((vendor / 'SOURCE.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        actual = hashlib.sha256((vendor / item['path']).read_bytes()).hexdigest()
        if actual != item['sha256']:
            raise SystemExit('MinHook source checksum mismatch: ' + item['path'])
    out = ROOT / 'build/native'
    obj = ROOT / 'build/native-obj'
    out.mkdir(parents=True, exist_ok=True)
    obj.mkdir(parents=True, exist_ok=True)
    flags = ['-O2', '-Wall', '-Wextra', '-Werror', '-finput-charset=UTF-8',
             '-I' + str(ROOT / 'native'), '-I' + str(vendor / 'include')]

    def run(argv):
        subprocess.run([str(arg) for arg in argv], cwd=ROOT, check=True)

    objects = []
    for name in ('buffer', 'hook', 'trampoline', 'hde/hde32'):
        target = obj / (name.replace('/', '_') + '.o')
        run([args.cc, *flags, '-Wno-unused-parameter', '-c',
             vendor / 'src' / (name + '.c'), '-o', target])
        objects.append(target)
    cpp = [args.cxx, *flags, '-std=c++17', '-static', '-static-libgcc', '-static-libstdc++']
    run([*cpp, '-shared', '-Wl,--kill-at', ROOT / 'native/runtime.cpp', *objects,
         '-ladvapi32', '-o', out / 'uni2-frame-meter.dll'])
    run([*cpp, '-municode', ROOT / 'native/host.cpp', '-ladvapi32',
         '-o', out / 'uni2-frame-meter-host.exe'])
    receipt = {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
               for name in ('uni2-frame-meter-host.exe', 'uni2-frame-meter.dll')}
    (out / 'native-sha256.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
