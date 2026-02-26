# caesarCipherMain2.py
from caesarCipher import caesarCipher
import matplotlib.ticker as mticker
from collections import Counter
import matplotlib.pyplot as plt
from utils import checkPath
import pandas as pd
import argparse
import re
import os
import random
from typing import Optional, List


# -----------------------------
# Argparse
# -----------------------------
def getConsoleArguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Encrypt/decrypt text using Caesar Cipher and analyze frequencies."
    )

    parser.add_argument('--text', type=str, help='Plaintext/ciphertext input.')
    parser.add_argument('--textFile', type=str, help='Path to a text file input.')

    parser.add_argument('--shift', type=int, default=3,
                        help='Shift value for whole-text mode (default: 3).')

    parser.add_argument('--decrypt', action='store_true',
                        help='Decrypt instead of encrypt.')

    parser.add_argument('--countChars', action='store_true',
                        help='Print non-whitespace character count from raw input.')

    parser.add_argument('--saveFrecuencyTable', action='store_true',
                        help='Save frequency table to a CSV file.')
    parser.add_argument('--savePlots', action='store_true',
                        help='Save frequency plots for each shift.')
    parser.add_argument('--savePossibleShifts', action='store_true',
                        help='Save all possible shifts to a txt file.')
    parser.add_argument('--resultsPath', type=str,
                        default='../results/caesarCipher',
                        help='Path to save results (default: ../results/caesarCipher)')

    parser.add_argument('--keepNonAlpha', action='store_true',
                        help="Keep punctuation/digits as-is.")

    parser.add_argument('--wordCipher', action='store_true',
                        help='Apply Caesar cipher per-word instead of to the whole text.')

    parser.add_argument('--wordShiftMode', type=str, default='same',
                        choices=['same', 'random', 'sequence'],
                        help="Per-word shift behavior: same | random | sequence (default: same).")

    parser.add_argument('--wordShift', type=int, default=3,
                        help="Shift used when --wordShiftMode=same (default: 3).")

    parser.add_argument('--shiftSequence', type=str, default=None,
                        help='Comma-separated list of shifts for sequence mode. Example: 1,5,13,2')

    parser.add_argument('--seed', type=int, default=1234,
                        help='Seed for random per-word shifts (default: 1234).')

    parser.add_argument('--showWordShifts', action='store_true',
                        help='Print shift used for each word (and transformed word).')

    parser.add_argument('--saveWordShifts', action='store_true',
                        help='Save per-word shift log to resultsPath/word_shifts.txt')

    parser.add_argument('--noWizard', action='store_true',
                        help='Disable interactive prompts; require CLI flags.')

    return parser.parse_args()


# -----------------------------
# Helpers
# -----------------------------
def createPlot(frequency, shift, alphabet, resultsPath):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(list(alphabet), frequency.values)
    ax.set_title(f'Frequency Analysis for Shift {shift}')
    ax.set_xlabel('Letters')
    ax.set_ylabel('Frequency')
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    plot_filename = os.path.join(resultsPath, f'frequency_shift_{shift}.png')
    plt.savefig(plot_filename)
    plt.close(fig)


def readTextFile(path: str) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def countNonWhitespaceChars(raw_text: str) -> int:
    return sum(1 for ch in raw_text if not ch.isspace())


def cleanText_for_analysis(text: str) -> str:
    text = text.strip().lower()
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'[^a-z\s]', '', text)
    return text


def tokenize_preserving_whitespace_and_punct(raw_text: str):
    return re.findall(r"[A-Za-z]+|[^A-Za-z]+", raw_text)


def parse_shift_sequence(seq_str: str) -> Optional[List[int]]:
    if not seq_str:
        return None

    seq_str = seq_str.strip().strip('"').strip("'")
    parts = [p.strip() for p in seq_str.split(",") if p.strip() != ""]

    if not parts:
        return None

    shifts = []
    for p in parts:
        try:
            shifts.append(int(p))
        except ValueError:
            raise ValueError(f"Invalid shift '{p}'. Enter values like: 1,4,8,19")

    return shifts


