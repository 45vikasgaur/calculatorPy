import ast
import math
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


# ------------------------------------------------------------
# NEON GLASS CALCULATOR
# Python 3.10+ recommended. Uses only Python's standard library.
# ------------------------------------------------------------

BG = "#090914"
PANEL = "#121226"
PANEL_2 = "#191832"
PURPLE = "#8B5CF6"
PURPLE_DARK = "#5B21B6"
CYAN = "#22D3EE"
PINK = "#F472B6"
TEXT = "#F5F3FF"
MUTED = "#A5A3C7"
OP_BG = "#292044"
DANGER = "#54213C"
GREEN = "#34D399"


class SafeCalculator:
    """Evaluate only basic arithmetic AST nodes; never use raw eval()."""

    @staticmethod
    def evaluate(expression: str):
        expression = expression.strip()
        if not expression:
            return None

        # Convert calculator symbols into Python arithmetic operators.
        expression = expression.replace("×", "*").replace("÷", "/")
        expression = expression.replace("−", "-").replace("^", "**")
        tree = ast.parse(expression, mode="eval")

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.BinOp):
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Add):
                    result = left + right
                elif isinstance(node.op, ast.Sub):
                    result = left - right
                elif isinstance(node.op, ast.Mult):
                    result = left * right
                elif isinstance(node.op, ast.Div):
                    result = left / right
                elif isinstance(node.op, ast.Pow):
                    if abs(right) > 1000:
                        raise ValueError("Exponent bahut bada hai.")
                    result = left ** right
                elif isinstance(node.op, ast.Mod):
                    result = left % right
                else:
                    raise ValueError("Ye operator allowed nahi hai.")
                if isinstance(result, complex):
                    raise ValueError("Complex result supported nahi hai.")
                if isinstance(result, (int, float)) and abs(result) > 1e100:
                    raise ValueError("Result bahut bada hai.")
                return result
            if isinstance(node, ast.UnaryOp):
                value = visit(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return value
                if isinstance(node.op, ast.USub):
                    return -value
            raise ValueError("Expression valid nahi hai.")

        result = visit(tree)
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("Result finite nahi hai.")
        return result


class NeonCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("NEON • Premium Calculator")
        self.root.geometry("430x720")
        self.root.minsize(360, 610)
        self.root.configure(bg=BG)

        self.expression = ""
        self.just_evaluated = False
        self.history = []

        self._build_ui()
        self._bind_keyboard()