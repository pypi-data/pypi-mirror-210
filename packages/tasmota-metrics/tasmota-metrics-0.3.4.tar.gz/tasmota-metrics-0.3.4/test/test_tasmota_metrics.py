#!/usr/bin/env python
#
# SPDX-FileCopyrightText: 2018-2023 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Apache-2.0

from __future__ import print_function

import io
import sys
from typing import Dict

try:
    import tasmota_metrics.core
except ImportError:
    sys.path.append('..')
    import tasmota_metrics.core


if __name__ == '__main__':
    # Should deliver a RuntimeError as the 'test' header doesn't exist
    try:
        tasmota_metrics.core.scan_to_header([], 'test')
    except RuntimeError as e:
        assert "Didn't find line" in str(e)

    # Should deliver a RuntimeError as there's no content under the heading
    try:
        tasmota_metrics.core.load_segments(io.StringIO('Memory Configuration'))
        pass
    except RuntimeError as e:
        assert 'End of file' in str(e)

    segments = {'iram0_0_seg': {'origin': 0, 'length': 0},
                'dram0_0_seg': {'origin': 0, 'length': 0}}
    sections = {}  # type: Dict

    print(tasmota_metrics.core.get_summary('a.map', segments, sections, 'esp32'), end='')
