import importlib.util
import sys

# import settings
# module_name 只是声明了一个注册在sys.modules["xxx"]中的名字，不能直接import/调用
def import_module_from_path(file_path, module_name="settings", ):
    # 创建模块的规范
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Cannot find module {module_name} at {file_path}")

    # 从规范创建模块
    module = importlib.util.module_from_spec(spec)

    # 将模块添加到sys.modules
    sys.modules[module_name] = module

    # 执行模块
    spec.loader.exec_module(module)

    return module