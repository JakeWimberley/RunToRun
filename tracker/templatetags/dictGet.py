from django import template
register = template.Library()

# http://stackoverflow.com/questions/2024660/django-sort-dict-in-template

def dictGet(value, arg):
	#{{dictionary|dict_get:var}}
	#where var is a variable representing a key of dictionary

	return value[arg]

register.filter('dictGet',dictGet)
