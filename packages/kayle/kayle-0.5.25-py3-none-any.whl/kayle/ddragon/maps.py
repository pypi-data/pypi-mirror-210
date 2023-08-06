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
                10: "BOT-BASE-BLUE",
                20: "TOP-BASE-RED",
                30: "TOP-LANE-BLUE",
                40: "TOP-LANE-NEUTRAL",
                50: "TOP-LANE-RED",
                60: "MID-LANE-BLUE",
                70: "MID-LANE-NEUTRAL",
                80: "MID-LANE-RED",
                90: "BOT-LANE-BLUE",
                100: "BOT-LANE-NEUTRAL",
                110: "BOT-LANE-RED",
                120: "TOP-JUNGLE-BLUE",
                130: "TOP-JUNGLE-RED",
                140: "BOT-JUNGLE-BLUE",
                150: "BOT-JUNGLE-RED",
                160: "TOP-RIVER-NEUTRAL",
                170: "BOT-RIVER-NEUTRAL"
            }
            image_width, image_height = map.areas.size
            x, y = (position.normalized.x * image_width, image_height - (position.normalized.y * image_height))
            x, y = round(x), round(y)
            print(x, y)
            rgb = map.areas.load()[x, y]
            if rgb[0] not in color_mapping:
                rgb = map.areas.load()[x + 1, y + 1]
            cmap = color_mapping[rgb[0]]
            self.area_code = cmap

            if self.area_code is not None:
                self.vertical_side, self.area_type, self.side = self.area_code.split("-")
        else:
            self.defined = False
