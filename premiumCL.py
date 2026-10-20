import ast
import math
import tkinter as tk
from datetime import datetime

BG = "#090B16"
CARD = "#111629"
DISPLAY = "#0D1222"
KEY = "#1A2137"
HOVER = "#2A3452"
PURPLE = "#9270FF"
CYAN = "#55E6E0"
TEXT = "#F4F5FF"
MUTED = "#929BB8"
DANGER = "#49223A"
PINK = "#FF8EC7"
GREEN = "#72F1B8"


def calculate(expression):
    expression = expression.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
    tree = ast.parse(expression, mode="eval")

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.UnaryOp):
            n = walk(node.operand)
            if isinstance(node.op, ast.UAdd):
                return n
            if isinstance(node.op, ast.USub):
                return -n
        if isinstance(node, ast.BinOp):
            a, b = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Add): result = a + b
            elif isinstance(node.op, ast.Sub): result = a - b
            elif isinstance(node.op, ast.Mult): result = a * b
            elif isinstance(node.op, ast.Div): result = a / b
            elif isinstance(node.op, ast.Mod): result = a % b
            elif isinstance(node.op, ast.Pow):
                if abs(b) > 100: raise ValueError("Exponent is too large")
                result = a ** b
            else: raise ValueError("Unsupported operation")
            if isinstance(result, complex) or (isinstance(result, float) and not math.isfinite(result)):
                raise ValueError("Result is not a real number")
            if abs(result) > 1e100: raise ValueError("Result is too large")
            return result
        raise ValueError("Invalid expression")

    return walk(tree)


def fmt(value):
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError("Invalid result")
        if value.is_integer() and abs(value) < 1e16: return str(int(value))
        return f"{value:.10g}"
    return str(value)


