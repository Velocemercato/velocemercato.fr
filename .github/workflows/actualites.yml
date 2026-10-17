name: Veloce Mercato - Actualites

on:
  workflow_dispatch:
  schedule:
    - cron: '*/30 * * * *'

permissions:
  contents: write

jobs:
  actualites:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Update news
        run: python update_news.py
      - name: Validate articles
        run: python -m json.tool articles.json > /dev/null
      - name: Save articles
        run: |
          git add articles.json
          if git diff --cached --quiet; then
            echo 'No new articles'
          else
            git config user.name 'github-actions[bot]'
            git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
            git commit -m 'Update football news'
            git push
          fi
