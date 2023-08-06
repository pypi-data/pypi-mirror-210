import types
import yaml
from pathlib import Path
from _pytest.python import Module
import pytest
from requests.adapters import HTTPAdapter
from . import http_session
from . import runner
from .log import set_log_format, log
from .report_notify import ding_ding_notify, fei_shu_notify
from .create_funtion import import_from_file
import os
import platform
import time

g = {}   # 全局 g 对象，获取项目配置


@pytest.fixture(scope="session")
def requests_session(request):
    """全局session 全部用例仅执行一次"""
    s = http_session.HttpSession()
    # max_retries=2 重试2次
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    proxies_ip = request.config.getoption("--proxies-ip") or request.config.getini("proxies_ip")
    if proxies_ip:
        # 添加全局代理
        s.proxies = {
            "http": f"http://{proxies_ip}",
            "https": f"https://{proxies_ip}"
        }
    # 添加全局base_url
    s.base_url = request.config.option.base_url
    yield s
    s.close()


@pytest.fixture()
def requests_function(request):
    """用例级别 session， 每个用例都会执行一次"""
    s = http_session.HttpSession()
    # max_retries=2 重试2次
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    proxies_ip = request.config.getoption("--proxies-ip") or request.config.getini("proxies_ip")
    if proxies_ip:
        # 添加全局代理
        s.proxies = {
            "http": f"http://{proxies_ip}",
            "https": f"https://{proxies_ip}"
        }
    # 添加全局base_url
    s.base_url = request.config.option.base_url
    yield s
    s.close()


@pytest.fixture(scope="module")
def requests_module(request):
    """模块级别 session， 每个模块仅执行一次"""
    s = http_session.HttpSession()
    # max_retries=2 重试2次
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    proxies_ip = request.config.getoption("--proxies-ip") or request.config.getini("proxies_ip")
    if proxies_ip:
        # 添加全局代理
        s.proxies = {
            "http": f"http://{proxies_ip}",
            "https": f"https://{proxies_ip}"
        }
    # 添加全局base_url
    s.base_url = request.config.option.base_url
    yield s
    s.close()


def pytest_collect_file(file_path: Path, parent):  # noqa
    """
        收集测试用例：
        1.测试文件以.yml 或 .yaml 后缀的文件
        2.并且以 test 开头或者 test 结尾
    """
    if file_path.suffix in [".yml", ".yaml"] and (file_path.name.startswith("test") or file_path.name.endswith("test")):
        py_module = Module.from_parent(parent, path=file_path)
        # 动态创建 module
        module = types.ModuleType(file_path.stem)
        # 解析 yaml 内容
        raw_dict = yaml.safe_load(file_path.open(encoding='utf-8'))
        if not raw_dict:
            return
        # 用例名称test_开头
        run = runner.RunYaml(raw_dict, module, g)
        run.run()  # 执行用例
        # 重写属性
        py_module._getobj = lambda: module  # noqa
        return py_module


def pytest_generate_tests(metafunc):  # noqa
    """测试用例参数化功能实现
    :param metafunc:共有五个属性值
         metafunc.fixturenames:参数化收集时的参数名称
         metafunc.module:使用参数名称进行参数化的测试用例所在的模块d对象
         metafunc.config:测试用例会话
         metafunc.function:测试用例对象,即函数或方法对象
         metafunc.cls: 测试用例所属的类的类对象
    :return: none
    """
    if hasattr(metafunc.module, f'{metafunc.function.__qualname__}_params_data'):
        params_data = getattr(metafunc.module, f'{metafunc.function.__qualname__}_params_data')
        params_len = 0    # 参数化 参数的个数
        if isinstance(params_data, list):
            if isinstance(params_data[0], list):
                params_len = len(params_data[0])
            elif isinstance(params_data[0], dict):
                params_len = len(params_data[0].keys())
            else:
                params_len = 1
        params_args = metafunc.fixturenames[-params_len:]
        if len(params_args) == 1:
            if not isinstance(params_data[0], list):
                params_data = [[p] for p in params_data]
        metafunc.parametrize(
            params_args,
            params_data,
            scope="function"
        )


def pytest_addoption(parser):   # noqa
    # run env
    parser.addini('env', default=None, help='run environment by test or uat ...')
    parser.addoption(
        "--env", action="store", default=None, help="run environment by test or uat ..."
    )
    # base url
    if 'base_url' not in parser._ininames:
        parser.addini("base_url", help="base url for the api test.")
        parser.addoption(
            "--base-url",
            metavar="url",
            default=os.getenv("PYTEST_BASE_URL", None),
            help="base url for the api test.",
        )
    # proxies_ip
    parser.addini("proxies_ip", default=None, help="proxies_ip for the  test.")
    parser.addoption(
        "--proxies-ip",
        action="store", default=None,
        help="proxies_ip for the  test.",
    )

