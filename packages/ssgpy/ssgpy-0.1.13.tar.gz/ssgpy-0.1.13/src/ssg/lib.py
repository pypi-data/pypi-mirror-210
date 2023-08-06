
import os
import re
import yaml
import uuid
import json
import jsmin
import arrow
import cssmin 
import slugify
import requests
import datetime
import mimetypes
from scss import Compiler
from typing import Generator
from functools import reduce

"""
For Single File Component
"""

RE_SSG_BODY_BLOCK = re.compile(r'<ssg\:body\s*/>', re.IGNORECASE)
RE_SFC_TEMPLATE = re.compile(r'<ssg\:template\s*>\n?([\S\s]*?)<\/ssg\:template\s*>', re.IGNORECASE)
RE_SFC_SCRIPT = re.compile(r'<ssg\:script\s*(.*)\s*>\n?([\S\s]*?)<\/ssg\:script\s*>', re.IGNORECASE)
RE_SFC_STYLE = re.compile(r'<ssg\:style\s*(.*)\s*>\n?([\S\s]*?)<\/ssg\:style\s*>', re.IGNORECASE)
RE_BLOCK_BODY = re.compile(r'{%\s*block\s+__SSG_BODY_BLOCK__\s*%}')
RE_EXTENDS = re.compile(r'{%\s*extends\s+(.*?)\s*%}')
RE_BLOCK_BODY_PARSED = re.compile(r'{%\s*block\s+__SSG_BODY_BLOCK__\s*%}(.*?){%\s*endblock\s*%}')



def replace_layout_body_block(template:str) -> str:
  if RE_SSG_BODY_BLOCK.search(template):
    template = re.sub(RE_SSG_BODY_BLOCK, "{% block __SSG_BODY_BLOCK__ %}{% endblock %}", template, 1)
  return template

def destruct_sfc(content):
    """
    To destruct a single file component into template, script, style
    :param: string content 
    :returns: tuple - (Bool, {template, script, style, script_props, style_props})
    """
    s_template = re.search(RE_SFC_TEMPLATE, content)
    s_script = re.search(RE_SFC_SCRIPT, content)
    s_style = re.search(RE_SFC_STYLE, content)

    if s_template:
        return (True, {
            "template": s_template.group(1) if s_template else content,
            "script": s_script.group(2).replace("\"","'") if s_script else None,
            "script_props": s_script.group(1) if s_script else None,
            "style": s_style.group(2) if s_style else None,
            "style_props": s_style.group(1) if s_style else None,
        })
    else:
        return (False, {"template": content, "script": None, "style": None, "script_props": "", "style_props": ""})


"""
To get the macros in a content
Must be in this format
{% macro macro_name(...) %}
"""
RE_MACROS = re.compile(r'{%\s*macro\s+([\S\s]*?)\s*\(', re.IGNORECASE)
"""
To get macro document and match them to the macro 
Must be in this format:
{# macro_name: description #}
"""
RE_MACROS_DOC = re.compile(r'{#\s*([\S\s]*?)#}', re.IGNORECASE)

def get_macros_definition(tpl):
    """
    Get file/content containing macros, and return a dict of key and description
    To be used in documentation of macros
    :param text:
    :return dict:
    """
    macros = {m: '' for m in re.findall(RE_MACROS, tpl) if not m.startswith("_")}
    if macros:
      for d in re.findall(RE_MACROS_DOC, tpl):
        sd = d.split(':', 1)
        if len(sd) == 2:
            name, description = sd
            if name.strip() in macros:
                macros[name.strip()] = description.strip()
    return macros

class dictdot(dict):
    """
    A dict extension that allows dot notation to access the data.
    ie: dict.get('key.key2.0.keyx'). 
    Still can use dict[key1][k2]
    To create: dictdot(my)
    """
    def get(self, key, default=None):
        """ access data via dot notation """
        try:
            return self[key] if "." not in key else dict_get(obj=self, path=key, default=default)
        except (TypeError, KeyError, IndexError) as e:
            return default

def dict_get(obj, path, default=None):
    """
    Get a value via dot notaion

    Args:
        @obj: Dict
        @attr: String - dot notation path
            object-path: key.value.path
            object-with-array-index: key.0.path.value
    Returns:
        mixed
    """
    def _getattr(obj, path):
        try:
            if isinstance(obj, list) and path.isdigit():
                return obj[int(path)]
            return obj.get(path, default)
        except:
            return default
    return reduce(_getattr, [obj] + path.split('.'))


def load_conf(yml_file, conf={}) -> dict:
    """
    To load the config
    :param yml_file: the config file path
    :param conf: dict, to override global config
    :return: dict
    """
    with open(yml_file) as f:
        data = yaml.safe_load(f)
        if conf:
            data.update(conf)
        return dictdot(data)

def load_yaml_file(file):
    with open(file) as f:
        if d := yaml.safe_load(f):
            if isinstance(d, dict):
                return dictdot(d)
            return d
    return None

def load_json_file(file):
    with open(file) as f:
        if d := json.loads(f.read()):
            if isinstance(d, dict):
                return dictdot(d)
            return d
    return None

