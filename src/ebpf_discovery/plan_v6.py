"""Fixed fresh study cells and independent, reproducible arm-order streams."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

SYSTEMS = ('petclinic', 'otel_demo', 'deathstarbench')
MODES = ('absent', 'partial', 'full')
COLLECTORS = ('none', 'obi', 'coroot', 'deepflow')
REPETITIONS = (9, 10, 11)
STUDY = 'clean-restart-v6'


def random_stream(system: str, mode: str, repetition: int, purpose: str) -> random.Random:
    if system not in SYSTEMS or mode not in MODES or repetition not in REPETITIONS:
        raise ValueError('outside the fixed fresh study')
    encoded = json.dumps([STUDY, system, mode, repetition, purpose], separators=(',', ':')).encode()
    return random.Random(int.from_bytes(hashlib.sha256(encoded).digest(), 'big'))


def block(system: str, mode: str, repetition: int) -> dict:
    orders = {}
    for phase in ('training', 'validation'):
        order = list(COLLECTORS)
        random_stream(system, mode, repetition, phase + '-arm-order').shuffle(order)
        orders[phase] = order
    return {'study': STUDY, 'system': system, 'mode': mode, 'repetition': repetition,
            'block_id': f'{system}-{mode}-{repetition}', 'arm_orders': orders,
            'cells': [{'collector': c, 'cell_id': f'{system}-{mode}-{repetition}-{c}'}
                      for c in COLLECTORS]}


def complete_plan() -> dict:
    blocks = [block(s, m, r) for s in SYSTEMS for m in MODES for r in REPETITIONS]
    return {'study': STUDY, 'blocks': blocks, 'scientific_cells': 108,
            'deployment_segments': 216, 'historical_measurements_reused': False,
            'protocol': 'docs/PROTOCOL_V6.md'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('a frozen study plan must not be overwritten')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(complete_plan(), indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
