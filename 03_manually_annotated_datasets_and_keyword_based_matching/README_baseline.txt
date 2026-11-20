Independent keyword/rule baselines for 200-document LLM validation

Files:
- baseline_200_documents.csv: 200 original document titles and abstracts (60 associated; 140 no association).
- baseline_200_gold.csv: 250 unique manually labeled (document, RE, descriptor) links derived from supplied manual labels; not independently adjudicated.
- build_keyword_baseline.py: standalone Python 3 standard-library script; reads the two CSVs and creates two independent prediction outputs.
- baseline_rule_predictions.csv: same-sentence element--descriptor rule output.
- baseline_docwide_predictions.csv: whole-document co-occurrence rule output.

Run: python build_keyword_baseline.py

Rules have no dependence on GPT Matched Term, GPT Confidence, or human labels during prediction. Both baselines use a pre-specified lexicon and explicit 14-descriptor mapping. Comparison is retrospective and exploratory; no independent held-out dictionary-development set was supplied. The manual annotation set contains potential semantic inconsistencies, notably acid/corrosion descriptor labels without acid/corrosion mentions. Re-adjudicate before using final SI results.

Evaluation unit: unique (Reference Number, Rare Earth symbol, descriptor code). Do not equate row-level TP/FP/FN with element-level relation metrics when one row contains multiple REs. No document-level TN in relation-level F1.
