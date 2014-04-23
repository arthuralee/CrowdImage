from django import template
register = template.Library()

@register.filter('input_type')
def input_type(ob):
	html = str(ob)
	start = html.find('type="') + 6
	if start == -1: return ""
	end = html.find('"', start)
	return html[start:end]