<div align="center">
    <img src="./Shinigami/assets/logo.png" height="150px" alt="logo"/>
    <h2>Shinigami WhatsApp Bot [W.I.P]</h2>
</div>

<p>Install dependencies</p>

```bash
poetry install
```

<p>Then run this script on Linux</p>

```bash
python main.py
```

<p>Or on Windows</p>

```bash
python main-win.py
```

<h3>How to get characterai token and characterai character?</h3>
<h4>To get token you need to register on <a href="https://beta.character.ai">character.ai</a> then</h4>
<li>Open DevTools in your browser</li>
<li>Go to Storage -> Local Storage -> char_token</li>
<li>Copy <code>value</code></li>

<h4>How about character?</h4>
<p>Open <a href="https://beta.character.ai">character.ai</a> then select character you want, after that copy value of char parameter on url</p>
<p>Example: https://beta.character.ai/chat?char=NO8kNTeOovRCzsjECiz8GEOGSx-YiCwoTK2-SA1rWLU&source=recent-chats</p>
<p>Copy <code>NO8kNTeOovRCzsjECiz8GEOGSx-YiCwoTK2-SA1rWLU</code></p>

<h3>Note: Why the command run on Windows is different from Linux? That's because Windows doesn't support several dependencies.</h3>