def ask_choice(prompt: str, choices: List[str], default: Optional[str] = None) -> str:
    choices_display = " | ".join([f"{i+1}) {c}" for i, c in enumerate(choices)])
    while True:
        d = f" [default: {default}]" if default else ""
        ans = input(f"{prompt} ({choices_display}){d}: ").strip().lower()

        if ans == "" and default:
            return default

        if ans.isdigit():
            idx = int(ans) - 1
            if 0 <= idx < len(choices):
                return choices[idx]

        if ans in choices:
            return ans

        print(f"Invalid choice. Pick one of: {', '.join(choices)}")


def ask_int(prompt: str, default: Optional[int] = None, min_value: Optional[int] = None) -> int:
    while True:
        d = f" [default: {default}]" if default is not None else ""
        ans = input(f"{prompt}{d}: ").strip()

        if ans == "" and default is not None:
            val = default
        else:
            try:
                val = int(ans)
            except ValueError:
                print("Please enter an integer.")
                continue

        if min_value is not None and val < min_value:
            print(f"Please enter a value >= {min_value}.")
            continue

        return val


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    d = "Y/n" if default else "y/N"
    while True:
        ans = input(f"{prompt} [{d}]: ").strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer y or n.")


# -----------------------------
# Input collection
# -----------------------------
def collect_user_input(is_decrypt: bool) -> tuple[Optional[str], Optional[str]]:
    """
    Returns (text, textFile)
    """
    content_label = "ciphertext" if is_decrypt else "plaintext"

    input_type = ask_choice(
        f"How do you want to provide the {content_label}?",
        ["text", "file"],
        default="text"
    )

    if input_type == "text":
        user_text = input(f"Paste/type the {content_label}: ")
        return user_text, None

    while True:
        path = input(f"Enter path to {content_label} file (e.g., input.txt): ").strip().strip('"')
        if os.path.isfile(path):
            return None, path
        print("File not found. Try again.")


