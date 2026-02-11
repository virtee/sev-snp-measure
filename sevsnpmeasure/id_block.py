#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib
import base64
from abc import ABC, abstractmethod
import ctypes
from ctypes import c_uint8

from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

import sdkms.v1 as sdkms

class EcSigner(ABC):
    @abstractmethod
    def sign(self, data: bytes) -> bytes:
        """
        Sign `data`, returning the signature in DER-encoded ASN.1
        """
        pass

    @abstractmethod
    def public_key(self) -> ec.EllipticCurvePublicKey:
        """
        Retrieve the public key
        """
        pass

class FileSigner(EcSigner):
    def __init__(self, pem_file_path: str):
        with open(pem_file_path, "rb") as pem_file:
            pem_data = pem_file.read()

        private_key = serialization.load_pem_private_key(
            pem_data,
            password = None,
            backend = default_backend()
        )
        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            raise ValueError("The provided PEM file does not contain an EC private key.")

        self.k = private_key

    def sign(self, data: bytes) -> bytes:
        return self.k.sign(data, ec.ECDSA(hashes.SHA384(), deterministic_signing=True))

    def public_key(self) -> ec.EllipticCurvePublicKey:
        return self.k.public_key()

class SdkmsSigner(EcSigner):
    def __init__(self, api_client: sdkms.ApiClient, sobject: sdkms.SobjectDescriptor):
        self.k = sdkms.SecurityObjectsApi(api_client).get_security_object_ex(sobject)
        if self.k.obj_type != sdkms.ObjectType.EC:
            raise ValueError("The provided SobjectDescriptor doesn't refer to an EC key.")

        self.api_client = api_client

    def sign(self, data: bytes) -> bytes:
        req = sdkms.SignRequest(data=bytearray(data), hash_alg=sdkms.DigestAlgorithm.SHA384, deterministic_signature=True)
        return bytes(sdkms.SignAndVerifyApi(api_client=self.api_client).sign(self.k.kid, req).signature)

    def public_key(self) -> ec.EllipticCurvePublicKey:
        return serialization.load_der_public_key(self.k.pub_key)

DefaultVersion = 1
DefaultPolicy = 0x20000 # reserved bit 17 must be one. TODO: proper policy
DefaultKeyAlgo = 1
CurveP384 = 2
ECKeyLength = 1028
ECSigLength = 512
SnpSigLength = 72

LaunchDigest = c_uint8 * 48
ECParam = c_uint8 * 52
ECSignature = c_uint8 * 512
ECPubKey = c_uint8 * 1028
Qx = c_uint8 * 72
Qy = c_uint8 * 72
SigR = c_uint8 * SnpSigLength
SigS = c_uint8 * SnpSigLength

class CheckedCtypesStruct(ctypes.Structure):
    def __init__(self, *args, **kwargs):
        field_names = {name for name, _ in self._fields_}
        unknown = set(kwargs) - field_names

        if unknown:
            raise TypeError(
                f"{type(self).__name__}: Unknown fields: {', '.join(unknown)}"
            )
            for key in unknown:
                kwargs.pop(key)

        super().__init__(*args, **kwargs)

class IdBlock(CheckedCtypesStruct):
    _fields_ = [
        ("ld", LaunchDigest),
        ("family_id", ctypes.c_char * 16),
        ("image_id", ctypes.c_char * 16),
        ("version", ctypes.c_uint32),
        ("guest_svn", ctypes.c_char * 4),
        ("policy", ctypes.c_uint64)
    ]


class IdAuth(CheckedCtypesStruct):
    _fields_ = [
        ("id_key_algo", ctypes.c_uint32),
        ("auth_key_algo", ctypes.c_uint32),
        ("reserved1", ctypes.c_char * 56),
        ("id_block_sig", ECSignature),
        ("id_key", ECPubKey),
        ("reserved2", ctypes.c_char * 60),
        ("id_key_sig", ECSignature),
        ("author_key", ECPubKey),
        ("reserved3", ctypes.c_char * 892),
    ]


class ECPublicKey(CheckedCtypesStruct):
    _fields_ = [
        ("curve", ctypes.c_uint32),
        ("qx", Qx),
        ("qy", Qy),
        ("reserved", ctypes.c_char * 0x370)
    ]


class SnpSignature(CheckedCtypesStruct):
    _fields_ = [
        ("r", SigR),
        ("s", SigS),
        ("reserved", ctypes.c_char * 368)
    ]

def snp_calc_id_block(ld: bytes, family_id: bytes, image_id: bytes, guest_svn: int, id_privkey: EcSigner, author_privkey: EcSigner):
    digest = LaunchDigest.from_buffer_copy(ld)
    id_block = IdBlock(
        ld=digest,
        family_id=family_id,
        image_id=image_id,
        version=DefaultVersion,
        guest_svn=guest_svn.to_bytes(4, byteorder='little', signed=False),
        policy=DefaultPolicy
    )
    id_key = ECPubKey.from_buffer_copy(marshal_ec_public_key(id_privkey))
    block_sig = ECSignature.from_buffer_copy(sign_in_snp_format(id_privkey, bytes(id_block)))
    if author_privkey is not None:
        author_key = ECPubKey.from_buffer_copy(marshal_ec_public_key(author_privkey))
        id_key_sig = ECSignature.from_buffer_copy(sign_in_snp_format(author_privkey, marshal_ec_public_key(id_privkey)))
    else:
        author_key = ECPubKey()
        id_key_sig = ECSignature()
    id_auth = IdAuth(
        id_key_algo=DefaultKeyAlgo,
        auth_key_algo=DefaultKeyAlgo,
        id_block_sig=block_sig,
        id_key=id_key,
        id_key_sig=id_key_sig,
        author_key=author_key,
    )
    
    ret = {
        "id_block": bytes(id_block),
        "id_auth": bytes(id_auth),
        "id_key_digest": pub_to_digest(id_privkey),
    }
    
    if author_privkey is not None:
        ret["author_key_digest"] = pub_to_digest(author_privkey)

    return ret


def sign_in_snp_format(priv_key: EcSigner, data: bytes) -> bytes:
    signature_raw = priv_key.sign(data)
    r, s = utils.decode_dss_signature(signature_raw)
    sig_r = r.to_bytes(0x48, byteorder="little")
    sig_s = s.to_bytes(0x48, byteorder="little")
    signature = SnpSignature(
        r=SigR.from_buffer_copy(sig_r),
        s=SigS.from_buffer_copy(sig_s),
    )
    return bytes(signature)

def marshal_ec_public_key(priv_key: EcSigner) -> bytes:
    pub_key = priv_key.public_key()
    if not isinstance(pub_key.curve, ec.SECP384R1):
        raise ValueError('SNP only supports the EC curve P-384')
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


def pub_to_digest(priv_key: EcSigner) -> bytes:
    hasher = hashlib.new("sha384")
    pub_bytes = marshal_ec_public_key(priv_key)
    hasher.update(pub_bytes)
    digest = hasher.digest()
    return digest
