"""sgx_pck_extension module."""

from typing import Dict, Any

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

from ._lib_sgx_pck_extension import sgx_pck_extension_from_pem


def sgx_pck_extension_from_cert(cert: x509.Certificate) -> Dict[str, Any]:
    return sgx_pck_extension_from_pem(cert.public_bytes(encoding=Encoding.PEM))


__all__ = ["sgx_pck_extension_from_pem", "sgx_pck_extension_from_cert"]
