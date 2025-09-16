import argparse

from . import (
    CaptionConverter,
    detect_format,
    DFXPWriter,
    SAMIWriter,
    SCCWriter,
    SRTWriter,
    WebVTTWriter,
)


def main():
    writers = {
        'dfxp': DFXPWriter,
        'sami': SAMIWriter,
        'scc': SCCWriter,
        'srt': SRTWriter,
        'ttml': DFXPWriter,
        'vtt': WebVTTWriter,
        'webvtt': WebVTTWriter,
    }
    parser = argparse.ArgumentParser(
        'pycaption', description='Convert captions to different formats')

    parser.add_argument(
        'input', type=argparse.FileType('r'), metavar='FILE',
        help='Input file')
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default='-',
        metavar='FILE', help='Output file (default is stdout)')
    parser.add_argument(
        '--to', '-t', choices=writers.keys(), default='srt', metavar='FORMAT',
        help='Output format, one of: %(choices)s. Default is "%(default)s"')
    args = parser.parse_args()

    caps = args.input.read().decode()
    reader = detect_format(caps)
    if reader is None:
        parser.exit(1, 'Input format not supported\n')
    writer = writers[args.to]
    converter = CaptionConverter()
    converter.read(caps, reader())
    args.output.write(converter.write(writer()))
