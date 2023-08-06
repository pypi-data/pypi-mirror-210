from .utils import out_print


# 出现 未解析到配置 错误时，打印解决方案
def print_solution():
    out_print('未解析到指定的Nginx服务器，可能原因：')
    out_print('    1. 您填写的[server_name]参数未能匹配到对应的Nginx服务器;')
    out_print('    2. Nginx服务器配置中[server_name]参数不能为空;')
    # out_print('    3. Nginx服务器未配置以下参数:')
    # out_print(
    #     '''
    #     ...
    #     html {
    #         ...
    #         log_format salesea '$remote_addr - $remote_user [$time_local] "$request" '
    #                          '$status $body_bytes_sent "$http_referer" '
    #                          '"$http_user_agent" "$http_x_forwarded_for"';
    #         ...
    #         server {
    #             ...
    #             access_log /var/log/nginx/access.log salesea;
    #             ...
    #         }
    #     }
    #     ...'''
    # )
