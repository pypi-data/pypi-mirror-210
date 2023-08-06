import configparser
from pathlib import Path

from .log import logger
from .utils import out_print

#############################################################################
#####Config Parser###########################################################
LOG_FORMAT = '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for"'
SERVER_NAME = None
NGINX_PATH = None
REQUEST_CONCURRENCY = 1
VISIT_APIKEY = None
CHECK_INTERVAL = 5
DEFAULT_CONF_FILE = "salesea.ini"


def load_config(CONF_FILE=DEFAULT_CONF_FILE):
    global LOG_FORMAT, SERVER_NAME, NGINX_PATH, REQUEST_CONCURRENCY, VISIT_APIKEY, CHECK_INTERVAL
    CONF_FILE = Path(CONF_FILE)
    if not CONF_FILE.exists():
        logger.error(f"[{CONF_FILE}] 配置文件不存在")
        exit(1)
    try:
        config = configparser.ConfigParser()  # 类实例化
        config.read(f"{CONF_FILE}", encoding="utf-8")  # 读取配置文件
        # LOG_FORMAT = config.get("nginx", "log_format")
        SERVER_NAME = config.get("nginx", "server_name") or None
        NGINX_PATH = config.get("nginx", "nginx_path") or None
        REQUEST_CONCURRENCY = config.getint("request", "concurrency")
        VISIT_APIKEY = config.get("salesea", "visit_apikey")
        CHECK_INTERVAL = config.getint("salesea", "interval")

        if not SERVER_NAME:
            logger.error(f"[{CONF_FILE}] 配置文件错误 [nginx]下[server_name]不能为空")
            exit(1)

        if not VISIT_APIKEY:
            logger.error(f"[{CONF_FILE}] 配置文件错误 [salesea]下[visit_apikey]不能为空")
            exit(1)

        if not LOG_FORMAT:
            logger.error(f"[{CONF_FILE}] 配置文件错误 [nginx]下[log_format]不能为空")
            exit(1)

        CHECK_INTERVAL = 5 if CHECK_INTERVAL <= 5 else CHECK_INTERVAL
        REQUEST_CONCURRENCY = 1 if REQUEST_CONCURRENCY <= 1 else REQUEST_CONCURRENCY

    except configparser.NoSectionError as e:
        logger.error(f"[{CONF_FILE}] 配置文件错误 [{e.section}]不存在")
        exit(1)
    except configparser.NoOptionError as e:
        logger.error(f"[{CONF_FILE}] 配置文件错误 [{e.section}]下[{e.option}]不存在")
        exit(1)
    except ValueError as e:
        logger.error(f"[{CONF_FILE}] 配置文件错误 {e}")
        exit(1)


def generate_config():
    config = configparser.ConfigParser()
    config['nginx'] = {
        'server_name': '',
        'nginx_path': '',
    }
    config['request'] = {
        'concurrency': 10,
    }
    config['salesea'] = {
        'visit_apikey': '',
        'interval': 60,
    }
    # 询问用户
    while True:
        config['nginx']['server_name'] = input('请输入域名(必填): ')
        if config['nginx']['server_name']:
            break

    while True:
        config['salesea']['visit_apikey'] = input('请输入访问密钥(必填): ')
        if config['salesea']['visit_apikey']:
            break

    # 请输入日志扫描间隔 不能小于5秒
    while True:
        interval = config['salesea']['interval']
        try:
            i = input('请输入日志扫描间隔(默认60秒): ')
            interval = int(i) if i else 60
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            continue

        if interval >= 5:
            config['salesea']['interval'] = str(interval)
            break
        out_print('日志扫描间隔不能小于5秒')

    with open(DEFAULT_CONF_FILE, 'w') as f:
        config.write(f)
        out_print(f'配置文件已生成: {DEFAULT_CONF_FILE}')
        exit(0)
