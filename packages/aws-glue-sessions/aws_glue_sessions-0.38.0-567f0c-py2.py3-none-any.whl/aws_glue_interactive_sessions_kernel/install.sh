#!/bin/bash

# Move kernels to shared folder
SYSTEM_PYTHON_PREFIX=$(python3 -c "from __future__ import print_function;import sys; print(sys.prefix)")
PLATFORM_OS=$(python3 -c 'import platform; print(platform.system())')
case "${PLATFORM_OS}" in
  Darwin)
    shared_juptyer_path="$HOME/Library/Jupyter/kernels"
  ;;
  *)
  shared_juptyer_path="${SYSTEM_PYTHON_PREFIX}/share/jupyter/kernels"
  ;;
esac
mkdir -p ${shared_juptyer_path}
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
rm -rf "${shared_juptyer_path}/glue_pyspark"
rm -rf "${shared_juptyer_path}/glue_spark"
rm -rf "${shared_juptyer_path}/glue_kernel_utils"
cp -a "${DIR}/glue_pyspark" "${shared_juptyer_path}/"
cp -a "${DIR}/glue_spark" "${shared_juptyer_path}/"
cp -a "${DIR}/glue_kernel_utils" "${shared_juptyer_path}/"
cp -a "${DIR}/logos/" "${shared_juptyer_path}/glue_pyspark/"
cp -a "${DIR}/logos/" "${shared_juptyer_path}/glue_spark/"
