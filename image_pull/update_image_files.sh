#!/bin/bash
#
# Updates the local cache of full monster pics / portraits from the JP server and
# uploads them to GCS, setting them public.

# Full pictures
python3 /home/tactical0retreat/rpad-cogs-utils/image_pull/PADTextureDownload.py --output_dir=/home/tactical0retreat/image_data/na/full --server=NA
python3 /home/tactical0retreat/rpad-cogs-utils/image_pull/PADTextureDownload.py --output_dir=/home/tactical0retreat/image_data/jp/full --server=JP
gsutil -m rsync -r /home/tactical0retreat/image_data/na/full/corrected_data gs://mirubot/padimages/na/full/
gsutil -m rsync -r /home/tactical0retreat/image_data/jp/full/corrected_data gs://mirubot/padimages/jp/full/

# Portraits
python3 /home/tactical0retreat/rpad-cogs-utils/image_pull/PADPortraitsGenerator.py \
  --input_dir=/home/tactical0retreat/image_data/na/full/extract_data \
  --card_types_file=/home/tactical0retreat/hosted_services/bots/Red-DiscordBot-PrivateMiru/data/padguide2/card_data.csv \
  --card_templates_file=/home/tactical0retreat/rpad-cogs-utils/image_pull/wide_cards.png \
  --server=na \
  --output_dir=/home/tactical0retreat/image_data/na/portrait/local_tmp

python3 /home/tactical0retreat/rpad-cogs-utils/image_pull/PADPortraitsGenerator.py \
  --input_dir=/home/tactical0retreat/image_data/jp/full/extract_data \
  --card_types_file=/home/tactical0retreat/hosted_services/bots/Red-DiscordBot-PrivateMiru/data/padguide2/card_data.csv \
  --card_templates_file=/home/tactical0retreat/rpad-cogs-utils/image_pull/wide_cards.png \
  --server=jp \
  --output_dir=/home/tactical0retreat/image_data/jp/portrait/local

python3 /home/tactical0retreat/rpad-cogs-utils/image_pull/PADPortraitsCombiner.py \
  --na_dir=/home/tactical0retreat/image_data/na/portrait/local_tmp \
  --jp_dir=/home/tactical0retreat/image_data/jp/portrait/local \
  --output_dir=/home/tactical0retreat/image_data/na/portrait/local

gsutil -m rsync -r /home/tactical0retreat/image_data/na/portrait/local gs://mirubot/padimages/na/portrait/
gsutil -m rsync -r /home/tactical0retreat/image_data/jp/portrait/local gs://mirubot/padimages/jp/portrait/
