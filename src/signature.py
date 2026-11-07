# SPDX-License-Identifier: MIT
import base64, hashlib

# RFC 8032 section 5.1
P = 2 ** 255 - 19
L = 2 ** 252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P
I = pow(2, (P - 1) // 4, P)
EDDSA = 22
ED25519_OID = bytes.fromhex("2b06010401da470f01")
HASHES = {8: hashlib.sha256, 10: hashlib.sha512}

class BadSignature(Exception):
    pass

def _recover_x(y, sign):
    xx = (y * y - 1) * pow(D * y * y + 1, P - 2, P)
    x = pow(xx, (P + 3) // 8, P)
    if (x * x - xx) % P:
        x = x * I % P
    if (x * x - xx) % P:
        raise BadSignature("not a curve point")
    if x & 1 != sign:
        x = P - x
    return x

def _decode(data):
    y = int.from_bytes(data, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    if y >= P:
        raise BadSignature("not a curve point")
    x = _recover_x(y, sign)
    return (x, y, 1, x * y % P)

def _add(a, b):
    x1, y1, z1, t1 = a
    x2, y2, z2, t2 = b
    pa = (y1 - x1) * (y2 - x2) % P
    pb = (y1 + x1) * (y2 + x2) % P
    pc = 2 * D * t1 * t2 % P
    pd = 2 * z1 * z2 % P
    e, f, g, h = pb - pa, pd - pc, pd + pc, pb + pa
    return (e * f % P, g * h % P, f * g % P, e * h % P)

def _multiply(point, scalar):
    result = (0, 1, 1, 0)
    while scalar:
        if scalar & 1:
            result = _add(result, point)
        point = _add(point, point)
        scalar >>= 1
    return result

def _same(a, b):
    return (a[0] * b[2] - b[0] * a[2]) % P == 0 and (a[1] * b[2] - b[1] * a[2]) % P == 0

_BASE_Y = 4 * pow(5, P - 2, P) % P
BASE = (_recover_x(_BASE_Y, 0), _BASE_Y, 1, _recover_x(_BASE_Y, 0) * _BASE_Y % P)

def ed25519_verify(public, message, signature):
    if len(public) != 32 or len(signature) != 64:
        return False
    try:
        a = _decode(public)
        r = _decode(signature[:32])
    except BadSignature:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= L:
        return False
    h = int.from_bytes(hashlib.sha512(signature[:32] + public + message).digest(), "little") % L
    return _same(_multiply(BASE, s), _add(r, _multiply(a, h)))

def _packets(data):
    pos = 0
    while pos < len(data):
        head = data[pos]
        if not head & 0x80:
            raise BadSignature("not OpenPGP data")
        if head & 0x40:
            tag = head & 0x3f
            first = data[pos + 1]
            if first < 192:
                length, pos = first, pos + 2
            elif first < 224:
                length, pos = ((first - 192) << 8) + data[pos + 2] + 192, pos + 3
            elif first == 255:
                length, pos = int.from_bytes(data[pos + 2:pos + 6], "big"), pos + 6
            else:
                raise BadSignature("partial OpenPGP packets are not supported")
        else:
            tag = (head >> 2) & 0x0f
            size = {0: 1, 1: 2, 2: 4}.get(head & 3)
            if size is None:
                raise BadSignature("indeterminate OpenPGP packet length")
            length = int.from_bytes(data[pos + 1:pos + 1 + size], "big")
            pos += 1 + size
        yield tag, data[pos:pos + length]
        pos += length

def _mpi(data, pos):
    bits = int.from_bytes(data[pos:pos + 2], "big")
    end = pos + 2 + (bits + 7) // 8
    return data[pos + 2:end], end

def _dearmor(text):
    lines = text.strip().splitlines()
    body = []
    started = False
    for line in lines[1:]:
        if not started:
            started = line.strip() == ""
            continue
        if line.startswith("=") or line.startswith("-----"):
            break
        body.append(line.strip())
    return base64.b64decode("".join(body))

def signing_keys(armored):
    keys = {}
    for tag, body in _packets(_dearmor(armored)):
        if tag != 14 or body[0] != 4 or body[5] != EDDSA:
            continue
        oid_len = body[6]
        if body[7:7 + oid_len] != ED25519_OID:
            continue
        point, end = _mpi(body, 7 + oid_len)
        if len(point) != 33 or point[0] != 0x40:
            continue
        fingerprint = hashlib.sha1(b"\x99" + len(body[:end]).to_bytes(2, "big") + body[:end]).digest()
        keys[fingerprint] = point[1:]
    return keys

def _issuer(subpackets):
    pos = 0
    issuer = None
    while pos < len(subpackets):
        first = subpackets[pos]
        if first < 192:
            length, pos = first, pos + 1
        elif first < 255:
            length, pos = ((first - 192) << 8) + subpackets[pos + 1] + 192, pos + 2
        else:
            length, pos = int.from_bytes(subpackets[pos + 1:pos + 5], "big"), pos + 5
        kind = subpackets[pos] & 0x7f
        value = subpackets[pos + 1:pos + length]
        if kind == 33 and value[:1] == b"\x04":
            issuer = value[1:21]
        elif kind == 16 and issuer is None:
            issuer = value
        pos += length
    return issuer

def verify(data, signature, armored_key):
    keys = signing_keys(armored_key)
    for tag, body in _packets(signature):
        if tag != 2 or body[0] != 4 or body[1] != 0 or body[2] != EDDSA:
            continue
        hash_algo = HASHES.get(body[3])
        if hash_algo is None:
            continue
        hashed_len = int.from_bytes(body[4:6], "big")
        hashed = body[6:6 + hashed_len]
        pos = 6 + hashed_len
        unhashed_len = int.from_bytes(body[pos:pos + 2], "big")
        unhashed = body[pos + 2:pos + 2 + unhashed_len]
        pos += 2 + unhashed_len + 2
        r, pos = _mpi(body, pos)
        s, pos = _mpi(body, pos)
        issuer = _issuer(hashed) or _issuer(unhashed)
        trailer = body[:6 + hashed_len]
        digest = hash_algo(data + trailer + b"\x04\xff" + len(trailer).to_bytes(4, "big")).digest()
        for fingerprint, public in keys.items():
            if issuer not in (fingerprint, fingerprint[-8:]):
                continue
            if ed25519_verify(public, digest, r.rjust(32, b"\0") + s.rjust(32, b"\0")):
                return
    raise BadSignature("no valid signature by the Bande archive key")
