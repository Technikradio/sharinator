from django import template

register = template.Library()

@register.filter
def replace(value, args):
    if args is None:
        return value
    arg_list = [arg.strip() for arg in args.split(',')]
    if len(arg_list) < 2:
        return str(value).replace(" ", arg_list[0])
    return str(value).replace(arg_list[0], arg_list[1])

