# build.py
import os
import subprocess
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
mainpy = os.path.join(BASE_DIR, 'main.py')
# ico = os.path.join(BASE_DIR, 'user_data','logo.ico')

def build():
    # 输出目录
    output_dir = r"D:\Tvid"
    
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # 获取PySide6资源路径 - 更健壮的方式
        import PySide6
        pyside6_dir = Path(PySide6.__file__).parent
        pyside6_resources = str(pyside6_dir / "resources")
        
        # 检查资源目录是否存在
        if not os.path.exists(pyside6_resources):
            raise FileNotFoundError(f"PySide6资源目录不存在: {pyside6_resources}")
            
    except ImportError:
        print("错误: 无法导入PySide6，请确保已安装PySide6")
        return
    except Exception as e:
        print(f"获取PySide6资源路径时出错: {e}")
        return
    
    # 构建Nuitka命令
    command = [
        "python",
        "-m",
        "nuitka",
        # "--onefile",
        '--standalone',
        "--enable-plugin=pyside6",
        "--windows-disable-console",  # 如果需要隐藏控制台窗口可以取消注释
        "--include-data-files=config.json=config.json",  # 修改这里，指定明确的目标文件名
        # f"--windows-icon-from-ico={ico}",
        # "--include-data-dir=user_data=user_data",
        # "--include-data-dir=browser_data=browser_data",
        f"--output-dir={output_dir}",
        "--include-module=config",
        "--include-module=utils.hotkey",
        f"--include-data-dir={pyside6_resources}=PySide6/resources",
        "--include-qt-plugins=platforms",
        "--assume-yes-for-downloads",
        mainpy,
    ]

    
    # 执行打包命令
    print("开始打包...")
    print(f"包含的资源目录: {pyside6_resources}")
    subprocess.run(command, check=True)
    print(f"打包完成！输出文件在 {output_dir} 目录中")

if __name__ == "__main__":
    build()
