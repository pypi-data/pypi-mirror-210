"""
Data Lasso Tool

This module provides an interactive tool for data exploration using lasso selection.
The data is visualized in a 2D scatter plot, where the dimensions are reduced using
Principal Component Analysis (PCA). Users can lasso points of interest and analyze
the selected data in three modes: 'table', 'histogram', and 'explainer'.

The 'table' mode displays a table of the selected data points. The 'histogram' mode
displays interactive histograms of the selected data. The 'explainer' mode uses a
Decision Tree Classifier to predict which features lead to the clustered selection
and displays the feature importances.

This tool is designed for in-memory datasets. For larger datasets, consider using
a sampling method or dimensionality reduction techniques before using this tool.

Functions:
create_lasso(df, mode, label_col, exclude_cols, num_factors, dtreeviz_plot)
-- Creates a lasso tool for interactive data analysis.

Example:
>> create_lasso(df, mode='table', label_col=None, exclude_cols=[], num_factors = 10, dtreeviz_plot=True)

This module depends on the following libraries:
- Python 3.6+
- numpy
- pandas
- sklearn
- dtreeviz
- plotly
- ipywidgets
- itertools
"""
from itertools import cycle
from math import ceil, sqrt

from IPython.display import display, clear_output
from ipywidgets import Layout, widgets, VBox

from plotly.graph_objs import FigureWidget, Table
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeClassifier, plot_tree
import dtreeviz
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go

# # Load the Iris dataset
# iris = datasets.load_iris()
# df = pd.DataFrame(data= np.c_[iris['data'], iris['target']],
#                      columns= iris['feature_names'] + ['target'])

# create histogram
def create_histograms(df, exclude_cols=None, legend=True):
    """
    Creates histograms of features in selected region and all data
    ---
    Input: Datafame
    Output:
        If dtreeviz_plot=True, then dtreeviz.utils.DTreeVizRender
        Else, None
    ---
    df: Pandas Dataframe of data to analyze
    exclude_cols: Columns not to plot (output and otherwise)
    legend (default True): Whether to show legend on plots
    """
    curr_df = df.drop(exclude_cols, axis=1)
    if exclude_cols is None:
        exclude_cols = ['_x', '_y', 'target']
    # find number of rows and columns
    r = int(sqrt(len(curr_df.columns)))
    c = ceil(len(curr_df.columns) / r)

    fig = make_subplots(rows=r+1, cols=c+1)
    col_num = 0
    max_cols = len(curr_df.columns)
    # create grid
    for i in range(1, r+1):
        for j in range(1, c+1):
            if col_num < max_cols:
                fig.add_trace(go.Histogram(x=curr_df[curr_df.columns[col_num]],
                 name=curr_df.columns[col_num]), row=i, col=j)
                fig.add_annotation(xref="x domain",yref="y domain",x=0.5, y=1.2, showarrow=False,
                       text=f"<b>{curr_df.columns[col_num]}</b>", row=i, col=j)
            col_num += 1

    fig.update_layout(margin=dict(l=0, r=0, b=0))
    fig.update_traces(showlegend=legend)

    return fig

def explain_cluster(df, x_cols, num_factors = 10, dtreeviz_plot=True):
    """
    Runs decision tree on selected region and plots feature importance and decision boundaries
    ---
    Input: Pandas Datafame
    Output:
        If dtreeviz_plot=True, then dtreeviz.utils.DTreeVizRender
        Else, None
    ---
    df: Pandas Dataframe of data to analyze
    x_cols: Input columns of df
    dtreeviz_plot: 
     - If True, plots decision tree of selection boundaries using dtreeviz library
     - Else, plots decision tree of selection boundaries using sklearn (faster)
    """
    # Split data into features and target
    X = df[x_cols].values  # replace with the names of the columns you want to use as features
    y = df['_selected'].values  # replace with the name of the target column you want to predict

    # Create and fit a decision tree classifier
    clf = DecisionTreeClassifier()
    clf.fit(X, y)

    feature_importances = clf.feature_importances_
    # Print the feature importances
    # Combine feature names and importances into a list of tuples
    feature_importances = list(zip(x_cols, feature_importances))

    # Sort the list in descending order by feature importance
    feature_importances_sorted = sorted(feature_importances, key=lambda x: x[1], reverse=True)

    # Iterate over the sorted list and print out the feature names and importances
    print('Feature Importances in Decision Tree')
    for feature_name, importance in feature_importances_sorted[:num_factors]:
        importance_percent = importance * 100
        print(f"{feature_name}: {importance_percent:.2f}%")   
    if dtreeviz_plot:
        viz_model = dtreeviz.model(clf,
                               X_train=X, y_train=y,
                               feature_names=x_cols,
                               target_name=['_selected'], class_names=["not selected", "selected"])
        display(viz_model.view(scale=1.3))
    else:
        out = plot_tree(clf,
           feature_names = x_cols,
           class_names=['not selected', 'selected'],
           filled = True)
        out

