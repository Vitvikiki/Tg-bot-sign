import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from loguru import logger

CORE_DIR = Path(__file__).parent


class WaterMark:
    """Наложение текста на водяной знак"""

    def __init__(self, text, user_id):
        logger.info(text)

        # файл водяного знака
        self.im = Image.open(str(Path(CORE_DIR, 'watermark.jpg')))

        # объект для печатания текста на фото
        self.draw_text = ImageDraw.Draw(self.im)

        # файл для шрифта
        self.font_file = str(Path(CORE_DIR, 'font/Comic Sans MS.ttf'))

        # текст для печатания
        self.text = text

        # ID для сохранения полученного объекта с тим ID
        self.user_id = user_id

    def calc_plus_changes(self, i, size):
        """Проверить количество букв для переноса слова при увеличении"""
        k_changes = 0
        k_plus = i
        if self.text[k_plus] != ' ':
            try:
                while self.text[k_plus] != ' ':
                    k_changes += 1
                    k_plus += 1
                    logger.trace(f'calc_plus_changes text[k_plus]| {self.text[k_plus]}')
            except IndexError as e:
                logger.trace(e)

        return k_plus, k_changes, size - k_changes

    def calc_minus_changes(self, i):
        """Проверить количество букв для переноса слова при уменьшении"""
        k_changes = 0
        k_minus = i
        if self.text[k_minus - 1] != ' ':
            try:
                while self.text[k_minus] != ' ':
                    k_changes += 1
                    k_minus -= 1
                    logger.trace(f'calc_minus_changes text[k_minus| {self.text[k_minus]}')
            except IndexError as e:
                logger.trace(e)
        return k_minus, k_changes,

    def calculate_font_size(self, size: int = 93, divider: int = 30) -> tuple[str, int]:
        """
        Получить равномерно распределенный текст со знаками переноса после вычисления
         размера шрифта
        """
        # size = 93 divider = 30
        n = len(self.text)
        res = []
        if n > divider:
            pre = 0
            for i in range(divider, n, divider):
                logger.debug(f'i| {i}')
                if self.text[i] == ',':
                    i += 1

                # Changes occurrences until the word does not fit
                # Нахождения наименьшего расстояния для переноса слова или для уменьшения шрифта
                plus, plus_changes, p_size = self.calc_plus_changes(i, size)
                minus, minus_changes = self.calc_minus_changes(i, )

                if plus_changes < minus_changes:
                    i = plus
                    size = p_size
                    logger.trace(f'plus {plus}{plus_changes}')
                    logger.trace(f'con_minus {minus}{minus_changes}')
                else:
                    i = minus
                    logger.trace(f'minus {minus}{minus_changes}')
                    logger.trace(f'con_plus {plus}{plus_changes}')

                logger.debug(f'text[i]| {self.text[i]}, {i}')
                ch_text = self.text[pre:i]
                res.append(ch_text.strip())
                pre = i
            res.append(self.text[pre:].strip())

        res = '\n'.join(res)
        return (res or self.text), size

    # todo 30.01.2022 20:51 taima:

    def draw(self):
        # (1560, 677)

        # рассчитать размер шрифта
        text, size = self.calculate_font_size()
        font = ImageFont.truetype(self.font_file, size=size)

        # напечатать полученный текст
        self.draw_text.text(
            (30, 30),
            text,
            fill='black',
            font=font
        )

        # сохранение полученного изображения
        self.im.save(str(Path(CORE_DIR, f'{self.user_id}.jpg')))


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level='TRACE', diagnose=True, enqueue=True)
    text1 = 'Хочу протестировать печатание текста, бывает и то хуже напишукакуюнибдуь чепуху'
    w = WaterMark(text1, 123)
    w.draw()
