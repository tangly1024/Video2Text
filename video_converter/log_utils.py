import logging
import colorlog
'''
日志颜色配置
'''
log_colors_config = {
    'DEBUG': 'white',  # cyan white
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


def get_logger(logger_name):
    """得到日志对象"""
    logging.basicConfig(filename='log.log',
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    log = logging.getLogger(logger_name)
    # 控制台输出
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
        datefmt='%Y-%m-%d  %H:%M:%S',
        log_colors=log_colors_config
    )
    console.setFormatter(console_formatter)
    log.addHandler(console)
    return log

