import os

from PIL import Image
from munch import DefaultMunch


class Map:
    def __init__(self, min_x=-120, min_y=-120, max_x=14870, max_y=14980, name="Summoner's Rift"):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.name = name
        match name:
            case "Summoner's Rift":
                script_dir = os.path.dirname(__file__)
                rel_path = os.path.join(os.path.join('..', 'resources'), 'summonersRiftAreas.png')
                self.areas: Image = Image.open(os.path.join(script_dir, rel_path))
            case _:
                self.areas = None


maps = {
    11: Map(min_x=-120, min_y=-120, max_x=14870, max_y=14980, name="Summoner's Rift"),
    1: Map(min_x=-120, min_y=-120, max_x=14870, max_y=14980, name="Summoner's Rift")
}


class Position:
    def __init__(self, position_data, map: Map):
        self.absolute = position_data
        try:
            self.normalized = DefaultMunch.fromDict({
                "x": (position_data["x"] - map.min_x) / map.max_x,
                "y": (position_data["y"] - map.min_y) / map.max_y,
            })
            self.area = Area(self, map)
        except Exception as e:
            raise e
            # print(position_data)
            self.normalized = None


class Area:
    def __init__(self, position: Position, map: Map):
        if map.areas is not None and map.name == "Summoner's Rift":
            self.defined = True
            color_mapping = {
                0: None,
                10: "BOT-BASE-Blue",
                20: "TOP-BASE-Red",
                30: "TOP-LANE-Blue",
                40: "TOP-LANE-Neutral",
                50: "TOP-LANE-Red",
                60: "MID-LANE-Blue",
                70: "MID-LANE-Neutral",
                80: "MID-LANE-Red",
                90: "BOT-LANE-Blue",
                100: "BOT-LANE-Neutral",
                110: "BOT-LANE-Red",
                120: "TOP-JUNGLE-Blue",
                130: "TOP-JUNGLE-Red",
                140: "BOT-JUNGLE-Blue",
                150: "BOT-JUNGLE-Red",
                160: "TOP-RIVER-Neutral",
                170: "BOT-RIVER-Neutral"
            }
            image_width, image_height = map.areas.size
            x, y = (position.normalized.x * image_width, image_height - (position.normalized.y * image_height))
            x, y = round(x), round(y)
            rgb = map.areas.load()[x, y]
            if rgb[0] not in color_mapping:
                x = x + 3
                rgb = map.areas.load()[x, y]
                if rgb[0] not in color_mapping:
                    y = y + 3
                    rgb = map.areas.load()[x, y]
            cmap = color_mapping[rgb[0]]
            self.area_code = cmap

            if self.area_code is not None:
                self.vertical_side, self.area_type, self.side = self.area_code.split("-")
        else:
            self.defined = False
