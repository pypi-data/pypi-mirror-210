# Changelog

## [{{ tag_name }}]({{ tag_url }}) ({{ tag_timestamp.strftime('%Y-%m-%d') }})
{% if features %}

### New features

{% for feature in features %}
- {{ feature }}
{% endfor %}
{% endif %}
{% if improvements %}

### Improvements

{% for improvement in improvements %}
- {{ improvement }}
{% endfor %}
{% endif %}
{% if bug_fixes %}

### Bug fixes

{% for bug_fix in bug_fixes %}
- {{ bug_fix }}
{% endfor %}
{% endif %}
