'''PyConsoleAsciiEngine, (c) Kirill Fridrih (Кирилл Фридрих) https://t.me/a7r9x3
==================
Ascii games engine / движок для Ascii игр
Installing:
	py -m pip install windows-curses
'''
import curses as cu
from math import sqrt



class Colors:
    ALL_COLORS = BLACK, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE = "black", "red", "green", "blue", "yellow", "magenta", "cyan", "white"


class Anchors:
    LEFT_ANCHOR = "left"
    RIGHT_ANCHOR = "right"
    CENTER_X_ANCHOR = "centerX"
    DEFAULT_X_ANCHOR = LEFT_ANCHOR

    UP_ANCHOR = "up"
    DOWN_ANCHOR = "down"
    CENTER_Y_ANCHOR = "centerY"
    DEFAULT_Y_ANCHOR = UP_ANCHOR


class Styles:
    NORMAL = "normal"
    BOLD = "bold"
    BLINK = "blink"
    UNDERLINE = "underline"
    REVERSE = "reverse"
    DIM = "dim"
    STANDOUT = "standout"
    PROTECT = "protect"
    ALTCHARSET = "altcharset"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    HORIZONTAL = "horizontal"


class TextStyle:
    scr = cu.initscr()
    cu.start_color()
    pairs = set()
    COLORS = {"black": cu.COLOR_BLACK, "blue": cu.COLOR_BLUE, "green": cu.COLOR_GREEN,
              "yellow": cu.COLOR_YELLOW, "red": cu.COLOR_RED,
              "magenta": cu.COLOR_MAGENTA, "cyan": cu.COLOR_CYAN, "white": cu.COLOR_WHITE}

    OTHER_ATTRIBUTES = {"blink": cu.A_BLINK, "bold": cu.A_BOLD, "reverse": cu.A_REVERSE,
                        "dim": cu.A_DIM, "standout": cu.A_STANDOUT,
                        "protect": cu.A_PROTECT, "underline": cu.A_UNDERLINE,
                        "italic": cu.A_ITALIC, "normal": cu.A_NORMAL,
                        "left": cu.A_LEFT, "top": cu.A_TOP, "right": cu.A_RIGHT, "invis": cu.A_INVIS,
                        "altcharset": cu.A_ALTCHARSET, "horizontal": cu.A_HORIZONTAL}

    def __init__(self, fg="white", bg="black", *attrs):
        self.fgs = fg
        self.bgs = bg
        self.str_attrs = attrs
        self.attrs = set()
        self.add_count = 0
        self.pair = self.get_pair_id(self.fgs, self.bgs)
        for i in self.str_attrs:
            self.attrs.add(self.OTHER_ATTRIBUTES[i])
        for attr in self.attrs:
            self.add_count |= attr

    def get_paired(self):
        return cu.color_pair(self.pair) | self.add_count

    def get_pair_id(self, fg, bg):
        fg_id = self.COLORS[fg]
        bg_id = self.COLORS[bg]
        id = fg_id * 10 + bg_id + 1  # последний +1 чтобы 0 в ответе не было

        if not id in self.pairs:
            cu.init_pair(id, fg_id, bg_id)
            self.pairs.add(id)
        return id


class Symbol:
    def __init__(self, symbol, fg='white', bg='black', *attrs, style=None):
        self.symbol = symbol
        if style is None:
            self.style = TextStyle(fg, bg, *attrs)
        else:
            self.style = style

    def draw(self, scr, x, y):
        scr.setSymbol(x, y, self.symbol, self.style)


