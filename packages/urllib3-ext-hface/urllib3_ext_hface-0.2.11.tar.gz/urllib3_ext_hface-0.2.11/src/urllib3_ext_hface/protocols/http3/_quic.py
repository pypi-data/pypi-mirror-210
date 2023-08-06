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

from dataclasses import dataclass

import aioquic.buffer
import aioquic.quic.packet


class InvalidPacket(ValueError):
    pass


@dataclass
class PacketInfo:
    version: int | None
    packet_type: int
    destination_connection_id: bytes
    source_connection_id: bytes

    length: int

    @property
    def is_initial_packet(self) -> bool:
        if self.length < 1200:
            return False
        return self.packet_type == aioquic.quic.packet.PACKET_TYPE_INITIAL
