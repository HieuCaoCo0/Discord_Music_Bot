# Discord_Music_Bot

A simple Discord music bot built with Python using discord.py, yt-dlp, and FFmpeg.

## Features
- Play music from Youtube
- Search songs by keyword
- Queue songs
- Skip the current song
- Stop playback
- Leave the voice channel
- Slash command support

## Commands

| Command | Description |
| ------- | ----------- |
| `/play <song>` | Play a song or add it to the queue |
| `/skip` | Skip the current song |
| `/stop` | Stop playback and clear the queue |
| `/pause` | Pause playback |
| `/resume` | Resume playback |

## Requirements
- python 3.11 or later
- FFmpeg

## Dependencies
- discord.py
- yt-dlp
- PyNaCl
- python-dotenv