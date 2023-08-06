from typing import Any


def altair_theme_gray() -> dict[str, Any]:
    """A simple altair theme.

    Returns
    -------
    dict
        Dictionary with parameters that define the theme.
    """
    color = "gray"
    font_weight = "normal"
    small_font = 14
    medium_font = 16
    large_font = 30
    height = 350
    width = 1400
    return {
        "config": {
            "text": {
                "color": color,
                "fontSize": small_font,
            },
            "title": {
                "anchor": "middle",
                "fontWeight": font_weight,
                "titleFontWeight": font_weight,
                "labelFontWeight": font_weight,
                "fontSize": large_font,
                "titleFontSize": medium_font,
                "labelFontSize": small_font,
                "color": color,
                "titleColor": color,
                "labelColor": color,
                "tickColor": color,
                "domainColor": color,
            },
            "header": {
                "titleFontSize": medium_font,
                "labelFontSize": medium_font,
                # "labelAngle": 0,
                "color": color,
                "titleColor": color,
                "labelColor": color,
                "titleFontWeight": font_weight,
            },
            "view": {
                "height": height,
                "width": width,
                "strokeWidth": 0,
                "fill": "white",
            },
            "axis": {
                "domain": True,
                "domainColor": color,
                "domainWidth": 1,
                "gridWidth": 1,
                "labelAngle": 0,
                "tickSize": 5,
                "gridCap": "round",
                "gridDash": [2, 4],
                "fontWeight": font_weight,
                "titleFontWeight": font_weight,
                "labelFontWeight": font_weight,
                "fontSize": large_font,
                "titleFontSize": medium_font,
                "labelFontSize": small_font,
                "color": color,
                "titleColor": color,
                "labelColor": color,
                "tickColor": color,
            },
            "axisX": {
                "titleAnchor": "end",
                "titleAlign": "center",
            },
            "axisY": {
                "titleAnchor": "end",
                "titleAngle": 0,
                "titleAlign": "center",
                "titleY": -15,
                "titleX": 0,
            },
            "axisLeft": {
                "labelAlign": "right",
            },
            "axisRight": {
                "titleAnchor": "end",
                "titleAngle": 0,
                "titleAlign": "center",
                "titleY": -15,
                "tickSize": 5,
                "tickColor": color,
                "labelPadding": 5,
                "labelAlign": "left",
            },
            "facet": {
                "spacing": 50,
            },
            "legend": {
                "fontWeight": font_weight,
                "titleFontWeight": font_weight,
                "labelFontWeight": font_weight,
                "fontSize": large_font,
                "titleFontSize": medium_font,
                "labelFontSize": small_font,
                "color": color,
                "titleColor": color,
                "labelColor": color,
                "tickColor": color,
                "domainColor": color,
            },
        }
    }


def altair_theme_gray_label_in_plot() -> dict:
    color = "gray"
    font_weight = "normal"
    small_font = 14
    medium_font = 16
    large_font = 30
    height = 800
    width = 800
    return {
        "config": {
            "text": {
                "color": color,
                "fontSize": small_font,
            },
            "title": {
                "anchor": "middle",
                "fontWeight": font_weight,
                "titleFontWeight": font_weight,
                "labelFontWeight": font_weight,
                "fontSize": large_font,
                "titleFontSize": medium_font,
                "labelFontSize": small_font,
                "color": color,
                "titleColor": color,
                "labelColor": color,
                "tickColor": color,
                "domainColor": color,
            },
            "view": {
                "height": height,
                "width": width,
                "strokeWidth": 0,
                "fill": "white",
            },
            "axis": {
                "domain": True,
                "domainColor": color,
                "domainWidth": 1,
                "gridWidth": 1,
                "labelAngle": 0,
                "tickSize": 5,
                "gridCap": "round",
                "gridDash": [2, 4],
                "fontWeight": font_weight,
                "titleFontWeight": font_weight,
                "labelFontWeight": font_weight,
                "fontSize": large_font,
                "titleFontSize": medium_font,
                "labelFontSize": small_font,
                "color": color,
                "titleColor": color,
                "labelColor": color,
                "tickColor": color,
            },
            "axisX": {
                "titleAnchor": "end",
                "titleAlign": "right",
                "titleBaseline": "bottom",
                "titleY": -10,
                "titleX": 800 - 10,
            },
            "axisY": {
                "titleAnchor": "end",
                "titleAngle": 0,
                "titleBaseline": "top",
                "titleAlign": "left",
                "titleY": 10,
                "titleX": 10,
            },
            "legend": {
                "fontWeight": font_weight,
                "titleFontWeight": font_weight,
                "labelFontWeight": font_weight,
                "fontSize": large_font,
                "titleFontSize": medium_font,
                "labelFontSize": small_font,
                "color": color,
                "titleColor": color,
                "labelColor": color,
                "tickColor": color,
                "domainColor": color,
            },
        }
    }
