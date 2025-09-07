# DNS Digger

**DNS Digger** is a fast, interactive Python tool to discover valid subdomains using DNS queries.  
It supports multi-threading, caching, custom or default wordlists, and outputs organized results into a structured folder.

---

## Features

- Interactive CLI interface with clean prompts
- Colored terminal output using [Rich](https://github.com/Textualize/rich)
- Fast multi-threaded DNS scanning
- Output saved as:
```bash
  output/
  └── google.com/
      ├── valid.txt
      └── invalid.txt
```
- Caching with JSON to avoid duplicate lookups
- Use your own wordlist or the default one included

---

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage
```bash
python main.py
```

---

Created with ❤️ by [1gcw](https://github.com/1gcw/)
