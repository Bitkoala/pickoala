#!/bin/bash
# 切换到脚本所在目录
cd "$(dirname "$0")"

# === 开启文件日志记录 ===
LOG_FILE="$(pwd)/startup_debug.log"
exec 1>>"$LOG_FILE" 2>&1

echo "=========================================="
echo "Starting at $(date)"
echo "User: $(whoami)"
echo "Current directory: $(pwd)"
echo "Listing directories:"
ls -d *_venv/ 2>/dev/null || echo "No venv directories found matching *_venv/"

# 定义查找函数
find_python() {
    local venv_dir="$1"
    if [ -f "$venv_dir/bin/python3" ]; then
        echo "$venv_dir/bin/python3"
    elif [ -f "$venv_dir/bin/python" ]; then
        echo "$venv_dir/bin/python"
    else
        echo ""
    fi
}

PYTHON_BIN=""

# 1. 尝试特定的 hash 目录
if [ -d "b798abe6e1b1318ee36b0dcb3fb9e4d3_venv" ]; then
    echo "Found explicit venv dir: b798..."
    PYTHON_BIN=$(find_python "b798abe6e1b1318ee36b0dcb3fb9e4d3_venv")
fi

# 2. 如果没找到，尝试搜索任意 _venv
if [ -z "$PYTHON_BIN" ]; then
    VENV_DIR=$(find . -maxdepth 1 -type d -name '*_venv' | head -n 1)
    if [ -n "$VENV_DIR" ]; then
        echo "Found dynamic venv dir: $VENV_DIR"
        PYTHON_BIN=$(find_python "$VENV_DIR")
    fi
fi

# 3. 尝试 standard venv
if [ -z "$PYTHON_BIN" ] && [ -d "venv" ]; then
     echo "Found standard venv dir"
     PYTHON_BIN=$(find_python "venv")
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "CRITICAL ERROR: Could not find any python executable in any venv directory!"
    echo "Checking contents of current directory:"
    ls -F
    exit 1
fi

echo "Using Python: $PYTHON_BIN"
echo "Python version: $($PYTHON_BIN --version)"

# 启动服务
echo "Executing uvicorn..."
exec $PYTHON_BIN -m uvicorn app.main:app --host 0.0.0.0 --port 8000

