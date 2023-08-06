This is the data directory that contains data json or yaml file

Usage: 

{% for car in get_data("cars.my_list") %}
  <li>{{ car }}</li>
{% endfor %}