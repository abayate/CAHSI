# caesarCipherMain.py
from caesarCipher import caesarCipher
import matplotlib.ticker as mticker
from collections import Counter
import matplotlib.pyplot as plt
from utils import checkPath
import pandas as pd
import argparse
import re
import os


def getConsoleArguments() -> argparse.Namespace:
    """
    Parses and returns the command-line arguments for the Caesar Cipher script.
    """
    parser = argparse.ArgumentParser(
        description="Encrypt/decrypt text using Caesar Cipher and analyze frequencies."
    )

    parser.add_argument('--text', type=str, help='The text to encrypt and analyze.')
    parser.add_argument('--textFile', type=str, help='Path to a text file to encrypt/analyze.')
    parser.add_argument('--shift', type=int, default=3,
                        help='The shift value for the Caesar Cipher (default: 3)')

    parser.add_argument('--saveFrecuencyTable', action='store_true',
                        help='Save the frequency table to a CSV file.')
    parser.add_argument('--savePlots', action='store_true',
                        help='Save frequency plots for each shift.')
    parser.add_argument('--savePossibleShifts', action='store_true',
                        help='Save all possible shifts to a txt file.')
    parser.add_argument('--resultsPath', type=str,
                        default='../results/caesarCipher',
                        help='Path to save results (default: ../results/caesarCipher)')
    parser.add_argument('--decrypt', action='store_true',
                        help='Decrypt the text instead of encrypting it.')
    parser.add_argument('--countChars', action='store_true',
                        help='Print non-whitespace character count from the raw input (before cleaning).')

    return parser.parse_args()


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


def cleanText(text) -> str:
    """
    Cleans the input text for analysis mode.
    """
    text = text.strip().lower()
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'[^a-z\s]', '', text)
    return text


def readTextFile(path: str) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def countNonWhitespaceChars(raw_text: str) -> int:
    return sum(1 for ch in raw_text if not ch.isspace())


if __name__ == "__main__":
    args = getConsoleArguments()

    if args.textFile:
        raw_text = readTextFile(args.textFile)
    elif args.text:
        raw_text = args.text
    else:
        raw_text = input("Enter a text to encrypt: ")

    if args.countChars:
        print(f"Non-whitespace character count: {countNonWhitespaceChars(raw_text)}")

    text = cleanText(raw_text)

    cipher = caesarCipher()
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    if not (args.saveFrecuencyTable or args.savePlots or args.savePossibleShifts):
        cipher.setConfig({
            'shift': args.shift,
            'alphabet': alphabet,
            'preserve_nonalpha': True
        })
        modifiedText = cipher.encrypt(text) if not args.decrypt else cipher.decrypt(text)
        print(f"{'Decrypted' if args.decrypt else 'Encrypted'} text: {modifiedText}")
        raise SystemExit(0)

    checkPath(os.path.abspath(args.resultsPath))

    frequencyTable = pd.DataFrame(columns=list(alphabet))
    shiftLabels = []

    shiftsFilename = os.path.join(args.resultsPath, 'possible_shifts.txt')
    possible_shifts_file = None

    if args.savePossibleShifts:
        possible_shifts_file = open(shiftsFilename, 'w', encoding='utf-8')

    print(f"All possible shifts for the text (cleaned): '{text}': ")
    for shift in range(1, len(alphabet)):
        cipher.setConfig({
            'shift': shift,
            'alphabet': alphabet,
            'preserve_nonalpha': True
        })

        newText = cipher.encrypt(text) if not args.decrypt else cipher.decrypt(text)

        frequency = Counter(ch for ch in newText if ch in alphabet)

        newRowSeries = pd.Series(0, index=list(alphabet))
        newRowSeries.update(pd.Series(frequency))

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