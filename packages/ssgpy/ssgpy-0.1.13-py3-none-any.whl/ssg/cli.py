
import os
import sys
import time
import click
import pkg_resources
from livereload import Server, shell
from . import Generator, lib
from .ssg import PAGE_FORMAT
from .__about__ import *

CWD = os.getcwd()


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    

TPL_HEADER = """
---
title: Page Title
description: Page Description
meta:
    key: value
---

"""

TPL_BODY = {
    # HTML

    "html": """
<template>
    <div>
        <h1>{{ page.title }}</h1>
    </div>
</template>

<script>

</script>

<style>

</style>
""",

    # MD
    "md": """

# My markdown SSG!

"""

}


def copy_resource(src, dest):
    """
    To copy package data to destination
    """
    package_name = "ssg"
    dest = (dest + "/" + os.path.basename(src)).rstrip("/")
    if pkg_resources.resource_isdir(package_name, src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for res in pkg_resources.resource_listdir(__name__, src):
            copy_resource(src + "/" + res, dest)
    else:
        if not os.path.isfile(dest) \
                and os.path.splitext(src)[1] not in [".pyc"]:
            with open(dest, "wb") as f:
                f.write(pkg_resources.resource_string(__name__, src))
        else:
            print("File exists: %s " % dest)


def stamp_ssg_current_version(dir):
    f = os.path.join(dir, "ssg.yml")
    if os.path.isfile(f):
        with open(f, "r+") as file:
            content = file.read()
            content = content.replace("##VERSION##", __version__)
            file.seek(0)
            file.write(content)
            file.truncate()


def title(txt):
    message = "%s" % txt
    print(color.BOLD + message + color.END)


def footer():
    print("-" * 80)

def done():
    info('DONE!')
    footer()

def error(message):
    print(color.BOLD + color.RED + "::ERROR::" + color.END)
    print(color.RED + message + color.END )

def error_exit(message):
    error(message)
    footer()
    exit()

def info(message):
    print(color.DARKCYAN + message + color.END )

def log(message): 
    print(message)

@click.group()
def cli():
    """
    SSG: An elegant static site generator
    """
    pass


@cli.command("version")
def version():
    """Return the vesion of SSG"""
    print(__version__)
    footer()


@cli.command("generate")
@click.option("--site", default=None)
def generate(site=None):
    """Generate a new site directory from --site or base_dir in the ssg.yml"""
    title('Generate new site')
    ssg_conf = os.path.join(CWD, "ssg.yml")

    if not site and os.path.isfile(ssg_conf):
        if conf := lib.load_conf(ssg_conf):
            if base_dir := conf.get("base_dir"):
                site = base_dir
            else:
                error_exit("SSG already initialized in '%s'. Or delete 'ssg.yml' if a mistake " % CWD)
    if not site:
        error_exit("site or base_dir not set. Use 'ssg init' to initialize in the current directory")

    sitepath = os.path.join(CWD, site)
    if not os.path.isdir(sitepath):
        info("Generating site: %s..." % site)
        os.makedirs(sitepath)
        copy_resource("skel/", sitepath)
        stamp_ssg_current_version(sitepath)
        info("Site created successfully!")
        info("Update the [base_dir:'%s'] in ssg.yml and run 'ssg serve' to view the site" % site)
    else:
        error_exit("Site directory '%s' exists already!" % site)

    done()




@cli.command("init")
def init():
    """Initialize SSG in the current directory """
    title("Init SSG...")
    ssg_conf = os.path.join(CWD, "ssg.yml")
    if os.path.isfile(ssg_conf):
        error_exit("SSG already initialized in '%s'. Or delete 'ssg.yml' if a mistake " % CWD)
    else:
        copy_resource("skel/", CWD)
        stamp_ssg_current_version(CWD)
        info("SSG init successfully!")
        info("Run 'ssg serve' to view the site")
    done()


@cli.command("page")
@click.argument("pagenames", nargs=-1)
def create_page(pagenames):
    """Create new pages"""
    K = Generator(CWD)
    defaultExt = "html"
    pages = []
    title("Creating new pages...")

    # Prepare and check the files
    for pagename in pagenames:
        page = pagename.lstrip("/").rstrip("/")
        _, _ext = os.path.splitext(pagename)

        # If the file doesn't have an extension, we'll just create one
        if not _ext or _ext == "":
            page += ".%s" % defaultExt

        # Destination file
        dest_file = os.path.join(K.pages_dir, page)
        if not page.endswith(PAGE_FORMAT):
            error_exit("Invalid file format: '%s'. Only '%s'" %
                       (page, " ".join(PAGE_FORMAT)))
        elif os.path.isfile(dest_file):
            error_exit("File exists already: '%s'" % dest_file)
        else:
            pages.append((page, dest_file))

    for page, dest_file in pages:
        # Making sure dir is created
        dest_dir = os.path.dirname(dest_file)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        markup = os.path.splitext(page)[1].strip('.')
        content = TPL_HEADER
        content += TPL_BODY[markup]
        with open(dest_file, "w") as f:
            f.write(content)
        log("- %s" % page)
    done()



@cli.command("build")
@click.option("-i", "--info", is_flag=True)
@click.option("--env", default=None)
def build(info, env):
    """Build the site"""
    title("Building site...")
    K = Generator(CWD, {"env": env, "build": "build"})
    build_dir = K.build_dir.replace(CWD, "")
    log('Env: %s' % K.site_env)
    log('Base Url: %s' % K.base_url)
    log('Static Url: %s' % K.static_url)
    log("Build Dir: %s" % build_dir)  
    total_pages = K.build(print_info=info)
    log("Total pages: %s" % total_pages)

    done()

@cli.command("serve")
@click.option("-p", "--port", default=None)
@click.option("--no-livereload", default=None)
@click.option("--open-url", default=None)
@click.option("--env", default=None)
def serve(port, no_livereload, open_url, env):
    """Serve the site """
    
    K = Generator(CWD, {"env": env, "build": "serve"})
    if not port:
        port = K.config.get("serve.port", 8000)
    if no_livereload is None:
        no_livereload = True if K.config.get("serve.livereload") is False else False
    if open_url is None:
        open_url = False if K.config.get("serve.open_url") is False else True
    build_dir = K.build_dir.replace(CWD, "")
    title('Serving on port %s' % port)
    log('Env: %s' % K.site_env)
    log('Base Url: %s' % K.base_url)
    log('Static Url: %s' % K.static_url)
    log("Build Dir: %s" % build_dir)  
    log("Livereload: %s" % ("OFF" if no_livereload else "ON"))
    total_pages = K.build()
    log("Total pages: %s" % total_pages)

    def _build_data():
        log("Rebuilding...")
        K.load_data_resources()
        total_pages = K.build_pages()
        log("Total pages: %s" % total_pages)
        print()

    def _build_pages():
        log("Rebuilding...")
        total_pages = K.build_pages()
        log("Total pages: %s" % total_pages)
        print()

    def _build_static():
        K.build_static()


    server = Server()
    if no_livereload is False:
        server.watch(K.data_dir + "/", _build_data)
        server.watch(K.static_dir + "/", _build_static)
        for c in [K.templates_dir, K.pages_dir]:
            server.watch(c + "/", _build_pages)

    server.serve(open_url_delay=open_url, port=str(port), root=K.build_dir)


@cli.command("clean")
def clean():
    """Clean the build dir """
    title("Cleaning build dir...")
    Generator(CWD).clean_build_dir()
    done()

#@cli.command("macros")
def macros():
    """ List all macros """
    title("SSG macros")
    K = Generator(CWD)
    macros = K.ssg_macros
    for m in sorted(macros):
        log("- %s: %s" % (m, macros[m]))
    done()


def cmd():
    try:
        print("*" * 80)
        print("=" * 80)
        title("SSG.py %s!" % __version__)
        print("-" * 80)
        sys_argv = sys.argv
        exempt_argv = ["init", "create", "version", "--version", "-v"]
        ssg_conf = os.path.join(CWD, "ssg.yml")
        ssg_init = os.path.isfile(ssg_conf)
        if len(sys_argv) > 1:
            if sys_argv[1] in ['-v', '--version']:
                pass                
            elif not ssg_init and sys_argv[1] not in exempt_argv:
                error("SSG is not initialized yet in this directory: %s" % CWD)
                log("Run 'ssg init' to initialize SSG in the current directory")
                footer()
            else:
                cli()
        else:
            cli()
    except Exception as e:
        
        error("Ohhh noooooo! Something bad happens")
        raise e
        log(">> %s " % e)
        footer()
