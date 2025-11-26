from manim import *


class Node(VGroup):
    def __init__(
        self,
        value=None,
        width=0.6,
        height=0.6,
        font_size=22,
        label=None,
        label_pos=UP,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.value = " " if value is None else value
        self.width = width
        self.height = height
        self.label_value = label
        self.label_pos = label_pos
        self.font_size = font_size
        self.label_font_size = font_size * 0.7

        # main cell
        self.cell = Rectangle(
            width=width, height=height, fill_color=BLACK, fill_opacity=1
        )
        self.text = Text(str(value), font_size=font_size, z_index=1).move_to(
            self.cell.get_center()
        )

        self.add(self.cell, self.text)

        # optional label
        if label is not None:
            self.label = Text(str(label), font_size=self.label_font_size).next_to(
                self.cell, label_pos
            )
            self.add(self.label)
        else:
            self.label = None

    def get_cell(self):
        return self.cell

    def get_text(self):
        return self.text

    def get_label(self):
        return self.label

    def set_text(self, value=None):
        value = " " if value is None else value
        self.value = value
        new_text = Text(str(value), font_size=self.font_size, z_index=1).move_to(
            self.get_cell().get_center()
        )
        self.text.become(new_text)


class Vector(VGroup):
    def __init__(
        self,
        data=None,
        width=0.6,
        height=0.6,
        dir_right=True,
        index=True,
        index_from=0,
        index_step=1,
        buff=0,
        font_size=22,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.data = data or []
        self.len = len(data)

        self.buff = buff
        self.dir_right = dir_right
        self.dir = RIGHT if dir_right else UP

        self.index = index
        self.index_from = index_from
        self.index_step = index_step

        self.nodes = VGroup()

        label_pos = UP if dir_right else LEFT
        indices = range(index_from, index_from + self.len * index_step, index_step)
        for i, (value, idx) in enumerate(zip(data, indices)):
            node = Node(
                value=value,
                width=width,
                height=height,
                font_size=font_size,
                label=(idx if index else None),
                label_pos=label_pos,
            )
            self.nodes.add(node)

        self.nodes.arrange(self.dir, buff=buff)
        self.add(self.nodes)

    def focus(self, start=0, end=None, color=GREEN, buff=0.1):
        end = self.len if end is None else end
        cells = VGroup(*[self.nodes[x].get_cell() for x in range(start, end)])
        return (
            SurroundingRectangle(cells, buff=buff)
            .set_fill(color, opacity=0.3)
            .set_stroke(color, width=2)
        )

    def set(self, *cells, texts=None, fill=" "):
        texts = texts or []
        texts += [fill] * (len(cells) - len(texts))

        for cell, text in zip(cells, texts):
            self.data[cell] = text
            self.nodes[cell].set_text(text)

    def swap(self, scene, n1, n2):
        if n1 == n2:
            return

        arcup, arcdwn = [
            ArcBetweenPoints(a.get_center(), b.get_center(), angle=-PI)
            for a, b in (
                (self.nodes[n1].get_cell(), self.nodes[n2].get_cell()),
                (self.nodes[n2].get_cell(), self.nodes[n1].get_cell()),
            )
        ]

        scene.play(
            MoveAlongPath(self.nodes[n1].get_text(), arcup),
            MoveAlongPath(self.nodes[n2].get_text(), arcdwn),
        )

        self.set(n1, n2, texts=[self.data[n2], self.data[n1]])

    def swap_and_shift(self, scene, fromx, tox):
        if fromx == tox:
            return

        step = 1 if fromx < tox else -1
        angle = -PI
        shift_dir = LEFT if fromx < tox else RIGHT
        width = self.nodes[0].get_cell().width

        if not self.dir_right:
            shift_dir = DOWN if fromx < tox else UP

        cells = VGroup(*[self.nodes[x].get_cell() for x in [fromx, tox]])
        texts = VGroup(
            *[self.nodes[x].get_text() for x in range(fromx, tox + step, step)]
        )

        arc = ArcBetweenPoints(cells[0].get_center(), cells[1].get_center(), angle=-PI)
        scene.play(
            MoveAlongPath(texts[0], arc),
            texts[1:].animate.shift(shift_dir * width),
        )

        texts = [self.data[fromx]] + self.data[tox:fromx:-step]
        self.set(*range(fromx, tox + step, step), texts=list(reversed(texts)))
