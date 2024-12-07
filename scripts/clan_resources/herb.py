import ujson


class Herb:
    def __init__(
            self,
            herb_name,
            season,
            biome
            ):
        self.herb_name: str = herb_name
        self.herb_dict: dict = HERBS.get(self.herb_name, {})

        self.clan_biome: str = season.casefold()
        self.game_season: str = biome.casefold()

        self.display_dict = self.herb_dict.get("display", {})
        self.singular_display = self.display_dict.get("singular", self.herb_name)
        self.plural_display = self.display_dict.get("plural", self.herb_name)

        self.expiration: int = self.herb_dict.get("expiration", 1)

    @property
    def rarity(self):
        """
        rarity of the herb within clan's current biome and season
        """
        rarity_dict = self.herb_dict.get("rarity", {})

        return rarity_dict.get(self.clan_biome, {}).get(self.game_season, 0)


with open("resources/dicts/herbs.json", "r", encoding="utf-8") as read_file:
    HERBS = ujson.loads(read_file.read())