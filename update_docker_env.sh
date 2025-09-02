#!/bin/bash

# 获取当前脚本所在目录（即 vue-fastapi-admin 的根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 更新 .env 文件中的 PROJECT_ROOT
sed -i "s|PROJECT_ROOT=.*|PROJECT_ROOT=${SCRIPT_DIR}|" "${SCRIPT_DIR}/conf.d/docker/.env"

echo "Updated PROJECT_ROOT to: ${SCRIPT_DIR}"
