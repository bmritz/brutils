from imblearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
def organize_colnames(X):
    """
    Organizes a keep_fxn so we can use it in a pipeline to subset columns

    Inputs
    ------
    X: A pandas dataframe

    Outputs
    -------
    colnames, keep_fxn

    colnames: A numpy array of the column names of X
    keep_fxn: A Function that can be used to subset the numpy array underlying X using column names, not position
    """   
    
    colnames = X.columns
    # make startswith a string list
    def keep_fxn(X_t, columns=[], startswith=[]):
        """This can be used in a pipeline to subset columns"""
        if columns:
            cols = columns
        else:
            cols = []
        cols.extend([x for s in startswith for x in colnames if x.startswith(s)])
        indxer = [colnames.tolist().index(cname) for cname in cols]
        return X_t[:, indxer]
        
    return colnames, keep_fxn


## CREATE PIPELINE 
def link_pipes(*args):
    """Links pipelines of form ('name', Pipeline) together in hierarchical fashion,
    concatenates the names with "->" to create the name of the new pipeline

    Inputs
    ------
    *args, tuples of the form ("name", sklearn.pipeline.Pipeline)

    Outputs
    -------
    A tuple of the form ("newname", sklearn.pipeline.Pipeline) 
    Where the new pipeline is a pipeline linking the args together in order
    """
    final_name = "->".join([name for name, transform in args])
    final_pipe = Pipeline(list(args))
    return ("("+final_name+")", final_pipe)

def union_pipes(*args):
    """Unions pipelines of form ('name', Pipeline) together using FeatureUnion,
    concatenates the names with "||" to create the name of the new pipeline

    Inputs
    ------
    *args, tuples of the form ("name", sklearn.pipeline.Pipeline)

    Outputs
    -------
    A tuple of the form ("newname", sklearn.pipeline.FeatureUnion) 
    Where the new pipeline is a FeatureUnion linking the args together through concatination on axis1
    """
    final_name = "||".join([name for name, transform in args])
    final_name = "("+final_name+")"
    final_union = FeatureUnion(list(args))
    return (final_name, final_union)


def tree_to_code(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree.tree_.feature
    ]
    print("def tree({}):".format(", ".join(feature_names)))

    def recurse(node, depth):
        indent = "    " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            print("{}if {} <= {}:".format(indent, name, threshold))
            recurse(tree_.children_left[node], depth + 1)
            print("{}else:  # if {} > {}".format(indent, name, threshold))
            recurse(tree_.children_right[node], depth + 1)
        else:            
            print("{}return {}".format(indent, np.argmax(tree_.value[node])))

    recurse(0, 1)
