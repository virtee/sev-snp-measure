#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib
import base64
import ctypes
import argparse
from ctypes import c_uint8

from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

LaunchDigest = c_uint8 * 48
ECParam = c_uint8 * 52
ECSignature = c_uint8 * 512
ECPubKey = c_uint8 * 1028
Qx = c_uint8 * 72
Qy = c_uint8 * 72

DefaultIDs = bytes(0x20)
DefaultVersion = 1
DefaultGuestSVN = bytes(4)
DefaultPolicy = 196608  # [0,0,3,0,0,0,0,0]
DefaultKeyAlgo = 1
CurveP384 = 2
ECKeyLength = 1028
ECSigLength = 512
SnpSigLength = 72


def main() -> int:
    parser = argparse.ArgumentParser(prog='snp-create-id-block',
                                     description='Calculate AMD SEV-SNP guest id block')
    parser.add_argument('--measurement', metavar='VALUE', type=str,
                        help='Guest launch measurement in Base64 encoding', default=None)
    parser.add_argument('--idkey', metavar='PATH', help='id private key file')
    parser.add_argument('--authorkey', metavar='PATH', help='author private key file')
    args = parser.parse_args()

    if args.idkey is None or args.authorkey is None:
        parser.error("missing key files for id block")
    ld = base64.b64decode(args.measurement)
    result = snp_calc_id_block(ld, args.idkey, args.authorkey)

    print(result)
    return 0


class IdBlock(ctypes.Structure):
    _fields_ = [
        ("launch_digest", LaunchDigest),
        ("ids", ctypes.c_char * 32),
        ("version", ctypes.c_uint32),
        ("guest_svn", ctypes.c_char * 4),
        ("policy", ctypes.c_uint64)
    ]


class IdAuth(ctypes.Structure):
    _fields_ = [
        ("id_key_algo", ctypes.c_uint32),
        ("auth_key_algo", ctypes.c_uint32),
        ("reserved1", ctypes.c_char * 56),
        ("block_sig", ECSignature),
        ("id_key", ECPubKey),
        ("reserved2", ctypes.c_char * 60),
        ("id_key_sig", ECSignature),
        ("author_key", ECPubKey),
        ("reserved3", ctypes.c_char * 892),
    ]


class ECPublicKey(ctypes.Structure):
    _fields_ = [
        ("curve", ctypes.c_uint32),
        ("qx", Qx),
        ("qy", Qy),
        ("reserved", ctypes.c_char * 0x370)
    ]


class SnpSignature(ctypes.Structure):
    _fields_ = [
        ("sig_r", ctypes.c_char * SnpSigLength),
        ("sig_s", ctypes.c_char * SnpSigLength),
        ("reserved", ctypes.c_char * 368)
    ]


def snp_calc_id_block(ld: bytes, idkey_file: str, authorkey_file: str) -> str:
    digest = LaunchDigest.from_buffer_copy(ld)
    id_block = IdBlock(
        launch_digest=digest,
        ids=DefaultIDs,
        version=DefaultVersion,
        guest_svn=DefaultGuestSVN,
        policy=DefaultPolicy
    )
    id_privkey = load_private_key_from_pem_file(idkey_file)
    author_privkey = load_private_key_from_pem_file(authorkey_file)
    author_key = ECPubKey.from_buffer_copy(marshal_ec_public_key(author_privkey))
    id_key = ECPubKey.from_buffer_copy(marshal_ec_public_key(id_privkey))
    block_sig = ECSignature.from_buffer_copy(sign_in_snp_format(id_privkey, bytes(id_block)))
    id_key_sig = ECSignature.from_buffer_copy(sign_in_snp_format(author_privkey, marshal_ec_public_key(id_privkey)))
    id_auth = IdAuth(
        id_key_algo=DefaultKeyAlgo,
        auth_key_algo=DefaultKeyAlgo,
        block_sig=block_sig,
        id_key=id_key,
        id_key_sig=id_key_sig,
        author_key=author_key,
    )
    # key digests for attestation report validating
    id_key_digest = pub_to_digest(id_privkey)
    author_key_digest = pub_to_digest(author_privkey)
    output_str = f"id-block={base64.b64encode(bytes(id_block)).decode()},"
    output_str += f"id-auth={base64.b64encode(bytes(id_auth)).decode()}\n"
    output_str += f"id_key_hash: {base64.b64encode(id_key_digest).decode()}\n"
    output_str += f"author_key: {base64.b64encode(author_key_digest).decode()}"

    return output_str


def sign_in_snp_format(priv_key: ec.EllipticCurvePrivateKey, data: bytes) -> bytes:
    signature_raw = priv_key.sign(data, ec.ECDSA(hashes.SHA384()))
    r, s = utils.decode_dss_signature(signature_raw)
    sig_r = r.to_bytes(0x48, byteorder="little")
    sig_s = s.to_bytes(0x48, byteorder="little")
    signature = SnpSignature(
        sig_r=sig_r,
        sig_s=sig_s,
    )
    return bytes(signature)


def load_private_key_from_pem_file(pem_file_path: str) -> ec.EllipticCurvePrivateKey:
    with open(pem_file_path, "rb") as pem_file:
        pem_data = pem_file.read()

    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,  # Change this to a password if your PEM file is encrypted
        backend=default_backend()
    )
    if isinstance(private_key, ec.EllipticCurvePrivateKey):
        return private_key

    raise ValueError("The provided PEM file does not contain an EC private key.")


def marshal_ec_public_key(priv_key: ec.EllipticCurvePrivateKey) -> bytes:
    pub_key = priv_key.public_key()
    x = pub_key.public_numbers().x
    y = pub_key.public_numbers().y
    qx = x.to_bytes(0x48, byteorder="little")
    qy = y.to_bytes(0x48, byteorder="little")
    result = ECPublicKey(
        curve=CurveP384,
        qx=Qx.from_buffer_copy(qx),
        qy=Qy.from_buffer_copy(qy),
    )
    return bytes(result)


def pub_to_digest(priv_key: ec.EllipticCurvePrivateKey) -> bytes:
    hasher = hashlib.new("sha384")
    pub_bytes = marshal_ec_public_key(priv_key)
    hasher.update(pub_bytes)
    digest = hasher.digest()
    return digest
