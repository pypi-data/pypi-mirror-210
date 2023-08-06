#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# kuri_pome
"""Scrollbar"""
import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class Scrollbar:
    """Widgetへ付属するScrollbarの情報"""

    x: Any
    y: Any
    # スクロールバーのデフォルトのサイズは17がしっくりくる。
    size: int = 17