def create_lasso(df, mode='table', label_col=None, exclude_cols=None, num_factors = 10, dtreeviz_plot=True):
    """
    Create Lasso tool to analyze lassoed data via below mode options
    ---
    Input: Datafame
    Output: Plotly FigureWidget with lasso select tool
    ---
    data: Pandas Dataframe of data
    exclude_cols: columns to exclude
    mode:
     - 'table' shows a table of selected points
     - 'histogram' shows an interactive histogram selected points
     - 'explainer' predicts which factors lead to clustered selection
    dtreeviz_plot: 
     - If mode = 'explainer' and True, plots decision tree of selection boundaries w/ dtreeviz library
     - Else, plots decision tree of selection boundaries using sklearn (faster)

    """    
    IS_HIST = mode == 'histogram'
    TOP_FACTORS = mode == 'explainer'
    IS_TABLE = mode == 'table'

    if exclude_cols is None:
        exclude_cols = []
    
    s = widgets.Output()

    # format PCA
    pca = PCA(n_components=2)
    pca_cols = [x for x in df.columns if x not in exclude_cols]
    included_cols_df = df[pca_cols]
    pca.fit(included_cols_df)
    pca_df = pd.DataFrame(pca.transform(included_cols_df), columns=['_x', '_y'])
    df['_x'] = pca_df['_x']
    df['_y'] = pca_df['_y']
    
    # Create a FigureWidget
    f = go.FigureWidget()
    f.update_layout(dragmode='lasso')
    f.layout.title = "Data Lasso Scatterplot"
    # If label_col is provided, add color-coding for labels
    if label_col is not None:
        # define color cycle
        colors = cycle(plotly.colors.qualitative.Pastel)
        for label in np.unique(df[label_col]):
            df_label = df[df[label_col] == label]
            scatter = go.Scatter(y = df_label["_x"], x = df_label["_y"], mode = 'markers',
                                 marker=dict(color=next(colors)), name=label)
            f.add_trace(scatter)
        # create invisible layer w/ all labels to perform decision tree on
        scatter = go.Scatter(y = df["_x"], x = df["_y"], mode = 'markers', opacity=0)
        f.add_trace(scatter)
    else:
        # If no label_col is provided, create a single scatter
        scatter = go.Scatter(y = df["_x"], x = df["_y"], mode = 'markers')
        f.add_trace(scatter)

    scatter = f.data[-1]
    df.dropna()
    exclude_cols.extend(['_x', '_y'])
    N = len(df)
    scatter.marker.opacity = 0.5
    # t is for "table", but can also be where data is
    t = None

    # drop non-numeric types
    dropped_columns = [col for col in df.columns if col not in df.select_dtypes(include='number').columns]
    df = df.select_dtypes(include='number')
    exclude_cols = [col for col in exclude_cols if col not in dropped_columns]

    if IS_TABLE:
        # Create a table FigureWidget that updates on selection from points in the scatter plot of f
        t = FigureWidget([Table(
            header=dict(values=df.columns,
                        fill = dict(color='#C2D4FF'),
                        align = ['left'] * 5),

            cells=dict(values=[df[col] for col in df.columns],
                    fill = dict(color='#F5F8FF'),
                    align = ['left'] * 5
                    ))])
    if IS_HIST:
        hist = create_histograms(df, exclude_cols=exclude_cols, legend=True)
        no_legend = create_histograms(df, exclude_cols=exclude_cols)
        
        t = go.FigureWidget(no_legend, )
        t.layout.title = 'All Points'
        
        # s is selected
        s = go.FigureWidget(hist)
        s.layout.title = 'Selected Points'
        
    if TOP_FACTORS:
        pass

    # call on every reselection
    def selection_fn(trace,points,selector):
        nonlocal s
        if mode=='table':
            t.data[0].cells.values = [df.loc[points.point_inds][col] for col in df.columns]
        if IS_HIST:
            selected = df[df.index.isin(points.point_inds)]
            new_charts = create_histograms(selected, exclude_cols=exclude_cols, legend=True)
            s.data = []
            s.add_traces(new_charts.data)
        if TOP_FACTORS:
            df['_selected'] = df.index.isin(points.point_inds)
            x_cols = list(filter(lambda x: x not in exclude_cols and x != '_selected', df.columns))
            with s:
                clear_output(wait=True)
            out = explain_cluster(df, x_cols, num_factors, dtreeviz_plot=dtreeviz_plot)    
    scatter.on_selection(selection_fn)

    # Put everything together
    if IS_HIST:
        return VBox((f, s, t), 
            layout=Layout(align_items='flex-start', margin='0px', justify_content='center'))

    return VBox(tuple(x for x in [f, s, t] if x))
