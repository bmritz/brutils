import StringIO
import matplotlib.pyplot as plt
from jinja2 import Template

def fig_to_svg(fig, bbox_inches="tight", pad_inches=0.0):
    imgdat = StringIO.StringIO()
    fig.savefig(imgdat, format='svg', bbox_inches=bbox_inches, pad_inches=pad_inches)
    imgdat.seek(0)
    svg_dat = imgdat.buf
    return  imgdat.buf

def str_identity(s):
    """ returns the same string that is input """
    return s

class Content(object):
    
    def __init__(self, obj, html_id="", html_class=""):  
        """
        obj -- str or matplotlib Figure for now -- object that will be placed as content
        id -- str -- html id of the div that wraps the content space separated
        classes -- str -- html classes of the div that wraps the content space separated
        """
        self.orig = obj
        self.parsers = {
            plt.Figure: fig_to_svg,
            str: str_identity
        }
        self.html_class=html_class
        self.html_id = html_id

        self.supported_types = self.parsers.keys()

        self.template = Template(
            """
            
            <span style="display:table;margin:0 auto;">
                <div  id="{{ content_id }}" class="{{ content_classes }}" >
                    {{ html_string }}
                </div>
            </span>
            """
            )

        if isinstance(obj, (plt.Figure,)):
            self.html_string = fig_to_svg(obj)
        elif isinstance(obj, basestring):
            self.html_string = obj
        else:
            raise TypeError("Objects of type %s not currently supported for Content. Only types %s are supported" % (type(obj), str(self.supported_types))) 
        
    def build_html(self):
        self.html = self.template.render(html_string = self.html_string, content_class = self.html_class, content_id=self.html_id)
        return self.html

def coerce_to_content(c):
    if isinstance(c, Content):
        return c
    else:
        return Content(c)
