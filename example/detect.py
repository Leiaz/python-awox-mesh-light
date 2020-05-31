#!/usr/bin/env python3
# -*- mode: python; python-indent-offset: 4; indent-tabs-mode: nil -*-
# SPDX-License-Indentifier: MIT

''' Example '''

import os
import sys

PARENT_PATH = os.path.join(__file__, '..', '..', 'awoxmeshlight', '..')
LIB_PATH = os.path.abspath(PARENT_PATH)
sys.path.append(LIB_PATH)

from awoxmeshlight import AwoxMeshLight

MAC = os.getenv('MAC') or "A4:C1:38:FF:FF:FF"
print("info: Looking up mac=%s" % MAC)
LIGHT = AwoxMeshLight(MAC)
LIGHT.connect()
print("info: model=%s" % LIGHT.getModelNumber())
print("info: hardware=%s" % LIGHT.getHardwareRevision())
print("info: firmware=%s" % LIGHT.getFirmwareRevision())
LIGHT.disconnect()
