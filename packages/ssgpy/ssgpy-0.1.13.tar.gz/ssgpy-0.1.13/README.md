
# SSG.py! 

SSG.py is an elegant static site generator built in Python

 It is optimized for speed and easy to use. With no dependencies, SSG.py is easy to install and update.

SSG.py takes a directory with content and templates and renders them into a full html website. 
It’s a great choice for website, blogs and documentation. Content can be written in HTML and Markdown, oganized however you want with any URL structure, and metadata can be definied in front-matter. All this is done with almost no configuration, meaning with SSG.py, you can just get straight to work.


## Get Started

### Install

```
pip install ssgpy
```
    
### Create/Init site

```
cd /my-site-dir

ssg init
```

### Serve 
```
ssg serve
```

### To build the content only to be uploaded 

```
ssg build 
```

### Clean the build directory 

```
ssg clean 
```

---

## Technology

SSG.py is built in Python, and features the powerful templating language Jinja2. 

SSG.py allows you to write your content in either Markdown or plain HTML. 

HTML gives you full independence.

Markdown, for simply writing article.

To get creative, SSG.py allows you to write your HTML/JS/CSS in a single file component style.

All three are powered by the powerful Jinja2 template language.

Features:

- Friendly Url
- Jinja
- HTML
- Markdown
- Single file component


It helps you create static and deploy to S3.


Technology uses:

- Jinja2: Powerful templating language
- Front Matter, to add context to the page
- Arrow to write date and time

---

## Install

```
pip install ssgpy
```
    
## Create and serve a new site on local

```
cd ~/into-your-dir

ssg create mysite.com

cd mysite.com 

ssg serve
``` 

---

Structure:

    ____
        |
        |-- data
            |
        |-- pages
            |
        |-- public
            |
        |-- static
            |
        |-- templates
            |-- /layouts
            |-- /partials
            |-- /content

---------

**/pages**:
    Contains all the pages to be built
    If the pages contain local context -> {{ page.title }}

**/static**: Hold the assets static files

**/public**: Hold public files that will not be parsed. This directory will be copied to the `build` as is

**/data**:
    Contains JSON data context to inject in the templates.
    To access the data, use the file name as as the namespace -> mydata.json -> {{ data.mydata }}


**/templates**:
    Contains all the templates to be included, including layouts and custom. Anything related to templates should be placed in here.
    If you want to create a content file to include, it is recommended to place it in the content folder.

**/templates/layouts**
    Contains all the layouts to use

**/template/partials**
    Contains custom content to include in the pages

**/_build**: This where the build sites will be created. The content of this dir is ready for upload

---


## Content:

### Supported format:

SSG.py support  `.html` and `.md` files. It will ignore all other extensions in the `/pages` directory

Files starting with `_` (underscore) will be ignored


### Organization:

The pages in SSG.py should be arranged in the same way they are intended for the rendered website.
Without any additional configuration, the following will just work. Hugo supports content nested at any level.

    /pages
        |
        |- index.html               // <- http://a.com/
        |
        |- about-us.md              // <- http://a.com/about-us
        |
        |- /post
            |
            |- my-awesome-post.html // <- http://a.com/post/my-awesome-post.html


### Front Matter & Page Context

It enables you to include the meta data and context of the content right with it.
It only supports the Yaml format, it is placed on top of the page. 

    ---
    title: My site title
    slug: /a-new-path/
    description: 
    
    ---

Your front matter data get parsed as a local object, ie: {{ page.title }}

You can also include your own context


# Advanced

## Data Driven

In addition to data files, you can load a resource from any api endpoint. 

The data returned must be in the json format.



## Generators

To generate pages dynamically from a data source

##### context

Generators return a `context` key in the page variable. 

For `single` type, the context is the data for that page

For `pagination` type, the context is a list (array) of data chunk

##### paginator

Generators returns `paginator` key in the page variable, if the `type` is 'pagination'

`pagination` contains: `total_pages`, `current_pages`, `page_slug`, `index_slug`


### Generator: Single

Generate single pages from a source containing list (array) of data

    ---
    
    _generator:
        type: single
        data_source: posts
        slug: /
    ---

`data_source`:  Dot notation can be use to 
 access other node of the data: ie: 
 
    // data/posts.json
    
    {
        "all": [
            {},
            ...
        ],
        "archived": [
            {},
            ...
        ]
    }

You can access the data as:
    
    data_source: posts.archived


`slug`: Will dynamically build the slug. Having the `slug` will overwrite the 
data slug if it has one. 

`slug` format based on the data, so data token must be provided 

ie: `/{post_type}/{id}/{post_slug}`

### Generator: Pagination

Will generated a paginated 

    ---
    
    _generator:
        type: pagination
        data_source: posts
        per_page: 20
        limit: 100
        slug: /all/page/{page_num}
        index_slug: /all
    ---

---

## Single File Component

Single file component allows you to put together HTML, CSS, and JS into one file.

Upon building, SSG.py will separate them and 
place them into their respective files to be 
included in the page.

```
---
title: My Page Title
---

{# Page body #}
<ssg-template>
    <h1>Hello</h1>
    <button id="myButton">My Button</button>
</ssg-template>


{# Page style #}
<ssg-style>
    .color-button {
        color: blue;
    }
</ssg-style>


{# Page script #}
<ssg-script>
    const button = document.querySelector('#myButton');
    button.addEventListener('click', () => {
        button.classList.toggle('color-button');
    });
</ssg-script>


```


## Asset Bundling

```
= Bundle
    <link rel="stylesheet" type="text/css" href="{{ get_page_static_bundle_url(page, 'page_css_bundle') }}">

    <script type="text/javascript" src="{{ get_page_static_bundle_url(page, 'page_js_bundle') }}"></script>

= No bundle

    {% for file in page.__assets.js %}
        <script type="text/javascript" src="{{ get_static_url_for(file) }}"></script>
    {% endfor %}

    {% for file in page.__assets.css %}
        <link rel="stylesheet" type="text/css" href="{{ get_static_url_for(file) }}">
    {% endfor %}

```

## Functions 

- get_page_meta
- get_url_for 
- get_static_url_for 
- get_static_bundle_url_for
- get_public_url_for
- get_data 
- format_date
- get_current_date
- __page__: the current page object
- __site__:dict
- __info__: dict


---

## ssg.yml

### ssg.yml advanced

When dealing with multiple build, you can leverage multi directories


```
---
base_dir: . # the directory relative to ssg.yml that contains the artifacts
build_dir: output # the directory relative to ssg.yml that contains the output
site:
    ...
env:
    ...
```

## TODO
 
RSS