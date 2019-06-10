---
layout: categoriespage
title: Categories
permalink: /categories/
redirect_from:
  {%- for category in categories %}
  - {{ category }}/index.html
  {%- for i in range(10) %}
  - {{ category }}/page-{{ i }}.html
  {%- endfor %}
  {%- endfor %} 
---
