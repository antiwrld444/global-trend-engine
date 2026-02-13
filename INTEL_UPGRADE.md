# INTEL UPGRADE REPORT (2026-02-13)

## 1. Source Weighting System
- **Implementation**: Added `source_weights` dictionary to `NewsCollector`.
- **Weights**:
  - Wired: 1.5
  - TechCrunch: 1.4
  - The Verge: 1.3
  - NYT (Technology): 1.2
  - NYT (Business): 1.1
  - Others/Global: 1.0
- **Database**: Added `source_weight` column to `trends` table.
- **Scoring**: Updated `ScoringEngine` formula to incorporate `source_weight`.
  - New Formula: `(sentiment * 0.4) + (mentions_count * 0.3) + (source_weight * 0.3)`

## 2. Named Entity Extraction (NER)
- **Logic**: Implemented a regex-based extraction in `NLPProcessor.extract_entities`. It identifies capitalized words that are not at the beginning of a sentence.
- **Database**: Added `entities` column to `trends` table.
- **Automation**: Entities are now automatically extracted during the news collection process and saved to the database.

## 3. Pipeline Verification
- **Collection**: Verified via logs that `source_weight` and `entities` are being processed.
- **Storage**: Database schema updated successfully.
- **Analytics**: `ScoringEngine` successfully uses new data for ranking.

## 4. Git Status
- Changes committed and pushed to GitHub.
- Token: [REDACTED FOR SECURITY]
