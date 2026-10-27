# SPDX-License-Identifier: MIT

def build(src, dest, vars):
    if isinstance(vars, (list, tuple)):
        vars = b"".join(i.encode("ascii") + b"\n" for i in vars) + b"\0\0\0\0"

    with open(src, "rb") as fd:
        unboot_data = fd.read()

    with open(dest, "wb") as fd:
        fd.write(unboot_data + vars)

def extract_vars(src):
    with open(src, "rb") as fd:
        unboot_data = fd.read()

    try:
        vars = unboot_data.split(b"STACKBOT")[1].split(b"\0")[0].decode("ascii")
    except Exception:
        return None

    return [i for i in vars.split("\n") if i]

def get_version(path):
    data = open(path, "rb").read()
    if b"##unboot_ver##" in data:
        return data.split(b"##unboot_ver##")[1].split(b"\0")[0].decode("ascii")
    else:
        return None
