---
nickname: {{ author.nickname }}
name: {{ author.full_name() }}
email: {{ author.email }}
redirect_from:
    - /authors/{{ author.nickname }}/index.html
    {%- for i in range(10) %}
    - /authors/{{ author.nickname }}/page-{{ i }}.html
    {%- endfor %}
---

