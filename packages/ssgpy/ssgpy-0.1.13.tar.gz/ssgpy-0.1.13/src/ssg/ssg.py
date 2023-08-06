"""
~ SSG.py ~
"""

import os
import re
import sys
import copy
import json
import time
import uuid
import yaml
import jsmin
import arrow
import shutil
import cssmin
import jinja2
import logging
import datetime
import frontmatter
import pkg_resources
from slugify import slugify
from . import ext
from distutils.dir_util import copy_tree
from .__about__ import *
from . import lib
from scss import Compiler


# ------------------------------------------------------------------------------

NAME = "SSG.py"
PAGE_FORMAT = (".html", ".md")
DEFAULT_LAYOUT = "layouts/default.html"


# ==============================================================================
# -------------------------------- SSG.py -------------------------------------
# ==============================================================================

HTML_REDIRECT_TEMPLATE = """<meta http-equiv="Refresh" content="0; url='{url}'" />"""


__slots__ = [ "pages_data__", "resources__" ]

pages_data__ = {}
resources__ = {}


def print_info(message):
    print("- %s" % message)

cached = {}
    
def _clean_hashfile_key(src_file) -> str:
  """
  create a name for the hash key map by removing extension
  Returns str
  """
  if not src_file.endswith((".html", ".md")):
    src_file += ".html"
  short_name, _ = os.path.splitext(src_file)
  return short_name


