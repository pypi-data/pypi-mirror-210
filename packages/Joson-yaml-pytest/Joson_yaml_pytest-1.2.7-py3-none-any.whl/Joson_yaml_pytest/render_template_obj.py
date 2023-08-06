from jinja2 import Template
import re
from .log import log
import jinja2


def add(value, num=0):
    """jinja2 过滤器 add函数"""
    return int(value)+num


env_filter = jinja2.Environment(
    variable_start_string='${', variable_end_string='}'
)
env_filter.filters["add"] = add


class NewDict(dict):
    """dict按点方式取值
        a = {
                "x": 123,
                "y": "hello"
            }
        print(a.x)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        value = self[name]
        if isinstance(value, dict):
            value = NewDict(value)
        return value


def rend_template_str(template_str, *args, **kwargs):
    """
       渲染模板字符串, 改写了默认的引用变量语法{{var}}, 换成${var}
            模板中引用变量语法 ${var},
            调用函数 ${fun()}
        :return: 渲染之后的值
    """
    # -------------解决函数内部参数引用变量-------
    def re_replace_template_str(match) -> str:
        """匹配的值--渲染模板加载内部引用变量"""
        res_result = match.group()
        res_result_ = str(res_result).lstrip('${').rstrip('}')
        if '${' in res_result_ and '}' in res_result_ and res_result_.find('${') < res_result_.find('}'):
            # 渲染结果
            # instance_temp = Template(res_result_, variable_start_string='${', variable_end_string='}')
            # temp_render_res = instance_temp.render(*args, **kwargs)
            instance_temp = env_filter.from_string(res_result_)
            temp_render_res = instance_temp.render(*args, **kwargs)
            return '${' + temp_render_res + '}'
        else:
            return res_result

    template_str = re.sub('\$\{(.+)\}', re_replace_template_str, template_str) # noqa
    # ----------------end----------

    # instance_template = Template(template_str, variable_start_string='${', variable_end_string='}')
    # template_render_res = instance_template.render(*args, **kwargs)
    instance_template = env_filter.from_string(template_str)
    template_render_res = instance_template.render(*args, **kwargs)
    if template_str.startswith("${") and template_str.endswith("}") and template_str.count('${') == 1:
        try:
            template_raw_str = template_str.rstrip('}').lstrip('${')
            log.info(f"取值表达式 {template_raw_str}")
            # 先判断有没有list 取值如： user.0 换成[0]
            template_find_res = re.findall('\.[0-9]+', template_raw_str)
            if template_find_res:
                for template_i in template_find_res:
                    template_raw_str = template_raw_str.replace(template_i, f"[{str(template_i).lstrip('.')}]")
            # 根据表达式取值
            locals().update(**NewDict(kwargs))  # 更新成本地变量
            for kwargs_locals_key, kwargs_locals_value in kwargs.items():
                if isinstance(kwargs_locals_value, dict):
                    locals()[kwargs_locals_key] = NewDict(kwargs_locals_value)
                else:
                    locals()[kwargs_locals_key] = kwargs_locals_value
            template_render_result = eval(template_raw_str)
            log.info(f"取值结果：{template_render_result}, {type(template_render_result)}")
            return template_render_result
        except Exception:      # noqa
            log.info(f"取值结果: {template_render_res}, {type(template_render_res)}")
            return template_render_res
    else:
        return template_render_res


def rend_template_obj(t_obj: dict, *args, **kwargs):
    """
       传 dict 对象，通过模板字符串递归查找模板字符串，转行成新的数据
    """
    if isinstance(t_obj, dict):
        for key, value in t_obj.items():
            if isinstance(value, str):
                t_obj[key] = rend_template_str(value, *args, **kwargs)
            elif isinstance(value, dict):
                rend_template_obj(value, *args, **kwargs)
            elif isinstance(value, list):
                t_obj[key] = rend_template_array(value, *args, **kwargs)
            else:
                pass
    return t_obj


def rend_template_array(t_array, *args, **kwargs):
    """
       传 list 对象，通过模板字符串递归查找模板字符串
    """
    if isinstance(t_array, list):
        new_array = []
        for item in t_array:
            if isinstance(item, str):
                new_array.append(rend_template_str(item, *args, **kwargs))
            elif isinstance(item, list):
                new_array.append(rend_template_array(item, *args, **kwargs))
            elif isinstance(item, dict):
                new_array.append(rend_template_obj(item, *args, **kwargs))
            else:
                new_array.append(item)
        return new_array
    else:
        return t_array


def rend_template_any(any_obj, *args, **kwargs):
    """渲染模板对象:str, dict, list"""
    if isinstance(any_obj, str):
        return rend_template_str(any_obj, *args, **kwargs)
    elif isinstance(any_obj, dict):
        return rend_template_obj(any_obj, *args, **kwargs)
    elif isinstance(any_obj, list):
        return rend_template_array(any_obj, *args, **kwargs)
    else:
        return any_obj
