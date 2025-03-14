import logging
import sys
from datetime import datetime
import os

# 配置控制台输出为 UTF-8 编码，确保控制台能够正确显示中文
sys.stdout.reconfigure(encoding='utf-8')

# 创建日志记录器，并设置日志级别
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # 最详细的日志级别

# 检查是否已经添加了处理器，防止重复添加
if not logger.handlers:
    # record exp results
    datetime_now = datetime.now().strftime("%Y%m%d-%H%M%S")
    exp_name = f"{datetime_now}"
    exp_dir = os.path.join("outputs", exp_name)
    os.makedirs(exp_dir, exist_ok=True)

    # 创建文件处理器，并指定日志文件名和编码
    file_handler = logging.FileHandler(exp_dir + '/_output_.log', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 将文件处理器添加到 logger
    logger.addHandler(file_handler)

    # 创建控制台处理器，并设置日志级别
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
