import ujson
import i18n

from scripts.game_structure.localization import load_lang_resource


class Herb:
    def __init__(
            self,
            herb_name,
            season,
            biome
    ):
        self.name: str = herb_name
        self._herb_dict: dict = HERBS.get(self.name, {})

        self._display_dict = self._herb_dict.get("display", {})
        self.singular_display = i18n.t(
            f"conditions.herbs.{self.name}",
            count=1,
        )
        self.plural_display = i18n.t(
            f"conditions.herbs.{self.name}",
            count=2,
        )

        self.expiration: int = self._herb_dict.get("expiration", 1)

    def get_rarity(self, biome, season) -> int:
        """
        returns rarity of the herb within clan's current biome and season
        """
        rarity_dict = self._herb_dict.get("rarity", {})

        return rarity_dict.get(biome.casefold(), {}).get(season.casefold(), 0)


HERBS = load_lang_resource("herb_info.json")

