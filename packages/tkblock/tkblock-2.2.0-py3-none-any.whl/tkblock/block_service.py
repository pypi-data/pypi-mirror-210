#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# kuri_pome
"""BlockService

このクラスを使用することでblock指定でwidgetを配置することができる。
"""
import time
import threading
from typing import Any
from functools import wraps, partial

from .canvas import ResizingCanvas
from .block_framebase import *
from .layout import Layout
from .scrollbar import Scrollbar
from .block_framework import BlockFramework


def wait_processe(frame):
    """処理の完了を待つ。その間、待機描画処理を行う。

    Arguments:
        args (tuple): 位置引数
        kwargs (dict): キーワード引数 (名前で指定する引数)
    """

    def _create_wait_toplevel(frame, is_exit):
        toplevel = BlockService.create_toplevel(
            frame, "wait", 300, 300, is_focus=True, is_grab=True
        )
        frame: BlockFrame = BlockService.create_frame(
            "wait_toplevel",
            col=10,
            row=10,
            root=toplevel,
        )
        label = BlockService.create_label(frame, 1, 9, 1, 9, text="")
        BlockService.place_frame_widget(frame=toplevel)
        toplevel.update_idletasks()
        # toplevel.wait_window(toplevel)

        while True:
            if is_exit[0]:
                break
            label.config(text="実行中です。(ぐるぐる描画にしたい。)")
            time.sleep(0.5)
            label.config(text="少々お待ちを。(ぐるぐる描画にしたい。)")
            time.sleep(0.5)
            toplevel.update_idletasks()

        toplevel.destroy()

    def wrapper(func):
        @wraps(func)
        def wait_processe(*args, **kwargs):
            is_exit = [False]
            result = [None]

            def _execute(result, func, *args, **kwargs):
                result[0] = func(*args, **kwargs)
                is_exit[0] = True

            wait_thread = threading.Thread(
                target=partial(_create_wait_toplevel, frame, is_exit)
            )
            main_thread = threading.Thread(
                target=partial(_execute, result, func, *args, **kwargs)
            )
            wait_thread.start()
            time.sleep(0.5)
            main_thread.start()
            return result[0]

        return wait_processe

    return wrapper