class Generator(object):
    
    default_page_meta = {
        "title": "",            # The title of the page
        "markup": None,         # The markup to use. ie: md | html (default)
        "slug": None,           # The pretty url new name of the file. A file with the same name will be created
        "permalink": None,      # to create a full unique name. It can have slashes etc. ie: /some/page/deep/pages
        "url": "",              # This will be added when processed. Should never be modified
        "description": "",      # Page description
        # By default, all url will be pretty (search engine friendly) Set to False to keep the .html
        "pretty_url": True,
        "meta": {},
        "redirect": None,       # To allow an html redirect - the page to redirect to. 
        "layout": None,         # The layout for the page
        "template": None,       # The page template.
        "sfc": True,            # For single file component
        "__assets": {           # Contains all assets generated
            "js": [],           # List of all js url in the page
            "css": []           # List of all CSS url in the page
        }
    }
    root_dir = None 
    base_dir = None
    tpl_env = None
    _templates = {}
    #pages_data__ = {}

    def __init__(self, root_dir, options={}):
        """

        :param root_dir: The application root dir, where ssg.yml exists
        :param options: options to build
        """

        self.root_dir = self.base_dir = root_dir
        self.config_file = os.path.join(self.root_dir, "ssg.yml")
        self.config = lib.load_conf(self.config_file)
        self.config.setdefault("env", {})
        self.config.setdefault("serve", {})
        self.config.setdefault("build", {})
        self.config.setdefault("globals", {})
        self.config.setdefault("assets_bundles", {})

        # * base_dir
        # base_dir: relative to the ssg.yml, the dir containing the artifact
        if base_dir := self.config.get("base_dir"):
            self.base_dir = os.path.join(self.root_dir, base_dir)

        # * build_dir
        # build_dir: relative to the ssg.yml, the dir that contains the output
        if not (build_dir := self.config.get("build_dir")):
            build_dir = "_build"
        self.build_dir = os.path.join(self.root_dir, build_dir)

        self.public_dir = os.path.join(self.base_dir, "public")
        self.static_dir = os.path.join(self.base_dir, "static")
        self.pages_dir = os.path.join(self.base_dir, "pages")
        self.templates_dir = os.path.join(self.base_dir, "templates")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.build_static_dir = os.path.join(self.build_dir, "_static")
        self.build_static_gen_dir = os.path.join(self.build_static_dir, "_gen")

        self.layout = self.config.get("globals.layout", DEFAULT_LAYOUT)

        build_type = options.get("build", "build")

        self.build_config = lib.dictdot(self.config[build_type])
        site_env = self.build_config.get("env")
        if options and options.get("env") is not None:
            site_env = options.get("env")

        self.site_config = lib.dictdot(self.config.get("site", {}))
        if site_env:
            if site_env in self.config["env"]:
                self.site_config = lib.merge_dicts(self.site_config, self.config.get('env.%s' % site_env))
            else:
                raise ValueError("Environment Error: env %s@%s not found" % (site_env, build_type))

        self.site_env = site_env
        self.site_config.setdefault("base_url", "/")
        self.site_config.setdefault("static_url", "/_static")
        self.base_url = self.site_config.get("base_url")
        self.static_url = self.site_config.get("static_url")
        self._context_root = "./"
        # self._data = {}
        self.load_data_resources()

        self.print_info = False

        self._init_jinja({
            "get_page_meta": self._get_page,
            "get_url_for": self._get_page_url,
            "get_static_url_for": self._get_static_url,
            "get_static_bundle_url_for": self._get_page_static_bundle_url,
            "get_public_url_for": None,
            "get_data": self._get_resources,
            "get_site": self._get_site,
            "format_date": lambda dt, format="MM/DD/YYYY h:mm a": arrow.get(dt).format(format),
            "get_current_date": lambda: arrow.now(),
            "__site__": self.site_config,
            "__info__": self._load_info()
        })
 
    def _load_info(self):
        """ Global variables """
        now = datetime.datetime.now()
        return {
            "name": __title__,
            "version": __version__,
            "url": __uri__,
            "generator": "%s %s" % (__title__, __version__),
            "year": now.year,
            "timestamp": int(time.time())
        }

    def _init_jinja(self, global_context={}):


        loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(self.templates_dir)
        ])

        # Extension
        env_extensions = [
            'ssg.ext.MarkdownExtension',
            'ssg.ext.MarkdownTagExtension',
        ]
        if self.build_config.get("compress_html") is True:
            env_extensions.append('ssg.ext.HTMLCompress')

        self.tpl_env = jinja2.Environment(loader=loader, extensions=env_extensions)

        self.tpl_env.add_extension('jinja2.ext.do')
        self.tpl_env.globals.update(global_context)

    def _get_resources(self, path):
        """
        Get the data from /data dir

        Params:
            path:dotNotationStr
        Returns: mixed
        """
        return resources__.get(path)

    def _get_page_meta_data(self, page):
        """ A shortcut to retrieve the page meta data """
        hashed_name = _clean_hashfile_key(page)
        return pages_data__.get(hashed_name)

    def _get_file_data(self, page) -> dict:
        """
        Retrieve the file data that's in the front matter

        Returns: dict
        """
        meta = {}
        src_file = os.path.join(self.pages_dir, page)
        with open(src_file) as f:
            _, _ext = os.path.splitext(src_file)
            markup = _ext.replace(".", "")
            _meta, _content = frontmatter.parse(f.read())
            meta = self.default_page_meta.copy()
            meta["meta"].update(self.config.get("site.meta", {}))
            meta.update(_meta)
            dest_file, url = self._get_dest_file_and_url(page, meta)
            meta["url"] = url
            meta["filepath"] = dest_file
            meta["is_generator"] = "_generator" in meta
            meta["markup"] = meta.get("markup") or markup
            meta["content"] = _content
            return lib.dictdot(meta)

    def _get_page(self, page_dot_path:str):
        """
        To get page properties, ie: title, description, data, etc

        Example
            {{ get_page("about.title")}}
            {{ get_page("about.description") }}
            {{ get_page("about.data") }} : dict|list

        Params:
            page_dot_path:str - a page dot path notation, ie: $[page].$path -> [about].[title]
        
        Returns: mixed
        """
        s = page_dot_path.split(".", 1)
        if len(s) == 2:
            return self._get_page_meta_data(s[0]).get(s[1])
        else:
            return self._get_page_meta_data(s[0])
        
    def _get_page_url(self, page, full_url=False):
        """ Get the url of a  page """
        anchor = ""
        if "#" in page:
            page, anchor = page.split("#")
            anchor = "#" + anchor
        meta = self._get_page_meta_data(page)
        return self._make_url(meta.get("url"), full_url=full_url)

    def _make_url(self, url, full_url=False):
        """
        """
        if full_url:
            return self.base_url.rstrip("/") + "/" + url.lstrip("/")
        if len(self._context_root.split("..")) > 1:
            return self._context_root.rstrip("/") + url
        if "./" + url.strip("/") == "./":
            return "../"
        return url 

    def _get_page_static_bundle_url(self, page, bundle_name):
        _page = lib.dictdot(page)
        if url := _page.get("__assets.%s" % bundle_name):
            return self._get_static_url(url)
        return ""

    def _get_static_url(self, url):
        """Returns the static url """
        if url.startswith("//") or bool(re.match('https?://', url)):
            return url
        url = self.static_url.rstrip("/") + "/" + url.lstrip("/")
        if len(self._context_root.split("..")) > 1:
            self._context_root.rstrip("/") + url
        return url

    def _get_public_url(self, url):
        """Returns the static url """
        if url.startswith("//") or bool(re.match('https?://', url)):
            return url
        url = self.static_url.rstrip("/") + "/" + url.lstrip("/")
        if len(self._context_root.split("..")) > 1:
            self._context_root.rstrip("/") + url
        return url

    def _get_dest_file_and_url(self, filepath, page_meta={}):
        """ Return tuple of the file destination and url """

        slugname = None
        # permalink 
        if permalink := page_meta.get("permalink"):
            filepath = permalink
            if not filepath.endswith((".html", ".md")):
                filepath += ".html"

        elif slug := page_meta.get("slug"):
            slugname = slugify(slug)

        filename = filepath.split("/")[-1]
        slugname = slugname or filename
        filepath_base = filepath.replace(filename, "").rstrip("/")
        fname = slugname.replace(".html", "").replace(".md", "")
            
        if page_meta.get("pretty_url") is False:
            dest_file = os.path.join(filepath_base, "%s.html" % fname)
        else:
            dest_dir = filepath_base
            if filename not in ["index.html", "index.md"]:
                dest_dir = os.path.join(filepath_base, fname)
            dest_file = os.path.join(dest_dir, "index.html")

        url = "/" + dest_file.replace("index.html", "")
        return dest_file, url

    def load_data_resources(self):
        global resources__
        data = {}

        # load data from the data directory
        for root, _, files in os.walk(self.data_dir):
            for fname in files:
                if fname.endswith((".json", ".yml")):
                    name = fname.replace(".json", "").replace(".yml", "")
                    fname = os.path.join(root, fname)
                    if os.path.isfile(fname):
                        m = lib.load_yaml_file if fname.endswith(".yml") else lib.load_json_file
                        data[name] = m(fname)

        # load the data from config.datasources
        """
        format:
            name:str
            request:dict
                url:str
                method:str
                headers:dict|None
                data:dict|None
                params:dict|None
                data_path:str - the path to resolve the data
            cached:bool - To use a cached version when getting rebuilt. To improve speed
            saved:bool - to save as file. Takes precedence over cached, as the file will exist
            disabled:bool - to disabled the request
        """

        if datasources := self.config.get("datasources"):
            for d in datasources:
                if name := d.get("name"):
                    if not d.get("request"):
                        raise Exception("BUILD ERROR: remote resource '%s' missing request object" % name)
                    if d.get("disabled") is True:
                        continue
                    if d.get("cached") is True and data.get(name):
                        continue

                    if _data := lib.make_http_requests(**d.get("request")):
                        # save to data
                        if d.get("saved") is True:
                            save_file = "%s/%s.json" % (self.data_dir.rstrip("/"), name)
                            if not os.path.exists(save_file):
                                lib.write_file(dest=save_file, contents=lib.json_dumps(_data))
                        data[name] = _data

        resources__ = lib.dictdot(data)

    def _get_site(self, prop):
        return self.site_config.get(prop)

    def _build_page(self, filepath) -> list:
        
        """ To build from filepath, relative to pages_dir """
        filename = filepath.split("/")[-1]
        # If filename starts with _ (underscore) or . (dot) do not build
        if not filename.startswith(("_", ".")) and (filename.endswith(PAGE_FORMAT)):
            # The default context for the page
            _default_page = {
                "build_dir": self.build_dir,
                "filepath": None,
                "context": {"page": {}, "this": {}, "__page__": {}},
                "content": "",
                "markup": None,
                "template": None,
                "layout": None or self.layout
            }

            # only non generator will contain the data
            if mdata := self._get_page_meta_data(filename):
                #!== regular pages
                if not mdata.get("is_generator"):
                    return [{
                        "build_dir": self.build_dir,
                        "filepath": mdata.get("filepath"),
                        "context": {"page": mdata, "this": mdata, "__page__": mdata},
                        "content": mdata.get("content"),
                        "markup": mdata.get("markup"),
                        "template": mdata.get("template"),
                        "layout": mdata.get("layout") or self.layout
                    }]

                else:
                    """
                    #!== Generator 
                    Generators generates pages from data sources.
                    A data source can be from the data folder, or from a `data_requests` in ssg.yml

                    Properties:
                        - resources: somename_from_dataDir_or_remoteResources
                        - type: single|list

                    # single 
                    To display a single entry. 
                    The page reference will be $pagename:$page_id or a $permalink

                    # list
                    To create a list of item. 
                    Optionally, individual pages can exist for more details
                    href = $pagename:page_num or $permalink
                    

                    Example: 
                    Having the data `data/articles.json` -> [{title, slug, content, ...},...]
                    and the page `pages/article_generator.html`

                    ``` pages/article_generator.html
                    ---
                    _generator:
                        - resources: articles
                        - type: single
                        - slug: article/{slug}
                    ---
                        <h1>{{ this.title }}</h1>
                        <main>{{ this.content }}</main>
                    ```
                    """
                    lpages = []
                    # We want these back in meta in they exists in the data
                    special_meta = ["title", "permalink", "description"]                    
                    _generator = mdata.get("_generator")
                    _gen_type = _generator.get("type", "single") # The generator type: single|list
                    _resources_name = _generator.get("resources")
                    rdata = resources__.get(_resources_name)
                    # expecting data to be a list to iterate over
                    if not isinstance(rdata, list):
                        raise Exception("BUILD ERROR: Generator data type must be of List|Array for '%s'" % _resources_name)

                    # ::SINGLE
                    # generates single pages off of the data

                    if not _gen_type or _gen_type.upper() == "SINGLE":
                        
                        for data in rdata:
                            dmeta = copy.deepcopy(mdata)

                            for _ in special_meta:
                                if _ in data:
                                    dmeta[_] = data.get(_)

                            # If generator has the permalink, it will substitute if
                            # Slug in the generator must have token from the data
                            # to generate the slug
                            if "permalink" in _generator:
                                dmeta["permalink"] = lib.slugify_with_slash(_generator.get("permalink").format(**data))

                            # Slug is required
                            if "permalink" not in dmeta:
                                print("WARNING: Skipping page because it's missing `permalink`")
                                continue

                            permalink = dmeta.get("permalink")
                            dmeta["url"] = permalink
                            this = {
                                **dmeta,
                                "data": data,
                            }
                            lpages.append({
                                **copy.deepcopy(_default_page),
                                "filepath": permalink,
                                "context": {
                                    "page": this,
                                    "this": this,
                                    "__page__": this
                                },
                                "content": mdata.get("content"),
                                "markup": mdata.get("markup"),
                                "template": mdata.get("template"),
                                "layout": mdata.get("layout") or self.layout
                            })
   
                    # ::LIST
                    # To create a paginated listing page similar to a blog page. 
                    # Each page will contain a chunk list of the data
                    # This can be use to show a list.
                    # NOTE: While a list contain the list of the content, 
                    # it's can be necessary to create another Generator to show single/indivual page.
                    # This way you can link to them.
                    #
                    #
                    # create a paginated with [Prev] [Next]
                    # Each page will contain a chunk of the data
                    # will split the content into multi pages.
                    # Also a index/default page will be created for the first page
                    if _gen_type.upper() == "LIST":
                        raise NotImplementedError()

                        per_page = int(_generator.get(
                            "per_page", self.site_config.get("pagination.per_page", 10)))
                        left_edge = int(_generator.get(
                            "left_edge", self.site_config.get("pagination.left_edge", 2)))
                        left_current = int(_generator.get(
                            "left_edge", self.site_config.get("pagination.left_current", 3)))
                        right_current = int(_generator.get(
                            "right_current", self.site_config.get("pagination.right_current", 4)))
                        right_edge = int(_generator.get(
                            "right_edge", self.site_config.get("pagination.right_edge", 2)))
                        padding = _generator.get("padding")
                        slug = _generator.get("slug")
                        limit = _generator.get("limit")

                        if "limit" in _generator:
                            data = data[:int(limit)]
                        data_chunks = lib.chunk_list(data, per_page)
                        len_data = len(data)
                        total_pages = len(data_chunks)

                        for i, d in enumerate(data_chunks):
                            dmeta = copy.deepcopy(mdata)
                            page = copy.deepcopy(_default_page)

                            page_num = i + 1
                            _paginator = Paginator([],
                                                total=len_data,
                                                page=page_num,
                                                per_page=per_page,
                                                padding=padding,
                                                left_edge=left_edge,
                                                right_edge=right_edge,
                                                left_current=left_current,
                                                right_current=right_current)
                            _paginator.slug = slug
                            _paginator.index_slug = _generator.get("index_slug")

                            current_page = i + 1
                            prev_page = current_page - 1
                            has_prev_page = prev_page < 0
                            next_page = current_page + 1
                            has_next_page = next_page < total_pages

                            pagination = {
                                "items_per_page": per_page,
                                "current_page": current_page,
                                "prev_page": prev_page,
                                "has_prev_page": has_prev_page,
                                "next_page": next_page,
                                "has_next_page": has_next_page
                            }

                            dmeta = copy.deepcopy(mdata)

                            for _ in special_meta:
                                if _ in data:
                                    dmeta[_] = data.get(_)

                            # If generator has the permalink, it will substitute if
                            # Slug in the generator must have token from the data
                            # to generate the slug
                            if "permalink" in _generator:
                                dmeta["permalink"] = lib.slugify_with_slash(_generator.get("permalink").format(**data))

                            # Slug is required
                            if "permalink" not in dmeta:
                                print("WARNING: Skipping page because it's missing `permalink`")
                                continue

                            permalink = dmeta.get("permalink")
                            dmeta["url"] = permalink
                            this = {
                                **dmeta,
                                "data": data,
                            }
                            lpages.append({
                                **copy.deepcopy(_default_page),
                                "filepath": permalink,
                                "context": {
                                    "page": this,
                                    "this": this,
                                    "__page__": this
                                },
                                "content": mdata.get("content"),
                                "markup": mdata.get("markup"),
                                "template": mdata.get("template"),
                                "layout": mdata.get("layout") or self.layout,
                                "pagination": {
                                    "has_prev": ""
                                }
                            })



                            _slug = slug.format(**{"page_num": page_num})
                            dmeta["url"] = _slug
                            dmeta["context"] = d
                            dmeta["paginator"] = _paginator


                            permalink = dmeta.get("permalink")
                            dmeta["url"] = permalink
                            this = {
                                **dmeta,
                                "data": data,
                            }





                            page.update({
                                "filepath": _slug,
                                "context": {"page": dmeta}
                            })
                            self.create_page(**page)

                            # First page need to generate the index
                            if i == 0 and _generator.get("index_slug"):
                                page["filepath"] = _generator.get("index_slug")
                                self.create_page(**page)

                    return lpages
        
        return []

    def _reset_page_context_assets(self, context):
        context["page"]["__assets"] = {
            "js": [],
            "css": []
        }

    def clean_build_dir(self):
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir)

    def build_static(self):
        """ Build static files """
        if not os.path.isdir(self.build_static_dir):
            os.makedirs(self.build_static_dir)
        if not os.path.isdir(self.build_static_gen_dir):
            os.makedirs(self.build_static_gen_dir)
            
        if (self.print_info):
            print_info('copying static dir to build folder...')
        copy_tree(self.static_dir, self.build_static_dir)

        if os.path.exists(self.public_dir):
            print_info('copying public dir content to build folder...')
            copy_tree(self.public_dir, self.build_dir)


    def build_pages(self) -> int:
        """Iterate over the pages_dir and build the pages """
        src_files = []

        # Aggregate all the files
        for root, _, files in os.walk(self.pages_dir):
            if (self.print_info):
                print_info('aggregating pages files...')

            base_dir = root.replace(self.pages_dir, "").lstrip("/")
            if not base_dir.startswith("_"):
                for f in files:
                    src_file = os.path.join(base_dir, f)
                    src_files.append(src_file)
                    _file_meta = self._get_file_data(src_file)
                    hashed_name = _clean_hashfile_key(src_file)
                    pages_data__[hashed_name] = _file_meta
                    
        # Build pages
        if (self.print_info):
            print_info('initiating page building...')
        
        _pages = [p for s in src_files for p in self._build_page(s) if p]


        for p in _pages:
            self.create_page(**p)
        return len(_pages)

    def create_page(self, build_dir, filepath, context={}, content=None, template=None, markup=None, layout=None):
        """
        To dynamically create a page and save it in the build_dir
        :param build_dir: (path) The base directory that will hold the created page
        :param filepath: (string) the name of the file to create. May  contain slash to indicate directory
                        It will also create the url based on that name
                        If the filename doesn't end with .html, it will create a subdirectory
                        and create `index.html`
                        If file contains `.html` it will stays as is
                        ie:
                            post/waldo/where-is-waldo/ -> post/waldo/where-is-waldo/index.html
                            another/music/new-rap-song.html -> another/music/new-rap-song.html
                            post/page/5 -> post/page/5/index.html
        :param context: (dict) context data
        :param content: (text) The content of the file to be created. Will be overriden by template
        :param template: (path) if source is not provided, template can be used to create the page.
                         Along with context it allows to create dynamic pages.
                         The file is relative to `/templates/`
                         file can be in html|md
        :param markup: (string: html|md), when using content. To indicate which markup to use.
                        based on the markup it will parse the data
                        html: will render as is
                        md: convert to the appropriate format
        :param layout: (string) when using content. The layout to use.
                        The file location is relative to `/templates/`
                        file can be in html|md
        :return:
        """

        _context = lib.dictdot(context)
        build_dir = build_dir.rstrip("/")
        filepath = filepath.lstrip("/").rstrip("/")
        if not filepath.endswith(".html"):
            filepath += "/index.html"

        dest_file = os.path.join(build_dir, filepath)
        dest_dir = os.path.dirname(dest_file)

        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        if "page" not in _context:
            _context["page"] = self.default_page_meta.copy()
        if "url" not in _context["page"]:
            _context["page"]["url"] = "/" + \
                filepath.lstrip("/").replace("index.html", "")
        
        if "page" in _context:
            _context["__page__"] = _context.get("page")

        self._reset_page_context_assets(_context)

        #! redirect
        if redirect := _context.get("page.redirect"):
            url = redirect if lib.is_external_url(redirect) else self._get_page_url(redirect, full_url=True)
            content = HTML_REDIRECT_TEMPLATE.format(url=url)
            lib.write_file(dest=dest_file, contents=content)
            return


        if template:
            if template not in self._templates:
                self._templates[template] = self.tpl_env.get_template(template)
            tpl = self._templates[template]
        else:
            is_sfc, sfc_c = lib.destruct_sfc(content)
            content = sfc_c.get('template')
            if markup == "md":
                content = ext.convert(content)

            # Page must be extended by a layout and have a block 'body'
            # These tags will be included if they are missing
            if re.search(lib.RE_EXTENDS, content) is None:
                layout = layout or self.layout
                content = "\n{% extends '{}' %} \n\n".replace("{}", layout) + content

            if re.search(lib.RE_BLOCK_BODY, content) is None:
                _layout_block = re.search(lib.RE_EXTENDS, content).group(0)
                content = content.replace(_layout_block, "")
                content = "\n" + _layout_block + "\n" + \
                          "{% block __SSG_BODY_BLOCK__ %} \n" + content.strip() + \
                    "\n{% endblock %}"
                
            # Create SFC Assets
            if is_sfc is True:
                sfc_uuid = lib.gen_uuid()
                sfc_asset_filepath = slugify(filepath)
                sfc_o = {"script": "js", "style": "css"}
                for o in sfc_o:

                    if (sfc_c.get(o)):
                        _ff = os.path.join(self.build_static_gen_dir, "%s_%s.%s" % (
                            sfc_asset_filepath, sfc_uuid, sfc_o[o]))
                        _sff = _ff.replace(self.build_static_dir, '').lstrip("/")
                        _context["page"]["sfc_%s_path" % sfc_o[o]] = _sff

                        # write content
                        o_content = sfc_c.get(o)
                        o_content = o_content.replace('{%STATIC_URL%}', self.static_url.rstrip("/"))
                        # convert SCSS to css -> <style scss>
                        if o == 'style' and "scss" in sfc_c["style_props"].strip():
                            o_content = lib.scss_to_css(o_content)
                        lib.write_file(dest=_ff, contents=o_content)

                        if o == "script":
                            # "attributes": sfc_c["script_props"]
                            _context["page"]["__assets"]["js"].append(_sff)
                        elif o == "style":
                            _context["page"]["__assets"]["css"].append(_sff)

            tpl = self.tpl_env.from_string(content)

        # Bundle assets
        if True:
            """
            With bundle enabled, you can instead put the bundle on the page instead of individual files

            = Bundle
                <link rel="stylesheet" type="text/css" href="{{ get_static_bundle_url_for(page, 'page_css_bundle') }}">

                <script type="text/javascript" src="{{ get_static_bundle_url_for(page, 'page_js_bundle') }}"></script>

            = No bundle

                {% for file in page.__assets.js %}
                    <script type="text/javascript" src="{{ get_static_url_for(file) }}"></script>
                {% endfor %}

                {% for file in page.__assets.css %}
                    <link rel="stylesheet" type="text/css" href="{{ get_static_url_for(file) }}">
                {% endfor %}

            """
            name = "bundle_%s_%s" % (slugify(filepath), lib.gen_uuid())
            filepath_ = os.path.join(self.build_static_gen_dir, name)
            bundlename_ = filepath_.replace(self.build_static_dir, '').lstrip("/")
        
            ftypes = {
                "css": ("assets_bundles.page_css_bundle", "page.__assets.css", "page_css_bundle"),
                "js": ("assets_bundles.page_js_bundle", "page.__assets.js", "page_js_bundle"),
            }
            for ftype, s in ftypes.items():
                cached_contents_ = cached.get(s[2]) or ""
                if not cached_contents_:
                    if self.config.get(s[0]):
                        cached[s[2]] = lib.minify_static_contents(ftype=ftype, contents=lib.merge_files_contents([os.path.join(self.static_dir, f) for f in self.config.get(s[0]) or []]))
                        cached_contents_ = cached[s[2]]

                if _c := _context.get(s[1]):
                    cached_contents_ += lib.minify_static_contents(ftype=ftype, contents=lib.merge_files_contents([os.path.join(self.build_static_dir, f) for f in _c]))

                if cached_contents_:
                    _context["page"]["__assets"][s[2]] = "%s.%s" %  (bundlename_, ftype)
                    lib.write_file(contents=cached_contents_, dest="%s.%s" %  (filepath_, ftype))


        # Write file
        if (self.print_info):
            print_info('creating page: %s...' % filepath)
        self._context_root = lib.context_root(_context.get("page.url"))
        lib.write_file(dest=dest_file, contents=tpl.render(**_context))

    def build(self, print_info=False) -> int:
        self.print_info = print_info
        self.clean_build_dir()
        if not os.path.isdir(self.build_dir):
            os.makedirs(self.build_dir)
        self.build_static()
        return self.build_pages()
