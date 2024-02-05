<div align="center">
    <img src="./Shinigami/assets/logo.png" height="200px" alt="Shinigami Logo"/>
    <h1>Shinigami WhatsApp Bot [Work in Progress]</h1>
</div>

## Requirements
- Python 3.10+
- Ffmpeg

## Install Ffmpeg on Windows

```cmd
winget install Gyan.FFmpeg :: using winget
choco install ffmpeg-full :: using chocolatey
```

## Install Dependencies

```bash
poetry install
```

> [!NOTE]
> Sadly, on Windows, you need to configure the bot settings manually in `Shinigami/config.json`. <br>

## Run Shinigami

```bash
python main.py # if you're using Linux
python main-win.py # if you're using Windows
```

> [!NOTE]
> The difference in command execution between Windows and Linux is due to Windows not supporting certain dependencies.

## FAQ

- How to obtain characterai token?
  > - Register on [character.ai](https://beta.character.ai).
  > - Open DevTools in your browser.
  > - Navigate to Storage -> Local Storage -> char_token.
  > - Copy the `value`.
- How to obtain characterai character
  > - Open [character.ai](https://beta.character.ai).
  > - Select the desired character.
  > - Copy the value of the `char` parameter from the URL.
  > - Example URL: `https://beta.character.ai/chat?char=NO8kNTeOovRCzsjECiz8GEOGSx-YiCwoTK2-SA1rWLU&source=recent-chats`.
  > - Copy `NO8kNTeOovRCzsjECiz8GEOGSx-YiCwoTK2-SA1rWLU`.

## Contributing

Feel free to contribute to this project if you have any further ideas.
