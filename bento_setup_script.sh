#!/bin/bash
set -euxo pipefail

# used to create a custom container for BentoML
pip install 'numpy==1.23.5' --force-reinstall
