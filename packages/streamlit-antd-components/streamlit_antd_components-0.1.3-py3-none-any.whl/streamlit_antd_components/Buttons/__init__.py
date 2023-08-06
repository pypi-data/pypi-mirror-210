#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time     : 2023/5/18 9:43
@Author   : ji hao ran
@File     : __init__.py.py
@Project  : StreamlitAntdComponents
@Software : PyCharm
"""
import os
from typing import List, Union, Literal, Callable
from dataclasses import dataclass
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "my_component",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("my_component", path=build_dir)


@dataclass
class ButtonsItem:
    label: str = None  # label
    icon: str = None  # boostrap icon,https://icons.getbootstrap.com/
    disabled: bool = False  # disabled item
    href: str = None  # link address


def _parse_items(items: List[Union[str, ButtonsItem]], func):
    r = []
    for i in items:
        item = i.__dict__.copy() if isinstance(i, ButtonsItem) else {'label': i}
        label = item.get('label')
        if label is None:
            item.update(label='')
        if func is not None:
            item.update(label=func(item.get('label')))
        r.append(item)
    return r


def buttons(
        items: List[Union[str, ButtonsItem]],
        index: Union[int, None] = 0,
        format_func: Callable = None,
        align: Literal["start", "center", "end"] = 'start',
        direction: Literal["horizontal", "vertical"] = 'horizontal',
        shape: Literal["default", "round"] = 'default',
        compact: bool = False,
        grow: bool = False,
        return_index: bool = False,
        key=None
) -> Union[str, int, None]:
    """antd design a group of buttons

    :param items: buttons data
    :param index: default selected button index.if none,click button will not show active style
    :param format_func: format label function,must return str
    :param align: buttons align,available when direction='horizontal'
    :param direction: buttons direction
    :param shape: buttons shape type
    :param compact: buttons compact style
    :param grow: grow to fill space area
    :param return_index: if True,return button index,default return label
    :param key: component unique identifier
    :return: selected button label or index
    """
    parse_items = _parse_items(items, format_func)
    r = _component_func(
        items=parse_items,
        index=index,
        align=align,
        direction=direction,
        shape=shape,
        compact=compact,
        grow=grow,
        key=key
    )
    r = index if r is None and index is not None else r
    if r is not None and not return_index:
        return items[r].__dict__.get('label') if isinstance(items[r], ButtonsItem) else items[r]
    return r
