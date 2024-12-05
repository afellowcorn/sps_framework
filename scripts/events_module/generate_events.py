#!/usr/bin/env python3
# -*- coding: ascii -*-
import random

import ujson
import re

from scripts.events_module.ongoing.ongoing_event import OngoingEvent
from scripts.events_module.short.short_event import ShortEvent
from scripts.game_structure.game_essentials import game
from scripts.utility import (
    filter_relationship_type,
    get_living_clan_cat_count,
    get_alive_status_cats,
)

resource_directory = "resources/dicts/events/"


# ---------------------------------------------------------------------------- #
#                Tagging Guidelines can be found at the bottom                 #
# ---------------------------------------------------------------------------- #


class GenerateEvents:
    loaded_events = {}

    INJURY_DISTRIBUTION = None
    with open(
            f"resources/dicts/conditions/event_injuries_distribution.json", "r"
    ) as read_file:
        INJURY_DISTRIBUTION = ujson.loads(read_file.read())

    INJURIES = None
    with open(f"resources/dicts/conditions/injuries.json", "r") as read_file:
        INJURIES = ujson.loads(read_file.read())

    @staticmethod
    def get_short_event_dicts(file_path):
        try:
            with open(
                    file_path,
                    "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load {file_path}.")
            return None

        return events

    @staticmethod
    def get_ongoing_event_dicts(file_path):
        events = None
        try:
            with open(
                    file_path,
                    "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load events from biome {file_path}.")

        return events

    @staticmethod
    def get_death_reaction_dicts(family_relation, rel_value):
        try:
            file_path = f"{resource_directory}/death/death_reactions/{family_relation}/{family_relation}_{rel_value}.json"
            with open(
                    file_path,
                    "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            events = None
            print(
                f"ERROR: Unable to load death reaction events for {family_relation}_{rel_value}."
            )
        return events

    @staticmethod
    def get_lead_den_event_dicts(event_type: str, success: bool):
        try:
            file_path = f"{resource_directory}/leader_den/{'success' if success else 'fail'}/{event_type}.json"
            with open(file_path, "r") as read_file:
                events = ujson.loads(read_file.read())
        except:
            events = None
            print(
                f"ERROR: Unable to load lead den events for {event_type} {'success' if success else 'fail'}."
            )

        return events

    @staticmethod
    def clear_loaded_events():
        GenerateEvents.loaded_events = {}

    @staticmethod
    def generate_short_events(event_triggered, biome):
        file_path = f"{resource_directory}{event_triggered}/{biome}.json"

        try:
            if file_path in GenerateEvents.loaded_events:
                return GenerateEvents.loaded_events[file_path]
            else:
                events_dict = GenerateEvents.get_short_event_dicts(file_path)

                event_list = []
                if not events_dict:
                    return event_list
                for event in events_dict:
                    event_text = event["event_text"] if "event_text" in event else None
                    if not event_text:
                        event_text = (
                            event["death_text"] if "death_text" in event else None
                        )

                    if not event_text:
                        print(
                            f"WARNING: some events resources which are used in generate_events have no 'event_text'."
                        )
                    event = ShortEvent(
                        event_id=event["event_id"] if "event_id" in event else "",
                        location=event["location"] if "location" in event else ["any"],
                        season=event["season"] if "season" in event else ["any"],
                        sub_type=event["sub_type"] if "sub_type" in event else [],
                        tags=event["tags"] if "tags" in event else [],
                        weight=event["weight"] if "weight" in event else 20,
                        text=event_text,
                        new_accessory=event["new_accessory"]
                        if "new_accessory" in event
                        else [],
                        m_c=event["m_c"] if "m_c" in event else {},
                        r_c=event["r_c"] if "r_c" in event else {},
                        new_cat=event["new_cat"] if "new_cat" in event else [],
                        injury=event["injury"] if "injury" in event else [],
                        history=event["history"] if "history" in event else [],
                        relationships=event["relationships"]
                        if "relationships" in event
                        else [],
                        outsider=event["outsider"] if "outsider" in event else {},
                        other_clan=event["other_clan"] if "other_clan" in event else {},
                        supplies=event["supplies"] if "supplies" in event else [],
                        new_gender=event["new_gender"] if "new_gender" in event else []
                    )
                    event_list.append(event)

                # Add to loaded events.
                GenerateEvents.loaded_events[file_path] = event_list
                return event_list
        except:
            print(f"WARNING: {file_path} was not found, check short event generation")

    @staticmethod
    def generate_ongoing_events(event_type, biome, specific_event=None):
        file_path = f"resources/dicts/events/{event_type}/{biome}.json"

        if file_path in GenerateEvents.loaded_events:
            return GenerateEvents.loaded_events[file_path]
        else:
            events_dict = GenerateEvents.get_ongoing_event_dicts(file_path)

            if not specific_event:
                event_list = []
                for event in events_dict:
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        rarity=event["rarity"],
                        trigger_events=event["trigger_events"],
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        secondary_disasters=event["secondary_disasters"],
                        collateral_damage=event["collateral_damage"],
                    )
                    event_list.append(event)
                return event_list
            else:
                event = None
                for event in events_dict:
                    if event["event"] != specific_event:
                        continue
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        collateral_damage=event["collateral_damage"],
                    )
                    break
                return event

    @staticmethod
    def possible_short_events(event_type=None):
        event_list = []

        # skip the rest of the loading if there is an unrecognised biome
        if game.clan.biome not in game.clan.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES "
                f"in clan.py?"
            )

        biome = game.clan.biome.lower()

        # biome specific events
        event_list.extend(GenerateEvents.generate_short_events(event_type, biome))

        # any biome events
        event_list.extend(GenerateEvents.generate_short_events(event_type, "general"))

        return event_list

    def filter_possible_short_events(
            self,
            Cat_class,
            possible_events,
            cat,
            random_cat,
            other_clan,
            freshkill_active,
            freshkill_trigger_factor,
            sub_types=None,
    ):
        final_events = []
        incorrect_format = []

        # Chance to bypass the skill or trait requirements.
        trait_skill_bypass = 15

        # check if generated event should be a war event
        if "war" in sub_types and random.randint(1, 10) == 1:
            sub_types.remove("war")

        for event in possible_events:
            if event.history:
                if (
                        not isinstance(event.history, list)
                        or "cats" not in event.history[0]
                ):
                    if (
                            f"{event.event_id} history formatted incorrectly"
                            not in incorrect_format
                    ):
                        incorrect_format.append(
                            f"{event.event_id} history formatted incorrectly"
                        )
            if event.injury:
                if not isinstance(event.injury, list) or "cats" not in event.injury[0]:
                    if (
                            f"{event.event_id} injury formatted incorrectly"
                            not in incorrect_format
                    ):
                        incorrect_format.append(
                            f"{event.event_id} injury formatted incorrectly"
                        )

            # check for event sub_type
            if set(event.sub_type) != set(sub_types):
                continue

            if not self.event_for_location(event.location):
                continue

            if not self.event_for_season(event.season):
                continue

            # check tags
            if not self.event_for_tags(Cat_class, event.tags, cat):
                continue

            prevent_bypass = "skill_trait_required" in event.tags

            # make complete leader death less likely until the leader is over 150 moons (or unless it's a murder)
            if cat.status == "leader":
                if "all_lives" in event.tags and "murder" not in event.sub_type:
                    if int(cat.moons) < 150 and int(random.random() * 5):
                        continue

            # check for old age
            if (
                    "old_age" in event.sub_type
                    and cat.moons < game.config["death_related"]["old_age_death_start"]
            ):
                continue
            # remove some non-old age events to encourage elders to die of old age more often
            if (
                    "old_age" not in event.sub_type
                    and cat.moons > game.config["death_related"]["old_age_death_start"]
                    and int(random.random() * 3)
            ):
                continue

            # if the event is marked as changing romantic interest, check that the cats are allowed to be romantic
            if random_cat:
                if "romantic" in event.tags and not random_cat.is_potential_mate(cat):
                    continue

            # check if already trans
            if (
                    "transition" in event.sub_type
                    and cat.gender != cat.genderalign
            ):
                continue

            if event.m_c:
                if cat.age not in event.m_c["age"] and "any" not in event.m_c["age"]:
                    continue
                if (
                        cat.status not in event.m_c["status"]
                        and "any" not in event.m_c["status"]
                ):
                    continue
                if event.m_c["relationship_status"]:
                    if not filter_relationship_type(
                            group=[cat, random_cat],
                            filter_types=event.m_c["relationship_status"],
                            event_id=event.event_id,
                    ):
                        continue

                # check cat trait and skill
                if (
                        int(random.random() * trait_skill_bypass) or prevent_bypass
                ):  # small chance to bypass
                    has_trait = False
                    if event.m_c["trait"]:
                        if cat.personality.trait in event.m_c["trait"]:
                            has_trait = True

                    has_skill = False
                    if event.m_c["skill"]:
                        for _skill in event.m_c["skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("Cat skill incorrectly formatted", _skill)
                                continue

                            if cat.skills.meets_skill_requirement(
                                    split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if event.m_c["trait"] and event.m_c["skill"]:
                        if not has_trait or has_skill:
                            continue
                    elif event.m_c["trait"]:
                        if not has_trait:
                            continue
                    elif event.m_c["skill"]:
                        if not has_skill:
                            continue

                    # check cat negate trait and skill
                    has_trait = False
                    if event.m_c["not_trait"]:
                        if cat.personality.trait in event.m_c["not_trait"]:
                            has_trait = True

                    has_skill = False
                    if event.m_c["not_skill"]:
                        for _skill in event.m_c["not_skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("Cat skill incorrectly formatted", _skill)
                                continue

                            if cat.skills.meets_skill_requirement(
                                    split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if has_trait or has_skill:
                        continue

                # check backstory
                if event.m_c["backstory"]:
                    if cat.backstory not in event.m_c["backstory"]:
                        continue

                # check gender for transition events
                if event.m_c["gender"]:
                    if (
                            cat.gender not in event.m_c["gender"]
                            and "any" not in event.m_c["gender"]
                    ):
                        continue

            # check that a random_cat is available to use for r_c
            if event.r_c and random_cat:
                if (
                        random_cat.age not in event.r_c["age"]
                        and "any" not in event.r_c["age"]
                ):
                    continue
                if (
                        random_cat.status not in event.r_c["status"]
                        and "any" not in event.r_c["status"]
                ):
                    continue
                if event.r_c["relationship_status"]:
                    if not filter_relationship_type(
                            group=[cat, random_cat],
                            filter_types=event.r_c["relationship_status"],
                            event_id=event.event_id,
                    ):
                        continue

                # check cat trait and skill
                if (
                        int(random.random() * trait_skill_bypass) or prevent_bypass
                ):  # small chance to bypass
                    has_trait = False
                    if event.r_c["trait"]:
                        if random_cat.personality.trait in event.r_c["trait"]:
                            has_trait = True

                    has_skill = False
                    if event.r_c["skill"]:
                        for _skill in event.r_c["skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("random_cat skill incorrectly formatted", _skill)
                                continue

                            if random_cat.skills.meets_skill_requirement(
                                    split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if event.r_c["trait"] and event.r_c["skill"]:
                        if not has_trait or has_skill:
                            continue
                    elif event.r_c["trait"]:
                        if not has_trait:
                            continue
                    elif event.r_c["skill"]:
                        if not has_skill:
                            continue

                    # check cat negate trait and skill
                    has_trait = False
                    if event.r_c["not_trait"]:
                        if random_cat.personality.trait in event.r_c["not_trait"]:
                            has_trait = True

                    has_skill = False
                    if event.r_c["not_skill"]:
                        for _skill in event.r_c["not_skill"]:
                            split = _skill.split(",")

                            if len(split) < 2:
                                print("random_cat skill incorrectly formatted", _skill)
                                continue

                            if random_cat.skills.meets_skill_requirement(
                                    split[0], int(split[1])
                            ):
                                has_skill = True
                                break

                    if has_trait or has_skill:
                        continue

                # check backstory
                if event.r_c["backstory"]:
                    if random_cat.backstory not in event.r_c["backstory"]:
                        continue

            # check that injury is possible
            if event.injury:
                # determine which injury severity list will be used
                allowed_severity = None
                discard = False
                if cat.status in GenerateEvents.INJURY_DISTRIBUTION:
                    minor_chance = GenerateEvents.INJURY_DISTRIBUTION[cat.status][
                        "minor"
                    ]
                    major_chance = GenerateEvents.INJURY_DISTRIBUTION[cat.status][
                        "major"
                    ]
                    severe_chance = GenerateEvents.INJURY_DISTRIBUTION[cat.status][
                        "severe"
                    ]
                    severity_chosen = random.choices(
                        ["minor", "major", "severe"],
                        [minor_chance, major_chance, severe_chance],
                        k=1,
                    )
                    if severity_chosen[0] == "minor":
                        allowed_severity = "minor"
                    elif severity_chosen[0] == "major":
                        allowed_severity = "major"
                    else:
                        allowed_severity = "severe"

                for block in event.injury:
                    for injury in block["injuries"]:
                        if injury in GenerateEvents.INJURIES:
                            if (
                                    GenerateEvents.INJURIES[injury]["severity"]
                                    != allowed_severity
                            ):
                                discard = True
                                break

                            if "m_c" in block["cats"]:
                                if injury == "mangled tail" and (
                                        "NOTAIL" in cat.pelt.scars
                                        or "HALFTAIL" in cat.pelt.scars
                                ):
                                    continue

                                if injury == "torn ear" and "NOEAR" in cat.pelt.scars:
                                    continue
                            if "r_c" in block["cats"]:
                                if injury == "mangled tail" and (
                                        "NOTAIL" in random_cat.pelt.scars
                                        or "HALFTAIL" in random_cat.pelt.scars
                                ):
                                    continue

                                if (
                                        injury == "torn ear"
                                        and "NOEAR" in random_cat.pelt.scars
                                ):
                                    continue

                if discard:
                    continue

            # check if outsider event is allowed
            if event.outsider:
                if not self.event_for_reputation(event.outsider["current_rep"]):
                    continue

            # other Clan related checks
            if event.other_clan:
                if not other_clan:
                    continue

                if not self.event_for_clan_relations(event.other_clan["current_rep"], other_clan):
                    continue

                # during a war we want to encourage the clans to have positive events
                # when the overall war notice was positive
                if "war" in event.sub_type:
                    rel_change_type = game.switches["war_rel_change_type"]
                    if (
                            event.other_clan["changed"] < 0
                            and rel_change_type != "rel_down"
                    ):
                        continue

            # clans below a certain age can't have their supplies messed with
            if game.clan.age < 5 and event.supplies:
                continue

            elif event.supplies:
                clan_size = get_living_clan_cat_count(Cat_class)
                discard = False
                for supply in event.supplies:
                    trigger = supply["trigger"]
                    supply_type = supply["type"]
                    if supply_type == "freshkill":
                        if not freshkill_active:
                            continue

                        if not self.event_for_freshkill_supply(
                            game.clan.freshkill_pile,
                            trigger,
                            freshkill_trigger_factor,
                            clan_size
                        ):
                            discard = True
                            break
                        else:
                            discard = False

                    else:  # if supply type wasn't freshkill, then it must be a herb type
                        if not self.event_for_herb_supply(trigger, supply_type, clan_size):
                            discard = True
                            break
                        else:
                            discard = False
                        
                if discard:
                    continue

            final_events.extend([event] * event.weight)

        for notice in incorrect_format:
            print(notice)

        return final_events

    @staticmethod
    def possible_ongoing_events(event_type=None, specific_event=None):
        event_list = []

        if game.clan.biome not in game.clan.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?"
            )

        else:
            biome = game.clan.biome.lower()
            if not specific_event:
                event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, biome)
                )
                """event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, "general", specific_event)
                )"""
                return event_list
            else:
                event = GenerateEvents.generate_ongoing_events(
                    event_type, biome, specific_event
                )
                return event

    @staticmethod
    def possible_death_reactions(family_relation, rel_value, trait, body_status):
        possible_events = []
        # grab general events first, since they'll always exist
        events = GenerateEvents.get_death_reaction_dicts("general", rel_value)
        possible_events.extend(events["general"][body_status])
        if trait in events and body_status in events[trait]:
            possible_events.extend(events[trait][body_status])

        # grab family events if they're needed. Family events should not be romantic.
        if family_relation != "general" and rel_value != "romantic":
            events = GenerateEvents.get_death_reaction_dicts(family_relation, rel_value)
            possible_events.extend(events["general"][body_status])
            if trait in events and body_status in events[trait]:
                possible_events.extend(events[trait][body_status])

        return possible_events

    def possible_lead_den_events(
            self,
            cat,
            event_type: str,
            interaction_type: str,
            success: bool,
            other_clan_temper=None,
            player_clan_temper=None,
    ) -> list:
        """
        finds and generates a list of possible leader den events
        :param cat: the cat object of the cat attending the Gathering
        :param other_clan_temper: the temperament of the other clan
        :param player_clan_temper: the temperament of the player clan
        :param event_type: other_clan or outsider
        :param interaction_type: str retrieved from object_ID of selected interaction button
        :param success: True if the interaction was a success, False if it was a failure
        """
        possible_events = []

        events = GenerateEvents.get_lead_den_event_dicts(event_type, success)
        for event in events:
            if event["interaction_type"] != interaction_type:
                continue

            if "other_clan_temper" in event or "player_clan_temper" in event:
                if (
                        other_clan_temper not in event["other_clan_temper"]
                        and "any" not in event["other_clan_temper"]
                ):
                    continue
                if (
                        player_clan_temper not in event["player_clan_temper"]
                        and "any" not in event["player_clan_temper"]
                ):
                    continue

            elif "reputation" in event:
                if not self.event_for_reputation(event["reputation"]):
                    continue

            cat_info = event["m_c"]
            if "status" in cat_info:
                # special lost cat check
                if event_type == "outsider":
                    if cat.status not in [
                        "loner",
                        "rogue",
                        "kittypet",
                        "former Clancat",
                        "exiled",
                    ]:
                        if "lost" not in cat_info["status"]:
                            continue
                    elif (
                            cat.status.casefold() not in [x.casefold() for x in cat_info["status"]]
                            and "any" not in cat_info["status"]
                    ):
                        continue
                elif (
                        cat.status not in cat_info["status"]
                        and "any" not in cat_info["status"]
                ):
                    continue
            if "age" in cat_info:
                if cat.age not in cat_info["age"]:
                    continue
            if "trait" in cat_info:
                if cat.personality.trait not in cat_info["trait"]:
                    continue
            if "skill" in cat_info:
                has_skill = False
                for _skill in cat_info["skill"]:
                    split = _skill.split(",")

                    if len(split) < 2:
                        print("Cat skill incorrectly formatted", _skill)
                        continue

                    if cat.skills.meets_skill_requirement(split[0], int(split[1])):
                        has_skill = True
                        break
                if not has_skill:
                    continue

            possible_events.append(event)

        return possible_events

    def event_for_location(self, locations: list) -> bool:
        """
        checks if the clan is within the given locations
        """
        if "any" in locations:
            return True

        for place in locations:
            if ":" in place:
                info = place.split(":")
                req_biome = info[0]
                req_camps = info[1].split("_")
            else:
                req_biome = place
                req_camps = ["any"]

            if req_biome == game.clan.biome.lower():
                if "any" in req_camps or game.clan.camp_bg in req_camps:
                    return True
                else:
                    return False
            else:
                return False

    def event_for_season(self, seasons: list) -> bool:
        """
        checks if the clan is within the given seasons
        """
        if "any" in seasons:
            return True
        elif game.clan.current_season.lower() in seasons:
            return True
        else:
            return False

    def event_for_tags(self, Cat_class, tags: list, main_cat) -> bool:
        """
        checks if current tags disqualify the event
        """
        # some events are mode specific
        mode = game.clan.game_mode
        possible_modes = ["classic", "expanded", "cruel_season"]
        for _poss in possible_modes:
            if _poss in tags and mode != _poss:
                return False

        # check leader life tags
        if main_cat.status == "leader":
            leader_lives = game.clan.leader_lives

            life_lookup = {
                "some_lives": 4,
                "lives_remain": 2,
                "high_lives": 7,
                "mid_lives": 4,
                "low_lives": 1
            }

            for _con, _val in life_lookup.items():
                if _con in tags and leader_lives < _val:
                    return False

        # check for required ranks within the clan
        for _tag in tags:
            rank_match = re.match(r"clan:(.+)", _tag)
            if not rank_match:
                continue
            ranks = [x for x in rank_match.split(",")]

            for rank in ranks:
                if rank == "apps":
                    if not get_alive_status_cats(
                            Cat_class,
                            ["apprentice", "medicine cat apprentice", "mediator apprentice"]):
                        return False
                    else:
                        continue

                if rank in ["leader", "deputy"] and not get_alive_status_cats(Cat_class, [rank]):
                    return False

                elif not len(get_alive_status_cats(Cat_class, [rank])) >= 2:
                    return False

        # check if main cat will allow for adoption
        if "adoption" in tags:
            if main_cat.no_kits:
                return False
            if main_cat.moons <= 14 + main_cat.age_moons["kitten"][1]:
                return False
            if any(Cat_class.fetch_cat(i).no_kits for i in main_cat.mate):
                return False

        return True

    def event_for_reputation(self, required_rep: list) -> bool:
        """
        checks if the clan has reputation matching required_rep
        """
        if "any" in required_rep:
            return True

        clan_rep = game.clan.reputation

        if "hostile" in required_rep and 0 <= clan_rep <= 30:
            return True
        elif "neutral" in required_rep and 31 <= clan_rep <= 70:
            return True
        elif "welcoming" in required_rep and 71 <= clan_rep:
            return True
        else:
            return False

    def event_for_clan_relations(self, required_rel: list, other_clan) -> bool:
        """
        checks if the clan has clan relations matching required_rel
        """
        if "any" in required_rel:
            return True

        current_rel = other_clan.relations

        if "hostile" in required_rel and 0 <= current_rel <= 6:
            return True
        elif "neutral" in required_rel and 7 <= current_rel <= 17:
            return True
        elif "ally" in required_rel and 18 <= current_rel:
            return True
        else:
            return False

    def event_for_freshkill_supply(self, pile, trigger, factor, clan_size) -> bool:
        """
        checks if clan has the correct amount of freshkill for event
        """
        if game.clan.game_mode == "classic":
            return False

        needed_amount = pile.amount_food_needed()
        half_amount = needed_amount / 2

        if "always" in trigger:
            return True
        if "low" in trigger and half_amount > pile.total_amount:
            return True
        if "adequate" in trigger and half_amount < pile.total_amount < needed_amount:
            return True

        # find how much is too much freshkill
        # it would probably be good to move this section of finding trigger_value to the freshkill class
        divider = 35 if game.clan.game_mode == "expanded" else 20
        factor = factor - round(
            pow((clan_size / divider), 2)
        )
        if factor < 2 and game.clan.game_mode == "expanded":
            factor = 2

        trigger_value = round(factor * needed_amount, 2)

        if "full" in trigger and needed_amount < pile.total_amount < trigger_value:
            return True
        if "excess" in trigger and pile.total_amount > trigger_value:
            return True

        # if it hasn't returned by now, it doesn't qualify
        return False

    def event_for_herb_supply(self, trigger, supply_type, clan_size):
        """
        checks if clan's herb supply qualifies for event
        """
        herb_supply = game.clan.herbs.copy()
        possible_herbs = game.clan.HERBS
        num_of_herbs = len(possible_herbs)

        if not herb_supply and "low" in trigger:
            return True

        for herb in possible_herbs:
            if herb not in herb_supply:
                herb_supply[herb] = 0

        needed_amount = clan_size * 2
        half_amount = needed_amount / 2

        if supply_type == "all_herb":
            if "always" in trigger:
                return True
            elif "low" in trigger and len([x for x in herb_supply if herb_supply[x] < half_amount]) == num_of_herbs:
                return True
            elif "adequate" in trigger and len([x for x in herb_supply if herb_supply[x] < needed_amount]) == num_of_herbs:
                return True
            elif "full" in trigger and len([x for x in herb_supply if herb_supply[x] < needed_amount * 2]) == num_of_herbs:
                return True
            elif "excess" in trigger and len([x for x in herb_supply if needed_amount * 2 < herb_supply[x]]) == num_of_herbs:
                return True
            else:
                return False

        elif supply_type == "any_herb":
            if "always" in trigger:
                return True
            elif "low" in trigger and [x for x in herb_supply if herb_supply[x] < half_amount]:
                return True
            elif "adequate" in trigger and [x for x in herb_supply if herb_supply[x] < needed_amount]:
                return True
            elif "full" in trigger and [x for x in herb_supply if herb_supply[x] < needed_amount * 2]:
                return True
            elif "excess" in trigger and [x for x in herb_supply if needed_amount * 2 < herb_supply[x]]:
                return True
            else:
                return False

        else:
            chosen_herb = supply_type
            if chosen_herb not in possible_herbs:
                print(f"WARNING: possible typo in supply constraint: {chosen_herb}")
                return False
            elif "always" in trigger:
                return True
            elif "low" in trigger and herb_supply[chosen_herb] < half_amount:
                return True
            elif "adequate" in trigger and herb_supply[chosen_herb] < needed_amount:
                return True
            elif "full" in trigger and herb_supply[chosen_herb] < needed_amount * 2:
                return True
            elif "excess" in trigger and needed_amount * 2 < herb_supply[chosen_herb]:
                return True
            else:
                return False















generate_events = GenerateEvents()
