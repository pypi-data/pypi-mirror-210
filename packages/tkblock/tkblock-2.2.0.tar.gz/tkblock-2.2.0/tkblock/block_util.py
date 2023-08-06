#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# kuri_pome
"""main"""
import tkinter as tk


def change_frame(frame: tk.Frame) -> None:
    def _change_frame(frame) -> None:
        for _, widget in frame.children.items():
            if widget.__class__.__name__ in ("Frame", "BlockFrame"):
                widget.tkraise()
                _change_frame(widget)

    frame.tkraise()
    _change_frame(frame)
