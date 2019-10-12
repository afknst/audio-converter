#!/usr/bin/env python3

import ffmpeg, mutagen
import os, sys, shutil, argparse
from tqdm import tqdm


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "input",
            nargs='+',
        )
        parser.add_argument(
            "-cl",
            '--compression_level',
            dest='level',
            type=int,
            choices=range(13),
        )
        parser.add_argument(
            '-nc',
            '--no-cover',
            dest='cover',
            action='store_false',
        )
        parser.add_argument(
            '-i',
            '--inplace',
            dest='inplace',
            action='store_true',
        )
        parser.add_argument(
            '-ni',
            '--not-inplace',
            dest='inplace',
            action='store_false',
        )
        parser.add_argument(
            '-r',
            '--replace',
            dest='replace',
            action='store_true',
        )
        parser.add_argument(
            '-nr',
            '--not-replace',
            dest='replace',
            action='store_false',
        )
        parser.add_argument(
            '-t',
            '--title',
            dest='title',
            action='store_true',
        )
        parser.set_defaults(inplace=True)
        parser.set_defaults(replace=False)
        parser.set_defaults(title=False)
        parser.set_defaults(cover=True)
        parser.set_defaults(level=5)
        return parser.parse_args()
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


def find_cover(dir=os.getcwd(), exts=['.jpg']):
    l = [
        os.path.join(root, file) for ext in exts
        for root, dirs, files in os.walk(dir) for file in files
        if file.lower().endswith(ext)
    ]
    return sorted([(os.path.getsize(file), file) for file in l],
                  key=lambda s: s[0])[-1][1]


args = parse_cli()
output = os.path.expanduser("~/Music/")
bar = tqdm(args.input,
           bar_format='{l_bar}{bar}{{{n_fmt}/{total_fmt}{postfix}}}',
           dynamic_ncols=True)
cl = args.level

for file in bar:
    head, tail = os.path.split(file)
    if not head:
        head = tail
    if head[:2] == './':
        head = head[2:]
    # if len(head) >= 15:
    #     head = head[:8] + '...' + head[-3:]
    head = head[:8]
    bar.set_description(head)

    try:
        ffmpeg.input(file).output('.Noname.flac',
                                  loglevel="quiet",
                                  compression_level=cl).run()
        data = mutagen.File('.Noname.flac')
        sample_rate = data.info.sample_rate
        bps = data.info.bits_per_sample

        if args.title:
            try:
                title = data.tags['title'][0]
            except:
                title = os.path.splitext(file)[0]
        else:
            title = os.path.splitext(file)[0]

        if args.cover:
            try:
                if len(data.pictures) < 1:
                    pic = mutagen.flac.Picture()

                    with open(find_cover(), "rb") as f:
                        pic.data = f.read()

                    pic.type = mutagen.id3.PictureType.COVER_FRONT
                    pic.mime = u"image/jpeg"
                    data.add_picture(pic)
                    data.save()
            except Exception as e:
                print(e)

        try:
            artist = data.tags['artist'][0]
        except:
            artist = 'Unknown'

        if sample_rate > 96e3:
            ffmpeg.input('.Noname.flac').output('.temp.flac',
                                                ar='96k',
                                                loglevel="quiet",
                                                compression_level=cl).run()
            os.remove('.Noname.flac')
            shutil.move('.temp.flac', '.Noname.flac')

        def move_to(location):
            dst = location
            if os.path.exists(dst + '.flac'):
                dst += '_' + artist
                print('Destination already exists.')
                print('Renamed to: ' + os.path.split(dst + '.flac')[1])
            shutil.move('.Noname.flac', dst + '.flac')

        if args.replace:
            os.remove(file)

        if args.inplace:
            move_to(title)
        else:
            move_to(output + title)

        bar.set_postfix_str(
            str(int(sample_rate * 1e-3)) + 'kHz, ' + str(bps) + 'bit')
    except Exception as e:
        print(e)
