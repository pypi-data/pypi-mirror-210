#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# kuri_pome
"""Layout"""
import dataclasses


@dataclasses.dataclass(frozen=True)
class Layout:
    """BlockFrameworkのwidgetの配置情報"""

    # フレームの行列の番号0~*
    col_start: int
    col_end: int
    row_start: int
    row_end: int
    # 行列のセル内のオブジェクトの余白指定設定0～1
    pad_left: float = 0
    pad_right: float = 0
    pad_up: float = 0
    pad_down: float = 0
