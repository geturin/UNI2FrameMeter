"""Compact display switches and their shared frame-meter color legend."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
import tkinter as tk
from tkinter import ttk

from display_config import DisplayItem


class DisplayControls(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        items: Iterable[DisplayItem],
        colors: Mapping[str, str],
        toggle: Callable[[str], None],
        labels: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(master, padding=8)
        self.colors = colors
        self.variables: dict[str, tk.BooleanVar] = {}
        self.checkboxes: dict[str, ttk.Checkbutton] = {}
        self.swatches: dict[str, tk.Canvas] = {}
        self.swatch_items: dict[str, int] = {}
        for row, item in enumerate(items):
            variable = tk.BooleanVar(master=self, value=item.display)
            self.variables[item.token] = variable
            checkbox = ttk.Checkbutton(
                self,
                name=f"{item.token}_check",
                text=labels.get(item.token, item.token) if labels else item.token,
                variable=variable,
                command=lambda token=item.token: toggle(token),
            )
            if item.status != "confirmed":
                checkbox.state(["disabled"])
            self.checkboxes[item.token] = checkbox
            checkbox.grid(row=row, column=0, sticky="w", pady=1)
            swatch = tk.Canvas(
                self,
                name=f"{item.token}_color",
                width=16,
                height=16,
                borderwidth=0,
                highlightthickness=0,
                background=ttk.Style(self).lookup("TFrame", "background") or "#f0f0f0",
                takefocus=False,
            )
            swatch.grid(row=row, column=1, sticky="w", padx=(7, 0), pady=1)
            self.swatches[item.token] = swatch
            self.swatch_items[item.token] = swatch.create_rectangle(
                1, 1, 15, 15, outline="#808080", fill=""
            )
            self.refresh_swatch(item.token)
        self.status_variable = tk.StringVar(master=self, value="")
        self.status_label = ttk.Label(self, textvariable=self.status_variable)
        self.status_row = len(self.variables)
        self.column_count = 1
        # Measure the actual themed rows once. This also covers larger Windows
        # font/DPI settings, without continually moving controls during use.
        self.update_idletasks()
        if self.winfo_reqheight() > self.winfo_screenheight() - 120:
            self.column_count = 2
            self.status_row = (len(self.variables) + 1) // 2
            for index, token in enumerate(self.variables):
                group, row = divmod(index, self.status_row)
                self.checkboxes[token].grid_configure(
                    row=row, column=group * 2, padx=(16 if group else 0, 0)
                )
                self.swatches[token].grid_configure(row=row, column=group * 2 + 1)

    def refresh_swatch(self, token: str) -> None:
        checked = self.variables[token].get()
        enabled = not self.checkboxes[token].instate(["disabled"])
        self.swatches[token].itemconfigure(
            self.swatch_items[token],
            fill=self.colors[token] if checked and enabled else "",
        )

    def show_status(self, message: str) -> None:
        if self.status_variable.get() == message:
            return
        self.status_variable.set(message)
        if message:
            self.status_label.grid(
                row=self.status_row, column=0, columnspan=self.column_count * 2, sticky="w", pady=(6, 0)
            )
        else:
            self.status_label.grid_remove()
