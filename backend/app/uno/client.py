"""UNO GAME LOGIC
inspired by https://github.com/bennuttall/uno
"""
from __future__ import annotations

import logging
import random
from itertools import chain, product, repeat
from typing import Optional
from . import enums
from . import schemas


_game_sessions = {}
logger = logging.getLogger(__name__)


class UnoCard:
    color: enums.CardColors
    suit: enums.CardSuits

    def __init__(self, color: enums.CardColors, suit: enums.CardSuits):
        self.color = color
        self.suit = suit

    def __eq__(self, other: UnoCard):
        if not isinstance(other, UnoCard):
            return False

        if all([
            self.color == other.color,
            self.suit == other.suit,
        ]):
            return True

        return False

    def __hash__(self):
        return hash(str(self))

    def __contains__(self, item):
        return self == item

    def __str__(self):
        return f'{self.color}:{str(self.suit)}'


class UNOPlayer:
    user_id = None
    cards: list[UnoCard] = None

    def __init__(self, user_id: str, cards: list[UnoCard]):
        self.user_id = user_id
        self.cards = cards

    def has_card(self, card):
        if card in self.cards:
            return True

        return False

    def drop_card(self, card):

        for temp_card in self.cards:
            if temp_card == card:
                self.cards.remove(temp_card)
                return temp_card

        raise ValueError(f'Card {card} not found in player\'s {self.user_id} hand')

    def get_cards(self):

        return [str(card) for card in self.cards]


class CardDeck:
    _cards: list[UnoCard] = None
    _played_cards: list[UnoCard] = []

    def __init__(self):
        self.build_deck()

    def build_deck(self):
        """Builds the deck according to values & colours."""
        color_cards = product(enums.CardColors, enums.CardSuits.color_card_types())
        black_cards = product(repeat(enums.CardColors.BLACK, 4), enums.CardSuits.black_cards())
        all_cards = chain(color_cards, black_cards)
        deck = [UnoCard(color, card_type) for color, card_type in all_cards]
        random.shuffle(deck)
        self._cards = deck
        return deck

    def get_card(self):
        if self._cards:
            return self._cards.pop()
        else:
            new_deck = self._played_cards[-2:-1]
            random.shuffle(new_deck)
            self._cards = new_deck
            self._played_cards = self._played_cards[-1:]
            return self._cards.pop()

    def deal_hand(self):
        """
        Return a list of 7 cards from the top of the deck, and remove these
        from the deck.
        """
        return [self.get_card() for _ in range(7)]

    def play_card(self, card):
        """Play card."""
        return self._played_cards.append(card)

    @property
    def last_played_card(self) -> Optional[UnoCard]:
        try:
            return self._played_cards[-1]
        except IndexError:
            return None

    def playable(self, card: UnoCard):
        try:
            return any([
                self.last_played_card is None,
                self.last_played_card.suit == card.suit,
                self.last_played_card.color == card.color,
            ])
        except AttributeError:
            return True


class UNOGameCycle:
    """
    Represents an interface to an iterable which can be infinitely cycled (like
    itertools.cycle), and can be reversed.
    Starts at the first item (index 0), unless reversed before first iteration,
    in which case starts at the last item.
    iterable: any finite iterable
    >>> rc = UNOGameCycle(range(3))
    >>> next(rc)
    0
    >>> next(rc)
    1
    >>> rc.reverse()
    >>> next(rc)
    0
    >>> next(rc)
    2
    """
    def __init__(self, iterable):
        self._items = list(iterable)
        self._pos = None
        self._reverse = False

    def __next__(self):
        if self.pos is None:
            self.pos = -1 if self._reverse else 0
        else:
            self.pos = self.pos + self._delta
        return self._items[self.pos]

    @property
    def _delta(self):
        return -1 if self._reverse else 1

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value % len(self._items)

    def reverse(self):
        """
        Reverse the order of the iterable.
        """
        self._reverse = not self._reverse


