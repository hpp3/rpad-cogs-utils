"""
Parses Dungeon and DungeonFloor data.
"""

import csv
from io import StringIO
import json
import os
from typing import List, Any

from ..common import pad_util
from ..common.dungeon_types import DUNGEON_TYPE, REPEAT_DAY

# The typical JSON file name for this data.
FILE_NAME = 'download_dungeon_data.json'


class DungeonFloor(pad_util.JsonDictEncodable):
    """A floor listed once you click into a Dungeon."""

    def __init__(self, raw: List[Any]):
        self.raw = raw

        self.floor_number = int(raw[0])
        self.raw_name = raw[1]
        self.unknown_002 = raw[2]
        self.unknown_003 = raw[3]
        self.stamina = raw[4]
        self.unknown_005 = raw[5]
        self.unknown_006 = raw[6]
        self.unknown_007 = raw[7]
        self.unknown_008 = raw[8]
        self.unknown_009 = raw[9]
        self.unknown_010 = raw[10]


prefix_to_dungeontype = {
    # #G#Ruins of the Star Vault 25
    '#G#': 'guerrilla',

    # #1#Star Treasure of the Night Sky 25
    '#1#': 'unknown-1',

    # #C#Rurouni Kenshin dung
    '#C#': 'collab',
}


class Dungeon(pad_util.JsonDictEncodable):
    """A top-level dungeon."""

    def __init__(self, raw: List[Any]):
        self.floors = []  # type: List[DungeonFloor]

        self.dungeon_id = int(raw[0])
        self.name = str(raw[1])
        self.unknown_002 = int(raw[2])

        self.clean_name = pad_util.strip_colors(self.name)

        # Using DUNGEON TYPES file in common.dungeon_types
        self.alt_dungeon_type = DUNGEON_TYPE[int(raw[3])]

        # Temporary hack. The newly added 'Guerrilla' type doesn't seem to be correct, and that's
        # the only type actively in use. Using the old logic for now.
        self.dungeon_type = None

        # I call it comment as it is similar to dungeon_type, but sometimes designates certain dungeons specifically
        # over others. See dungeon_types.py for more details.
        self.dungeon_comment = pad_util.get_dungeon_comment(int(raw[5]))

        # This will be a day of the week, or an empty string if it doesn't repeat regularly
        self.repeat_day = REPEAT_DAY[int(raw[4])]

        for prefix, dungeon_type in prefix_to_dungeontype.items():
            if self.clean_name.startswith(prefix):
                self.prefix = prefix
                self.dungeon_type = dungeon_type
                self.clean_name = self.clean_name[len(prefix):]
                break

        if len(raw) > 6:
            print('unexpected field count: ' + ','.join(raw))

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return 'Dungeon({} - {})'.format(self.dungeon_id, self.clean_name)


def load_dungeon_data(data_dir: str = None, dungeon_file: str = None) -> List[Dungeon]:
    """Converts dungeon JSON into an array of Dungeons."""
    if dungeon_file is None:
        dungeon_file = os.path.join(data_dir, FILE_NAME)

    with open(dungeon_file) as f:
        dungeon_json = json.load(f)

    if dungeon_json['v'] != 4:
        raise NotImplementedError('version: {}'.format(dungeon_json['v']))

    dungeon_info = dungeon_json['dungeons']

    dungeons = []
    cur_dungeon = None

    for line in dungeon_info.split('\n'):
        info = line[0:2]
        data = line[2:]
        data_values = next(csv.reader(StringIO(data), quotechar="'"))
        if info == 'd;':
            cur_dungeon = Dungeon(data_values)
            dungeons.append(cur_dungeon)
        elif info == 'f;':
            floor = DungeonFloor(data_values)
            cur_dungeon.floors.append(floor)
        elif info == 'c;':
            pass
        else:
            raise ValueError('unexpected line: ' + line)

    return dungeons
