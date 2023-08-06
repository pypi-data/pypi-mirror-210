# coding: utf-8
import hashlib
import json
import re
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import List

from .log import logger


class Server:
    def __init__(self, nginx: "Nginx", **kwargs):
        self.nginx = nginx
        self.names: tuple = kwargs.get("names", tuple())
        self.listens = kwargs.get("listens", None)
        self.locations = kwargs.get("locations", None)
        self.includes = kwargs.get("includes", None)
        self.serverConfigPath = kwargs.get("serverConfigPath", None)

        if platform.system() == 'Windows':
            self.log_path = f"./logs/salesea-{self.names[0]}.log"
            self.salesea_conf_name = f"{self.names[0]}.salesea.conf"
            self.salesea_conf_dir = Path(os.path.expandvars(r"%LOCALAPPDATA%")) / "salesea" / "nginx" / "conf"
            self.salesea_conf_path = self.salesea_conf_dir / self.salesea_conf_name
        else:
            self.log_path = f"/var/log/nginx/salesea-{self.names[0]}.log"
            self.salesea_conf_name = f"{self.names[0]}.salesea.conf"
            self.salesea_conf_dir = Path("/etc/salesea/nginx/conf/")
            self.salesea_conf_path = self.salesea_conf_dir / self.salesea_conf_name

        logfile = Path(self.log_path)
        self.logfile = logfile if logfile.is_absolute() else Path(self.nginx.nginx_path).parent / logfile
        self.logfile.parent.mkdir(parents=True, exist_ok=True)

    def eq_name(self, server_name):
        # pattern = server_name.replace(".", "\.").replace("*", ".*?") if server_name is not None else None
        # if server_name is None:
        #     return False
        # for _ in self.names:
        #     if re.match(pattern, _) is not None:
        #         return True
        #
        # return False
        if not server_name:
            return False
        return server_name.strip() in self.names

    def eq_listen(self, listen):
        if not listen:
            return False
        return str(listen.strip()) in self.listens

    def is_salesea(self):
        for include in self.includes:
            if include.endswith(".salesea.conf"):
                return True

    # 读取配置文件, 报错返回None
    def read_config(self):
        path = Path(self.salesea_conf_path)
        if not path.exists():
            return None

        with path.open(mode="r", encoding="utf-8") as fobj:
            return fobj.read()

    def write_config(self, content):
        path = Path(self.salesea_conf_path)
        with path.open(mode="w", encoding="utf-8") as fobj:
            logger.debug(f"写入[{self.salesea_conf_path}]文件")
            fobj.write(content)

    def include_salesea(self, api_key):
        logger.debug(f"检查[{self.names[0]}]服务是否包含[salesea.conf]")
        global_flag = 0

        self.salesea_conf_dir.mkdir(parents=True, exist_ok=True)
        salesea_conf = f'access_log {self.log_path} salesea;\n\n'
        salesea_conf += 'if ($uri = /salesea) {\n'
        salesea_conf += '    rewrite ^(.*)$ $1 last;\n'
        salesea_conf += '}\n\n'
        salesea_conf += 'location = /salesea {\n'
        salesea_conf += '    add_header Content-Type text/plain;\n'
        salesea_conf += f'    return 200 "{api_key}";\n'
        salesea_conf += '}'

        if self.read_config() != salesea_conf:
            global_flag = 1
            self.write_config(salesea_conf)

        if self.is_salesea():
            return global_flag

        content = self.nginx.nginxConfigs.get(self.serverConfigPath)
        server_name = r'\s+'.join(self.names)

        # 行数
        servers = []
        include_ln = -1
        listen_ln = -1
        server_name_ln = -1
        listens = []

        # 常量标识
        line_num = 0
        flag = False
        flag_name = False
        block = ''
        num_of_quote = 0

        # 去除注释 除了# configuration file
        delete_comment = lambda x: x.group(0) if x.group(0).startswith('# configuration file ') else ''
        content1 = re.sub(r'#[^\n]*', delete_comment, content)

        for line in content1.splitlines():
            line_num += 1
            x = line.replace(' ', '').replace('\t', '')
            _ = line.strip()

            # 查询是否包含 include
            result = re.search(r"^include\s+.*?" + self.salesea_conf_name + ";", _)
            if result is not None:
                include_ln = line_num

            # 查询是否包含 listen
            result = re.search(r"^listen\s*((?:\d|\s)*)[^;]*;", _)
            if result is not None:
                listens.append(result.group(1).strip())
                listen_ln = line_num

            # 查询是否包含 server_name
            result = re.search(rf"^server_name\s+{server_name}\s*;", _)
            if result is not None:
                server_name_ln = line_num

            if x == 'server':
                flag_name = True

            if x.startswith('server{') or (flag_name and x.startswith('{')):
                num_of_quote += 1
                flag = True
                block += line
                continue

            if flag and '{' in line:
                num_of_quote += 1

            if flag and num_of_quote != 0:
                block += line

            if flag and '}' in line:
                num_of_quote -= 1

            if flag and num_of_quote == 0:
                servers.append({
                    'include_ln': include_ln,
                    'listen_ln': listen_ln,
                    'server_name_ln': server_name_ln,
                    'listens': tuple(listens),
                })
                flag = False
                flag_name = False
                block = ''
                num_of_quote = 0
                include_ln = -1
                listen_ln = -1
                server_name_ln = -1
                listens = []

        for server in servers:
            if server['listens'] == self.listens and not server['server_name_ln'] == -1 and server['include_ln'] == -1:
                logger.info(f"更新[{self.serverConfigPath}]文件")
                content = content.splitlines()
                # 获取缩进
                salesea_conf_path = self.salesea_conf_path.__str__().replace("\\", "/")
                indent = re.search(r'^(\s*)', content[server['server_name_ln'] - 1]).group(1)
                include_line = f'{indent}# --------Salesea Config Start--------\n'
                include_line += f'{indent}include {salesea_conf_path};'
                include_line += f'\n{indent}# --------Salesea Config End--------'
                content.insert(server['server_name_ln'], include_line)
                content = '\n'.join(content)
                self.nginx.nginxConfigs[self.serverConfigPath] = content
                with open(self.serverConfigPath, mode="w", encoding="utf-8") as fobj:
                    fobj.write(content.strip('\n') + '\n')

                global_flag = 1
                break

        """if re.search(r"\n\s*include\s+.*?" + self.salesea_conf_name + ";", content) is None:
            flag = 1
            logger.info(f"更新[{self.serverConfigPath}]文件")
            server_name = r'\s+'.join(self.names)
            salesea_conf_path = self.salesea_conf_path.__str__().replace("\\", "/")

            # 在后面追加include {salesea_conf_path};
            def append_include(matched):
                # 缩进
                indent = matched.group(1).replace('\n', '')
                append_include = f'\n{indent}# --------Salesea Config Start--------\n'
                append_include += matched.group(1).replace('\n', '') + f"include {salesea_conf_path};"
                append_include += f'\n{indent}# --------Salesea Config End--------'
                return matched.group() + append_include

            content = re.sub(
                rf"[;\n]([\s\t]*)server_name\s+{server_name}\s*;",
                append_include,
                content
            )

            self.nginx.nginxConfigs[self.serverConfigPath] = content
            with open(self.serverConfigPath, mode="w", encoding="utf-8") as fobj:
                fobj.write(content.strip('\n') + '\n')"""
        return global_flag

    def __repr__(self):
        return f"<Server {self.names}:{self.listens} {self.includes} {self.serverConfigPath}>"