class AuraCalculator:
    def __init__(self, root):
        self.root = root
        root.title("AURA • Premium Calculator")
        root.geometry("460x760")
        root.minsize(320, 520)
        root.configure(bg=BG)
        self.expression = ""
        self.last_result = False
        self.history = []
        self._build()
        root.bind("<Key>", self.on_key)
        root.bind("<Escape>", lambda e: self.clear())
        root.bind("<Control-h>", lambda e: self.show_history())
        root.bind("<Configure>", self.resize)
        self.update_display()

    def _build(self):
        self.outer = tk.Frame(self.root, bg=BG, padx=16, pady=14)
        self.outer.pack(fill="both", expand=True)

        header = tk.Frame(self.outer, bg=BG)
        header.pack(fill="x", pady=(0, 14))
        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left")
        tk.Label(brand, text="✦ AURA", bg=BG, fg=CYAN,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(brand, text="SMART  •  SIMPLE  •  BEAUTIFUL", bg=BG, fg=MUTED,
                 font=("Segoe UI", 7, "bold")).pack(anchor="w")

        self.button(header, "◷ HISTORY", self.show_history, KEY, CYAN,
                    ("Segoe UI", 9, "bold")).pack(side="right", ipady=5)

        panel = tk.Frame(self.outer, bg=DISPLAY, highlightthickness=1,
                         highlightbackground="#35345F")
        panel.pack(fill="x", pady=(0, 13))
        tk.Label(panel, text="CURRENT EXPRESSION", bg=DISPLAY, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(13, 2))
        self.expr_label = tk.Label(panel, text=" ", bg=DISPLAY, fg="#B9A7FF",
                                   anchor="e", font=("Consolas", 13))
        self.expr_label.pack(fill="x", padx=16)
        self.result_label = tk.Label(panel, text="0", bg=DISPLAY, fg=TEXT,
                                     anchor="e", font=("Segoe UI", 34, "bold"))
        self.result_label.pack(fill="x", padx=16, pady=(2, 15))

        status = tk.Frame(self.outer, bg=BG)
        status.pack(fill="x", pady=(0, 8))
        tk.Label(status, text="● READY", bg=BG, fg=GREEN,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(status, text="ENTER = CALCULATE  •  ESC = CLEAR", bg=BG, fg=MUTED,
                 font=("Segoe UI", 7, "bold")).pack(side="right")

        self.pad = tk.Frame(self.outer, bg=BG)
        self.pad.pack(fill="both", expand=True)
        for c in range(4): self.pad.grid_columnconfigure(c, weight=1, uniform="col")
        for r in range(6): self.pad.grid_rowconfigure(r, weight=1, uniform="row")

        rows = [
            [("AC","clear",DANGER,PINK),("⌫","back",KEY,CYAN),("%","percent",KEY,CYAN),("÷","append",KEY,CYAN)],
            [("√","sqrt",KEY,CYAN),("x²","square",KEY,CYAN),("(","append",KEY,TEXT),(")","append",KEY,TEXT)],
            [("7","digit",KEY,TEXT),("8","digit",KEY,TEXT),("9","digit",KEY,TEXT),("×","append",KEY,CYAN)],
            [("4","digit",KEY,TEXT),("5","digit",KEY,TEXT),("6","digit",KEY,TEXT),("−","append",KEY,CYAN)],
            [("1","digit",KEY,TEXT),("2","digit",KEY,TEXT),("3","digit",KEY,TEXT),("+","append",KEY,CYAN)],
            [("0","digit",KEY,TEXT),(".","digit",KEY,TEXT),("±","sign",KEY,CYAN),("=","equals",PURPLE,TEXT)],
        ]
        for r, row in enumerate(rows):
            for c, (label, action, bg, fg) in enumerate(row):
                hover = "#B09AFF" if label == "=" else HOVER
                btn = self.button(self.pad, label,
                                  lambda l=label, a=action: self.press(l, a),
                                  bg, fg, ("Segoe UI", 15 if r < 5 else 16, "bold"), hover)
                btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4, ipady=5)

        tk.Label(self.outer, text="A little clarity in every calculation  •  AURA",
                 bg=BG, fg="#626D8E", font=("Segoe UI", 8)).pack(pady=(9, 0))

    def button(self, parent, text, command, bg, fg, font, hover=None):
        hover = hover or HOVER
        b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                      activebackground=hover, activeforeground=TEXT,
                      relief="flat", bd=0, cursor="hand2", font=font,
                      padx=5, pady=7, highlightthickness=1,
                      highlightbackground="#252D49", highlightcolor=CYAN)
        b.bind("<Enter>", lambda e: b.configure(bg=hover))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        return b

    def resize(self, event):
        if event.widget is self.root:
            size = 26 if event.width < 370 else 30 if event.width < 420 else 34
            self.result_label.configure(font=("Segoe UI", size, "bold"))

    def update_display(self, result=None):
        self.expr_label.configure(text=self.expression or " ")
        self.result_label.configure(text=(result if result is not None else (self.expression or "0"))[-22:])

    def press(self, label, action):
        try:
            if action == "clear":
                self.clear()
            elif action == "back":
                self.expression = self.expression[:-1]
                self.last_result = False
                self.update_display()
            elif action == "digit":
                if self.last_result: self.expression = ""
                self.expression += label
                self.last_result = False
                self.update_display()
            elif action == "append":
                if self.last_result and label not in ("+", "−", "×", "÷", "%", "^"):
                    self.expression = ""
                self.expression += label
                self.last_result = False
                self.update_display()
            elif action == "percent":
                self.unary(lambda n: n / 100)
            elif action == "sqrt":
                self.unary(lambda n: math.sqrt(n) if n >= 0 else (_ for _ in ()).throw(ValueError("Negative number ka square root nahi hota.")))
            elif action == "square":
                self.unary(lambda n: n * n)
            elif action == "sign":
                if self.expression: self.expression = fmt(-calculate(self.expression))
                else: self.expression = "-"
                self.last_result = False
                self.update_display()
            elif action == "equals":
                self.equals()
        except ZeroDivisionError:
            self.error("Zero se divide nahi kar sakte.")
        except (SyntaxError, ValueError, OverflowError) as e:
            self.error(str(e) or "Expression check karein.")

    def unary(self, fn):
        if not self.expression: return
        self.expression = fmt(fn(calculate(self.expression)))
        self.last_result = False
        self.update_display()

    def equals(self):
        if not self.expression: return
        original = self.expression
        try:
            result = fmt(calculate(original))
            self.history.insert(0, {"time": datetime.now().strftime("%H:%M:%S"),
                                    "expression": original, "result": result})
            self.history = self.history[:100]
            self.expression = result
            self.last_result = True
            self.expr_label.configure(text=f"{original}  =")
            self.update_display(result)
        except ZeroDivisionError:
            self.error("Zero se divide nahi kar sakte.")
        except (SyntaxError, ValueError, OverflowError) as e:
            self.error(str(e) or "Expression valid nahi hai.")

    def error(self, message):
        self.expr_label.configure(text=message[:48])
        self.result_label.configure(text="Error")
        self.root.bell()

    def clear(self):
        self.expression = ""
        self.last_result = False
        self.update_display()

    def on_key(self, event):
        key, char = event.keysym, event.char
        if key in ("Return", "KP_Enter", "equal"):
            self.equals()
            return "break"
        if key == "BackSpace":
            self.press("⌫", "back")
            return "break"
        if char and char in "0123456789.()":
            self.press(char, "digit" if char not in "()" else "append")
            return "break"
        if char and char in "+-*/%":
            if char == "%": self.press("%", "percent")
            else: self.press({"+":"+","-":"−","*":"×","/":"÷"}[char], "append")
            return "break"
        if char == "^":
            self.press("^", "append")
            return "break"

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("AURA • History")
        win.geometry("440x430")
        win.minsize(320, 260)
        win.configure(bg=BG)
        tk.Label(win, text="◷  CALCULATION HISTORY", bg=BG, fg=CYAN,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(16, 10))
        frame = tk.Frame(win, bg=CARD, highlightthickness=1, highlightbackground="#35345F")
        frame.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        scroll = tk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")
        listing = tk.Listbox(frame, bg=CARD, fg=TEXT, selectbackground="#5741A8",
                             selectforeground=TEXT, relief="flat", bd=0,
                             font=("Consolas", 10), yscrollcommand=scroll.set)
        listing.pack(fill="both", expand=True, padx=8, pady=8)
        scroll.config(command=listing.yview)
        if not self.history: listing.insert("end", "No calculations yet.")
        for item in self.history:
            listing.insert("end", f"{item['time']}  {item['expression']} = {item['result']}")

        actions = tk.Frame(win, bg=BG)
        actions.pack(fill="x", padx=14, pady=(0, 14))

        def use_selected(event=None):
            selected = listing.curselection()
            if selected and self.history:
                self.expression = self.history[selected[0]]["result"]
                self.last_result = True
                self.update_display()
                win.destroy()

        self.button(actions, "USE SELECTED", use_selected, PURPLE, TEXT,
                    ("Segoe UI", 9, "bold")).pack(side="left")
        def clear_history():
            self.history.clear()
            win.destroy()
            self.show_history()
        self.button(actions, "CLEAR HISTORY", clear_history, DANGER, PINK,
                    ("Segoe UI", 9, "bold")).pack(side="right")
        listing.bind("<Double-Button-1>", use_selected)


def main():
    root = tk.Tk()
    AuraCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
