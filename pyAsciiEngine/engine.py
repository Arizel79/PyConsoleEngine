'''pyAsciiEngine © @Arizel79 (t.me/Arizel79)
==================
Ascii games engine / движок для Ascii игр
Installing:
	py -m pip install windows-curses
'''
import curses as cu
from math import sqrt
import re
import html
from collections import defaultdict


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
        self.stdscr.keypad(True)
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

    def set_symbol_obj(self, x, y, symbol: Symbol):
        symbol.draw(self, x, y)

    def draw_rectangle(self, x1, y1, x2, y2, symbol, isFill=True, border_symbol=None):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Если символ границы не указан, используем основной символ
        border_sym = border_symbol if border_symbol is not None else symbol

        if isFill:
            # Заполненный прямоугольник
            for y in range(y1, y2 + 1):
                for x in range(x1, x2 + 1):
                    # Если это граница или заполненный прямоугольник
                    if x == x1 or x == x2 or y == y1 or y == y2:
                        self.set_symbol_obj(x, y, border_sym)
                    else:
                        self.set_symbol_obj(x, y, symbol)
        else:
            # Только контур прямоугольника
            # Верхняя и нижняя границы
            for x in range(x1, x2 + 1):
                self.set_symbol_obj(x, y1, border_sym)  # Верхняя граница
                self.set_symbol_obj(x, y2, border_sym)  # Нижняя граница

            # Боковые границы
            for y in range(y1 + 1, y2):
                self.set_symbol_obj(x1, y, border_sym)  # Левая граница
                self.set_symbol_obj(x2, y, border_sym)  # Правая граница

    def draw_circle(self, x, y, r, symbol, width=0):
        x1, y1, x2, y2 = x - r, y - r, x + r, y + r
        for x_ in range(x1, x2):
            for y_ in range(y1, y2):
                dx = x_ - x
                dy = y_ - y
                k = sqrt(dx ** 2 + (dy ** 2) * 3)
                if k + 0.5 <= r:
                    if width > 0 and k >= r - width:
                        self.set_symbol_obj(x_, y_, symbol)
                    elif width <= 0:
                        self.set_symbol_obj(x_, y_, symbol)

    def set_str(self, x, y, string, style=None, anchor=Anchors.DEFAULT_X_ANCHOR, parse_html=False):
        if not parse_html:
            if anchor == Anchors.LEFT_ANCHOR:
                sx = x
            elif anchor == Anchors.RIGHT_ANCHOR:
                sx = x - len(string)
            elif anchor == Anchors.CENTER_X_ANCHOR:
                sx = x - len(string) // 2
            else:
                assert False

            for i in range(0, len(string)):
                self.setSymbol(sx + i, y, string[i], style)
        else:
            self._render_html_text(x, y, string, style, anchor)

    def _render_html_text(self, x, y, text, base_style, anchor):
        """Рендерит HTML-текст с поддержкой вложенных тегов и переносов строк"""
        if not text:
            return

        # Вычисляем начальную позицию по X в зависимости от anchor
        text_without_tags = self._strip_html_tags(text)
        if anchor == Anchors.RIGHT_ANCHOR:
            pos_x = x - len(text_without_tags)
        elif anchor == Anchors.CENTER_X_ANCHOR:
            pos_x = x - len(text_without_tags) // 2
        else:
            pos_x = x

        # Парсим HTML и рендерим посимвольно
        current_style = base_style if base_style else TextStyle()
        style_stack = []
        pos_y = y
        i = 0
        max_x = self.get_max_coords()[0]

        while i < len(text):
            if text[i] == '<':
                # Обработка HTML-тега
                tag_end = text.find('>', i)
                if tag_end == -1:
                    break

                tag_content = text[i + 1:tag_end]
                if tag_content.startswith('/'):
                    # Закрывающий тег
                    tag_name = tag_content[1:].split()[0].lower()
                    if style_stack and style_stack[-1][0] == tag_name:
                        style_stack.pop()
                        current_style = style_stack[-1][1] if style_stack else (
                            base_style if base_style else TextStyle())
                else:
                    # Открывающий тег
                    tag_parts = tag_content.split()
                    tag_name = tag_parts[0].lower()
                    attrs = {}

                    # Парсим атрибуты
                    for part in tag_parts[1:]:
                        if '=' in part:
                            attr, value = part.split('=', 1)
                            attrs[attr.lower()] = value.strip('"\'')

                    # Сохраняем текущий стиль в стек
                    style_stack.append((tag_name, current_style))
                    # Создаем новый стиль
                    current_style = self._create_html_style(tag_name, attrs, current_style)

                i = tag_end + 1
            elif text[i] == '\n':
                # Перенос строки
                pos_y += 1
                if anchor == Anchors.RIGHT_ANCHOR:
                    pos_x = x - (len(text_without_tags) - i)  # Примерное вычисление, может потребоваться уточнение
                elif anchor == Anchors.CENTER_X_ANCHOR:
                    pos_x = x - (len(text_without_tags) - i) // 2
                else:
                    pos_x = x
                i += 1
            elif text[i] == '&':
                # HTML-сущности
                entity_end = text.find(';', i)
                if entity_end != -1:
                    entity = text[i:entity_end + 1]
                    char = html.unescape(entity)
                    for c in char:
                        if pos_x >= max_x:
                            pos_x = x
                            pos_y += 1
                        self.setSymbol(pos_x, pos_y, c, current_style)
                        pos_x += 1
                    i = entity_end + 1
            else:
                # Обычный символ
                if pos_x >= max_x:
                    pos_x = x
                    pos_y += 1
                self.setSymbol(pos_x, pos_y, text[i], current_style)
                pos_x += 1
                i += 1

    def _create_html_style(self, tag_name, attrs, current_style):
        """Создает новый стиль на основе HTML-тега"""
        fg = current_style.fgs
        bg = current_style.bgs
        style_attrs = list(current_style.str_attrs)

        # Обработка цветов
        if tag_name in Colors.ALL_COLORS:
            fg = tag_name
        elif tag_name == 'color' and 'value' in attrs:
            fg = attrs['value'].lower()

        # Обработка фона
        if tag_name.startswith('bg_') and tag_name[3:] in Colors.ALL_COLORS:
            bg = tag_name[3:]
        elif tag_name == 'bg' and 'value' in attrs:
            bg = attrs['value'].lower()
        elif tag_name == 'span' and 'bg' in attrs:
            bg = attrs['bg'].lower()

        # Обработка стилей текста
        style_map = {
            'b': 'bold',
            'i': 'italic',
            'u': 'underline',
            'strong': 'bold',
            'em': 'italic',
            'blink': 'blink',
            'reverse': 'reverse'
        }

        if tag_name in style_map:
            attr = style_map[tag_name]
            if attr not in style_attrs:
                style_attrs.append(attr)

        return TextStyle(fg, bg, *style_attrs)

    def _strip_html_tags(self, text):
        """Удаляет HTML-теги для вычисления длины текста"""
        result = []
        i = 0
        while i < len(text):
            if text[i] == '<':
                tag_end = text.find('>', i)
                if tag_end == -1:
                    break
                i = tag_end + 1
            elif text[i] == '&':
                entity_end = text.find(';', i)
                if entity_end != -1:
                    result.append(' ')  # Считаем сущности за один символ
                    i = entity_end + 1
                else:
                    result.append(text[i])
                    i += 1
            elif text[i] == '\n':
                result.append(' ')
                i += 1
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)

    def _create_html_style(self, tag_name, attrs, current_style):
        """Create new style based on HTML tag and attributes"""
        fg = current_style.fgs
        bg = current_style.bgs
        style_attrs = list(current_style.str_attrs)

        # Handle colors
        if tag_name in Colors.ALL_COLORS:
            fg = tag_name
        elif tag_name == 'color' and 'value' in attrs:
            fg = attrs['value'].lower()

        # Handle background
        if tag_name.startswith('bg_') and tag_name[3:] in Colors.ALL_COLORS:
            bg = tag_name[3:]
        elif tag_name == 'bg' and 'value' in attrs:
            bg = attrs['value'].lower()

        # Handle text styles
        style_map = {
            'b': 'bold',
            'i': 'italic',
            'u': 'underline',
            'strong': 'bold',
            'em': 'italic',
            'blink': 'blink',
            'reverse': 'reverse'
        }

        if tag_name in style_map:
            attr = style_map[tag_name]
            if attr not in style_attrs:
                style_attrs.append(attr)

        return TextStyle(fg, bg, *style_attrs)

    def set_col_ctr(self, x, y, string, style=None, anchor=Anchors.DEFAULT_X_ANCHOR):
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

    def set_text(self, x, y, text, style=None, anchor_x=Anchors.DEFAULT_X_ANCHOR,
                anchor_y=Anchors.DEFAULT_Y_ANCHOR, parse_html=False):
        if not parse_html:
            lines = text.split('\n')
        else:
            lines = self._split_html_lines(text)

        # Calculate Y position based on anchor
        if anchor_y == Anchors.UP_ANCHOR:
            start_y = y
        elif anchor_y == Anchors.CENTER_Y_ANCHOR:
            start_y = y - len(lines) // 2
        elif anchor_y == Anchors.DOWN_ANCHOR:
            start_y = y - len(lines)
        else:
            raise ValueError("Invalid Y anchor")

        for i, line in enumerate(lines):
            if parse_html:
                self._render_html_text(x, start_y + i, line, style, anchor_x)
            else:
                self.set_str(x, start_y + i, line, style, anchor_x)

    def _split_html_lines(self, text):
        """Split text into lines while preserving HTML tags across lines"""
        lines = []
        current_line = []
        tag_stack = []

        i = 0
        while i < len(text):
            if text[i] == '<':
                # Handle HTML tag
                tag_end = text.find('>', i)
                if tag_end == -1:
                    break

                tag_content = text[i:tag_end + 1]

                # Check if it's a closing tag
                if tag_content.startswith('</'):
                    tag_name = tag_content[2:-1].lower().split()[0]
                    if tag_stack and tag_stack[-1][0] == tag_name:
                        tag_stack.pop()
                else:
                    # Opening tag - parse tag name and attributes
                    tag_parts = tag_content[1:-1].split()
                    if tag_parts:
                        tag_name = tag_parts[0].lower()
                        tag_stack.append((tag_name, tag_content))

                current_line.append(tag_content)
                i = tag_end + 1
            elif text[i] == '\n':
                # Close all open tags before newline and reopen them after
                closed_tags = []
                for tag in reversed(tag_stack):
                    current_line.append(f'</{tag[0]}>')
                    closed_tags.append(tag[1])

                lines.append(''.join(current_line))
                current_line = []

                # Reopen tags in the same order
                for tag in closed_tags[::-1]:
                    current_line.append(tag)

                i += 1
            else:
                # Handle normal text and HTML entities
                if text[i] == '&':
                    entity_end = text.find(';', i)
                    if entity_end != -1:
                        current_line.append(text[i:entity_end + 1])
                        i = entity_end + 1
                        continue

                current_line.append(text[i])
                i += 1

        if current_line:
            lines.append(''.join(current_line))

        return lines

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
        except cu.error:
            pass

    def get_height(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[1]

    def get_width(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[0]

    def get_sizes(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[1], yx[0]

    def get_max_coords(self):
        cu.update_lines_cols()
        yx = self.stdscr.getmaxyx()
        return yx[1] - 1, yx[0] - 1

    def clear(self):
        self.stdscr.erase()

    def flash(self):
        cu.flash()

    def beep(self):
        cu.beep()

    def border(self):
        self.stdscr.border()

    def quit(self):
        cu.endwin()


def rainbow(text, k=0):
    out = ""
    for n, i in enumerate(text):
        color = Colors.ALL_COLORS[1:][(n + k) % len(Colors.ALL_COLORS[1:])]
        out += f"<{color}>{i}</{color}>"
    return out


def main():
    try:
        scr = ConsoleScreen()
        running = True
        n = "\n"
        test_text = f"""<red>Red text</red>
    Default text
    
    {rainbow(f'this text is rainbo{n}w... привет, мир!')}
    """

        while running:
            x, y = scr.get_sizes()
            scr.update()
            key = scr.get_key()
            if key == "q":
                running = False

            scr.clear()
            scr.set_text(0, 0, test_text, parse_html=True)
            scr.set_text(0, y - 2, f"sizes: {x} {y}")
            scr.set_text(0, y - 1, "Нажмите 'q' для выхода")
            scr.set_str(0, y - 4, f"<green>{html.escape('<b>lol</b>')} way</green>", parse_html=True)
            scr.set_str(0, y - 7, f"this is text", TextStyle(Colors.WHITE, Colors.BLACK))
            scr.set_str(0, y - 6, f"this is text", TextStyle(Colors.WHITE, Colors.BLACK, Styles.BOLD, Styles.BLINK))


    finally:
        scr.quit()

if __name__ == '__main__':
    main()
