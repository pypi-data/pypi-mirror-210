#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# kuri_pome
"""BlockFramework"""
import tkinter as tk
from tkinter import ttk
import dataclasses
from typing import Any

from .canvas import ResizingCanvas


PLACE_TARGET_OBJECTS: list[str] = []


def create_widget_class_list(
    now_list: list, class_name: str, base: str = "Widget"
) -> list:
    """Widgetを継承しているクラス一覧を取得する

    Args:
        now_list (list): 現在の取得しているクラス一覧
        class_name (str): 対象のクラス名
        base (str, optional): 親クラス名. Defaults to "Widget".

    Returns:
        list: _description_
    """
    for subclass in getattr(class_name, base).__subclasses__():
        if subclass.__subclasses__() != [] and subclass.__name__ not in now_list:
            now_list.append(subclass.__name__)
            now_list: list = create_widget_class_list(
                now_list, class_name, base=subclass.__name__
            )
        else:
            now_list.append(subclass.__name__)
    return now_list


PLACE_TARGET_OBJECTS += create_widget_class_list([], tk)
PLACE_TARGET_OBJECTS += create_widget_class_list([], ttk)
PLACE_TARGET_OBJECTS += [
    "ResizingCanvas",
    "BlockFrame",
    "BlockToplevel",
    "BlockCanvas",
    "BlockLabel",
    "BlockEntry",
    "BlockText",
    "BlockListbox",
    "BlockCheckbutton",
    "BlockRadiobutton",
    "BlockScale",
    "BlockMessage",
    "BlockSpinbox",
    "BlockScrollbar",
    "BlockButton",
    "BlockCombobox",
    "BlockTreeview",
    "BlockProgressbar",
    "BlockLabelframe",
    "BlockNotebook",
]
PLACE_TARGET_OBJECTS = list(set(PLACE_TARGET_OBJECTS))


# list(
#     set(
#         # subclassのsubclassをとりたいため。
#         # [cls.__name__ for cls in ttk.Widget.__subclasses__()]
#         ttk.__all__
#         + [cls.__name__ for cls in tk.Widget.__subclasses__()]
#         + ["ResizingCanvas", "BlockFrame"]
#     )
# )


