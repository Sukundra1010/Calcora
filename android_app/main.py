from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from calculator_core import calculate


BACKGROUND = (0.01, 0.04, 0.13, 1)
PANEL = (0.02, 0.08, 0.19, 1)
NUMBER_BUTTON = (0.06, 0.13, 0.25, 1)
OPERATOR_BUTTON = (0.03, 0.32, 0.48, 1)
SELECTED_BUTTON = (0.05, 0.76, 0.88, 1)
CYAN = (0.07, 0.91, 1, 1)
WHITE = (0.84, 0.93, 1, 1)


def format_number(number):
    return format(number, ".12g")


class CalculatorScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(18), spacing=dp(12), **kwargs)
        self.current = "0"
        self.first_number = None
        self.operator = None
        self.start_new_number = False
        self.operator_buttons = {}

        with self.canvas.before:
            Color(*PANEL)
            self.panel = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(26)],
            )
        self.bind(pos=self.update_panel, size=self.update_panel)

        self.expression_label = Label(
            text="",
            color=WHITE,
            font_size=dp(18),
            halign="right",
            valign="bottom",
            size_hint_y=None,
            height=dp(30),
        )
        self.expression_label.bind(size=self._fit_label)
        self.add_widget(self.expression_label)

        self.display_label = Label(
            text=self.current,
            color=CYAN,
            font_size=dp(48),
            halign="right",
            valign="middle",
            size_hint_y=None,
            height=dp(92),
            shorten=True,
            shorten_from="left",
        )
        self.display_label.bind(size=self._fit_label)
        self.add_widget(self.display_label)

        keypad = BoxLayout(
            orientation="vertical",
            spacing=dp(9),
            size_hint_y=1,
        )
        rows = [
            [
                ("AC", "clear", "special"),
                ("+/-", "sign", "special"),
                ("%", "percent", "special"),
                ("÷", "operator:/", "operator"),
            ],
            [
                ("7", "digit:7", "number"),
                ("8", "digit:8", "number"),
                ("9", "digit:9", "number"),
                ("×", "operator:*", "operator"),
            ],
            [
                ("4", "digit:4", "number"),
                ("5", "digit:5", "number"),
                ("6", "digit:6", "number"),
                ("−", "operator:-", "operator"),
            ],
            [
                ("1", "digit:1", "number"),
                ("2", "digit:2", "number"),
                ("3", "digit:3", "number"),
                ("+", "operator:+", "operator"),
            ],
            [
                ("0", "digit:0", "number"),
                (".", "decimal", "number"),
                ("=", "equals", "equals"),
            ],
        ]

        for row_index, keys in enumerate(rows):
            row = BoxLayout(
                orientation="horizontal",
                spacing=dp(9),
                size_hint_y=None,
                height=dp(58),
            )
            for text, action, style in keys:
                button = Button(
                    text=text,
                    font_size=dp(25),
                    color=CYAN if style in ("operator", "special") else WHITE,
                    background_normal="",
                    background_down="",
                    background_color=self._button_color(style),
                    border=(dp(10), dp(10), dp(10), dp(10)),
                )
                if row_index == len(rows) - 1 and action == "digit:0":
                    button.size_hint_x = 2
                button.bind(on_release=lambda _button, a=action: self.press(a))
                if action.startswith("operator:"):
                    self.operator_buttons[action[-1]] = button
                row.add_widget(button)
            keypad.add_widget(row)

        self.add_widget(keypad)
        Window.clearcolor = BACKGROUND

    @staticmethod
    def _fit_label(label, size):
        label.text_size = size

    def update_panel(self, *_args):
        self.panel.pos = self.pos
        self.panel.size = self.size

    @staticmethod
    def _button_color(style):
        if style == "operator":
            return OPERATOR_BUTTON
        if style == "equals":
            return SELECTED_BUTTON
        if style == "special":
            return (0.04, 0.20, 0.32, 1)
        return NUMBER_BUTTON

    def update_display(self):
        self.display_label.text = self.current

        symbols = {"/": "÷", "*": "×", "-": "−", "+": "+"}
        if self.operator is not None and self.first_number is not None:
            self.expression_label.text = (
                f"{format_number(self.first_number)} {symbols[self.operator]}"
            )
        else:
            self.expression_label.text = ""

        for operator, button in self.operator_buttons.items():
            button.background_color = (
                SELECTED_BUTTON if operator == self.operator else OPERATOR_BUTTON
            )
            button.color = (
                BACKGROUND if operator == self.operator else CYAN
            )

    def press(self, action):
        try:
            float(self.current)
        except ValueError:
            if action != "clear":
                self.current = "0"
                self.first_number = None
                self.operator = None
                self.start_new_number = False

        if action.startswith("digit:"):
            digit = action[-1]
            if not self.start_new_number and len(self.current) >= 16:
                return
            if self.start_new_number or self.current == "0":
                self.current = digit
            else:
                self.current += digit
            self.start_new_number = False
        elif action == "decimal":
            if self.start_new_number:
                self.current = "0."
                self.start_new_number = False
            elif "." not in self.current and len(self.current) < 16:
                self.current += "."
        elif action.startswith("operator:"):
            self.choose_operator(action[-1])
        elif action == "equals":
            self.equals()
        elif action == "clear":
            self.current = "0"
            self.first_number = None
            self.operator = None
            self.start_new_number = False
        elif action in ("sign", "percent"):
            self.apply_unary(action)

        self.update_display()

    def choose_operator(self, operator):
        if self.operator is not None and not self.start_new_number:
            if not self.equals():
                return

        self.first_number = float(self.current)
        self.operator = operator
        self.start_new_number = True

    def equals(self):
        if self.operator is None or self.first_number is None:
            return True

        try:
            result = calculate(
                self.first_number,
                self.operator,
                float(self.current),
            )
        except ValueError as error:
            self.current = str(error)
            self.first_number = None
            self.operator = None
            self.start_new_number = True
            return False

        self.current = format_number(result)
        self.first_number = None
        self.operator = None
        self.start_new_number = True
        return True

    def apply_unary(self, operation):
        try:
            result = calculate(float(self.current), operation)
        except ValueError as error:
            self.current = str(error)
            self.first_number = None
            self.operator = None
            self.start_new_number = True
            return

        self.current = format_number(result)


class NeonCalculatorApp(App):
    title = "Neon Calculator"

    def build(self):
        self.root = CalculatorScreen()
        return self.root


if __name__ == "__main__":
    NeonCalculatorApp().run()
