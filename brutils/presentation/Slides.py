from jinja2 import Template
import uuid
from .Content import Content, coerce_to_content


class BaseSlide(object):
    
    def __init__(self, resources={}, classes=None, name="", html_id=""):
        """resources is arbitrary objects of things you want associated with the slide
        classes is a list of html classes
        name is a string that makes the name of the slide
        html_id is a string that will be the html_id of the slide
        """
        
        self.resources = resources
        self.name = name
        if classes is None:
            classes=[]
        self.classes = classes
        self.uid = str(uuid.uuid1())
        self.html_id = html_id or self.uid
        self.base_template=Template(
"""
        <section id="{{- slide_id -}}">
        {% block container_open %}
            <div class="container newslide rendered_html"> <!-- newslide class is used for making sure printing new slides on a new page -->
        {% endblock %}
                {% block slide_area %}
                {% endblock %}
            </div>
        </section>
"""
)


class TitleSlide(BaseSlide):
    
    def __init__(self, title, subtitle=None, resources={}, name=None, author=None, classes=None, html_id=""):
        super(TitleSlide, self).__init__(resources=resources, classes=classes, html_id=html_id)
        self.title = title
        self.subtitle = subtitle
        self.template = Template(
"""
{% extends base_template %}
{% block slide_area %}

            <div class="row">
                <div class="col-sm-12 title-slide">
                    
                    <h1>{{ title_content.build_html() }}</h1>
                    <h3>{{ subtitle_content.build_html() }}</h3>
                    
                </div>
            </div>
{% endblock %}
"""
)
        
    def build_html(self):
        self.html = self.template.render(
            base_template=self.base_template,
            title_content=Content(self.title),
            subtitle_content=Content(self.subtitle),
            slide_id=self.html_id)
        return self.html



class SectionTitleSlide(BaseSlide):
    """The title slide for a section"""
    def __init__(self, title, subtitle, resources={}, name="", author=None, classes=None, html_id=""):
        super(SectionTitleSlide, self).__init__(resources=resources, classes=classes, html_id=html_id, name=name)
        self.title = title
        self.subtitle = subtitle
        self.template = Template(
"""
{% extends base_template %}
{% block container_open %}
            <div class="container newsection newslide rendered_html"> <!-- newslide class is used for making sure printing new slides on a new page -->
{% endblock %}
{% block slide_area %}
                <div class="row">
                    <div class="col-sm-12 section-title-slide">
                        
                        <h1>
                            {{ title_content.build_html() }}
                        </h1>
                        {% if subtitle_content.build_html() != "" %}
                        <h3>
                            {{ subtitle_content.build_html() }}
                        </h3>
                        {% endif %}
                    </div>
                </div>
{% endblock %}
"""
)
    
    def build_html(self):
        self.html = self.template.render(
            base_template = self.base_template,
            title_content=Content(self.title), 
            subtitle_content=Content(self.subtitle),
            slide_id=self.html_id
        )
        return self.html

    def build_pptx(self):
        pass

    def build_docx(self):
        pass


class ContentSlide(BaseSlide):
    """
    title -- string -- title of the slide
    subtitle -- string -- subtitle of the slide
    content -- list -- list of list objects of class Content or of objects that can be coerrced to class Content
    id -- html ID of the html slide <section> tag
    classes -- list of css classes that the slide and its children will belong to
    resources -- dict of arbitrary objects that are attached to the silde for any reason, store extra objects that need to be associated with the slide here

    TODO: 
    - add footer option
    - add location option
    """
    def __init__(self, title=None, subtitle=None, content=None, resources={}, classes=None, html_id=""):
        super(ContentSlide, self).__init__(resources=resources, classes=classes, html_id=html_id,)
        """ content should be a list of lists"""
        self.title = title
        self.subtitle = subtitle
        #self.content_shape = content_cols

        self.content=[]
        cols = 0
        rows = 0
        assert not isinstance(content, (basestring, Content)), "content must be a list, not a string or Content"

        n_boostrap_cols = 12
        for c1 in content:
            self.content.append([])
            assert n_boostrap_cols % len(c1) == 0, "length of each row must be divisible by %s" % n_boostrap_cols
            for c2 in c1:
                self.content[rows].append(coerce_to_content(c2))
            rows+=1
    
    def add_content(self):
        pass

    def build_html(self):
        self.helper="<style> .vertical-align {display: flex; align-items: center;} </style>"
        #col_width = 12 / self.content_shape[0]
        self.template = Template(
"""
{% extends base_template %}
{% block slide_area %}
        
            <div class="page-header" id="{{- html_id -}}">

                  <h2>{{ title }}</h2>
                  {% if subtitle %}
                  <h4>
                  {{ subtitle }}
                  </h4>
                  {% endif %}
            </div>
            {% for cont in content %}
            <div class="row vertical-align content-row">
                {% for c in cont %}
                <div class="col-sm- {{- 12 // cont.__len__() }} content-div ">
                    
                    {{ c.build_html() }}
                    
                </div>
                {% endfor %} 
            </div>
            {% endfor %}

{% endblock %}
"""
)
        
        self.html = self.template.render(title = self.title, subtitle=self.subtitle, content=self.content, html_id=self.html_id, base_template=self.base_template)
        return self.html


#class TOCSlide(BaseSlide):
#
#    def __init__(self, presentation, title="Executive Summary", subtitle="Click on the text to jump to the insight", resources={}, classes=[], html_id=""):
#        super(TOCSlide, self).__init__(resources=resources, classes=classes, html_id=html_id)
#
#    self.template = """
#
#{% extends base_template %}
#{% block slide_area %}
#{% for section in sections %}
#<h3> 
#    <a href="{{- section.html_id -}}" class="toc-section-title">
#        {{- section.title -}}
#    </a>
#</h3>
#<ul>
#{% for secslide in section.slides %}
#    <li>
#        <a href="#{{- secslide.html_id -}}">{{- secslide.title -}}</a>
#    </li>
#{% endfor %}
#</ul>
#{% endfor %}
#{% endblock %}
#"""
#
#    def build_html(self):
#        self.html = self.template_render(
#                title=self.title,
#                subtitle=self.subtitle,
#                sections=presentation.sections,
#                html_id=self.html_id)
#        return self.html
#

class SlideSection(object):
    """ a group of slides with a section break title slide"""
    def __init__(self, title, subtitle, resources={}, name="",  classes=None, slides=None, title_slide_html_id=""):
        self.title = title
        self.subtitle = subtitle
        self.resources=resources
        self.name=name
        if classes is None:
            classes = []
        self.classes=classes
        if slides is None:
            slides = []
        self.slides = slides
        self.uid = str(uuid.uuid1())
        self.html_id = title_slide_html_id or self.uid
        self.title_slide = SectionTitleSlide(title=title, subtitle=subtitle, html_id=self.html_id)
    
    def build_html(self, title=True):
        html_slides = "".join([s.build_html() for s in self.slides])
        html_title = self.title_slide.build_html() if title else ""
        self.html = html_title+html_slides
        return self.html

    def build_pptx(self, title=True):
        pass

    def build_docx(self, title=True):
        pass

