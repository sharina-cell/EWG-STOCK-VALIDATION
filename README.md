# EWG Stock Validation

Compares the **TC Product Master** stock quantities against marketplace
exports (TikTok, Shopee, Lazada, Amazon, Shopify) and produces a
color-coded Excel report of mismatches.

- 🔴 **Red** = marketplace stock is **higher** than TC Master
- 🟢 **Green** = marketplace stock is **lower** than TC Master

Available as both a **Streamlit web app** and a **command-line script**.

## Live app

Run it locally (see below) or deploy it to [Streamlit Community Cloud](https://streamlit.io/cloud) for a shareable link.

## How it works

| Platform | Source file | TC comparison column |
|---|---|---|
| TikTok | `EWG_TT_SC.xlsx` | `MyStock-MP quantity` (col M) |
| Shopee | `EWG_SH_SC.xlsx` | `MyStock-MP quantity` (col M) |
| Lazada | `EWG_LZ_SC.xlsx` | `MyStock-MP quantity` (col M) |
| Amazon | `EWG_AMAZON*.xlsx/.csv` | `MyStock-MP quantity` (col M) |
| Shopify | `EWG_SHOPIFY_*.csv` | `MyStock-d2c quantity` (col L) |

The output workbook contains:
- A **CONSOLIDATED** sheet (first) listing every unique SKU with a mismatch, across all platforms.
- One sheet per platform with row-level color coding.

## Project structure

```
ewg-stock-validation/
├── app.py                      # Streamlit web app
├── cli.py                      # Command-line script (folder-based, like the original)
├── stock_validation/
│   ├── __init__.py
│   └── core.py                 # Shared loading/comparison/report-building logic
├── requirements.txt
├── .streamlit/config.toml      # Streamlit theme
└── sample_data/                # (optional) sample files for testing
```

## Setup

```bash
git clone https://github.com/<your-username>/ewg-stock-validation.git
cd ewg-stock-validation
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Streamlit app

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`), upload the TC Product Master plus any marketplace files in the sidebar, click **Run validation**, and download the generated `.xlsx` report.

## Run the CLI version

Place your files in a folder (default `./uploads`) using these naming conventions (case-insensitive substring match):

- TC Master: filename containing `TC_PRODUCT_MASTER` or `PRODUCT_MASTER` (`.csv`)
- TikTok: `TT_SC` or `TIKTOK` (`.xlsx`)
- Shopee: `SH_SC` or `SHOPEE` (`.xlsx`)
- Lazada: `LZ_SC` or `LAZADA` (`.xlsx`)
- Amazon: `AMAZON` (`.xlsx`/`.csv`)
- Shopify: `SHOPIFY` (`.csv`/`.xlsx`)

```bash
python cli.py --upload-dir ./uploads --output-dir ./outputs
```

The report is saved to `./outputs/EWG_Stock_Validation_YYYYMMDD.xlsx`.

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in, and click **New app**.
3. Point it at your repo, branch, and `app.py`.
4. Deploy — Streamlit installs `requirements.txt` automatically.

## License

MIT — see [LICENSE](LICENSE).
