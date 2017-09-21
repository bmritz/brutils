import au_plot
import unittest, os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import bokeh
import gd

def matplot_plot(df, style):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(df.iloc[:,0], df.loc[:,"value"])
    return fig

GD_DIR = os.path.join(au_plot.GD_PATH, au_plot.GD_STORAGE_FOLDER)

class GDMetaDataTestCase(unittest.TestCase):
    """tests for the GDMetaData Class"""
    def setUp(self):
        self.metadat = au_plot.GDMetaData({'title':'My Plot', 'user':'britz', 'function':'serialized func'})
        self.GD_approved_labels = ['index', 'name', 'title', 'text', 
                            'labels', 'rank', 'export', 'file', 
                                                'pretext', 'id', 'showtitle', 'family', 'other']

    def test_is_dict(self):
        self.assertIsInstance(self.metadat, dict)

    def test_has_other(self):
        self.assertTrue('other' in self.metadat)

    def test_conformity(self):
        self.metadat.conform_to_GD()
        self.assertFalse(set(self.metadat.keys()).difference(self.GD_approved_labels))

    def test_user_was_moved_to_other(self):
        self.metadat.conform_to_GD()
        self.assertTrue('user' in self.metadat['other'])

    def test_that_yaml_outputs(self):
        self.metadat.conform_to_GD()
        yam = self.metadat.to_yaml()
        self.assertIsNotNone(yam)

class GDPlotTestCase(unittest.TestCase):
    """Tests for GDPlot"""
    def setUp(self):
        self.init_metadat_dict_no_text_all_GD = {"title": "MyPlot", "index":['cat1', 'cat2']}
        self.init_metadat_dict_text_all_GD ={"text": "Some text Description", 
                                            "title": "MyPlot",
                                            "index":['cat1', 'cat2']} 
        self.matplotlib_plot_fxn = matplot_plot
        self.data = pd.DataFrame({"x":[1,2,3,4], "value":[2,4,5,1]})
        self.style = 'dummy_style'
        self.myGDPlot = au_plot.GDPlot(self.data, 
            self.style, 
            self.matplotlib_plot_fxn,
            self.init_metadat_dict_no_text_all_GD)

    def test_fig_returns_Figure_obj(self):
        self.assertIsInstance(self.myGDPlot.fig, plt.Figure)

    def test_data_frame_returns_df_obj(self):
        self.assertIsInstance(self.myGDPlot.data_frame, pd.DataFrame)

    def test_data_json_returns_string(self):
        self.assertIsInstance(self.myGDPlot.data_json, str)

    def test_write_all_files_to_GD(self):
        self.myGDPlot.to_graphdash()
        uid = self.myGDPlot.metadata['other']['uuid']
        for ext in ['.json', '.yaml', '.png', '.svg']:
            self.assertTrue(os.path.exists(os.path.join(GD_DIR, uid+ext)))

    # TO BE IMPLEMENTED
    def test_data_frame_updates_correctly(self):
        self.assertTrue(True)

    def test_that_json_dataframe_is_in_same_order(self):
        self.myGDPlot.to_graphdash()
        uid = self.myGDPlot.metadata['other']['uuid']
        self.assertEqual(gd.get_plot_data(uid), self.myGDPlot.data_frame)

if __name__=="__main__":
    unittest.main()
