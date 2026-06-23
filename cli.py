#!/usr/bin/env python3
"""
EWG Stock Validation — CLI
===========================
Compares EWG TC Product Master stock against marketplace files found in a
local folder, and writes a color-coded Excel report.

Usage:
    python cli.py [--upload-dir DIR] [--output-dir DIR]

Defaults:
    --upload-dir  ./uploads
    --output-dir  ./outputs

Expected filenames in --upload-dir (case-insensitive substring match):
    TC Master : *TC_PRODUCT_MASTER* or *PRODUCT_MASTER*   (.csv)
    TikTok    : *TT_SC* or *TIKTOK*                        (.xlsx)
    Shopee    : *SH_SC* or *SHOPEE*                        (.xlsx)
    Lazada    : *LZ_SC* or *LAZADA*                        (.xlsx)
    Amazon    : *AMAZON*                                   (.xlsx/.csv)
    Shopify   : *SHOPIFY*                                  (.csv/.xlsx)
"""

import argparse
import os
from datetime import date

from stock_validation.core import run_validation


def find_files(upload_dir: str, *keywords) -> list[str]:
    """Return all files in upload_dir whose name contains ANY keyword (case-insensitive)."""
    results = []
    for f in os.listdir(upload_dir):
        fl = f.lower()
        if any(kw.lower() in fl for kw in keywords) and (f.endswith('.xlsx') or f.endswith('.csv')):
            results.append(os.path.join(upload_dir, f))
    return results


def main():
    parser = argparse.ArgumentParser(description="EWG Stock Validation CLI")
    parser.add_argument('--upload-dir', default='./uploads', help='Folder containing input files')
    parser.add_argument('--output-dir', default='./outputs', help='Folder to write the report to')
    args = parser.parse_args()

    upload_dir = args.upload_dir
    output_dir = args.output_dir

    tc_files = find_files(upload_dir, 'TC_PRODUCT_MASTER', 'PRODUCT_MASTER')
    tiktok_files = find_files(upload_dir, 'TT_SC', 'TIKTOK')
    shopee_files = find_files(upload_dir, 'SH_SC', 'SHOPEE')
    lazada_files = find_files(upload_dir, 'LZ_SC', 'LAZADA')
    amazon_files = find_files(upload_dir, 'AMAZON')
    shopify_files = find_files(upload_dir, 'SHOPIFY')

    print("Files found:")
    print(f"  TC Master : {tc_files}")
    print(f"  TikTok    : {tiktok_files}")
    print(f"  Shopee    : {shopee_files}")
    print(f"  Lazada    : {lazada_files}")
    print(f"  Amazon    : {amazon_files}")
    print(f"  Shopify   : {shopify_files}")

    if not tc_files:
        raise FileNotFoundError(
            f"TC Product Master not found in {upload_dir}. "
            "Expected a filename containing TC_PRODUCT_MASTER or PRODUCT_MASTER (.csv)."
        )

    platform_files = {
        'tiktok': [(p, os.path.basename(p)) for p in tiktok_files],
        'shopee': [(p, os.path.basename(p)) for p in shopee_files],
        'lazada': [(p, os.path.basename(p)) for p in lazada_files],
        'amazon': [(p, os.path.basename(p)) for p in amazon_files],
        'shopify': [(p, os.path.basename(p)) for p in shopify_files],
    }

    print("\nComparing stocks...")
    wb, all_results = run_validation(tc_files[0], platform_files, log=print)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f'EWG_Stock_Validation_{date.today().strftime("%Y%m%d")}.xlsx')
    wb.save(out_path)
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