def pytest_configure(config):  # noqa
    # 配置日志文件和格式
    set_log_format(config)
    config.addinivalue_line(
        "filterwarnings", "ignore::DeprecationWarning"
    )
    config.addinivalue_line(
        "filterwarnings", "ignore::urllib3.exceptions.InsecureRequestWarning"
    )
    # 加载 项目 config 文件配置
    config_path = Path(config.rootdir).joinpath('config.py')
    if config_path.exists():
        # 如果有配置文件，加载当前运行环境的配置
        run_env_name = config.getoption('--env') or config.getini('env')
        if run_env_name:
            config_module = import_from_file(config_path)
            # config_module = __import__("config", globals(), locals(), [])
            if hasattr(config_module, 'env'):
                g["env"] = config_module.env.get(run_env_name)  # noqa
                g["env_name"] = run_env_name
    if g.get('env'):
        # 获取配置环境的 BASE_URL
        _base_url = g["env"].BASE_URL if hasattr(g.get('env'), 'BASE_URL') else None
    else:
        _base_url = None
    # base_url
    base_url = config.getoption("--base-url") or config.getini("base_url") or _base_url
    g["base_url"] = base_url
    if base_url is not None:
        config.option.base_url = base_url
        if hasattr(config, "_metadata"):
            config._metadata["base_url"] = base_url  # noqa

    # 获取 allure 报告的路径
    allure_dir = config.getoption('--alluredir')  # noqa
    if allure_dir:
        allure_report_path = Path(os.getcwd()).joinpath(allure_dir)
        if not allure_report_path.exists():
            allure_report_path.mkdir()
        allure_report_env = allure_report_path.joinpath('environment.properties')
        if not allure_report_env.exists():
            allure_report_env.touch()  # 创建
            # 写入环境信息
            root_dir = str(config.rootdir).replace("\\", "\\\\")
            allure_report_env.write_text(f'system={platform.system()}\n'
                                         f'systemVersion={platform.version()}\n'
                                         f'pythonVersion={platform.python_version()}\n'
                                         f'pytestVersion={pytest.__version__}\n'
                                         f'rootDir={root_dir}\n')


def pytest_terminal_summary(terminalreporter, exitstatus, config): # noqa
    """收集测试结果"""
    total = terminalreporter._numcollected  # noqa
    status = {
        0: "pass",
        1: "failed",
        2: "pytest 执行过程被中断",
        3: "pytest 内部错误",
        4: "pytest 用法错误",
        5: "没有收集到测试用例"
    }
    if exitstatus in [0, 1]:
        passed = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
        failed = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
        error = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
        skipped = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
        successful = len(terminalreporter.stats.get('passed', [])) / (terminalreporter._numcollected- skipped) * 100    # noqa
        duration = time.time() - terminalreporter._sessionstarttime  # noqa
        markdown_text = f"""## 执行报告: 
- 运行环境: {g.get('env_name')} 
- 运行base_url: {g.get('base_url')} 
- 持续时间: {duration: .2f} 秒 

## 本次运行结果:
- 总用例数: {total} 
- 通过用例：{passed} 
- 跳过用例：{skipped} 
- 失败用例： {failed} 
- 异常用例： {error} 
- 通过率： {successful: .2f} % 
"""
        if g.get('env'):
            if hasattr(g["env"], 'DING_TALK'):
                ding_text = markdown_text.replace('## 本次运行结果:', f'## 本次运行结果: {status.get(exitstatus)} ')
                ding_talk = g["env"].DING_TALK
                if ding_talk.get('text'):
                    ding_talk['text'] = ding_text + ding_talk['text']
                else:
                    ding_talk['text'] = ding_text
                ding_ding_notify(**ding_talk)
            if hasattr(g["env"], 'FEI_SHU'):
                color = 'green' if exitstatus == 0 else 'red'
                fei_shu_text = markdown_text.replace('## 执行报告:', '** 执行报告: ** ')
                fei_shu_text = fei_shu_text.replace(
                    '## 本次运行结果:',
                    f'** 本次运行结果: <font color="{color}">{status.get(exitstatus)}</font> **')
                fei_shu = g["env"].FEI_SHU
                if fei_shu.get('text'):
                    fei_shu['text'] = fei_shu_text+fei_shu['text']
                else:
                    fei_shu['text'] = fei_shu_text
                # 根据运行结果设置标题背景色
                fei_shu['color'] = color
                fei_shu_res = fei_shu_notify(**fei_shu)
                log.info(f"飞书通知结果: {fei_shu_res}")
    else:
        log.error(f"用例执行异常，失败原因: {status.get(exitstatus)}")
