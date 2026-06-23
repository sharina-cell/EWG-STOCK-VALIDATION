"""
EWG Stock Validation — Streamlit App
======================================
Upload the TC Product Master plus any combination of marketplace exports
(TikTok, Shopee, Lazada, Amazon, Shopify) and download a color-coded
Excel mismatch report.
"""

from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st

from stock_validation.core import run_validation

st.set_page_config(
    page_title="EWG Stock Validation",
    page_icon="📦",
    layout="wide",
)

st.title("📦 EWG Stock Validation")
st.caption(
    "Compare the TC Product Master against marketplace stock exports "
    "(TikTok, Shopee, Lazada, Amazon, Shopify) and download a color-coded mismatch report."
)

# ── Sidebar: uploads ────────────────────────────────────────────────────────
st.sidebar.header("1. Upload files")

tc_upload = st.sidebar.file_uploader(
    "TC Product Master (.csv) — required",
    type=["csv"],
    accept_multiple_files=False,
)

st.sidebar.markdown("**Marketplace files** (upload any that apply)")

tiktok_upload = st.sidebar.file_uploader("TikTok (EWG_TT_SC.xlsx)", type=["xlsx"])
shopee_upload = st.sidebar.file_uploader("Shopee (EWG_SH_SC.xlsx)", type=["xlsx"])
lazada_upload = st.sidebar.file_uploader("Lazada (EWG_LZ_SC.xlsx)", type=["xlsx"])
amazon_upload = st.sidebar.file_uploader("Amazon (.xlsx or .csv)", type=["xlsx", "csv"])
shopify_upload = st.sidebar.file_uploader("Shopify (.csv or .xlsx)", type=["csv", "xlsx"])

run_clicked = st.sidebar.button("Run validation", type="primary", use_container_width=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
def to_platform_files(upload, label):
    """Wrap a single Streamlit UploadedFile into the (file, filename) list format core expects."""
    if upload is None:
        return []
    # Streamlit's UploadedFile is already file-like and seekable
    return [(BytesIO(upload.getvalue()), upload.name)]


def log_to_list(buffer):
    def _log(msg):
        buffer.append(msg)
    return _log


# ── Main panel ───────────────────────────────────────────────────────────────
if not run_clicked:
    st.info("Upload the TC Product Master and at least one marketplace file, then click **Run validation** in the sidebar.")
    with st.expander("Expected file formats"):
        st.markdown(
            """
            | Platform | Expected columns | TC comparison column |
            |---|---|---|
            | TikTok | `Seller SKU`, `Quantity` (header on row 3) | MyStock-MP quantity |
            | Shopee | `SKU` / `Parent SKU`, `Stock` (header on row 3) | MyStock-MP quantity |
            | Lazada | `SellerSKU`, `Quantity` (header on row 1, data from row 4) | MyStock-MP quantity |
            | Amazon | auto-detected SKU + quantity columns | MyStock-MP quantity |
            | Shopify | `SKU`, `Available (not editable)` | MyStock-d2c quantity |
            | TC Master | `sellerSKU`, `Item title`, `MyStock-MP quantity`, `MyStock-d2c quantity` | — |
            """
        )
    st.stop()

if tc_upload is None:
    st.error("Please upload the TC Product Master CSV before running validation.")
    st.stop()

platform_files = {
    'tiktok': to_platform_files(tiktok_upload, 'tiktok'),
    'shopee': to_platform_files(shopee_upload, 'shopee'),
    'lazada': to_platform_files(lazada_upload, 'lazada'),
    'amazon': to_platform_files(amazon_upload, 'amazon'),
    'shopify': to_platform_files(shopify_upload, 'shopify'),
}

if not any(platform_files.values()):
    st.error("Please upload at least one marketplace file.")
    st.stop()

log_lines = []
with st.spinner("Comparing stock levels..."):
    try:
        tc_bytes = BytesIO(tc_upload.getvalue())
        wb, all_results = run_validation(tc_bytes, platform_files, log=log_to_list(log_lines))
    except Exception as e:
        st.error(f"Validation failed: {e}")
        with st.expander("Log"):
            st.code("\n".join(log_lines))
        st.stop()

with st.expander("Run log", expanded=False):
    st.code("\n".join(log_lines))

# ── Summary metrics ──────────────────────────────────────────────────────────
st.subheader("Summary")
cols = st.columns(len(all_results) or 1)
if not all_results:
    st.warning("No mismatches found, or none of the SKUs matched between TC Master and the uploaded files.")
else:
    for col, (label, df) in zip(cols, all_results.items()):
        higher = (df['Difference (Mktpl-TC)'] > 0).sum() if len(df) else 0
        lower = (df['Difference (Mktpl-TC)'] < 0).sum() if len(df) else 0
        col.metric(label.title(), f"{len(df)} mismatches", f"▲{higher} / ▼{lower}")

# ── Per-platform previews ────────────────────────────────────────────────────
st.subheader("Mismatch details")
if all_results:
    tabs = st.tabs([label.title() for label in all_results.keys()])
    for tab, (label, df) in zip(tabs, all_results.items()):
        with tab:
            if len(df) == 0:
                st.success("No mismatches for this platform 🎉")
            else:
                def highlight_diff(row):
                    diff = row['Difference (Mktpl-TC)']
                    color = '#ffe0e0' if diff > 0 else ('#e0ffe0' if diff < 0 else '')
                    return [f'background-color: {color}'] * len(row)

                st.dataframe(
                    df.style.apply(highlight_diff, axis=1),
                    use_container_width=True,
                    hide_index=True,
                )

# ── Download ─────────────────────────────────────────────────────────────────
st.subheader("Download report")
buf = BytesIO()
wb.save(buf)
buf.seek(0)

out_name = f'EWG_Stock_Validation_{date.today().strftime("%Y%m%d")}.xlsx'
st.download_button(
    label="⬇️ Download Excel report",
    data=buf,
    file_name=out_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
)
