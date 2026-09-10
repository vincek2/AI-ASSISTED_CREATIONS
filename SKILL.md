---
name: account-historical-value-analyzer
description: Analyze brokerage statements, transaction histories, PDFs, images, CSVs, or spreadsheets to reconstruct end-of-day holdings and determine the highest total account market value on any date in a requested period. Use for historical securities-account valuation; do not use for tax basis, capital gains, or regulatory reporting unless separately requested.
metadata:
  version: "0.1.2"
---

# Account Historical Value Analyzer

Use available PDF, document, spreadsheet, OCR, and web-research capabilities as needed. Historical prices are time-sensitive source data: verify them from reliable sources and cite them in the result.

## Purpose

Determine the highest total monetary value of an investment account during a specified period.

For each valid valuation date:

1. determine the securities held in the account,
2. reconstruct the end-of-day share balance for each security,
3. obtain the historical unadjusted closing price for each security,
4. calculate each security's market value,
5. sum all security values into a total account value,
6. compare total account value across dates,
7. report the highest total account value and the exact date on which it occurred.

The target metric is:

`security_value[i,d] = shares_held[i,d] * unadjusted_close[i,d]`

`account_value[d] = SUM(security_value[i,d])`

`maximum_account_value = MAX(account_value[d])`

The objective is account-level monetary value. Do not substitute highest share count, highest security price, or the sum of independently calculated per-security maxima.

---

# Scope

Version 0.1.2 supports:

- PDF brokerage statements,
- image-based brokerage statements,
- transaction confirmations,
- account-history files,
- CSV files,
- Excel files,
- BUY and SELL transactions,
- historical holding reconstruction,
- historical market-price lookup,
- daily security valuation,
- daily account valuation,
- maximum account-value calculation,
- source provenance and confidence flags.

Version 0.1.2 does not automatically perform:

- capital-gain calculations,
- tax-basis calculations,
- wash-sale calculations,
- PFIC calculations,
- FBAR calculations,
- Form 8938 calculations,
- regulatory-specific valuation rules,
- dividend accounting,
- cash-balance reconstruction,
- options valuation,
- margin-loan reconstruction,
- FX conversion unless explicitly requested.

---

# Critical Accuracy Principle

A transaction-direction error can materially distort historical account value.

Before any holding reconstruction or valuation, independently verify for every material transaction:

- security identity,
- transaction date,
- transaction direction,
- quantity,
- unit.

Never infer BUY versus SELL from expected behavior, cash amount, row location, or neighboring transactions when an explicit transaction label is present.

Preserve the original transaction label exactly as shown in the source and map it explicitly to the normalized transaction type.

Examples:

- `集買` -> `BUY`
- `集賣` -> `SELL`

If the transaction label cannot be read confidently, use:

`REVIEW_REQUIRED`

Do not guess.

---

# Reading PDFs and Image-Based Statements

If PDF text extraction is incomplete or unavailable:

1. inspect the rendered page visually,
2. identify the relevant transaction table,
3. read row values directly from the image,
4. verify transaction direction separately from quantity,
5. record page-level provenance.

Do not treat OCR or parsed text as authoritative when it conflicts with the visible source.

When transaction direction is important, explicitly inspect the source cell containing the BUY/SELL label.

---

# Canonical Transaction Ledger

For each transaction capture:

- account
- security_name
- ticker
- security_identifier
- exchange
- transaction_date
- original_transaction_label
- transaction_type
- original_quantity
- original_unit
- normalized_shares
- signed_shares
- source_file
- source_page
- supporting_source_text
- confidence
- review_status

Supported normalized transaction types:

- `BUY`
- `SELL`
- `SPLIT`
- `REVERSE_SPLIT`
- `TRANSFER_IN`
- `TRANSFER_OUT`
- `OTHER`
- `UNKNOWN`

Version 0.1.2 fully supports `BUY` and `SELL`.

Use:

`BUY  -> signed_shares = +shares`

`SELL -> signed_shares = -shares`

---

# Quantity Normalization

Never silently alter source units.

If the source reports lots rather than shares, preserve both the original and normalized values.

Example:

