#!/bin/bash

# 激活 conda 环境
source /opt/conda/etc/profile.d/conda.sh
conda activate py312

# ✅ 可选：限制 OpenMP 并发线程数，防止 TLS block 冲突
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# 启动应用
exec python run.py