Independent keyword/rule baselines for 200-document LLM validation

Files:
- baseline_200_documents.csv: 200 original document titles and abstracts (60 associated; 140 no association).
- baseline_200_gold.csv: 254 unique manually labeled (document, RE, descriptor) links derived from supplied manual labels; not independently adjudicated.
- build_keyword_baseline.py: standalone Python 3 standard-library script; reads the two CSVs and creates two independent prediction outputs.
- baseline_rule_predictions.csv: same-sentence element--descriptor rule output.
- baseline_docwide_predictions.csv: whole-document co-occurrence rule output.

Run: python build_keyword_baseline.py