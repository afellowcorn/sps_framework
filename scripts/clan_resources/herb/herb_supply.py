from random import choice, randint, choices

import ujson

from scripts.cat.cats import ILLNESSES, INJURIES, PERMANENT
from scripts.cat.skills import SkillPath
from scripts.clan_resources.herb.herb import Herb
from scripts.clan_resources.herb.herb_effects import HerbEffect
from scripts.clan_resources.supply import Supply
from scripts.game_structure.game_essentials import game
from scripts.utility import adjust_list_text, get_alive_status_cats


class HerbSupply:
    """Handles managing the Clan's herb supply."""

    def __init__(self,
                 herb_supply: dict = None
                 ):
        """
        Initialize the class
        """
        # a dict of current stored herbs - herbs collected this moon
        self.stored: dict = herb_supply if herb_supply else {}

        # a dict of herbs collected this moon
        self.collected: dict = {}

        # herb count required for clan
        self.required_herb_count: int = 0

        self.herb = {}
        for name in HERBS:
            self.herb[name] = Herb(
                name,
                biome=game.clan.biome,
                season=game.clan.current_season
            )

        # med den log for current moon
        self.log = []

    @property
    def sorted_by_lowest(self) -> list:
        """
        returns list of herbs ordered from the least supply to most
        """
        sort_list = [x for x in self.stored]
        sort_list.sort(key=lambda list_herb: self.get_single_herb_total(list_herb) + self.collected[list_herb])

        return sort_list

    @property
    def supply_total(self) -> int:
        """
        return total int of all herb inventory
        """
        total = 0
        for herb in self.stored:
            for stock in self.stored[herb]:
                total += stock
        for herb in self.collected:
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

    def handle_moon(self, clan_size: int, clan_cats: list, med_cats: list):
        """
        handle herbs on moon skip: add collected to supply, use herbs where needed, expire old herbs, look for new herbs
        """
        # clear log
        self.log = []

        # set herb count
        self.required_herb_count = clan_size * 2

        # TODO: this is where CAMP cats should have a chance to "combine" clumps to postpone expiration
        # add herbs acquired last moon
        for herb in self.collected:
            self.stored.get(herb, []).insert(0, self.collected[herb])

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
            self._use_herbs(kitty)

        # remove expired herbs
        for herb_name in self.stored.copy():
            expired = []
            if len(self.stored[herb_name]) > self.herb[herb_name].expiration:
                expired.append(self.herb[herb_name])
                self.stored.pop(-1)

            # add log entry to inform player of removal
            if expired:
                self.log.append(
                    f"It was discovered that some stores of "
                    f"{adjust_list_text([herb.plural_display for herb in expired])} "
                    f"were too old to be of use anymore.")

        # TODO: this is where we should handle looking for new herbs that moon
        for meddie in med_cats:
            herbs_gathered = self._gather_herbs(meddie)

    def get_supply_rating(self):
        """
        returns the rating of given supply, aka how "full" the supply is compared to clan size
        """
        rating = None
        for single_herb in self.stored:
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

    def get_herb_rating(self, herb):
        """
        returns the rating of given herb, aka how "full" the supply is compared to clan size
        """

        total = self.get_single_herb_total(herb)
        if self.low_qualifier < total <= self.adequate_qualifier:
            return Supply.LOW
        elif self.adequate_qualifier < total <= self.full_qualifier:
            return Supply.ADEQUATE
        elif self.full_qualifier < total <= self.excess_qualifier:
            return Supply.FULL
        elif self.excess_qualifier < total:
            return Supply.EXCESS

    def get_single_herb_total(self, herb: str) -> int:
        """
        returns int total stock of given herb
        """
        total = 0
        for stock in self.stored[herb]:
            total += stock

        for amt in self.collected[herb]:
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
        if self.collected.get(herb, []):
            self.collected[herb] += num_collected
        else:
            self.collected[herb] = num_collected

    def remove_herb(self, herb: str, num_removed: int):
        """
        removes given amount of given herb from the oldest supply first, then collection for that moon
        :param herb: herb to remove
        :param num_removed: POSITIVE number of herbs to remove
        """
        surplus = self._remove_from_supply(herb, num_removed)

        if surplus and self.collected.get(herb, []):
            self.collected[herb] -= surplus
            if self.collected[herb] < 0:
                self.collected[herb] = 0

    def _use_herbs(self, treatment_cat):
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

                self.__apply_herb_effect(treatment_cat, condition, herb_used, chosen_effect, amount_used)

    def _gather_herbs(self, meddie):
        """
        returns the herbs that an individual med cat gathered during moon skip
        """

        # meds with relevant skills will get a boost to the herbs they find
        # SENSE finds larger amount of herbs
        # CLEVER finds greater quantity of herbs
        primary = meddie.skills.primary_path
        secondary = meddie.skills.secondary_path
        amount_modifier = 1
        quantity_modifier = 1

        if primary == SkillPath.SENSE:
            amount_modifier = 3
        elif primary == SkillPath.CLEVER:
            quantity_modifier = 3

        if secondary == SkillPath.SENSE:
            amount_modifier = 2
        elif secondary == SkillPath.CLEVER:
            quantity_modifier = 2

        # list of the herbs, sorted by lowest currently stored
        herb_list = self.sorted_by_lowest

        # dict where key is herb name and value is the quantity found of that herb
        found_herbs = {}

        # the amount of herb types the med has found
        amount_of_herbs = choices(population=[1, 2, 3], weights=[3, 2, 1], k=1)[0] + amount_modifier

        # now we find what herbs have actually been found and their quantity
        for herb in herb_list:
            if amount_of_herbs == 0:
                break

            # rarity is set to 0 if the herb can't be found in the current season
            if not self.herb[herb].rarity:
                continue

            # chance to find a herb is based on it's rarity
            if randint(1, self.herb[herb].rarity) == 1:
                found_herbs[herb] = choices(population=[1, 2, 3], weights=[3, 2, 1], k=1)[0] * quantity_modifier
                amount_of_herbs -= 1

        if found_herbs:
            list_of_herb_strs = []
            for herb, count in found_herbs.items():
                if count > 1:
                    list_of_herb_strs.append(f"{count} {self.herb[herb].plural_display}")
                else:
                    list_of_herb_strs.append(f"{count} {self.herb[herb].singular_display}")

            self.log.append(f"{meddie.name} collected {adjust_list_text(list_of_herb_strs)} during this moon.")
        else:
            self.log.append(f"{meddie.name} didn't collect any herbs this moon.")

    def _remove_from_supply(self, herb: str, needed_num: int) -> int:
        """
        removes needed_num of given herb from supply until needed_num is met or supply is empty, if supply runs out
        before needed_num is met, returns excess
        """
        while needed_num > 0 and self.stored[herb]:
            # remove from oldest stock
            self.stored[herb][-1] -= needed_num
            # if that stock runs out, move to next oldest stock
            if self.stored[herb][-1] < 0:
                needed_num = abs(self.stored[herb][-1])
                self.stored[herb].pop(-1)

        return needed_num

    @staticmethod
    def __apply_herb_effect(treated_cat, condition, herb_used, effect, amount_used):
        # TODO: you'll need herb_used for determining strength

        # grab the correct condition dict so that we can modify it
        if condition in treated_cat.illnesses:
            con_info = treated_cat.illnesses[condition]
        elif condition in treated_cat.injuries:
            con_info = treated_cat.injuries[condition]
        else:
            con_info = treated_cat.permanent_condition[condition]

        # TODO: hook this up to the herb strength for that condition
        strength_modifier = 1
        amt_modifier = int(amount_used * 1.5)

        # apply mortality effect
        if effect == HerbEffect.MORTALITY:
            con_info[effect] += (
                    3 * strength_modifier + amt_modifier
            )

        # apply duration effect
        elif effect == HerbEffect.DURATION:
            # duration doesn't get amt_modifier, as that would be far too strong an affect
            con_info[effect] -= (
                    1 * strength_modifier
            )
            if con_info["duration"] < 0:
                con_info["duration"] = 0

        # apply risk effect
        elif effect == HerbEffect.RISK:
            for risk in con_info[effect]:
                con_info[risk]["chance"] += (
                        3 * strength_modifier + amt_modifier
                )

        # TODO: set up the effect log messages


with open("resources/dicts/herbs.json", "r", encoding="utf-8") as read_file:
    HERBS = ujson.loads(read_file.read())
