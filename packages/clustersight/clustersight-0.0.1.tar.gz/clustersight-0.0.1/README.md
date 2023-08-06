# Clustering Explorer
The Clustering Explorer allows users to interactively analyze which factors in a dataset are most associated with clusters. Users can lasso points of interest in a 2D plot of the data, which is created using Principal Component Analysis (PCA) for dimensionality reduction. The tool provides three modes of analysis: 'table', 'histogram', and 'explainer'.

## Usage
### Create Lasso Tool
```
create_lasso(df, mode='table', label_col=None, exclude_cols=[], num_factors = 10, dtreeviz_plot=True)
```

The create_lasso function creates a lasso tool for data analysis. The parameters for this function are:

`df`: A Pandas DataFrame of the data to be analyzed
`mode`: The mode of analysis. Can be 'table', 'histogram', or 'explainer'
`label_col`: The column name to be used for color coding of the plot
`exclude_cols`: A list of columns to exclude from the analysis
`num_factors`: Number of factors to consider when mode is 'explainer'
`dtreeviz_plot`: A boolean value to decide whether to plot decision tree using dtreeviz library

The mode parameter determines the type of analysis that will be performed:

`'table'`: shows a table of the selected points
`'histogram'`: shows an interactive histogram of each column's values among selected points compared with among all points
`'explainer'`: predicts which factors lead to the clustered selection with a decision tree

The dtreeviz_plot parameter is used when mode is 'explainer'. If dtreeviz_plot is True, the decision tree is plotted using the dtreeviz library. Otherwise, the decision tree is plotted using sklearn, which is faster.

## Dependencies
Python 3.6+
numpy
pandas
sklearn
dtreeviz
plotly
ipywidgets
itertools

## Notes
The tool is designed for datasets that can fit in memory. For larger datasets, consider using a sampling method or dimensionality reduction techniques before using this tool.