class UnoGame:
    players: dict[int, UNOPlayer] = None
    match_id: str = None
    _deck: CardDeck
    _winner = None
    max_players: int = 4
    _current_player: UNOPlayer

    def __init__(self, player_ids, match_id: str):
        self.match_id = match_id
        self._deck = CardDeck()
        self.players = dict()

        for player_id in player_ids:
            self.players[player_id] = UNOPlayer(player_id, self._deck.deal_hand())

        self._player_cycle = UNOGameCycle(self.players.values())
        self._current_player = next(self._player_cycle)
        temp_card = self._current_player.cards[-1]
        self.play_card(self._current_player.user_id, card_raw={
            'suit': temp_card.suit,
            'color': temp_card.color,
            'new_color': random.choice(list(enums.CardColors)),
        })
        self._winner = None

    def __next__(self):
        """
        Iteration sets the current player to the next player in the cycle.
        """
        self._current_player = next(self._player_cycle)

    @property
    def winner(self):
        return self._winner

    @property
    def current_card(self):
        return self._deck.last_played_card

    @property
    def is_active(self):
        return all(len(player.cards) > 0 for player in self.players.values())

    @property
    def current_player(self):
        return self._current_player

    def validate_player_turn(self, player: UNOPlayer):
        if self.current_player != player:
            raise ValueError('Invalid player: not their turn')

    def _validate_player_id(self, player_id: int):
        if not isinstance(player_id, int):
            raise ValueError('Invalid player id: should be the index number')

    def match_player(self, player_id: int) -> UNOPlayer:
        self._validate_player_id(player_id)

        player = self.players.get(player_id, None)

        if player:
            return player
        else:
            raise ValueError(
                f'Player with id {player_id} not found in current match {self.match_id}',
            )

    def match_card(self, card) -> Optional[UnoCard]:
        validated_data =  schemas.UnoCardModel(**card)

        if not validated_data.color and not validated_data.suit:
            return None

        return UnoCard(
            color=validated_data.color,
            suit=validated_data.suit,
        )

    def play_card(self, player_id, card_raw=None, new_color=None):
        """Process the player playing a card.
        player: int representing player index number
        card: int representing index number of card in player's hand
        It must be player's turn, and if card is given, it must be playable.
        If card is not given (None), the player picks up a card from the deck.
        If game is over, raise an exception.
        """

        if not self.is_active:
            raise ValueError('Game is over')

        _player = self.match_player(player_id)

        self.validate_player_turn(_player)

        card = self.match_card(card_raw)

        if card is None:
            self._pick_up(_player, 1)
            next(self)
            return

        if not _player.has_card(card):
            logger.warning(
                'Exception during player\'s card validation, '
                f'attempted card {card.color}: {card.suit}',
                f'user cards {[str(user_card) for user_card in self.current_player.cards]}',
            )
            raise ValueError(
                f'Player does not have such card {card.color}: {card.suit}'
            )

        if not self._deck.playable(card):
            raise ValueError(
                'Invalid card: {} not playable on {}'.format(
                    card, self.current_card
                )
            )

        if card.color == enums.CardColors.BLACK:
            if not new_color:
                raise ValueError(f'New color is not passed to a function {new_color = }')

            if new_color not in enums.CardColors:
                raise ValueError(
                    'Invalid new_color: must be red, yellow, green or blue'
                )

        played_card = _player.drop_card(card)
        self._deck.play_card(played_card)

        card_color = played_card.color
        card_type = played_card.suit

        if card_color == 'black':
            self.current_card.temp_color = new_color

            if card_type == '+4':
                next(self)
                self._pick_up(self.current_player, 4)

        elif card_type == 'reverse':
            self._player_cycle.reverse()

        elif card_type == 'skip':
            next(self)

        elif card_type == '+2':
            next(self)
            self._pick_up(self.current_player, 2)

        if self.is_active:
            next(self)
        else:
            self._winner = _player
            self._print_winner()

    def _pick_up(self, player: UNOPlayer, n: int):
        """Take n cards from the bottom of the deck and add it to the player's hand.

            player: UnoPlayer
            n: int
        """
        penalty_cards = [self._deck.get_card() for _ in range(n)]
        player.cards += penalty_cards

    def _print_winner(self):
        """Take n cards from the bottom of the deck and add it to the player's hand.

            player: UnoPlayer
            n: int
        """
        print(self._winner)


class UnoDriver:
    game: UnoGame = None

    def __init__(self, player_ids: list[str], match_id: str):
        self.game = UnoGame(player_ids, match_id)
        _game_sessions[match_id] = self.game

    def __call__(self, *args, **kwargs):
        self.game.play_card()