class NginxException(Exception):
    pass


class Nginx:

    def __init__(self, nginx_path=None):
        self.nginx_conf = None
        self.nginx_path = nginx_path
        # 分文件的nginx配置
        self.nginxConfigs = None
        self.httpConfigPath = None
        self.backend = None  # 保存后端ip和pool name
        self.httpBlock = None  # 保存解析后端每个http块
        self.logFormats = None  # 保存解析后端每个log_format块
        self.includes = None  # 保存解析后端每个include块
        self.serverBlock = None  # 保存解析后端每个server块
        self.servers: List[Server] = None
        self.init()

    def init(self):
        self.nginxConfigs = dict()
        self.httpConfigPath = None
        self.backend = list()
        self.httpBlock = list()
        self.logFormats = dict()
        self.includes = list()
        self.serverBlock = list()
        self.servers = list()
        self.load_nginx_config()
        self.parse_file()
        self.parse_http_block()
        self.parse_server_block()

    def is_salesea(self):
        return self.logFormats.get("salesea") is not None

    def write_salesea_log_format(self):
        logger.debug("检查[log_format salesea]状态")
        if self.is_salesea():
            return
        salesea_log_format = """    # --------Salesea Config Start--------
    log_format salesea '$remote_addr - $remote_user [$time_local] "$request" '
             '$status $body_bytes_sent "$http_referer" '
             '"$http_user_agent" "$http_x_forwarded_for"';
    # --------Salesea Config End--------"""

        content = self.nginxConfigs.get(self.httpConfigPath)
        if re.search(r"(\s*log_format\s+salesea\s+)", content) is None:
            logger.info(f"更新[{self.httpConfigPath}]文件")
            # 在http块前不能有注释符号# 前面可能是\n
            content = re.sub(
                r"(\n[\s\t]*http\s+\{)",
                r"\1\n" + salesea_log_format,
                content
            )
            with open(self.httpConfigPath, "w") as fp:
                fp.write(content.strip('\n') + '\n')

            self.reload()
            self.init()

    def include_saleseas(self, server_name, apikey):
        logger.debug("检查[server_name.salesea.conf]状态")
        flag = 0
        for server in self.servers:
            if server.eq_name(server_name) and server.eq_listen("443"):
                flag += server.include_salesea(apikey)

        if flag > 0:
            self.reload()
            self.init()

    def load_nginx_config(self):
        # 判断平台
        if platform.system() == 'Windows':
            self.get_nginx_path_win()
            cmd = f'cd /d "{Path(self.nginx_path).parent}" && nginx -T'
            with os.popen(cmd) as fp:
                bf = fp._stream.buffer.read()
                self.nginx_conf = bf.decode("utf-8", errors="ignore")
        else:
            self.get_nginx_path_linux()
            self.nginx_conf = os.popen(f"{self.nginx_path} -T").read()

    # 拆分nginx配置文件
    def parse_file(self):
        current_path = None
        for line in self.nginx_conf.splitlines():
            config_file = re.findall('^# configuration\s+file\s+(.*):', line)
            if len(config_file) > 0:
                current_path = config_file[0]
                self.nginxConfigs[current_path] = ""
            else:
                if current_path is not None:
                    self.nginxConfigs[current_path] += line + "\n"

    @property
    def snapshot_dir(self):
        if platform.system() == 'Windows':
            path = Path(os.path.expandvars(r"%LOCALAPPDATA%")) / "salesea" / "nginx" / "snapshot"
        else:
            path = Path("/etc/salesea/nginx/snapshot")

        path.mkdir(parents=True, exist_ok=True)

        return path

    # 存储快照
    def save_snapshot(self):
        content = json.dumps(self.nginxConfigs, indent=4, ensure_ascii=False)
        snapshot_name = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_md5 = str(hashlib.md5(content.encode("utf-8")).hexdigest())
        filename = hash_md5 + '-' + snapshot_name
        snapshot_dir = self.snapshot_dir
        snapshot_save_path = snapshot_dir / f"{filename}.json"
        # 通过hash_md5判断是否已经存在
        search = list(snapshot_dir.glob(f"{hash_md5}-*.json"))
        if search:
            logger.debug(f"快照[{search[0].name}]已经存在")
            return search[0]

        with open(snapshot_save_path, "w", encoding="utf-8") as fp:
            logger.info(f"保存快照[{snapshot_save_path.name}]")
            fp.write(
                json.dumps({
                    "name": snapshot_save_path.name,
                    "type": "nginx",
                    "content": content,
                }, indent=4, ensure_ascii=False)
            )

        return snapshot_save_path

    # 获取快照列表
    def get_snapshot_list(self):
        return [
            {
                "name": f.name.replace(".json", ""),
                "mtime": f.stat().st_mtime,
                "size": f.stat().st_size
            }
            for f in self.snapshot_dir.glob("*-*.json")
        ]

    # 恢复快照
    def restore_snapshot(self, filename):
        snapshot_path = self.snapshot_dir / f'{filename}.json'
        if not snapshot_path.exists():
            logger.error(f"快照[{filename}]不存在")
            return False

        logger.info(f"恢复快照[{filename}]")
        with open(snapshot_path, "r", encoding="utf-8") as fp:
            content = fp.read()
            obj = json.loads(content)
            if obj.get("type") != "nginx" or obj.get("content") is None or obj.get("name") is None:
                logger.error(f"快照[{filename}]已损坏")
                return False
            nginxConfigs = json.loads(obj.get("content"))
            for path, content in nginxConfigs.items():
                with open(path, "w", encoding="utf-8") as fp:
                    fp.write(content)
        logger.info(f"恢复快照[{filename}]成功")
        self.reload()
        return True

    # 删除快照
    def delete_snapshot(self, filename):
        snapshot_path = self.snapshot_dir / f'{filename}.json'
        if not snapshot_path.exists():
            logger.error(f"快照[{filename}]不存在")
            return False

        logger.info(f"文件[{snapshot_path}]已删除")
        snapshot_path.unlink()
        return True

    # 预览快照
    def get_snapshot(self, filename):
        snapshot_path = self.snapshot_dir / f'{filename}.json'
        if not snapshot_path.exists():
            logger.error(f"快照[{filename}]不存在")
            return False

        with open(snapshot_path, "r", encoding="utf-8") as fp:
            content = fp.read()
            obj = json.loads(content)
            if obj.get("type") != "nginx" or obj.get("content") is None or obj.get("name") is None:
                logger.error(f"快照[{filename}]已损坏")
                return False
            nginxConfigs = json.loads(obj.get("content"))
            return nginxConfigs

    # nginx reload  重载nginx配置
    def reload(self):
        if platform.system() == 'Windows':
            cmd = f'cd /d "{Path(self.nginx_path).parent}" && nginx -s reload'
            os.popen(cmd).read()
        else:
            os.popen(f"{self.nginx_path} -s reload").read()

    #############################################################################
    #####Parse Nginx Config######################################################
    def get_nginx_path_win(self):
        os.popen(f"chcp 65001")
        if self.nginx_path is not None and self.nginx_path.exists():
            return self.nginx_path

        nginx_paths = os.popen(f"where nginx").readlines()

        if not nginx_paths:
            raise NginxException('请将[nginx.exe]配置到环境变量中')

        for path in nginx_paths:
            path = Path(path.strip())
            if path.exists():
                self.nginx_path = path
                return path

    def get_nginx_path_linux(self):
        if self.nginx_path is not None and self.nginx_path.exists():
            return self.nginx_path

        nginx_paths = os.popen(f"which nginx").readlines()

        if not nginx_paths:
            raise NginxException('请将[nginx]配置到环境变量中')

        for path in nginx_paths:
            path = Path(path.strip())
            if path.exists():
                self.nginx_path = path
                return path

    def parse_block(self, block_name, block_content=None):
        flag = False
        flag_name = False
        block = ''
        file = ''
        result = []
        num_of_quote = 0

        content = (block_content or self.nginx_conf)

        # 去除注释 除了# configuration file
        delete_comment = lambda x: x.group(0) if x.group(0).startswith('# configuration file ') else ''
        content = re.sub(r'#[^\n]*', delete_comment, content)

        for line in content.splitlines():
            x = line.replace(' ', '').replace('\t', '')

            config_file = re.findall('^# configuration\s+file\s+(.*):', line)
            if len(config_file) > 0:
                file = config_file[0]

            if x == block_name:
                flag_name = True

            if x.startswith(block_name + '{') or (flag_name and x.startswith('{')):
                num_of_quote += 1
                flag = True
                block += line
                continue

            # 发现{，计数加1。发现}，计数减1，直到计数为0
            if flag and '{' in line:
                num_of_quote += 1

            # 将proxy_pass的别名换成ip
            # if flag and 'proxy_pass' in line:
            #     r = re.findall('proxy_pass\s+https?://([^;/]*)[^;]*;', line)
            #     if len(r) > 0:
            #         for pool in self.backend:
            #             if r[0] == pool['poolname']:
            #                 line = line.replace(r[0], pool['ip'])

            if flag and num_of_quote != 0:
                block += line

            if flag and '}' in line:
                num_of_quote -= 1

            if flag and num_of_quote == 0:
                result.append({
                    'block': block,
                    'file': file
                })
                flag = False
                flag_name = False
                block = ''
                num_of_quote = 0

        return result

    def parse_server_block(self):
        self.serverBlock = self.parse_block('server')

        if len(self.serverBlock) == 0:
            raise NginxException('没有解析到[server]配置文件')

        for block in self.serverBlock:
            serverBlock = block['block']
            serverConfigPath = block['file']

            # listen有可能有多个
            listens = tuple([_.strip() for _ in re.findall('listen\s*((?:\d|\s)*)[^;]*;', serverBlock)])
            r = re.findall('server_name\s+([^;]*);', serverBlock)  # server_name只有一个

            # 可能存在没有server_name的情况
            if not len(r) > 0:
                continue

            server_names = tuple(r[0].split())

            # 判断servername是否有ip，有ip就不存。比如servername 127.0.0.1这样的配置
            for server_name in server_names:
                if len(re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', server_name)) > 0:
                    continue

            includes = [_.strip() for _ in re.findall('include\s+([^;]*);', serverBlock)]
            # location可能不止一个
            locations = re.findall('location\s*[\^~\*=]{0,3}\s*([^{ ]*)\s*\{[^}]*proxy_pass\s+https?://([^;/]*)[^;]*;',
                                   serverBlock)

            backend_list = list()
            backend_ip = ''

            # 可能存在多个location
            if len(locations) > 0:
                for location in locations:
                    backend_path = location[0]
                    poolname = location[1]
                    # 如果不是ip的pool name，就取出后端对应的ip
                    if len(re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', poolname)) == 0:
                        for backend in self.backend:
                            if poolname == backend['poolname']:
                                backend_ip = backend['ip']
                                break
                    else:
                        backend_ip = poolname

                    backend_list.append({"backend_path": backend_path, "backend_ip": backend_ip})

            server = Server(
                self,
                **{
                    'names': server_names,
                    'listens': listens,
                    'locations': locations,
                    'includes': includes,
                    'backend': backend_list,
                    'serverConfigPath': serverConfigPath,
                }
            )

            self.servers.append(server)

    def parse_http_block(self):
        self.httpBlock = self.parse_block('http')
        httpConfigPath = None

        if len(self.httpBlock) == 0:
            raise NginxException('没有解析到[http]配置文件')

        for block in self.httpBlock:
            httpBlock = block['block']
            httpConfigPath = self.httpConfigPath or block['file']

            # 获取log_format log_format后面不能是\n
            for log_format in re.findall('\s*log_format\s+([^;]*);', httpBlock):
                log_format = log_format.strip()
                name, log_format = log_format.split(' ', 1)
                self.logFormats[name] = log_format

            # 获取include
            self.includes += [_.strip() for _ in re.findall('include\s+([^;]*);', httpBlock)]

            # 获取upstream
            self.upstreams = re.findall('upstream\s+([^{ ]+)\s*{([^}]*)}', httpBlock)

        self.httpConfigPath = httpConfigPath
