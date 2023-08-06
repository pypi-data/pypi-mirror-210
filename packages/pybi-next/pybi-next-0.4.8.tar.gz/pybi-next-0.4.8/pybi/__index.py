from pybi.core.components.reactiveComponent.echarts import EChartJsCode
from .app import App

# import pybi.core.styles as styles
from pybi.core.styles import *
from pybi.easyEcharts import *
import pybi.icons.material_icons as md_icons

md_icons = md_icons
"""material icons小图标
    >>> pbi.add_icon(pbi.md_icons.md_add_chart)
"""

app = App()

__all__ = [
    "set_source",
    "add_slicer",
    "add_table",
    "add_echart",
    "add_text",
    "colBox",
    "flowBox",
    "gridBox",
    "box",
    "app",
    "styles",
    "easy_echarts",
    "echartJsCode",
    "to_json",
    "sql",
    "set_dataView",
    "to_html",
    "clear_all_data",
    "add_upload",
    "_save_db",
    "meta",
    "save_zip_db",
    "add_tabs",
    "add_markdown",
    "add_icon",
    "affix",
    "add_mermaid",
    "add_input",
    "add_numberSlider",
    # "add_svg_icon",
    "md_icons",
    "space",
]

add_tabs = app.add_tabs
meta = app.meta
gridBox = app.gridBox
set_source = app.set_source
add_upload = app.add_upload
add_text = app.add_text
add_slicer = app.add_slicer
add_table = app.add_table
add_echart = app.add_echart
colBox = app.colBox
flowBox = app.flowBox
echartJsCode = EChartJsCode
box = app.box
to_json = app.to_json
set_dataView = app.set_dataView
sql = app.sql
clear_all_data = app.clear_all_data
_save_db = app.save_db
save_zip_db = app.save_zip_db

to_html = app.to_html
add_markdown = app.add_markdown
add_icon = app.add_icon
# add_svg_icon = app.add_svg_icon
affix = app.affix
add_mermaid = app.add_mermaid
add_input = app.add_input
add_numberSlider = app.add_numberSlider
space = app.space
