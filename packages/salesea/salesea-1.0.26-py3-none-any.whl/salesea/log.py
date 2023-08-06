import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

#############################################################################
#####Logger Handler##########################################################
# linux 和 windows 日志存储路径
# linux: /var/log/salesea/salesea.log
# windows: C:\Users\{username}\AppData\Local\salesea\logs\salesea.log

if os.name == "posix":
    log_path = Path("/var/log/salesea/")
else:
    log_path = Path(os.path.expandvars(r"%LOCALAPPDATA%")) / "salesea" / "logs"

log_path.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)  # 日志对象
logger.level = logging.INFO  # 日志级别
handler = logging.StreamHandler()  # 日志处理器
handler.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")  # 日志格式
logger.addHandler(handler)  # 添加日志处理器
# 日志文件处理器
fh = logging.handlers.RotatingFileHandler(log_path / "salesea.log", maxBytes=256 * 1024 * 10, backupCount=10)
fh.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")  # 日志格式
logger.addHandler(fh)  # 添加日志文件处理器
