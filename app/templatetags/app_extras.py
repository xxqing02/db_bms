from django import template
register = template.Library()

@register.filter
def calculate_days_difference(due_time, start_time):
    if due_time and start_time:
        difference = due_time - start_time
        return difference.days
    return None

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def enum(value):
    enum = {}
    for i in range(1, value + 1):
        enum[str(i)] = str(i)
    return enum