def make_http_requests(url, method="GET", headers=None, data=None, params=None, resolve_path=None, **kw) -> dict:
    """
    Make a request 

    Params:
        url:str 
        method:GET|POST
        headers:dict|None
        data:dict|None 
        params:dict|None
        resolve_path:str - the data path to return
    """
    resp = None
    if method.upper() == "POST":
        resp = requests.post(url=url, json=data, headers=headers)
    elif method.upper() == "GET":
        resp = requests.get(url, headers=headers, params=params, data=data)
    if resp:
        
        data = resp.json()
        if isinstance(data, dict):
            d = dictdot(data)
            if resolve_path:
                return d.get(resolve_path)
            return d
        return data
    return None 

def extract_sitename(s) -> str:
    """
    Return the site name from a full url 
    -> https://hello.com -> hello.com 
    """
    return re.sub(r"https?://(www\.)?", '', s).replace("www.", "")

def chunk_list(items, size) -> list:
    """
    Return a list of chunks
    :param items: List
    :param size: int The number of items per chunk
    :return: List

    """
    size = max(1, size)
    return [items[i:i + size] for i in range(0, len(items), size)]

def merge_dicts(dict1, dict2) -> dict:
    """ Recursively merges dict2 into dict1 """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1

def scss_to_css(content) -> str:
    """
    Convert SCSS to CSS
    """
    return Compiler().compile_string(content)


def bundle_assets(ftype: str, files: list, dest: str):
    """
    To  bundle assets files together

    Params:
        ftype: str - the file type [css|js]
        files:list - list of files to bundle
        dest: the destination to save file
    """
    contents = ""
    for file in files:
        with open(file) as f:
            contents += f.read()
    if ftype == "css":
        contents = cssmin.cssmin(contents)
    elif ftype == "js":
        contents = jsmin.jsmin(contents)
    if contents:
        with open(dest, "w") as f:
            f.write(contents)

def merge_files_contents(files: list) -> str:
    """
    Merge contents of files.
    """
    contents = ""
    for file in files:
        with open(file) as f:
            contents += f.read()
    return contents

def minify_static_contents(ftype:str, contents:str):
    """
    To minify contents for static files. 

    Params:
        ftype:str - type, css|js
        contents:str - the conent to minify
    """
    if ftype == "css":
        return cssmin.cssmin(contents)
    elif ftype == "js":
        return jsmin.jsmin(contents)
    return contents

def write_file(contents:str, dest:str):
    """
    To minify contents for static files. 

    Params:
        contents:str - the conent to minify
        dest:path - the output file 
    """
    if contents:
        with open(dest, "w") as f:
            f.write(contents)

def is_external_url(url:str) -> bool:
    """
    Returns if url is https url
    """
    return url.startswith(('http://', 'https://'))

def context_root(context:str) -> str:
  """
  Returns a context root from the path:
    - /a/b/c -> ../../..
  """
  contexts = context.strip("/").split("/")
  if len(contexts) == 1:
    return "./"
  return "/".join([".." for _ in contexts])

def gen_uuid() -> str:
    """
    Return a UUID4 key. 32 chars
    """
    return ("%s" % uuid.uuid4()).replace("-", "")


class json_ext:
    """ 
    JSON Extension class to loads and dumps json
    """

    @classmethod
    def dumps(cls, data: dict) -> str:
        """ Serialize dict to a JSON formatted """
        return json.dumps(data, default=cls._serialize)

    @classmethod
    def loads(cls, data: str) -> dict:
        """ Deserialize a JSON string to dict """
        if not data:
            return None
        if isinstance(data, list):
            return [json.loads(v) if v else None for v in data]
        return json.loads(data, object_hook=cls._deserialize)

    @classmethod
    def _serialize(cls, o):
        return cls._timestamp_to_str(o)

    @classmethod
    def _deserialize(cls, json_dict):
        for k, v in json_dict.items():
            if isinstance(v, str) and cls._timestamp_valid(v):
                json_dict[k] = arrow.get(v)
        return json_dict

    @staticmethod
    def _timestamp_valid(dt_str) -> bool:
        try:
            datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return False
        return True

    @staticmethod
    def _timestamp_to_str(dt) -> str:
        if isinstance(dt, arrow.Arrow):
            return dt.for_json()
        elif isinstance(dt, (datetime.date, datetime.datetime)):
            return dt.isoformat()
        return dt


json_dumps = lambda data : json_ext.dumps(data)
json_loads = lambda data : json_ext.loads(data)


def slugify_with_slash(path):
  """
  A slugify to preserve the slashes
  """
  if "/" in path:
    return "/".join([slugify.slugify(l) for l in path.split("/")])
  return slugify.slugify(path)



def gen_pagination_page_numbers(total_pages=0, page=1, left_edge=2, left_current=3, right_current=4, right_edge=2) -> Generator:
    """
    To generate a paginator elements

    -> gen_pagination_page_numbers(20)
        -> [1, 2, 3, 4, None, 19, 20]

    Returns: Generator 
    """
    page = int(page)
    last = 0
    for num in range(1, total_pages + 1):
        if (
            num <= left_edge
            or (
                (num >= page - left_current) and
                (num < page + right_current)
            )
            or (
                (num > total_pages - right_edge)
            )
        ):
          if last + 1 != num:
              yield None
          yield num
          last = num

