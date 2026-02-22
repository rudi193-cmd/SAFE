#!/usr/bin/env python3
"""Extract training data from Claude Code conversations."""
import json
from pathlib import Path

INPUT = r'C:\Users\Sean\Downloads\data-2026-02-16-19-55-28-batch-0000\conversations.json'
OUTPUT = r'C:\Users\Sean\Documents\GitHub\aios-minimal\training\kart_training.jsonl'

def extract_text(content_blocks):
    texts = []
    for block in content_blocks:
        if block.get('type') == 'text' and block.get('text'):
            texts.append(block['text'].strip())
    return ' '.join(texts).strip()

def main():
    with open(INPUT, 'r', encoding='utf-8') as f:
        data = json.load(f)

    training_pairs = []

    for conv in data:
        messages = conv.get('chat_messages', [])

        for i in range(len(messages) - 1):
            user_msg = messages[i]
            asst_msg = messages[i + 1]

            if user_msg.get('sender') != 'human':
                continue
            if asst_msg.get('sender') != 'assistant':
                continue

            user_text = extract_text(user_msg.get('content', []))
            if not user_text or len(user_text) < 3:
                continue

            asst_content = asst_msg.get('content', [])
            tool_output = None

            for block in asst_content:
                if block.get('type') == 'tool_use':
                    tool_name = block.get('name', '')
                    tool_input = block.get('input', {})

                    tool_json = json.dumps({"tool": tool_name, "params": tool_input})
                    tool_output = f"```tool\n{tool_json}\n```"
                    break

            if not tool_output:
                asst_text = extract_text(asst_content)
                if asst_text and len(asst_text) < 100:
                    if any(p in asst_text.lower() for p in ['will use', 'can use', 'let me', "i'll"]):
                        continue
                    tool_output = asst_text

            if tool_output:
                training_pairs.append({"instruction": user_text, "output": tool_output})

    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        for pair in training_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')

    print(f"Extracted {len(training_pairs)} training pairs -> {OUTPUT}")

if __name__ == '__main__':
    main()
