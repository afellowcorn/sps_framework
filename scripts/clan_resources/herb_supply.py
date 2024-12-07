from random import choice, randint

import ujson

from scripts.clan_resources.herb import Herb
from scripts.clan_resources.supply import Supply
from scripts.game_structure.game_essentials import game


class HerbSupply:
    """Handles managing the Clan's herb supply."""

    def __init__(self,
                 herb_supply: dict = None
                 ):
        """
        Initialize the class
        """
        # a dict of current stored herbs - herbs collected this moon
        self.herb_supply: dict = herb_supply if herb_supply else {}

        # a dict of herbs collected this moon
        self.herbs_collected: dict = {}

        # herb count required for clan
        self.required_herb_count: int = 0

        self.herb = {}
        for name in HERBS:
            self.herb[name] = Herb(
                name,
                biome=game.clan.biome,
                season=game.clan.current_season
            )

    @property
    def lowest_supply(self) -> str:
        """
        returns the herb with the lowest current supply + collected
        """

        # just getting a starting number I know will be higher than any herb's stock
        lowest_total = self.supply_total
        chosen_herb = None

        for herb in self.herb_supply:
            if self.get_single_herb_total(herb) + self.herbs_collected[herb] < lowest_total:
                chosen_herb = herb

        return chosen_herb

    @property
    def supply_total(self) -> int:
        """
        return total int of all herb inventory
        """
        total = 0
        for herb in self.herb_supply:
            for stock in self.herb_supply[herb]:
                total += stock
        for herb in self.herbs_collected:
            total += herb

        return total

    @property
    def low_qualifier(self) -> int:
        """
        returns the lowest qualifier for a low supply
        """
        return 0

    @property
    def adequate_qualifier(self) -> int:
        """
        returns the lowest qualifier for an adequate supply
        """
        return round(self.required_herb_count / 2)

    @property
    def full_qualifier(self) -> int:
        """
        returns the lowest qualifier for a full supply
        """
        return self.required_herb_count

    @property
    def excess_qualifier(self) -> int:
        """
        returns the lowest qualifier for an adequate supply
        """
        return self.required_herb_count * 2

    def get_supply_rating(self, all_herbs: bool = True, herb: str = None):
        """
        returns the rating of given supply, aka how "full" the supply is compared to clan size
        :param all_herbs: if true, returns rating of entire herb supply
        :param herb: if str name of herb is given, returns rating of that herb's supply
        """
        if all_herbs:
            rating = None
            for single_herb in self.herb_supply:
                total = self.get_single_herb_total(single_herb)
                if self.low_qualifier < total <= self.adequate_qualifier and rating not in [Supply.ADEQUATE,
                                                                                            Supply.FULL,
                                                                                            Supply.EXCESS]:
                    rating = Supply.LOW
                elif self.adequate_qualifier < total <= self.full_qualifier and rating not in [Supply.FULL,
                                                                                               Supply.EXCESS]:
                    rating = Supply.ADEQUATE
                elif self.full_qualifier < total <= self.excess_qualifier and rating != Supply.EXCESS:
                    rating = Supply.EXCESS
            return rating

        else:
            total = self.get_single_herb_total(herb)
            if self.low_qualifier < total <= self.adequate_qualifier:
                return Supply.LOW
            elif self.adequate_qualifier < total <= self.full_qualifier:
                return Supply.ADEQUATE
            elif self.full_qualifier < total <= self.excess_qualifier:
                return Supply.FULL
            elif self.excess_qualifier < total:
                return Supply.EXCESS

    def handle_moon(self, clan_size):
        """
        handle cycling of herbs during moon skip
        """
        # set herb count
        self.required_herb_count = clan_size * 2

        # add herbs acquired last moon
        for herb in self.herbs_collected:
            self.herb_supply.get(herb, []).insert(0, self.herbs_collected[herb])

        # remove expired herbs
        # TODO: consider how to inform player of expiration
        for herb in self.herb_supply.copy():
            if len(self.herb_supply[herb]) > HERBS[herb]["expiration"]:
                self.herb_supply.pop(-1)

    def get_single_herb_total(self, herb: str) -> int:
        """
        returns int total stock of given herb
        """
        total = 0
        for stock in self.herb_supply[herb]:
            total += stock

        for amt in self.herbs_collected[herb]:
            total += amt

        return total

    def add_herb(self, herb: str, num_collected: int):
        """
        adds herb given to count for that moon
        """
        if self.herbs_collected.get(herb, []):
            self.herbs_collected[herb] += num_collected
        else:
            self.herbs_collected[herb] = num_collected

    def remove_herb(self, herb: str, num_removed: int):
        """
        removes herb given from count for that moon, then from supply if necessary
        """
        surplus = 0

        if self.herbs_collected.get(herb, []):
            self.herbs_collected[herb] += num_removed
            if self.herbs_collected[herb] < 0:
                num_removed = abs(self.herbs_collected[herb])
                self.herbs_collected[herb] = 0
            else:
                return

        if num_removed:
            self._get_from_supply(herb, num_removed)

    def _get_from_supply(self, herb: str, needed_num: int):
        """
        removes needed_num of given herb from supply until needed_num is met or supply is empty
        """
        while needed_num > 0 and self.herb_supply[herb]:
            self.herb_supply[herb][-1] -= needed_num
            if self.herb_supply[herb][-1] > 0:
                needed_num = abs(self.herb_supply[herb][-1])
                self.herb_supply[herb].pop(-1)


with open("resources/dicts/herbs.json", "r", encoding="utf-8") as read_file:
    HERBS = ujson.loads(read_file.read())
