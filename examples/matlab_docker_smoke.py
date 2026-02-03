"""Smoke test for Docker-backed MATLABProvider.

Usage:
  export MATLAB_BACKEND=docker
  export MATLAB_DOCKER_CONTAINER=matlab_r2025a
  export MATLAB_WORK_MOUNT=/data/cmbagents/tmp/matlab_shared
  # optional: MATLAB_ENTRYPOINT=/data/cmbagents/tmp/matlab_shared/entrypoint.m
  python -m Denario.examples.matlab_docker_smoke
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from denario.providers.orchestrator import PremiumMathematicalOrchestrator  # noqa: E402


def main():
    cfg = {
        'matlab': {
            'enabled': True,
            'backend': os.getenv('MATLAB_BACKEND', 'docker'),
            'container_name': os.getenv(
                'MATLAB_DOCKER_CONTAINER', 'matlab_r2025a'),
            'work_mount': os.getenv(
                'MATLAB_WORK_MOUNT', '/data/cmbagents/tmp/matlab_shared'),
            'entrypoint': os.getenv('MATLAB_ENTRYPOINT'),
        },
        'wolfram_alpha': {'enabled': False},
    }
    orch = PremiumMathematicalOrchestrator(cfg)
    print('Health:', orch.healthcheck())
    result = orch.compute('integrate exp(-x^2) from -infinity to infinity')
    print('Result:', result.plaintext)
    print('LaTeX:', result.latex)


if __name__ == '__main__':
    main()
