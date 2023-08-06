#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# kuri_pome
"""BlockFrame"""
from typing import Any
import tkinter as tk
from tkinter import ttk


class BlockFrame(ttk.Frame):
    """BlockFrameworkで操作するための土台となるクラス"""

    def __init__(self, root: Any, **kwargs) -> None:
        """コンストラクタ

        Args:
            root (Any): このフレームを配置する先の親フレーム
        """
        super().__init__(root, **kwargs)


class BlockToplevel(tk.Toplevel):
    """tk.Toplevel"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BlockCanvas(tk.Canvas):
    """tk.Canvas"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockLabel(ttk.Label):
    """tk.Label"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockEntry(tk.Entry):
    """tk.Entry"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockText(tk.Text):
    """tk.Text"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockListbox(tk.Listbox):
    """tk.Listbox"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockCheckbutton(tk.Checkbutton):
    """tk.Checkbutton"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockRadiobutton(tk.Radiobutton):
    """Radiobutton"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockScale(tk.Scale):
    """tk.Scale"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockMessage(tk.Message):
    """tk.Message"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockSpinbox(tk.Spinbox):
    """tk.Spinbox"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockScrollbar(tk.Scrollbar):
    """tk.Scrollbar"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockButton(ttk.Button):
    """ttk.Button"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockCombobox(ttk.Combobox):
    """ttk.Combobox"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockTreeview(ttk.Treeview):
    """ttk.Treeview"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockProgressbar(ttk.Progressbar):
    """ttk.Progressbar"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockLabelframe(ttk.Labelframe):
    """ttk.Labelframe"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)


class BlockNotebook(ttk.Notebook):
    """tkt.Notebook"""

    def __init__(self, frame, *args, **kwargs):
        super().__init__(frame, *args, **kwargs)
