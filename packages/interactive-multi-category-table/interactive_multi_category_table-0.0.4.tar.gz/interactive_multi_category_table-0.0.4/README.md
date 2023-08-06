# interactive-multi-category-table

In many different scenarios, contents are single-categorized and multi-tagged, by which I mean there exist multiple tags but one single (though maybe hierarchical) category system, e.g., file systems, blogs, etc. However, sometimes contents can be categorized from different category views. For storage or lookup, one category system is OK; but for visualization and analysis, flexibly organizing the contents with different category views will be very handy.

This repo targets addressing such demand by creating interactive tables with alternative category views from formatted json input. It can both run as a service on the server side based on [dash](https://dash.plotly.com/), or generate a static webpage on the client side.

# usage

## run on the server side

```python
import interactive_multi_category_table as imct

imct.run_dash_app(json_file_path)
```
and the generated webpage can be accessed at http://127.0.0.1:8050/.

## generate a static webpage

```python
import interactive_multi_category_table as imct

imct.json_to_html(json_file_path)
```

## input json file format

Refer to the provided examples for the json file format.

Note that:
- There have to be at least two category trees.
- Leaf category items in the same category tree cannot be the same.
