### Model Leaderboard for {{project_name}}


|Model Number|Model Name|{% for metric in metrics %} {{ metric }} | {% endfor %}
| {% for model in models  %}{% if loop.index < 11 %} | M{{ model["modelNumber"] | string }} | {{model['modelType']}} | {% for metric in metrics %}{{ model['metrics'][metric] | metric_parser }} | {% endfor %}{% endif %} |
| -------------------------------------------------- |
{% endfor %}