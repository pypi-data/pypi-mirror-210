# Copyright 2022 Akamai Technologies, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import dataclasses

from aioquic.tls import CipherSuite, SessionTicket


@dataclasses.dataclass
class ClientTLSConfig:
    """
    Client TLS configuration.
    """

    #: Allows to proceed for server without valid TLS certificates.
    insecure: bool = False

    #: File with CA certificates to trust for server verification
    cafile: str | None = None

    #: Directory with CA certificates to trust for server verification
    capath: str | None = None

    #: Blob with CA certificates to trust for server verification
    cadata: bytes | None = None

    #: If provided, will trigger an additional load_cert_chain() upon the QUIC Configuration
    certfile: str | None = None

    keyfile: str | None = None

    keypassword: str | bytes | None = None

    #: Manually set ciphers to be used in your DTLS
    cipher_suites: list[CipherSuite] | None = None

    #: The DTLS session ticket which should be used for session resumption
    session_ticket: SessionTicket | None = None

    def clone(self) -> ClientTLSConfig:
        """
        Clone this instance.
        """
        return dataclasses.replace(self)
