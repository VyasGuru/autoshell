#!/usr/bin/env python3



import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

load_dotenv(dotenv_path=Path.home() / "bin" / ".env")

# List of dangerous command substrings to block
dangerous_patterns = [
    'rm -rf /', 'mkfs', 'dd if=', ':(){ :|:& };:', 'shutdown', 'reboot', 'halt',
    'init 0', 'init 6', 'poweroff', 'mklabel', 'mkfs.', '>:', 'chown -R /',
    'chmod 000 /', '>/dev/sda', '>/dev/nvme', '>/dev/vda'
]

def is_dangerous(cmd):
    cmd_lc = cmd.lower()
    return any(pattern in cmd_lc for pattern in dangerous_patterns)

def get_openrouter_key():
    token = os.environ.get('OPENROUTER_API_KEY')
    if not token:
        print('[autoshell] Error: No OpenRouter API key found. Please set OPENROUTER_API_KEY in your .env file.')
        sys.exit(1)
    return token

def query_openrouter_api(instruction, api_key):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    prompt = f"Translate this natural language instruction into a safe, one-line Unix shell command. Respond with only the command and nothing else.\n\nInstruction: {instruction}"
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=[
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                # Optionally set these for OpenRouter ranking:
                # "HTTP-Referer": "<YOUR_SITE_URL>",
                # "X-Title": "autoshell-cli",
            },
            extra_body={},
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[autoshell] Error: Failed to get command from OpenRouter API: {e}")
        sys.exit(2)

def main():
    parser = argparse.ArgumentParser(
        description='autoshell: Turn natural language into safe shell commands (powered by OpenRouter deepseek/deepseek-r1-0528-qwen3-8b:free)'
    )
    parser.add_argument('--dry-run', action='store_true', help='Show the command but do not execute it')
    parser.add_argument('instruction', nargs=argparse.REMAINDER, help='What do you want to do? (natural language)')
    args = parser.parse_args()

    if not args.instruction:
        print('Usage: wtd <your instruction>')
        sys.exit(1)

    instruction = ' '.join(args.instruction).strip()
    api_key = get_openrouter_key()

    print(f"\n[autoshell] Interpreting: {instruction}\n")
    cmd = query_openrouter_api(instruction, api_key)

    # Cleanup: strip formatting, keep first line
    cmd = cmd.strip('`\n ').split('\n')[0].strip()

    print(f"[autoshell] Suggested command:\n  {cmd}\n")

    if is_dangerous(cmd):
        print("[autoshell] ⚠️  Error: Command appears dangerous and will not be run.")
        sys.exit(3)

    try:
        user_input = input("Edit or press Enter to accept: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n[autoshell] Cancelled.")
        sys.exit(0)

    if user_input:
        cmd = user_input

    if is_dangerous(cmd):
        print("[autoshell] ⚠️  Error: Edited command appears dangerous and will not be run.")
        sys.exit(3)

    print(f"[autoshell] Final command:\n  {cmd}\n")

    if args.dry_run:
        print("[autoshell] (dry run) Command not executed.")
        sys.exit(0)

    try:
        result = subprocess.run(cmd, shell=True)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"[autoshell] Error running command: {e}")
        sys.exit(4)

if __name__ == '__main__':
    main()
