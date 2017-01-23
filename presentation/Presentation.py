from jinja2 import Template

from Slides import ContentSlide, TitleSlide
import os
package_directory = os.path.dirname(os.path.abspath(__file__))
class Presentation(object):
    """ a presentation is a group of slides -- right now this is used to put together a table of contents """
    
    def __init__(self, title, subtitle, author, resources=(), css="", include_bootstrap=True):
        self.resources=resources
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.css = css
        self.sections = []
        self.title_slide = TitleSlide(title=self.title, subtitle=self.subtitle)
        if include_bootstrap:
            with open(os.path.join(package_directory, "presentation_css.txt"), "r") as fil:
                self.bootstrap = fil.read()
        else:
            self.bootstrap=""


        self.template = Template(
        """
        <!doctype html>
        <html>
            <head>
                {% block head %}
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                <title> {{ title }} </title>
                {% endblock %}
                {% block css %}
                {{ css }}
                {{ bootstrap }}
                {% endblock%} 
            </head>
            <body>
                {% block body %}

                {{ section_html }}
                {% endblock %}
            </body>
        </html>

        """
        )
        self.templatef = Template("""
        <!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

                <title>Test</title>

                <link rel="stylesheet" href="css/reveal.css">
                {{ css }}

                <!-- Printing and PDF exports -->
                <script>
                    var link = document.createElement( 'link' );
                    link.rel = 'stylesheet';
                    link.type = 'text/css';
                    link.href = window.location.search.match( /print-pdf/gi ) ? 'css/print/pdf.css' : 'css/print/paper.css';
                    document.getElementsByTagName( 'head' )[0].appendChild( link );
                </script>
            </head>
            <body>
                <div class="reveal">
                    <div class="slides">
                        {{ section_html }}
                    </div>
                </div>

                <script src="lib/js/head.min.js"></script>
                <script src="js/reveal.js"></script>

                <script>
                    // More info https://github.com/hakimel/reveal.js#configuration
                    Reveal.initialize({

                    });
                </script>
            </body>
        </html>
        """)
    
    def build_html(self):
        """ todo add in the css """
        self.html = self.title_slide.build_html() + "".join([s.build_html() for s in self.sections])
        return self.html
    
    def build_html_full(self):
        self.html_full =  self.template.render(section_html=self.build_html(), css=self.css, title=self.title, bootstrap=self.bootstrap)
        return self.html_full

    def build_toc(self, section_title="Executive Summary", section_subtitle="", slide_title="Table of Contents", slide_subtitle="Click on an insight to jump to that section of the document", append_toc_pos=None):
        """ Build the table of contents section,
        and optionally append it to the presentation sections in a certain position"""

        self.content_template = """
        {% for section in sections %}
        <h3> 
            <a href="{{- section.html_id -}}" class="toc-section-title">
                {{- section.title -}}
            </a>
        </h3>
        <ul>
        {% for secslide in section.slides %}
            <li>
                <a href="#{{- secslide.html_id -}}">{{- secslide.title -}}</a>
            </li>
        {% endfor %}
        </ul>
        {% endfor %}
        """

        toc_slide = ContentSlide(
            title=slide_title,
            subtitle=slide_subtitle,
            content=[[
            self.content_template.render(
                sections=self.sections
            )
            ]]

        )
        toc_section = SlideSection(
                title=section_title,
                subtitle=section_subtitle
        )
        toc_section.slides.append(toc_slide)
        if append_toc_pos is not None:
            new_sections = []
            for i, section in enumerate(self.sections):
                if i == append_toc_pos:
                    new_sections.append(toc_section)
                new_sections.append(section)
            self.sections = new_sections
        return toc_section

