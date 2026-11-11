import html
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from math import isfinite
from pathlib import Path
from urllib.parse import parse_qs


PROJECT_FOLDER = Path(__file__).parent
NUMBER_PATTERN = re.compile(r"-?(?:\d+(?:\.\d*)?|\.\d+)\Z")
OPERATORS = {"+", "-", "*", "/"}
OPERATOR_SYMBOLS = {"+": "+", "-": "−", "*": "×", "/": "÷"}


def calculate(first_number, operator, second_number=None):
    if operator == "sign":
        result = -first_number
    elif operator == "percent":
        result = first_number / 100
    elif operator == "+":
        result = first_number + second_number
    elif operator == "-":
        result = first_number - second_number
    elif operator == "*":
        result = first_number * second_number
    elif operator == "/":
        if second_number == 0:
            raise ValueError("Cannot divide by zero.")
        result = first_number / second_number
    else:
        raise ValueError("Unknown operation.")

    if not isfinite(result):
        raise ValueError("Result is too large.")
    return result


def read_number(value):
    if len(value) > 100 or not NUMBER_PATTERN.fullmatch(value):
        raise ValueError("Invalid calculator number.")
    number = float(value)
    if not isfinite(number):
        raise ValueError("Invalid calculator number.")
    return number


def format_number(number):
    return format(number, ".12g")


def update_calculator(state, action):
    message = ""

    if action == "clear":
        return {
            "current": "0",
            "first": "",
            "operator": "",
            "start_new": False,
        }, message

    current = read_number(state["current"])

    if action.startswith("digit:"):
        digit = action.removeprefix("digit:")
        if digit not in "0123456789" or len(digit) != 1:
            raise ValueError("Invalid button.")
        if state["start_new"] or state["current"] == "0":
            state["current"] = digit
        else:
            state["current"] += digit
        state["start_new"] = False
    elif action == "decimal":
        if state["start_new"]:
            state["current"] = "0."
            state["start_new"] = False
        elif "." not in state["current"]:
            state["current"] += "."
    elif action.startswith("operator:"):
        new_operator = action.removeprefix("operator:")
        if new_operator not in OPERATORS:
            raise ValueError("Unknown operation.")

        if state["operator"] and not state["start_new"]:
            state["current"] = format_number(
                calculate(
                    read_number(state["first"]),
                    state["operator"],
                    current,
                )
            )
        state["first"] = state["current"]
        state["operator"] = new_operator
        state["start_new"] = True
    elif action == "equals":
        if state["operator"] and state["first"]:
            result = calculate(
                read_number(state["first"]),
                state["operator"],
                current,
            )
            state["current"] = format_number(result)
            state["first"] = ""
            state["operator"] = ""
            state["start_new"] = True
    elif action in ("sign", "percent"):
        result = calculate(current, action)
        state["current"] = format_number(result)
    else:
        raise ValueError("Unknown button.")

    return state, message


class CalculatorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_FOLDER), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_page(
                {
                    "current": "0",
                    "first": "",
                    "operator": "",
                    "start_new": False,
                }
            )
            return
        super().do_GET()

    def do_POST(self):
        if self.path != "/":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 0:
                raise ValueError("Invalid request.")
            if content_length > 4096:
                self.send_error(413, "Request is too large.")
                return

            form = parse_qs(
                self.rfile.read(content_length).decode("utf-8"),
                keep_blank_values=True,
                max_num_fields=10,
            )
            state = self.read_state(form)
            action = form.get("action", [""])[0]
            state, message = update_calculator(state, action)
        except (ValueError, UnicodeDecodeError) as error:
            state = {
                "current": "0",
                "first": "",
                "operator": "",
                "start_new": False,
            }
            message = str(error)

        self.send_page(state, message)

    @staticmethod
    def read_state(form):
        current = form.get("current", ["0"])[0]
        read_number(current)

        first = form.get("first", [""])[0]
        if first:
            read_number(first)

        operator = form.get("operator", [""])[0]
        if operator and operator not in OPERATORS:
            raise ValueError("Invalid calculator operation.")

        return {
            "current": current,
            "first": first,
            "operator": operator,
            "start_new": form.get("start_new", ["0"])[0] == "1",
        }

    def send_page(self, state, message=""):
        template = (PROJECT_FOLDER / "index.html").read_text(encoding="utf-8")
        expression = ""
        if state["operator"] and state["first"]:
            expression = (
                f'{state["first"]} '
                f'{OPERATOR_SYMBOLS[state["operator"]]}'
            )

        replacements = {
            "{{CURRENT_STATE}}": state["current"],
            "{{FIRST_STATE}}": state["first"],
            "{{OPERATOR_STATE}}": state["operator"],
            "{{START_NEW_STATE}}": "1" if state["start_new"] else "0",
            "{{EXPRESSION}}": expression,
            "{{DISPLAY}}": message or state["current"],
            "{{DIVIDE_SELECTED}}": (
                "is-selected" if state["operator"] == "/" else ""
            ),
            "{{MULTIPLY_SELECTED}}": (
                "is-selected" if state["operator"] == "*" else ""
            ),
            "{{SUBTRACT_SELECTED}}": (
                "is-selected" if state["operator"] == "-" else ""
            ),
            "{{ADD_SELECTED}}": (
                "is-selected" if state["operator"] == "+" else ""
            ),
        }
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, html.escape(value))

        response = template.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), CalculatorHandler)
    server.daemon_threads = True
    print(f"Calculator website is running on {host}:{port}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCalculator server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
