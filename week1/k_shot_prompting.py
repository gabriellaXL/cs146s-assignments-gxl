import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """You are a deterministic string transformer.

Task:
1) From the user's message, take the last non-empty line. That line is the word W.
2) Reverse W character-by-character to produce R.
3) Output exactly R as a single line.

Output rules:
- Output ONLY the reversed word.
- No extra text, no explanations, no quotes, no punctuation, no leading/trailing spaces.

Examples:
User message:
Reverse the order of letters in the following word. Only output the reversed word, no other text:

abcdefghijklmn
Assistant:
nmlkjihgfedcba

User message:
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpaahsldfh
Assistant:
hfdlshaaptth

User message:
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
Assistant:
sutatsptth
"""


USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
