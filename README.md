<div align="center">
    <img src="./Shinigami/assets/logo.png" height="200px" alt="Shinigami Logo"/>
    <h2>Shinigami WhatsApp Bot [Work in Progress]</h2>
</div>

## Requirements
- Python 3.10+
- Ffmpeg

## Install on Windows (using winget)
```powershell
winget install Gyan.FFmpeg
```
## or using chocolatey
```powershell
choco install ffmpeg-full
```

## Install Dependencies
```bash
poetry install
```

## Run on Linux
```bash
python main.py
```

## Run on Windows
```powershell
python main-win.py
```

## How to Obtain Characterai Token and Characterai Character
### Token Retrieval:
- Register on [character.ai](https://beta.character.ai).
- Open DevTools in your browser.
- Navigate to Storage -> Local Storage -> char_token.
- Copy the `value`.

### Character Retrieval:
- Open [character.ai](https://beta.character.ai).
- Select the desired character.
- Copy the value of the char parameter from the URL.
- Example URL: https://beta.character.ai/chat?char=NO8kNTeOovRCzsjECiz8GEOGSx-YiCwoTK2-SA1rWLU&source=recent-chats.
- Copy `NO8kNTeOovRCzsjECiz8GEOGSx-YiCwoTK2-SA1rWLU.`

## Note
The difference in command execution between Windows and Linux is due to Windows not supporting certain dependencies.
