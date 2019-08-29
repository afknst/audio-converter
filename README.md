# audio-converter
Convert audio files to FLAC with Python

## Dependences
[tqdm](https://github.com/tqdm/tqdm)
[ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
[mutagen](https://github.com/quodlibet/mutagen)

## Usage
Add to path (change `acflac` to whatever you like):
`ln -s <This script> <Somewhere in PATH/acflac>`

Convert all .wav files in curent directory with `wav2flac`:
`alias wav2flac="find . -name '*.wav' -exec acflac -r {} +"`
`wav2flac`
