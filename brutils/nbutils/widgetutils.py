from ipywidgets import widgets
import numpy as np


def get_possible_widget_values(w):
    """
    returns a list of the possible widget values
    """

    if isinstance(w, widgets.widget_int.IntSlider):
        return range(w.min, w.max+1, w.step)
    elif isinstance(w, widgets.widget_float.FloatSlider):
        return np.arange(w.min, w.max+w.step, w.step)
    elif isinstance(w, widgets.widget_bool.Checkbox):
        return [True, False]
    elif isinstance(w, widgets.widget_selection.RadioButtons) or isinstance(w, widgets.widget_selection.Select)\
            or isinstance(w, widgets.widget_selection.SelectionSlider) or isinstance(w, widgets.widget_selection.Dropdown):
        if isinstance(w.options, dict):
            return w.options.values()
        elif isinstance(w.options, list):
            return w.options
    else:
        raise NotImplementedError, "That type of widget is not handled by get_possible_widget_values yet"