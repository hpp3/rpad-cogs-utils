import argparse
import os
import re
import shutil
import sys
import urllib.request

from PIL import Image
import padtools


parser = argparse.ArgumentParser(description="Downloads P&D portraits.", add_help=False)

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")
outputGroup.add_argument("--server", help="One of [NA, JP]")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()


output_dir = args.output_dir


def download_file(url, file_path):
    response_object = urllib.request.urlopen(url)
    with response_object as response:
        file_data = response.read()
        with open(file_path, "wb") as f:
            f.write(file_data)


assets = []
if args.server == 'NA':
    assets = padtools.regions.north_america.server.assets
elif args.server == 'JP':
    assets = padtools.regions.japan.server.assets

print('Found', len(assets), 'assets total')


pdx_dir = os.path.join(output_dir, 'pdx_data')
gamewith_dir = os.path.join(output_dir, 'gamewith_data')
override_dir = os.path.join(output_dir, 'override_data')
corrected_dir = os.path.join(output_dir, 'corrected_data')

os.makedirs(gamewith_dir, exist_ok=True)
os.makedirs(pdx_dir, exist_ok=True)
os.makedirs(override_dir, exist_ok=True)
os.makedirs(corrected_dir, exist_ok=True)


IMAGE_SIZE = (100, 100)

THUMBNAIL_GAMEWITH_TEMPLATE = 'https://gamewith.akamaized.net/article_tools/pad/gacha/{}.png'
THUMBNAIL_PDX_TEMPLATE = 'http://www.puzzledragonx.com/en/img/book/{}.png'


# This was overwritten by voltron. PDX opted to copy it +10,000 ids away
CROWS_1 = {x: x + 10000 for x in range(2601, 2635 + 1)}
# This isn't overwritten but PDX adjusted anyway
CROWS_2 = {x: x + 10000 for x in range(3460, 3481 + 1)}

PDX_JP_ADJUSTMENTS = {}
PDX_JP_ADJUSTMENTS.update(CROWS_1)
PDX_JP_ADJUSTMENTS.update(CROWS_2)

for asset in assets:
    asset_url = asset.url
    raw_file_name = os.path.basename(asset_url)

    if not raw_file_name.endswith('.bc') or 'mons' not in raw_file_name:
        print('skipping', raw_file_name)
        continue
    else:
        print('processing', asset_url)

    raw_monster_id = raw_file_name.strip('.bc').strip('mons_')
    gamewith_url = THUMBNAIL_GAMEWITH_TEMPLATE.format(raw_monster_id)

    stripped_monster_id = raw_monster_id.lstrip('0')
    pdx_url = THUMBNAIL_PDX_TEMPLATE.format(stripped_monster_id)

    output_file_name = '{}.png'.format(stripped_monster_id)

    gamewith_path = os.path.join(gamewith_dir, output_file_name)
    try:
        if os.path.exists(gamewith_path) or args.server == 'NA':
            print('skipping existing/unused file', gamewith_path)
        else:
            download_file(gamewith_url, gamewith_path)
    except Exception as e:
        print('failed to download', gamewith_url, 'to', gamewith_path)

    pdx_path = os.path.join(pdx_dir, output_file_name)
    try:
        if os.path.exists(pdx_path):
            print('skipping existing file', pdx_path)
        else:
            # Account for mapped PDX monsters
            if args.server == 'JP':
                id_value = int(stripped_monster_id)
                mapped_id_value = PDX_JP_ADJUSTMENTS.get(id_value, id_value)
                pdx_url = THUMBNAIL_PDX_TEMPLATE.format(mapped_id_value)

            download_file(pdx_url, pdx_path)
    except Exception as e:
        print('failed to download', pdx_url, 'to', pdx_path)

    corrected_file_path = os.path.join(corrected_dir, output_file_name)
    if os.path.exists(pdx_path):
        shutil.copy(pdx_path, corrected_file_path)
    elif os.path.exists(gamewith_path):
        shutil.copy(gamewith_path, corrected_file_path)
    else:
        print('failed to copy any file to', corrected_file_path)