class BlockFramework(tk.Tk):
    """WidgetをBlock形式で指定することで配置操作を行うためのFramework

    Args:
        tk (tk.Tk): tk.Tk
    """

    def __init__(
        self, max_col: int, max_row: int, width: int, height: int, is_debug=False
    ) -> None:
        """コンストラクタ

        Args:
            max_col (int): 分割を行う行数
            max_row (int): 分割を行う列数
            width (int): frameの横幅
            height (int): frameの縦幅
            is_debug (bool, optional): デバッグモードならTrue
        """

        super().__init__()
        self.max_col: int = max_col
        self.max_row: int = max_row
        self.width: int = width
        self.height: int = height
        self._name: str = "main"
        self.is_debug: bool = is_debug
        super().geometry(f"{width}x{height}")

    def _override_valiable(
        self, default_valiable: Any, attribute_name: str, class_object: Any
    ) -> Any:
        """値の上書きリターン

        クラスオブジェクトの属性をチェックして、属性が定義されている場合は、
        それをデフォルト値の代わりに返します。属性が定義されていない場合は、
        デフォルト値を返します。

        Args:
            default_valiable (Any): デフォルトの値
            attribute_name (str): チェックする属性名
            class_object (Any): クラスオブジェクト

        Returns:
            Any: デフォルト値またはクラスオブジェクトの属性
        """
        valiable: Any = default_valiable
        if hasattr(class_object, attribute_name):
            valiable = getattr(class_object, attribute_name)
        return valiable

    def _acquire_calc_place_info(
        self, frame_widget: Any
    ) -> tuple[int, int, int, int, float, float]:
        """FrameにWidgetを配置するための情報取得する。

        Args:
             frame_widget (Any): 定義している先の対象class object

        Returns:
            Tuple[int, int, int, int, float, float]: 列数、行数、幅、高さ、列サイズ、行サイズのタプル
        """
        col_num: int = self._override_valiable(self.max_col, "max_col", frame_widget)
        row_num: int = self._override_valiable(self.max_row, "max_row", frame_widget)
        width: int = self._override_valiable(self.width, "width", frame_widget)
        height: int = self._override_valiable(self.height, "height", frame_widget)
        col_size: float = width / col_num
        row_size: float = height / row_num
        return col_num, row_num, width, height, col_size, row_size

    def _calc_place_rel(
        self,
        width: int,
        height: int,
        col_size: int,
        row_size: int,
        col_start: int = 0,
        col_end: int = 1,
        row_start: int = 0,
        row_end: int = 1,
        pad_left: float = 0,
        pad_right: float = 0,
        pad_up: float = 0,
        pad_down: float = 0,
    ) -> tuple[float, float, float, float]:
        """指定された列や行、空白設定から、placeで指定するrelを計算する。

        Args:
            width (int): フレームの横幅
            height (int): フレームの縦幅
            col_size (int): 列サイズ
            row_size (int): 行サイズ
            col_start (int, optional): 列の開始位置. Defaults to 0.
            col_end (int, optional): 列の終了位置. Defaults to 1.
            row_start (int, optional): 行の開始位置. Defaults to 0.
            row_end (int, optional): 行の終了位置. Defaults to 1.
            pad_left (float, optional): 横幅の左側の空白割合. Defaults to 0.
            pad_right (float, optional): 横幅の右側の空白割合. Defaults to 0.
            pad_up (float, optional): 縦幅の上側の空白割合. Defaults to 0.
            pad_down (float, optional): 縦幅の下側の空白割合. Defaults to 0.

        Returns:
            dict: placeで指定する値
        """
        values: dict = {}
        # チェックをコメントアウト、paddingがlayout合計でのpaddingではないため
        # check
        # if pad_left + pad_right >= col_end - col_start:
        #     raise Exception(
        #         f"width_padding value error: {pad_left + pad_right} >= {col_end - col_start}"
        #     )
        # if pad_up + pad_down >= row_end - row_start:
        #     raise Exception(
        #         f"height_padding value error: {pad_up + pad_down} >= {row_end - row_start}"
        #     )

        # relx
        width_start: float = col_size * col_start
        width_end: float = col_size * col_end
        pad_left_size: float = col_size * pad_left
        pad_right_size: float = col_size * pad_right
        width_object_start: float = width_start + pad_left_size
        width_object_end: float = width_end - pad_right_size
        width_object_size: float = width_object_end - width_object_start
        values["relx"]: float = width_object_start / width
        values["relwidth"]: float = width_object_size / width
        # rely
        height_start: float = row_size * row_start
        height_end: float = row_size * row_end
        pad_up_size: float = row_size * pad_up
        pad_down_size: float = row_size * pad_down
        height_object_start: float = height_start + pad_up_size
        height_object_end: float = height_end - pad_down_size
        height_object_size: float = height_object_end - height_object_start
        values["rely"]: float = height_object_start / height
        values["relheight"]: float = height_object_size / height
        return values

    def _calc_place_rel_with_scroll(
        self,
        width: int,
        height: int,
        col_size: int,
        row_size: int,
        scroll_x_size: int,
        scroll_y_size: int,
        col_start: int = 0,
        col_end: int = 1,
        row_start: int = 0,
        row_end: int = 1,
        pad_left: float = 0,
        pad_right: float = 0,
        pad_up: float = 0,
        pad_down: float = 0,
    ) -> tuple[float, float, float, float]:
        """指定された列や行、空白設定から、placeで指定するrelを計算する。

        Args:
            width (int): フレームの横幅
            height (int): フレームの縦幅
            col_size (int): 列サイズ
            row_size (int): 行サイズ
            scroll_x_size (int): スクロールのxサイズ
            scroll_y_size (int): スクロールyサイズ
            col_start (int, optional): 列の開始位置. Defaults to 0.
            col_end (int, optional): 列の終了位置. Defaults to 1.
            row_start (int, optional): 行の開始位置. Defaults to 0.
            row_end (int, optional): 行の終了位置. Defaults to 1.
            pad_left (float, optional): 横幅の左側の空白割合. Defaults to 0.
            pad_right (float, optional): 横幅の右側の空白割合. Defaults to 0.
            pad_up (float, optional): 縦幅の上側の空白割合. Defaults to 0.
            pad_down (float, optional): 縦幅の下側の空白割合. Defaults to 0.

        Returns:
            dict: placeで指定する値
        """
        values: dict = {}
        scrollbar_x_values: dict = {}
        scrollbar_y_values: dict = {}
        # relx
        if scroll_x_size == 0:
            width_start: float = col_size * col_start
            width_end: float = col_size * col_end
            pad_left_size: float = col_size * pad_left
            pad_right_size: float = col_size * pad_right
            width_object_start: float = width_start + pad_left_size
            width_object_end: float = width_end - pad_right_size
            width_object_size: float = width_object_end - width_object_start
            values["relx"]: float = width_object_start / width
            values["relwidth"]: float = width_object_size / width
            scrollbar_x_values["relx"]: float = width_object_start / width
            scrollbar_x_values["relwidth"]: float = width_object_size / width
            scrollbar_y_values["relx"]: float = 0
            scrollbar_y_values["relwidth"]: float = 0
        else:
            width_start: float = col_size * col_start
            width_end: float = col_size * col_end
            pad_left_size: float = col_size * pad_left
            pad_right_size: float = col_size * pad_right
            width_object_start: float = width_start + pad_left_size
            width_object_end: float = width_end - pad_right_size - scroll_x_size
            width_object_size: float = width_object_end - width_object_start
            width_scroll_object_start: float = width_object_end
            width_scroll_object_size: float = scroll_x_size
            values["relx"]: float = width_object_start / width
            values["relwidth"]: float = width_object_size / width
            scrollbar_x_values["relx"]: float = width_object_start / width
            scrollbar_x_values["relwidth"]: float = width_object_size / width
            scrollbar_y_values["relx"]: float = width_scroll_object_start / width
            scrollbar_y_values["relwidth"]: float = width_scroll_object_size / width

        # rely
        if scroll_y_size == 0:
            height_start: float = row_size * row_start
            height_end: float = row_size * row_end
            pad_up_size: float = row_size * pad_up
            pad_down_size: float = row_size * pad_down
            height_object_start: float = height_start + pad_up_size
            height_object_end: float = height_end - pad_down_size
            height_object_size: float = height_object_end - height_object_start
            values["rely"]: float = height_object_start / height
            values["relheight"]: float = height_object_size / height
            scrollbar_x_values["rely"]: float = 0
            scrollbar_x_values["relheight"]: float = 0
            scrollbar_y_values["rely"]: float = height_object_start / height
            scrollbar_y_values["relheight"]: float = height_object_size / height
        else:
            height_start: float = row_size * row_start
            height_end: float = row_size * row_end
            pad_up_size: float = row_size * pad_up
            pad_down_size: float = row_size * pad_down
            height_object_start: float = height_start + pad_up_size
            height_object_end: float = height_end - pad_down_size - scroll_y_size
            height_object_size: float = height_object_end - height_object_start
            height_scroll_object_start: float = height_object_end
            height_scroll_object_size: float = scroll_y_size
            values["rely"]: float = height_object_start / height
            values["relheight"]: float = height_object_size / height
            scrollbar_x_values["rely"]: float = height_scroll_object_start / height
            scrollbar_x_values["relheight"]: float = height_scroll_object_size / height
            scrollbar_y_values["rely"]: float = height_object_start / height
            scrollbar_y_values["relheight"]: float = height_object_size / height
        return values, scrollbar_x_values, scrollbar_y_values

    def _place_widget(
        self,
        widget: Any,
        width: int,
        height: int,
        col_size: float,
        row_size: float,
    ) -> None:
        """Widgetを配置する

        Args:
            frame (Any): 配置先のフレーム
            value (Any): 配置対象のウィジェット
            width (int): 配置するフレームの横幅
            height (int): 配置するフレームの縦幅
            col_size (int): 列サイズ
            row_size (int): 行サイズ
            frame (BlockFrame): 配置するフレーム
        """
        # objcetが最初に置く対象のクラスなら終了
        if widget.__class__.__name__ not in PLACE_TARGET_OBJECTS:
            raise Exception(f"cannot place object error: {widget.__class__.__name__}")
        # layout属性を持っていないなら終了
        # Frameの下に直接配置しているものはここでreturn
        if not ("layout" in dir(widget)):
            return

        if hasattr(widget, "scrollbar"):
            x_size: int = 0
            y_size: int = 0
            if widget.scrollbar.x is not None:
                # x軸のスクロールバーがないということは、y軸つまり高さのサイズは調整しない
                y_size = widget.scrollbar.size
                widget.scrollbar.x.config(command=widget.xview)
                widget.config(xscrollcommand=widget.scrollbar.x.set)
            if widget.scrollbar.y is not None:
                # y軸のスクロールバーがないということは、x軸つまり幅のサイズは調整しない
                x_size = widget.scrollbar.size
                widget.scrollbar.y.config(command=widget.yview)
                widget.config(yscrollcommand=widget.scrollbar.y.set)

            (
                widget_values,
                scrollbar_x_values,
                scrollbar_y_values,
            ) = self._calc_place_rel_with_scroll(
                width,
                height,
                col_size,
                row_size,
                x_size,
                y_size,
                **dataclasses.asdict(widget.layout),
            )
            widget.place(widget_values)
            if widget.scrollbar.x is not None:
                widget.scrollbar.x.place(scrollbar_x_values)
            if widget.scrollbar.y is not None:
                widget.scrollbar.y.place(scrollbar_y_values)
        else:
            widget.place(
                self._calc_place_rel(
                    width,
                    height,
                    col_size,
                    row_size,
                    **dataclasses.asdict(widget.layout),
                )
            )

    def _place_frame_widget(self, frame) -> None:
        """Frame上のwidgetを全て配置する。

        Layout指定をしている全てのwidgetを配置する。
        この関数は、Frame配下に子Frameを考慮して、再起処理で実現している。

        Args:
            frame (Any): 配置する先のFrame. Defaults to None.
        """
        width: int
        height: int
        col_size: float
        row_size: float
        (
            _,
            _,
            width,
            height,
            col_size,
            row_size,
        ) = self._acquire_calc_place_info(frame)
        for name, widget in frame.children.items():
            if widget.__class__.__name__ == "Menu":
                # rootフレームの配下のBlockFrameのみが対象。Menu等は何もしない。
                continue
            elif widget.__class__.__name__ == "BlockFrame":
                # BlockFrameは作成時に配置するので配置処理は不要。
                # widgetを配置するため再起処理のみ実施
                if hasattr(widget, "layout"):
                    self._place_widget(widget, width, height, col_size, row_size)
                self.place_frame_widget(frame=widget)
            elif widget.__class__.__name__ == "Frame":
                # FrameはFrameの配置を実施。
                self._place_widget(widget, width, height, col_size, row_size)
                # Frameは配置後にサイズが判明するため、ここでサイズをセット
                widget.update_idletasks()
                widget.width = widget.winfo_width()
                widget.height = widget.winfo_height()
                # Frame内のWidgetを配置するための再起処理を実施。
                self.place_frame_widget(frame=widget)
            else:
                # 上記以外は、Widgetのみになるので配置処理を実施。
                self._place_widget(widget, width, height, col_size, row_size)
        # 最後にFrameを最前面に移動しておく。
        for _, widget in frame.children.items():
            if widget.__class__.__name__ in ("Frame", "BlockFrame"):
                widget.tkraise()

    def place_frame_widget(self, frame: Any = None) -> None:
        """Frame上のwidgetを全て配置する。

        Layout指定をしている全てのwidgetを配置する。
        この関数は、Frame配下に子Frameを考慮して、再起処理で実現している。

        Args:
            frame (Any, optional): 配置する先のFrame. Defaults to None.
        """
        frame: Any = self if frame is None else frame
        self._place_frame_widget(frame=frame)
        if self.is_debug:
            self._create_auxiliary_line(frame)

    def _write_auxiliary_line(self, frame: Any, widget: ResizingCanvas) -> None:
        """debug用に補助線を引く

        Args:
            frame (_type_):  Canvasを保持しているFrameまたは、その上位のFrame
            widget (ResizingCanvas): 補助線を引くcanvas
        """
        col_num: int
        row_num: int
        col_size: float
        row_size: float
        col_num, row_num, _, _, col_size, row_size = self._acquire_calc_place_info(
            frame
        )
        start_y: int = 0
        end_y: int = widget.height
        start_x: int = 0
        end_x: int = widget.width
        for index in range(0, col_num):
            x: int = int(index * col_size)
            widget.create_line(x, start_y, x, end_y)
        for index in range(0, row_num):
            y: int = int(index * row_size)
            widget.create_line(start_x, y, end_x, y)

    def _create_auxiliary_line(self, frame: Any) -> None:
        """補助線を作成する

        この関数は、Frame配下に子Frameを考慮して、再起処理で実現している。

        Args:
            frame (Any, optional): Canvasを保持しているFrameまたは、その上位のFrame. Defaults to None.
        """
        for name, widget in frame.children.items():
            if widget.__class__.__name__ == "ResizingCanvas":
                self._write_auxiliary_line(frame, widget)
            if widget.__class__.__name__ in ("Frame", "BlockFrame"):
                self._create_auxiliary_line(widget)

    def create_auxiliary_line(self, frame: Any = None, is_debug=None) -> None:
        """補助線を作成する

        この関数は、Frame配下に子Frameを考慮して、再起処理で実現している。

        Args:
            frame (Any, optional): Canvasを保持しているFrameまたは、その上位のFrame. Defaults to None.
        """
        frame: Any = self if frame is None else frame
        for name, widget in frame.children.items():
            if widget.__class__.__name__ == "ResizingCanvas":
                self._write_auxiliary_line(frame, widget)
            if widget.__class__.__name__ in ("Frame", "BlockFrame"):
                is_debug: bool = self.is_debug if is_debug is None else is_debug
                if is_debug:
                    self._create_auxiliary_line(widget)