class BlockService:
    """BlockFrameworkを操作するためのクラス"""

    root = None

    @classmethod
    def init(
        cls,
        title: str,
        max_col: int,
        max_row: int,
        width: int,
        height: int,
        is_debug=False,
    ) -> BlockFramework:
        """コンストラクタ

        Args:
            title (str): rootのタイトル名
            max_col (int): defaultとなる分割する列数
            max_row (int): defaultとなる分割する行数
            width (int): フレームの横幅
            height (int): フレームの縦幅
            is_debug (bool, optional): デバッグモードならTrue

        Returns:
            BlockFramework: 大本のrootとなるFrameを継承したクラスのインスタンス
        """
        cls.root: BlockFramework = BlockFramework(
            max_col, max_row, width, height, is_debug=is_debug
        )
        cls.root.grid_rowconfigure(0, weight=1)
        cls.root.grid_columnconfigure(0, weight=1)
        cls.root.title(title)
        return cls.root

    @classmethod
    def place_frame_widget(cls, frame=None, is_debug=False) -> None:
        """root配下のwidgetを配置する"""
        frame = cls.root if frame is None else frame
        cls.root.place_frame_widget(frame=frame)

    @classmethod
    def create_auxiliary_line(cls, is_debug=None, frame=None) -> None:
        """debug用に補助線を作成する関数

        補助線を引かない場合はこの関数をcallしないこと
        """
        frame = cls.root if frame is None else frame
        cls.root.create_auxiliary_line(is_debug=is_debug, frame=frame)

    @classmethod
    def create_frame(
        cls,
        frame_name: str,
        col: int = None,
        row: int = None,
        width: int = None,
        height: int = None,
        root: Any = None,
    ) -> BlockFrame:
        """BlockFrameとデバッグ用のキャンバスを生成する。

        Args:
            frame_name (str): 生成するフレームの名称
            col (int, optional): 生成するフレームの分割行.大本のフレームの分割数と一致させる場合は指定しない. Defaults to None.
            row (int, optional): 生成するフレームの分割行.大本のフレームの分割数と一致させる場合は指定しない. Defaults to None.
            width (int, optional): 生成するフレームの横幅.大本のフレームの横幅と一致させる場合は指定しない. Defaults to None.
            height (int, optional): 生成するフレームの縦幅.大本のフレームの縦幅と一致させる場合は指定しない. Defaults to None.
            root (Any, optional): 大本のフレーム. Defaults to None.

        Returns:
            BlockFrame: BaseとなるFrame
        """
        if root is None:
            root: BlockFramework = cls.root
        frame: BlockFrame = BlockFrame(
            root, name=f"{root._name}-BlockFrame_{frame_name}"
        )
        # grid(row=0, column=0, sticky="nsew")だとtoplevelのとき上手くいかないのでplaceにする
        frame.place(relx=0, rely=0, relheight=1, relwidth=1)
        # BlockFrameを配置する先がBlockFrame以外の場合は各情報がないので、rootを取得
        # Frameの場合はplace_frame_widgetが動いた後に、widthとheightが決まる。
        Inheritance_root: Any = root
        if root.__class__.__name__ != "BlockFrame":
            Inheritance_root = cls.root
        if col is None:
            col: int = Inheritance_root.max_col
        if row is None:
            row: int = Inheritance_root.max_row
        if width is None:
            width: int = Inheritance_root.width
        if height is None:
            height: int = Inheritance_root.height
        frame.max_col = col
        frame.max_row = row
        frame.width = width
        frame.height = height
        canvas: ResizingCanvas = ResizingCanvas(
            frame, name=f"{root._name}-canvas_{frame_name}"
        )
        canvas.layout = cls.layout(0, col, 0, row)
        return frame

    @classmethod
    def layout(
        cls,
        col_start: int,
        col_end: int,
        row_start: int,
        row_end: int,
        # 行列のセル内のオブジェクトの余白指定設定0～1
        pad_left: float = 0.0,
        pad_right: float = 0.0,
        pad_up: float = 0.0,
        pad_down: float = 0.0,
    ) -> Layout:
        """指定する座標情報

        Args:
            col_start (int): 列の開始位置、つまり、横の開始位置。つまり左座標。配置する座標(左を0起点)。
            col_end (int): 列の終了位置、つまり、横の終了位置。つまり右座標。配置する座標(左を0起点)。
            row_start (int): 行の開始位置、つまり、縦の開始位置。つまり上座標。配置する座標(上を0起点)。
            row_end (int): 行の終了位置、つまり、縦の終了位置。つまり下座標。配置する座標(上を0起点)。
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            Layout: BlockFrameworkのwidgetを配置するための位置情報
        """
        return Layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )

    @classmethod
    def scrollbar(
        cls, frame, x_enable: bool = False, y_enable: bool = False, size: int = None
    ) -> Scrollbar:
        """Widgetにスクロールバーをを付与する

        Args:
            x_enable (Any, optional): 横のスクロールバーを付与するかどうか.Trueで付与する. Defaults to False.
            y_enable (Any, optional): 縦のスクロールバーを付与するかどうか.Trueで付与する. Defaults to False.
            size (int, optional): スクロールバーのサイズ. Defaults to None.

        Returns:
            Scrollbar: Scrollbar
        """
        x = None
        if x_enable:
            x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        y = None
        if y_enable:
            y = tk.Scrollbar(frame, orient=tk.VERTICAL)
        if size is None:
            return Scrollbar(x, y)
        else:
            return Scrollbar(x, y, size=size)

    @classmethod
    def create_toplevel(cls, frame, title, width, height, is_focus=True, is_grab=False):
        """BlockToplevelとデバッグ用のキャンバスを生成する。

        Args:
            frame (Any): 親フレーム
            title (str): タイトル
            width (int): 横幅
            height (int): 縦幅
            is_focus (bool, optional): 最全面にするかどうか. Defaults to True.
            is_grab (bool, optional): モーダルにするかどうか. Defaults to False.

        Returns:
            BlockToplevel: toplevel
        """
        toplevel = BlockToplevel(frame)
        toplevel.title(title)
        toplevel.geometry(f"{width}x{height}")
        toplevel.width = width
        toplevel.hegith = height
        if is_focus:
            toplevel.focus_set()
        if is_grab:
            toplevel.grab_set()  # モーダルにする
        # dialog.transient(self.root)  # タスクバーに表示しない

        return toplevel

    @classmethod
    def create_canvas(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockCanvasを作成する

        例
        cavas1 = BlockService.create_canvas(self.frame, 42, 49, 15, 20)
        cavas1.create_line(0, 0, 430, 300)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockCanvas: BlockCanvas
        """
        canvas = BlockCanvas(frame, *args, **kwargs)
        canvas.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return canvas

    @classmethod
    def create_label(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockLabelを作成する

        例
        BlockService.create_label(self.frame, 0, 1, 0, 1, text="left_pad", anchor=tk.CENTER)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockLabel: BlockLabel
        """
        label = BlockLabel(frame, *args, **kwargs)
        label.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return label

    @classmethod
    def create_entry(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        init_value="",
        **kwargs,
    ):
        """BlockEntryを作成する

        textvariableというオプション引数にtk.StringVarをセットすることも可能。

        例
        entry, _ = BlockService.create_entry(self.frame, 4, 9, 0, 2, name="entry", width=20)
        entry.insert(tk.END, "test")

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.
            init_value (str, optional): 初期値. Defaults to "".

        Returns:
            BlockEntry: BlockEntry
            tk.StringVar: string_var
        """
        if "textvariable" in kwargs:
            string_var = kwargs["textvariable"]
        else:
            string_var = tk.StringVar(value=init_value)
            kwargs["textvariable"] = string_var
        entry = BlockEntry(frame, *args, **kwargs)
        entry.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return entry, string_var

    @classmethod
    def create_text(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockTextを作成する

        例
        def echo_text(_):
            print(text1.get("1.0", "end - 1c"))

        text1 = BlockService.create_text(
            self.frame, 30, 40, 15, 20, name="text1", wrap="none"
        )
        text1.scrollbar = BlockService.scrollbar(
            self.frame, x_enable=True, y_enable=True
        )
        text1.insert(tk.END, "hoge\nfuga")
        BlockService.create_button(self.frame, 30, 40, 20, 21, function=echo_text)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockText: BlockText
        """
        text = BlockText(frame, *args, **kwargs)
        text.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return text

    @classmethod
    def create_listbox(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        init_value="",
        **kwargs,
    ):
        """BlockListboxを作成する

        listvariableというオプション引数にtk.StringVarをセットすることも可能。

        例
        listbox, _ = BlockService.create_listbox(self.frame, 0, 5, 3, 10, init_value=("tkinter", "os", "datetime", "math"), name="listbox")
        listbox.insert(2, "hogehoge")

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.
            init_value (str, optional): 初期値. Defaults to "".

        Returns:
            BlockListbox: BlockListbox
            tk.StringVar: string_var
        """
        if "listvariable" in kwargs:
            string_var = kwargs["listvariable"]
        else:
            string_var = tk.StringVar(value=init_value)
            kwargs["listvariable"] = string_var
        listbox = BlockListbox(frame, *args, **kwargs)
        listbox.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )

        return listbox, string_var

    @classmethod
    def create_checkbutton(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        init_value=False,
        **kwargs,
    ):
        """BlockCheckbuttonを作成する

        textvariableというオプション引数にtk.IntVarをセットすることも可能。

        例
        def echo_checkbutton(_):
            print(checkbutton1_var.get())
            print(checkbutton2_var.get())

        _, checkbutton1_var = BlockService.create_checkbutton(
            self.frame,
            14,
            20,
            0,
            1,
            name="checkbutton1",
            text="checkbutton1",
            init_value=True,
        )
        _, checkbutton2_var = BlockService.create_checkbutton(
            self.frame,
            14,
            20,
            1,
            2,
            name="checkbutton2",
            text="checkbutton2",
            init_value=False,
        )
        BlockService.create_button(self.frame, 14, 20, 2, 3, function=echo_checkbutton)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.
            init_value (bool, optional): チェックなし. Defaults to False.

        Returns:
            BlockCheckbutton: BlockCheckbutton
            tk.BooleanVar: bool_var
        """
        if "variable" in kwargs:
            bool_var = kwargs["variable"]
        else:
            bool_var = tk.BooleanVar(value=init_value)
            kwargs["variable"] = bool_var
        checkbutton = BlockCheckbutton(frame, *args, **kwargs)
        checkbutton.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return checkbutton, bool_var

    @classmethod
    def create_radiobutton(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        init_value=0,
        **kwargs,
    ):
        """BlockRadiobuttonを作成する

        textvariableというオプション引数にtk.IntVarをセットすることも可能。

        例
        _, radiobutton_var = BlockService.create_radiobutton(self.frame, 6, 15, 5, 7, init_value=0, name="radiobutton1_1", text="radiobutton1_1", value=10)
        _, _ = BlockService.create_radiobutton(self.frame, 6, 15, 7, 10, name="radiobutton1_2", text="radiobutton1_2", value=20, variable=radiobutton_var)
        BlockService.create_label(self.frame, 6, 15, 3, 5, name="radiobutton1_label", textvariable=radiobutton_var)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockRadiobutton: BlockRadiobutton
            tk.IntVar: int_var
        """
        if "variable" in kwargs:
            int_var = kwargs["variable"]
        else:
            int_var = tk.IntVar(value=init_value)
            kwargs["variable"] = int_var
        radiobutton = BlockRadiobutton(frame, *args, **kwargs)
        radiobutton.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return radiobutton, int_var

    @classmethod
    def create_scale(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        init_value="",
        **kwargs,
    ):
        """BlockScaleを作成する

        varというオプション引数にtk.StringVarをセットすることも可能。

        例
        _, scale_var = BlockService.create_scale(self.frame, 16, 20, 5, 10, init_value="", name="scale1")
        BlockService.create_label(self.frame, 16, 20, 3, 5, name="scale_label", textvariable=scale_var)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.
            init_value (str, optional): 初期値. Defaults to "".

        Returns:
            BlockScale: BlockScale
            tk.StringVar: string_var
        """
        if "var" in kwargs:
            string_var = kwargs["var"]
        else:
            string_var = tk.StringVar(value=init_value)
            kwargs["var"] = string_var
        scale = BlockScale(frame, *args, **kwargs)
        scale.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return scale, string_var

    @classmethod
    def create_message(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockMessageを作成する

        例
        BlockService.create_message(self.frame, 21, 24, 0, 10, name="message1", text="Messageの自動改行テスト", relief="raised")

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockMessage: BlockMessage
        """
        message = BlockMessage(frame, *args, **kwargs)
        message.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return message

    @classmethod
    def create_spinbox(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        init_value=0,
        **kwargs,
    ):
        """BlockSpinboxを作成する

        textvariableというオプション引数にtk.IntVarをセットすることも可能。

        例
        _, spinbox1_var = BlockService.create_spinbox(self.frame, 16, 25, 21, 23, init_value=0, from_=-10, to=10, increment=1)
        _ = BlockService.create_label(self.frame, 16, 25, 23, 25, textvariable=spinbox1_var)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockSpinbox: BlockSpinbox
            tk.IntVar: int_var
        """
        if "textvariable" in kwargs:
            int_var = kwargs["textvariable"]
        else:
            int_var = tk.IntVar(value=init_value)
            kwargs["textvariable"] = int_var
        spinbox = BlockSpinbox(frame, *args, **kwargs)
        spinbox.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return spinbox, int_var

    @classmethod
    def create_scrollbar(cls, frame, *args, layout=None, **kwargs):
        """BlockScrollbarを作成する（非推奨）

        BlockService.scrollbarの戻り地をwidget.scrollbarに指定することで自動で作成されるので、そちらを推奨

        例
        scrollbar1_listbox, _ = BlockService.create_listbox(self.frame, 30, 40, 0, 10, init_value=tuple([str(x) for x in range(0, 100)]), name="scrollbar1_listbox")
        layout = BlockService.layout(40, 41, 0, 10)
        scrollbar1 = BlockService.create_scrollbar(self.frame, layout=layout, orient=tk.VERTICAL)
        scrollbar1.config(command=scrollbar1_listbox.yview)
        scrollbar1_listbox.config(yscrollcommand=scrollbar1.set)

        Args:
            frame (Any): 親フレーム
            layout (BlockLayout, optional): セットする位置. Defaults to None.

        Returns:
            BlockScrollbar: BlockScrollbar
        """
        scrollbar = BlockScrollbar(frame, *args, **kwargs)
        if layout is not None:
            scrollbar.layout = layout
        return scrollbar

    @classmethod
    def create_button(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        function=None,
        **kwargs,
    ):
        """BlockButtonを作成する

        例1
        def _button_config(event) -> None:
            logger.debug(event.widget["text"])

        BlockService.create_button(self.frame, 10, 13, 0, 2, name="button1", text="button", function=_button_config)

        例2
        import functools
        def _create_splited_file(self, button_layout):
            toplevel_split_file = ToplevelSplitFile()

        BlockService.create_button(self.frame, *button_layout, text="ファイル分割", command=functools.partial(toplevel_split_file.create, self.frame))

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.
            function (None, function): ボタン押下のbindする関数. Defaults to None.

        Returns:
            BlockButton: BlockButton
        """
        button = BlockButton(frame, *args, **kwargs)
        button.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        if function is not None:
            button.bind("<Button-1>", function)
        return button

    @classmethod
    def create_combobox(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        init_value="",
        function=None,
        **kwargs,
    ):
        """BlockComboboxを作成する

        textvariableというオプション引数にtk.StringVarをセットすることも可能。

        例
        BlockService.create_combobox(self.frame, 0, 5, 11, 15, name="combobox1", values=["Easy", "Normal", "Hard"])

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.
            init_value (str, optional): 初期値. Defaults to "".
            function (None, function): 押下のbindする関数. Defaults to None.

        Returns:
            BlockCombobox: BlockCombobox
            tk.StringVar: string_var
        """
        if "textvariable" in kwargs:
            string_var = kwargs["textvariable"]
        else:
            string_var = tk.StringVar(value=init_value)
            kwargs["textvariable"] = string_var
        combobox = BlockCombobox(frame, *args, **kwargs)
        combobox.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        if function is not None:
            combobox.bind("<<ComboboxSelected>>", function)
        return combobox, string_var

    @classmethod
    def create_treeview(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockTreeviewを作成する

        例
        treeview1 = BlockService.create_treeview(self.frame, 6, 15, 11, 20, name="treeview1")
        treeview1_parent = treeview1.insert("", "end", text="parent")  # 親要素の挿入
        treeview1_child = treeview1.insert(treeview1_parent, "end", text="child")  # 子要素の挿入

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockTreeview: BlockTreeview
        """
        treeview = BlockTreeview(frame, *args, **kwargs)
        treeview.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return treeview

    @classmethod
    def create_progressbar(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockProgressbarを作成する

        例
        progressbar1 = BlockService.create_progressbar(self.frame, 16, 24, 11, 12, mode="indeterminate")
        def timer():
            progressbar1.start(5)  # プログレスバー開始
            for i in range(6):
                time.sleep(1)  # 1秒待機
                progressbar1_button["text"] = i  # 秒数表示
            progressbar1.stop()  # プログレスバー停止

        def button_clicked():
            t = threading.Thread(target=timer)  # スレッド立ち上げ
            t.start()  # スレッド開始

        progressbar1_button = BlockService.create_button(self.frame, 16, 24, 13, 20, text="start", command=button_clicked)

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockProgressbar: BlockProgressbar
        """
        progressbar = BlockProgressbar(frame, *args, **kwargs)
        progressbar.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return progressbar

    @classmethod
    def create_labelframe(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockLabelframeを作成する

        例
        labelframe1 = BlockService.create_labelframe(self.frame, 10, 15, 21, 25, relief="ridge", text="Labelframe", labelanchor="n")
        labelframe1_label = tk.Label(
            labelframe1, relief="groove", width=15, text="frame test"
        )
        labelframe1_label.pack()
        labelframe1_entry = tk.Entry(labelframe1, width=15)
        labelframe1_entry.pack()

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockLabelframe: BlockLabelframe
        """
        labelframe = BlockLabelframe(frame, *args, **kwargs)
        labelframe.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return labelframe

    @classmethod
    def create_notebook(
        cls,
        frame,
        col_start,
        col_end,
        row_start,
        row_end,
        *args,
        pad_left=0.0,
        pad_right=0.0,
        pad_up=0.0,
        pad_down=0.0,
        **kwargs,
    ):
        """BlockNotebookを作成する

        例
        notebook1 = BlockService.create_notebook(self.frame, 0, 9, 21, 25)
        notebook1_frame1 = tk.Frame(self.frame)
        notebook1_frame2 = tk.Frame(self.frame)
        notebook1_frame3 = tk.Frame(self.frame)
        notebook1.add(notebook1_frame1, text="fram1")
        notebook1.add(notebook1_frame2, text="fram2")

        Args:
            frame (Any): 親フレーム
            col_start (int): 列の開始位置
            col_end (int): 列の終了位置
            row_start (int): 行の開始位置
            row_end (int): 行の終了位置
            pad_left (float, optional): 横幅の左側の隙間(0~1). Defaults to 0.0.
            pad_right (float, optional): 横幅の右側の隙間(0~1). Defaults to 0.0.
            pad_up (float, optional): 立幅の上側の隙間(0~1). Defaults to 0.0.
            pad_down (float, optional): 立幅の下側の隙間(0~1). Defaults to 0.0.

        Returns:
            BlockNotebook: BlockNotebook
        """
        notebook = BlockNotebook(frame, *args, **kwargs)
        notebook.layout = cls.layout(
            col_start,
            col_end,
            row_start,
            row_end,
            pad_left=pad_left,
            pad_right=pad_right,
            pad_up=pad_up,
            pad_down=pad_down,
        )
        return notebook
