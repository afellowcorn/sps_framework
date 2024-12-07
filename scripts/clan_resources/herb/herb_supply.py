from random import choice, randint

import ujson

from scripts.cat.cats import ILLNESSES, INJURIES, PERMANENT
from scripts.clan_resources.herb.herb import Herb
from scripts.clan_resources.herb.herb_effects import HerbEffect
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

    def handle_moon(self, clan_size, clan_cats):
        """
        handle herbs on moon skip: add collected to supply, use herbs where needed, expire old herbs, look for new herbs
        """
        # set herb count
        self.required_herb_count = clan_size * 2

        # add herbs acquired last moon
        for herb in self.herbs_collected:
            self.herb_supply.get(herb, []).insert(0, self.herbs_collected[herb])

        # TODO: this is where we should handle using herbs
        severity_ranking = {
            "severe": [],
            "major": [],
            "minor": []
        }
        cats_to_treat = [kitty for kitty in clan_cats if kitty.is_ill() or kitty.is_injured() or kitty.is_disabled()]
        for kitty in cats_to_treat:
            severities = []
            conditions = kitty.permeanent_conditions
            conditions.update(kitty.injuries)
            conditions.update(kitty.illnesses)
            for con in conditions:
                severities.append(conditions[con]["severity"])
            if "severe" in severities:
                severity_ranking["severe"].append(kitty)
            elif "major" in severities:
                severity_ranking["major"].append(kitty)
            elif "minor" in severities:
                severity_ranking["minor"].append(kitty)

        treatment_cats = severity_ranking["severe"] + severity_ranking["major"] + severity_ranking["minor"]
        for kitty in treatment_cats:
            self.use_herbs(kitty)

        # remove expired herbs
        # TODO: consider how to inform player of expiration
        for herb_name in self.herb_supply.copy():
            if len(self.herb_supply[herb_name]) > self.herb[herb_name].expiration:
                self.herb_supply.pop(-1)

        # TODO: this is where we should handle looking for new herbs that moon

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

    def get_highest_herb_in_group(self, group) -> str:
        """
        returns the herb in group that has the highest supply
        """
        chosen_herb = group[0]
        highest_supply = 0

        for herb in group:
            total = self.get_single_herb_total(herb)
            if total > highest_supply:
                highest_supply = total
                chosen_herb = herb

        return chosen_herb

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
        removes given amount of given herb from the oldest supply first, then collection for that moon
        :param herb: herb to remove
        :param num_removed: POSITIVE number of herbs to remove
        """
        surplus = self._remove_from_supply(herb, num_removed)

        if surplus and self.herbs_collected.get(herb, []):
            self.herbs_collected[herb] -= surplus
            if self.herbs_collected[herb] < 0:
                self.herbs_collected[herb] = 0

    def use_herbs(self, treatment_cat):
        """
        utilize current herb supply on given condition
        """
        # collate all cat's conditions
        condition_dict = treatment_cat.injuries
        condition_dict.update(treatment_cat.illnesses)
        condition_dict.update(treatment_cat.permanent_condition)

        # collate all the source info for conditions
        source_dict = ILLNESSES
        source_dict.update(INJURIES)
        source_dict.update(PERMANENT)

        for condition in condition_dict:
            # get the herbs that the condition allows as treatment
            try:
                required_herbs = source_dict[condition]["herbs"]
            except KeyError:
                print(
                    f"WARNING: {condition} does not exist in it's condition dict! That condition may have been removed "
                    f"from the game. If not intentional, check that your condition is in the correct dict or report "
                    f"this as a bug. "
                )
                return

            # if condition has no herbs listed, return
            if not required_herbs:
                return

            # find which required herbs the clan currently has
            herbs_available = [herb for herb in required_herbs if self.get_single_herb_total(herb) > 0]

            if herbs_available or game.clan.game_mode == "classic":
                # find the possible effects of herb for the condition
                possible_effects = []
                current_condition_info = condition_dict[condition]

                if current_condition_info.get("mortality", 0):
                    possible_effects.append(HerbEffect.MORTALITY)
                if current_condition_info.get("risks", []):
                    possible_effects.append(HerbEffect.RISK)
                if current_condition_info.get("duration", 0) > 1:
                    possible_effects.append(HerbEffect.DURATION)

                if not possible_effects:
                    return

                chosen_effect = choice(possible_effects)

                herb_used = self.get_highest_herb_in_group(herbs_available)
                total_herb_amount = self.get_single_herb_total(herb_used)

                # TODO: consider making this a flat 1
                amount_used = randint(1, total_herb_amount if total_herb_amount < 4 else 4)

                self.remove_herb(herb_used, amount_used)

                self.apply_herb_effect(treatment_cat, condition, herb_used, chosen_effect, amount_used)

    def apply_herb_effect(self, treated_cat, condition, herb_used, effect, amount_used):

        if condition in treated_cat.illnesses:
            con_info = treated_cat.illnesses[condition]
        elif condition in treated_cat.injuries:
            con_info = treated_cat.injuries[condition]
        else:
            con_info = treated_cat.permanent_condition[condition]

        # TODO: hook this up to the herb strength for that condition
        strength_modifier = 1
        amt_modifier = int(amount_used * 1.5)

        if effect == HerbEffect.MORTALITY:
            con_info[effect] += (
                3 * strength_modifier + amt_modifier
            )
        elif effect == HerbEffect.DURATION:
            # duration doesn't get amt_modifier, as that would be far too strong an affect
            con_info[effect] -= (
                1 * strength_modifier
            )
            if con_info["duration"] < 0:
                con_info["duration"] = 0
        elif effect == HerbEffect.RISK:
            for risk in con_info[effect]:
                con_info[risk]["chance"] += (
                    3 * strength_modifier + amt_modifier
                )

    def _remove_from_supply(self, herb: str, needed_num: int) -> int:
        """
        removes needed_num of given herb from supply until needed_num is met or supply is empty, if supply runs out
        before needed_num is met, returns excess
        """
        while needed_num > 0 and self.herb_supply[herb]:
            # remove from oldest stock
            self.herb_supply[herb][-1] -= needed_num
            # if that stock runs out, move to next oldest stock
            if self.herb_supply[herb][-1] < 0:
                needed_num = abs(self.herb_supply[herb][-1])
                self.herb_supply[herb].pop(-1)

        return needed_num


with open("resources/dicts/herbs.json", "r", encoding="utf-8") as read_file:
    HERBS = ujson.loads(read_file.read())
