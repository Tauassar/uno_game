import enum


class CardSuits(enum.Enum):
    ZERO = 'ZERO'
    ONE = 'ONE'
    TWO = 'TWO'
    THREE = 'THREE'
    FOUR = 'FOUR'
    FIVE = 'FIVE'
    SIX = 'SIX'
    SEVEN = 'SEVEN'
    EIGHT = 'EIGHT'
    NINE = 'NINE'
    SKIP = 'SKIP'
    REVERSE = 'REVERSE'
    PLUS_TWO = 'PLUS_TWO'
    WILD = 'WILD'
    PLUS_FOUR = 'PLUS_FOUR'

    @classmethod
    def numbers(cls):
        cards = [
            cls.ONE,
            cls.TWO,
            cls.THREE,
            cls.FOUR,
            cls.FIVE,
            cls.SIX,
            cls.SEVEN,
            cls.EIGHT,
            cls.NINE,
        ] * 2
        cards.append(cls.ZERO)
        return cards

    @classmethod
    def specials(cls):
        return [cls.SKIP, cls.REVERSE, cls.PLUS_TWO]

    @classmethod
    def black_cards(cls):
        return [cls.WILD, cls.PLUS_FOUR]

    @classmethod
    def color_card_types(cls):
        return cls.numbers() + cls.specials() * 2


class CardColors(enum.Enum):
    BLUE = 'BLUE'
    GREEN = 'GREEN'
    RED = 'RED'
    YELLOW = 'YELLOW'
    BLACK = 'BLACK'
