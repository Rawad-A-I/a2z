"""
Context processors for the accounts app.
"""

def default_context(request):
    """
    Add default context variables to all templates.
    """
    return {
        'show_search_bar': False,  # Default to False, override in specific views
    }