- original_quantity = 2
- original_unit = lots
- normalized_shares = 2000
- normalization_rule = "1 lot = 1,000 shares"

If the conversion rule is uncertain, mark the record:

`REVIEW_REQUIRED`

Do not guess.

---

# Opening Holdings and Incomplete Transaction History

A supplied statement may begin after the account already owned securities.

This is especially important when the first visible transaction for a security is a SELL.

A SELL without an earlier BUY does not mean the account opened a short position.

If the source shows a SELL with no earlier acquisition in the supplied history:

1. classify the transaction as `SELL`,
2. do not convert it into a BUY,
3. do not create a new long position after the sale,
4. recognize that the sold shares may have existed before the supplied transaction history,
5. mark the opening history as incomplete or pre-existing,
6. exclude those sold shares from later holdings after the sale date.

Use one of:

- `KNOWN_OPENING_POSITION`
- `INFERRED_PREEXISTING_POSITION`
- `UNKNOWN_OPENING_POSITION`

If the requested analysis period begins before complete opening holdings are known, clearly state that account-level valuation may be incomplete until opening positions are established.

---

# Holding Reconstruction

For each account and each security:

1. sort transactions chronologically,
2. determine opening holdings if available,
3. apply each transaction in date order,
4. maintain end-of-day share balances,
5. create holding periods and/or daily balances.

Default convention:

> Transactions are reflected in end-of-day holdings on the transaction date.

Therefore:

- shares bought on a date are included in that date's end-of-day valuation,
- shares sold on a date are excluded from that date's end-of-day valuation.

Do not allow unexplained negative holdings unless the source explicitly supports a short position.

If a negative balance occurs unexpectedly:

1. stop valuation for that security,
2. investigate missing opening holdings or missing transactions,
3. mark the issue `REVIEW_REQUIRED`.

---

# Historical Market Price Rules

Default historical valuation price:

`UNADJUSTED DAILY CLOSE`

Do not use adjusted close unless explicitly requested.

Adjusted prices may reflect distributions, dividends, or corporate actions and can differ from the actual quoted market price on the historical date.

For every price record preserve:

- security_name
- ticker
- exchange
- date
- price
- price_type
- currency
- source
- source_url_or_identifier
- retrieval_date

If multiple sources materially disagree:

1. prefer an authoritative exchange or reliable historical-market-data source,
2. verify ticker and exchange,
3. flag unresolved discrepancies.

Do not substitute current prices for missing historical prices.

---

# Non-Trading Days

Do not interpolate market prices.

For maximum-account-value analysis, normally calculate values on actual trading days for which valid historical prices exist.

If securities within the same account trade on different calendars, document how valuation dates are aligned.

---

# Security-Level Valuation

For security `i` on date `d`:

`security_value[i,d] = shares_held[i,d] * close_price[i,d]`

Store:

- date
- account
- security
- ticker
- shares_held
- unadjusted_closing_price
- currency
- security_market_value
- price_source

---

# Account-Level Valuation

For each date:

`account_value[d] = SUM(security_value[i,d])`

The maximum must be calculated only after all securities for the same date are aggregated.

Never calculate:

`max(Security A) + max(Security B)`

unless both maxima occurred on the same date.

This rule is mandatory because individual securities can peak on different dates.

---

# Maximum Account Value

Within the requested analysis period:

1. calculate account value for each valid valuation date,
2. compare all daily totals,
3. identify the highest total,
4. report the exact date,
5. show the complete security-level breakdown for that date,
6. preserve historical price sources,
7. disclose all material assumptions and unresolved uncertainties.

Report:

- account
- analysis period
- maximum account value
- maximum-value date
- valuation currency
- valuation method
- holdings on maximum-value date
- shares held for each security
- closing price for each security
- market value for each security
- price source for each security
- review status

---

# Required Output Tables

## Table 1 — Extracted Transaction Ledger

Columns:

- Account
- Security
- Ticker
- Exchange
- Transaction Date
- Original Transaction Label
- Normalized Transaction Type
- Original Quantity
- Original Unit
- Normalized Shares
- Signed Shares
- Source File
- Source Page
- Confidence
- Review Status

