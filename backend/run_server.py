
import os
import sys
import uvicorn

# 1. 强制切换工作目录到脚本所在目录 (backend)
# 这样不仅能找到 app 模块，也能让 .env 正确加载
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.insert(0, current_dir)

print(f"Server starting in: {current_dir}")

if __name__ == "__main__":
    # 2. 直接启动 uvicorn
    # 避免使用 shell 命令，减少中间环节
    try:
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"Startup Failed: {e}")
        # 将错误写入文件以防控制台丢失
        with open("startup_error.log", "w") as f:
            f.write(str(e))
