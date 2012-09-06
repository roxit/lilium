from django.template import Library

register = Library()

@register.filter
def section_text(board_manager, idx):
    return str(board_manager[idx])

