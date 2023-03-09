from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """
    The AboutAuthorView renders the 'about/author.html' template,
    which contains information about the author of the website.
    """
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """
    The AboutTechView renders the 'about/tech.html' template,
    which contains information about the technology
    used to build the website.
    """
    template_name = 'about/tech.html'