class ConsoleScreen:
    def __init__(self, use_colors=True, use_attrs=True):
        self.use_colors = use_colors
        self.use_attrs = use_attrs

        self.stdscr = cu.initscr()
        self.stdscr.keypad(True)  # иначе будут проблемы отрисовки
        cu.noecho()
        cu.cbreak()
        self.stdscr.move(0, 0)
        cu.curs_set(False)

    def update(self):
        self.stdscr.refresh()

    def setSymbol(self, x, y, symbol, style=None):
        if style == None or not self.use_colors:
            style_code = 0
        else:
            style_code = style.get_paired()
        try:
            self.stdscr.addch(y, x, str(symbol)[0], style_code)
        except:
            pass

    def setSymbolObj(self, x, y, symbol: Symbol):
        symbol.draw(self, x, y)

    def drawRectangle(self, x1, y1, x2, y2, symbol, isFill=True):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        if isFill:

            for y in range(y1, y2):
                self.setStr(x1, y, symbol.symbol * (x2 - x1), symbol.style)
        else:
            self.setStr(x1, y1, symbol.symbol * (x2 - x1), symbol.style)

    def drawCircle(self, x, y, r, symbol, width=0):
        x1, y1, x2, y2 = x - r, y - r, x + r, y + r
        for x_ in range(x1, x2):
            for y_ in range(y1, y2):
                dx = x_ - x
                dy = y_ - y
                k = sqrt(dx ** 2 + (dy ** 2) * 3)
                if k + 0.5 <= r:
                    if width > 0 and k >= r - width:
                        self.setSymbolObj(x_, y_, symbol)
                    elif width <= 0:
                        self.setSymbolObj(x_, y_, symbol)

    def setStr(self, x, y, string, style=None, anchor=Anchors.DEFAULT_X_ANCHOR, ):
        string = str(string)

        if anchor == Anchors.LEFT_ANCHOR:
            sx = x
        elif anchor == Anchors.RIGHT_ANCHOR:
            sx = x - len(string)
        elif anchor == Anchors.CENTER_X_ANCHOR:
            sx = x - len(string) // 2
        else:
            assert False

        for i in range(0, len(string), 1):
            self.setSymbol(sx + i, y, string[i], style)

    def setColStr(self, x, y, string, style=None, anchor=Anchors.DEFAULT_X_ANCHOR, ):
        string = str(string)
        if anchor == Anchors.UP_ANCHOR:
            sy = y
        elif anchor == Anchors.DOWN_ANCHOR:
            sy = x - len(string)
        elif anchor == Anchors.CENTER_Y_ANCHOR:
            sy = y - len(string) // 2
        else:
            assert False
        for i in range(0, len(string), 1):
            self.setSymbol(x, sy + i, string[i], style)

    def setText(self, x, y, text, style=None, anchor_x=Anchors.DEFAULT_X_ANCHOR, anchor_y=Anchors.DEFAULT_Y_ANCHOR):
    	lst = text.splitlines()
    	if anchor_y == Anchors.UP_ANCHOR:
    		sy = y
    	elif anchor_y==Anchors.CENTER_Y_ANCHOR:
    		sy = y - len(lst)//2
    	elif anchor_y==Anchors.ANCHOR_DOWN:
    		sy =  y - len(lst)
    	for i, ln in enumerate(lst):
            self.setStr(x, sy+i, ln, style, anchor=anchor_x)
    def wait_key(self):
        key = self.get_key(-1)
        return key

    def get_key(self, wait_time_sec=0.1):
        try:
            self.stdscr.timeout(int(wait_time_sec * 1000))
            k = self.stdscr.get_wch()
            if k == -1:
                key = None
            if k == 410:
                key = 'RESIZE'
            else:
                key = str(k)
            return key
        except cu.error:  # если ничего не нажато
            pass  # нам пофиг на это

    def getHeight(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[1]

    def getWidth(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[0]

    def getHW(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[1], yx[0]

    def getMaxCoords(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[1] - 1, yx[0] - 1

    def clear(self):
        self.stdscr.erase()

    def flashScreen(self):
        cu.flash()

    def beepSound(self):
        cu.beep()

    def border(self):
        self.stdscr.border()

    def quit(self):
        cu.endwin()


def main():
    scr = ConsoleScreen()
    txt = TextStyle("white", "black")
    h1 = TextStyle("white", "black")
    smbl = Symbol("#", "yellow", "black")
    smbl2 = Symbol("*", Colors.GREEN, Colors.BLACK, Styles.DIM)
    smbl3 = Symbol("#", style=TextStyle("red"))
    running = True
    border_width = 8.6
    cx,cy,cr=15, 10, 5
    while running:
        key = scr.get_key(.1)
        w, h = scr.getHW()
        if key == "q":
            scr.quit()
            running = False

        elif key == " ":
            scr.flashScreen()
        elif key == "w":
            border_width += 0.5
        elif key == "s":
            border_width -= 0.5
        if not key is None:
            last_prees = key
        scr.clear()

        scr.setStr(0, 0, "PyConsoleEngine, (c) Kirill Fridrih", style=h1)
        scr.setStr(0, 1, f"Telegram: t.me/a7r9x3", style=txt)
        scr.setStr(0, 2, f"Prees W or S to edit border width", style=txt)
        scr.setStr(0, h - 1, f"height and width: {h}, {w}", style=txt)

        scr.drawCircle(cx, cy, r=cr,  symbol=smbl2)

        scr.setColStr(w - 1, 0, f"vertical text ", style=txt, anchor=Anchors.UP_ANCHOR)
        scr.setText(w//2, h//2, """Hello, world!\nПривет, мир!\n1234567890\n-----\n""" * 3,TextStyle("black", "red"), anchor_x=Anchors.CENTER_X_ANCHOR, anchor_y=Anchors.CENTER_Y_ANCHOR)
        # scr.setSymbolObj(5, 5, smbl)
        scr.update()

    scr.quit()


if __name__ == '__main__':
    main()