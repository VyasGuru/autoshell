# autoshell (`wtd`)

A minimal, safe, and pleasant CLI tool to turn natural language into shell commands using DeepSeek API (with deepseek/deepseek-r1-0528-qwen3-8b:free model).

## Installation

1. Ensure you have Python 3 and the required packages:
   ```sh
   pip install -r requirements.txt
   ```
2. Copy `autoshell.py` somewhere in your PATH and make it executable:
   ```sh
   cp autoshell.py ~/bin/wtd
   chmod +x ~/bin/wtd
   # Or symlink:
   ln -s "$PWD/autoshell.py" ~/bin/wtd
   ```
3. Create a `.env` file in `~/bin` with your OpenRouter API key:
   ```sh
   echo 'OPENROUTER_API_KEY=your_openrouter_api_key_here' > ~/bin/.env
   ```
   Replace `your_openrouter_api_key_here` with your actual OpenRouter API key.

## Usage

```sh
wtd make a file called notes.txt in my current directory
```

- The tool will suggest a shell command, let you edit/confirm it, and then run it.
- Use `--dry-run` to only show the command, not execute it.

## Safety
- Blocks dangerous commands (e.g., `rm -rf /`, `mkfs`, etc.).
- Prompts for confirmation/edit before running anything.

## Requirements
- Python 3
- `openai` and `python-dotenv` (install with `pip install -r requirements.txt`)
- macOS or Linux
- OpenRouter API key (get one at [https://openrouter.ai/](https://openrouter.ai/))

---
