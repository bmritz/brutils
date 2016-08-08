import itertools
from . import widgetutils
from ipywidgets import interact, widgets
from IPython.display import display
from ipywidgets.widgets.interaction import _widget_from_abbrev
from traitlets import TraitError

def widg_from_seq(seq):
    """
    seq is a sequence of tuples (name, abbrev), returns a sequence of widgets
    """
    result = []
    for name, abbrev in seq:
        w = _widget_from_abbrev(abbrev)
        if not w.description:
            w.description = name
        w._kwarg = name
        try:
            w.set_trait("continuous_update", False)
        except TraitError:
            pass
        result.append(w)
    return result

class NBInteract(object):
    """
    Sets up a function to be able to interact with it in an IPython notebook.

    __init__:
        NBInteract(func)
            func: function with all variables wrapped and fixed except those you want to interact with
                    only variables that are "exposed" are the ones you want to interact with
    methods:
        pre_compute(**kwargs):
            arguments are iterables that you would like to pre-compute on
    """
    def __init__(self, func, **kwargs):
        """

        Allows interaction with a function in a notebook context using widgets

        Args:
            func: Function you would like to interact with

            kwargs: widgets or abbreviations for widgets (see below) that can be accepted by func
                Abbreviations:
                    tuple will return a slider 
                        (min, max, step)
                        if step is omitted, it is assumed to be 0.1 if min and max are floats, otherwise 2
                    list will return a drop down string
                    a boolean value will return a checkbox
        """
        self.func = func      
        self.widgets = widg_from_seq(kwargs.items())
        self.keyword_order = kwargs.keys()
        self.cached_results = {}
        
    def _kwargs_to_tuple_key(self, keyword_dict):
        """
        This keeps the order of the tuple identifying the results dictionary consistent from call to call
        The order of the tuple will always bee the order of the widgets_order in __init__
        """
        to_return = []
        for key in self.keyword_order:
            to_return.append(keyword_dict[key])
        return tuple(to_return)
    
    def call_func(self, **kwargs):
        """
        Calculate the function, taking parameters through a dictionary
        keep track of all results ever received through this method
        
        If the result_key is not cached, run the function
        if it is, return the cached result
        """
        result_key = self._kwargs_to_tuple_key(kwargs)
        if result_key not in self.cached_results:
            # semi-colon here so the plot does not show in IPython notebooks every time
            self.cached_results[result_key] = self.func(**kwargs); 
        return self.cached_results[result_key];
    
    def pre_compute(self):
        ## TODO: Handle the error if get_possible_widget_values cannot get values becase not implemented
        
        # find all possible values of the widgets
        possible_combos = list(itertools.product(*[widgetutils.get_possible_widget_values(w) for w in self.widgets]))
        
        #loop through the values and call_func
        f = widgets.FloatProgress(min=0, max=len(possible_combos)-1)
        lab = widgets.HTML(value="")
        display(f); display(lab)
        lab.value = "Beginning processing..."

        for i, kword_vals in enumerate(possible_combos):
            params = dict(zip(self.keyword_order, kword_vals))
            lab.value = "Now processing parameters: %s" % ("<ul><li>" + "<li>".join(["<b>"+str(k)+":</b> "+str(v)+"</li>" for k, v in params.items()]) + "</ul>")
            self.call_func(**params);
            f.value = i

    def interact(self, key=None):
        """
        Interact with the result of the function

        Parameters:
        key (optional): Parameter to apply to the result of the NBInteract function to produce
                        the output that will be interacted with

        Example (interact with only the square of x):
        def myfunc(x):
            return (x, x**2)
        myNBI = NBInteract(myfunc, x=widgets.IntSlider()
        NBInteract.interact(lambda x: x[1])
        """

        # break down to if/then clause to cut down on potentially expensive function calls
        if key is None:
            dumb = interact(self.call_func, **dict(zip(self.keyword_order, self.widgets)));
        else:
            def _interact_func(**kwargs):
                return key(self.call_func(**kwargs));
            dumb = interact(_interact_func, **dict(zip(self.keyword_order, self.widgets)));

