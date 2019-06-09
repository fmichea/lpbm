---
layout: post
title: "{{ article.title }}"
authors: [{% for author_id in article.authors|sort %}{{ authors_mod[author_id].nickname }},{% endfor %}]
categories: [{% for category in article.categories %}"{{ categories_mod[category].full_path()|join(' > ') }}"{% endfor %}]
redirect_from:
  - /articles/{{ article.html_filename() }}
excerpt_separator: <!--more-->
---

{{ article.jekyll_content }}