## Table 2 — Holding Period Table

Columns:

- Account
- Security
- Ticker
- Start Date
- End Date
- Shares Held
- Opening Position Status

## Table 3 — Daily Security Valuation

Columns:

- Date
- Account
- Security
- Ticker
- Shares Held
- Unadjusted Closing Price
- Currency
- Security Market Value
- Price Source

## Table 4 — Daily Account Value

Columns:

- Date
- Account
- Total Account Value
- Currency

## Table 5 — Maximum Account Value Summary

Columns:

- Account
- Analysis Period Start
- Analysis Period End
- Maximum Account Value
- Maximum Value Date
- Currency
- Valuation Method
- Price Sources
- Review Status

Also provide the full security-level breakdown for the maximum-value date.

---

# Mandatory QA Checklist

Before reporting a final maximum:

1. verify every transaction date,
2. verify every security identifier,
3. verify every transaction direction directly from the source row,
4. verify the original transaction label,
5. verify every quantity and unit,
6. verify quantity normalization,
7. identify missing opening-position history,
8. verify cumulative share balances,
9. investigate unexplained negative holdings,
10. verify that sold securities are not incorrectly carried forward,
11. verify ticker and exchange,
12. confirm valuation currency,
13. verify historical prices are unadjusted closes,
14. verify historical price dates,
15. recompute every `shares * price` calculation,
16. recompute every daily account total,
17. independently recompute the maximum from the daily account-value table,
18. verify the reported date matches the actual maximum,
19. disclose unresolved uncertainties.

---

# Confidence and Review Rules

Use confidence levels:

- `HIGH`
- `MEDIUM`
- `LOW`

Use:

`REVIEW_REQUIRED`

when any material value is uncertain.

Examples:

- unclear transaction label,
- ambiguous date,
- uncertain security identifier,
- unclear quantity,
- unknown unit,
- missing opening position,
- conflicting transaction records,
- missing historical price,
- conflicting price sources.

Never convert uncertainty into a fabricated value.

---

# Regression Rule: SELL Must Never Be Carried Forward as a Holding

If a row explicitly indicates a sale, the security must not remain in post-sale holdings unless some shares remain after the transaction.

Example:

A statement shows:

- 11,000 shares of Security A sold on July 21,
- no earlier purchase appears in the supplied statement.

Correct behavior:

- classify July 21 as SELL,
- recognize the shares as pre-existing before the supplied history,
- exclude the sold 11,000 shares from holdings after July 21,
- do not reinterpret the transaction as a purchase.

Incorrect behavior:

- treating the sale as a buy,
- adding 11,000 shares to subsequent account holdings,
- inflating later account values.

This regression rule is mandatory.

---

# Example

Transactions:

| Date | Security | Type | Shares |
|---|---|---|---:|
| Jan 1 | ABC | BUY | 100 |
| Jan 2 | ABC | BUY | 100 |
| Jan 3 | ABC | SELL | 100 |

Historical unadjusted closing prices:

| Date | ABC Close |
|---|---:|
| Jan 1 | 100 |
| Jan 2 | 60 |
| Jan 3 | 150 |

End-of-day holdings:

| Date | Shares |
|---|---:|
| Jan 1 | 100 |
| Jan 2 | 200 |
| Jan 3 | 100 |

Account values:

| Date | Shares | Price | Account Value |
|---|---:|---:|---:|
| Jan 1 | 100 | 100 | 10,000 |
| Jan 2 | 200 | 60 | 12,000 |
| Jan 3 | 100 | 150 | 15,000 |

Result:

- Maximum account value: 15,000
- Maximum-value date: Jan 3

This is correct even though Jan 3 does not have the highest share count.

---

# Future Extensions

Potential later versions may add:

- multiple currencies,
- historical FX conversion,
- cash balances,
- dividends,
- stock splits,
- corporate actions,
- transfers between accounts,
- tax-year-specific reporting,
- FBAR valuation rules,
- Form 8938 valuation rules,
- PFIC lot histories,
- tax basis,
- account aggregation,
- brokerage-statement reconciliation,
- automated discrepancy reports.
