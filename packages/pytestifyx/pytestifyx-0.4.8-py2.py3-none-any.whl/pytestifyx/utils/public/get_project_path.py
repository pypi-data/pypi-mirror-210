from pathlib import Path
import os

def get_project_path():
    """
    获取当前项目根路径
    :return: 根路径
    """

    current_path = Path.cwd()
    while True:
        if (current_path / 'requirements.txt').exists():
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            raise Exception("项目根目录未找到")
        current_path = parent_path
    return current_path


def ensure_path_sep(path):
    """兼容 windows 和 linux 不同环境的操作系统路径 """

    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))

    return path