# -----------------------------
# Word cipher core
# -----------------------------
def apply_word_cipher(raw_text: str, cipher_obj: caesarCipher, alphabet: str, decrypt: bool,
                      word_shift_mode: str, word_shift: int, shift_sequence, seed: int,
                      show_word_shifts: bool = False, save_word_shifts_path: Optional[str] = None) -> str:
    tokens = tokenize_preserving_whitespace_and_punct(raw_text)
    out_tokens = []

    rng = random.Random(seed)
    seq_idx = 0
    word_idx = 0

    log_lines = []
    if word_shift_mode == "same":
        log_lines.append(f"[wordShiftMode=same] shift={word_shift}")
    elif word_shift_mode == "random":
        log_lines.append(f"[wordShiftMode=random] seed={seed} (shift chosen per word)")
    elif word_shift_mode == "sequence":
        log_lines.append(f"[wordShiftMode=sequence] sequence={shift_sequence}")
    log_lines.append("")

    for tok in tokens:
        if tok.isalpha():
            word_idx += 1

            if word_shift_mode == 'same':
                shift = word_shift
            elif word_shift_mode == 'random':
                shift = rng.randint(1, len(alphabet) - 1)
            elif word_shift_mode == 'sequence':
                if not shift_sequence:
                    raise ValueError("wordShiftMode=sequence requires --shiftSequence.")
                shift = shift_sequence[seq_idx % len(shift_sequence)]
                seq_idx += 1
            else:
                raise ValueError(f"Unknown wordShiftMode: {word_shift_mode}")

            cipher_obj.setConfig({
                'shift': shift,
                'alphabet': alphabet,
                'preserve_nonalpha': True
            })

            original_word = tok.lower()
            transformed_word = cipher_obj.decrypt(original_word) if decrypt else cipher_obj.encrypt(original_word)
            out_tokens.append(transformed_word)

            log_lines.append(f'word #{word_idx}: "{original_word}" | shift={shift} | result="{transformed_word}"')
        else:
            out_tokens.append(tok)

    if show_word_shifts:
        print("\n".join(log_lines))

    if save_word_shifts_path:
        os.makedirs(os.path.dirname(save_word_shifts_path), exist_ok=True)
        with open(save_word_shifts_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
            f.write("\n")

    return "".join(out_tokens)


# -----------------------------
# Wizard
# -----------------------------
def run_wizard(args: argparse.Namespace) -> argparse.Namespace:
    print("\n=== Caesar Cipher Wizard ===")

    action = ask_choice("Do you want to encrypt or decrypt?", ["encrypt", "decrypt"], default="encrypt")
    args.decrypt = (action == "decrypt")

    # Explicitly ask for plaintext/ciphertext
    args.text, args.textFile = collect_user_input(args.decrypt)

    args.wordCipher = ask_yes_no("Apply cipher per-word (wordCipher)?", default=True)

    if args.decrypt:
        known = ask_choice("Is the shift known or unknown?", ["known", "unknown"], default="known")

        if known == "known":
            if args.wordCipher:
                args.wordShiftMode = ask_choice(
                    "How was the ciphertext encrypted per-word?",
                    ["same", "random", "sequence"],
                    default="same"
                )

                if args.wordShiftMode == "same":
                    args.wordShift = ask_int(
                        "Enter the per-word shift used during encryption",
                        default=args.wordShift,
                        min_value=0
                    )
                elif args.wordShiftMode == "random":
                    args.seed = ask_int(
                        "Enter the seed used during encryption",
                        default=args.seed,
                        min_value=0
                    )
                else:
                    seq = input('Enter shift sequence used during encryption (example 1,5,3,2): ').strip()
                    args.shiftSequence = seq
            else:
                args.shift = ask_int(
                    "Enter the shift used during encryption",
                    default=args.shift,
                    min_value=0
                )

        else:
            args.savePossibleShifts = ask_yes_no("Save all possible shifts to a file?", default=True)
            args.saveFrecuencyTable = ask_yes_no("Save frequency table CSV?", default=False)
            args.savePlots = ask_yes_no("Save plots per shift?", default=False)

            rp = input(f"Results folder path [default: {args.resultsPath}]: ").strip()
            if rp:
                args.resultsPath = rp

            args.wordCipher = False
            print("Note: Unknown-shift cracking is done in whole-text mode.")

    else:
        if args.wordCipher:
            args.wordShiftMode = ask_choice(
                "Per-word shift mode?",
                ["same", "random", "sequence"],
                default=args.wordShiftMode
            )

            if args.wordShiftMode == "same":
                args.wordShift = ask_int(
                    "Enter shift for each word",
                    default=args.wordShift,
                    min_value=0
                )
            elif args.wordShiftMode == "random":
                args.seed = ask_int(
                    "Enter seed (for reproducible random shifts)",
                    default=args.seed,
                    min_value=0
                )
            else:
                seq = input('Enter shift sequence (example 1,5,3,2): ').strip()
                args.shiftSequence = seq

            args.showWordShifts = ask_yes_no("Show per-word shifts on screen?", default=True)
            args.saveWordShifts = ask_yes_no("Save per-word shift log to file?", default=False)

            if args.saveWordShifts:
                rp = input(f"Results folder path [default: {args.resultsPath}]: ").strip()
                if rp:
                    args.resultsPath = rp
        else:
            args.shift = ask_int(
                "Enter shift for whole-text encryption",
                default=args.shift,
                min_value=0
            )

    args.keepNonAlpha = ask_yes_no("Keep punctuation/digits (keepNonAlpha)?", default=True)
    args.countChars = ask_yes_no("Show non-whitespace character count?", default=False)

    print("=== Wizard complete ===\n")
    return args


def should_run_wizard(args: argparse.Namespace) -> bool:
    if args.noWizard:
        return False

    has_input = bool(args.textFile or args.text)
    if not has_input:
        return True

    minimal = has_input and not args.wordCipher and not args.decrypt and args.shift == 3 \
              and not (args.saveFrecuencyTable or args.savePlots or args.savePossibleShifts)
    return minimal


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    args = getConsoleArguments()

    if should_run_wizard(args):
        args = run_wizard(args)

    if args.textFile:
        raw_text = readTextFile(args.textFile)
    elif args.text:
        raw_text = args.text
    else:
        raw_text = input("Paste ciphertext: " if args.decrypt else "Paste plaintext: ")

    if args.countChars:
        print(f"Non-whitespace character count: {countNonWhitespaceChars(raw_text)}")

    cipher = caesarCipher()
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    # WORD-BY-WORD MODE
    if args.wordCipher:
        shift_sequence = parse_shift_sequence(args.shiftSequence)

        if args.keepNonAlpha:
            processed_text = raw_text.strip().lower()
        else:
            processed_text = cleanText_for_analysis(raw_text)

        save_path = None
        if args.saveWordShifts:
            checkPath(os.path.abspath(args.resultsPath))
            save_path = os.path.join(args.resultsPath, "word_shifts.txt")

        modifiedText = apply_word_cipher(
            raw_text=processed_text,
            cipher_obj=cipher,
            alphabet=alphabet,
            decrypt=args.decrypt,
            word_shift_mode=args.wordShiftMode,
            word_shift=args.wordShift,
            shift_sequence=shift_sequence,
            seed=args.seed,
            show_word_shifts=args.showWordShifts,
            save_word_shifts_path=save_path
        )

        print(f"{'Decrypted' if args.decrypt else 'Encrypted'} text (word-by-word):\n{modifiedText}")
        raise SystemExit(0)

    # WHOLE-TEXT MODE
    if args.keepNonAlpha:
        text = raw_text.strip().lower()
    else:
        text = cleanText_for_analysis(raw_text)

    if not (args.saveFrecuencyTable or args.savePlots or args.savePossibleShifts):
        cipher.setConfig({
            'shift': args.shift,
            'alphabet': alphabet,
            'preserve_nonalpha': args.keepNonAlpha
        })
        modifiedText = cipher.decrypt(text) if args.decrypt else cipher.encrypt(text)
        print(f"{'Decrypted' if args.decrypt else 'Encrypted'} text:\n{modifiedText}")
        raise SystemExit(0)

    checkPath(os.path.abspath(args.resultsPath))

    cleaned_for_analysis = cleanText_for_analysis(raw_text)
    frequencyTable = pd.DataFrame(columns=list(alphabet))
    shiftLabels = []

    shiftsFilename = os.path.join(args.resultsPath, 'possible_shifts.txt')
    possible_shifts_file = None

    if args.savePossibleShifts:
        possible_shifts_file = open(shiftsFilename, 'w', encoding='utf-8')

    print(f"All possible shifts for the text (cleaned): '{cleaned_for_analysis}': ")
    for shift in range(1, len(alphabet)):
        cipher.setConfig({
            'shift': shift,
            'alphabet': alphabet,
            'preserve_nonalpha': True
        })

        newText = cipher.decrypt(cleaned_for_analysis) if args.decrypt else cipher.encrypt(cleaned_for_analysis)

        freq_counts = Counter(ch for ch in newText if ch in alphabet)
        newRowSeries = pd.Series(0, index=list(alphabet))
        newRowSeries.update(pd.Series(freq_counts))

        newRow = pd.DataFrame([newRowSeries])
        frequencyTable = pd.concat([frequencyTable, newRow], ignore_index=True)

        shiftLabels.append(f'Shift {shift}')
        print(f"Shift {shift}: {newText}")

        if args.savePlots:
            createPlot(newRowSeries, shift, alphabet, args.resultsPath)

        if args.savePossibleShifts and possible_shifts_file:
            possible_shifts_file.write(f"Shift {shift}: {newText}\n")

    if possible_shifts_file:
        possible_shifts_file.close()

    if args.saveFrecuencyTable:
        frequencyTable.index = shiftLabels
        table_filename = os.path.join(args.resultsPath, 'frequency_table.csv')
        frequencyTable.to_csv(table_filename, index=True)
        print(f"Frequency table saved to '{table_filename}'.")