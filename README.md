# Account Historical Value Analyzer

A reusable Codex skill for reconstructing historical securities holdings from brokerage records and identifying the date on which the **total account market value** was highest.

The skill is designed around an important accounting rule: account value must be calculated from all same-day holdings and prices before comparing dates. It must never add together the independent peak values of different securities.

## Key safeguards

- Reads PDF, image, CSV, Excel, and transaction-history inputs.
- Verifies every material `BUY` or `SELL` direction from the source row.
- Preserves the original transaction label and normalized interpretation.
- Treats same-day transactions as part of end-of-day holdings.
- Uses historical **unadjusted closing prices** by default.
- Detects missing opening positions and unexplained negative balances.
- Prevents sold shares from being carried forward as later holdings.
- Produces transaction, holding-period, daily valuation, and maximum-value tables.
- Marks uncertain records `REVIEW_REQUIRED` instead of inventing values.

## Repository structure

```text
account-historical-value-analyzer/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── validate_skill.py
├── .github/
│   └── workflows/
│       └── validate.yml
├── .gitignore
├── LICENSE
└── README.md
```

## Installation

Clone the repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/YOUR-USERNAME/account-historical-value-analyzer.git \
  ~/.codex/skills/account-historical-value-analyzer
```

Restart Codex after installation if the skill does not appear immediately.

## Usage

Invoke the skill explicitly:

```text
Use $account-historical-value-analyzer to analyze this brokerage statement and
find the highest total account value between January 1 and December 31, 2025.
```

Provide the brokerage records, analysis period, desired valuation currency, and any known opening holdings. If opening holdings or transaction direction cannot be established, the skill will disclose the limitation instead of silently guessing.

## Scope

The current version focuses on security holdings and historical market value. It does not automatically calculate cash balances, dividends, options, margin debt, capital gains, tax basis, wash sales, PFIC amounts, FBAR values, Form 8938 values, or currency conversion unless the user separately requests and supplies the information needed for those calculations.

## Validation

Run the repository’s dependency-free structural validation:

```bash
python3 scripts/validate_skill.py
```

GitHub Actions runs the same check on pushes and pull requests.

## Disclaimer

This skill supports document extraction and historical valuation analysis. Its output is not financial, investment, legal, or tax advice. Review all material transactions, opening positions, prices, and currency assumptions before relying on the result.

## License

Released under the MIT License.
