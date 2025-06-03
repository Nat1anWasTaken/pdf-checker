#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyPDF2 import PdfReader
from colorama import init, Fore, Style

def get_pdf_info(filepath):
    """
    讀取單一 PDF 檔案，回傳 (author, num_pages, is_encrypted)。
    若加密無法讀取頁數時，num_pages 以 None 表示。
    """
    try:
        reader = PdfReader(filepath)
    except Exception as e:
        # 如果無法初始化 PdfReader，直接回傳錯誤資訊
        return None, None, f"Error: {e}"

    # 檢查加密狀態
    encrypted = reader.is_encrypted

    author = None
    num_pages = None

    if encrypted:
        # 如果 PDF 有密碼保護，嘗試以空密碼解密（部分 PDF 允許空字串）
        try:
            reader.decrypt('')
            encrypted = False  # 若成功 decrypt，則視為未加密
        except Exception:
            # 解密失敗，保持 encrypted = True
            pass

    # 只有在未加密或成功解密後，才能取得頁數
    if not encrypted:
        try:
            num_pages = len(reader.pages)
        except Exception:
            num_pages = None

        # metadata 可能為 None 或屬性不存在
        try:
            meta = reader.metadata
            author = meta.author if meta and hasattr(meta, 'author') else None
        except Exception:
            author = None

    return author, num_pages, encrypted


def print_colored_info(filepath, author, num_pages, encrypted):
    """
    以彩色格式輸出單一 PDF 的資訊：
    - 檔名：淡藍色 (Fore.CYAN)
    - 標籤：綠色 (Fore.GREEN)
    - 值：黃色 (Fore.YELLOW)，若為警告或錯誤則紅色 (Fore.RED)
    """
    basename = os.path.basename(filepath)
    print(f"{Fore.CYAN}{basename}{Style.RESET_ALL}")

    # 作者
    label = f"  {Fore.GREEN}Author:{Style.RESET_ALL}"
    if isinstance(author, str) and author.strip():
        print(f"{label} {Fore.YELLOW}{author}{Style.RESET_ALL}")
    else:
        print(f"{label} {Fore.RED}N/A{Style.RESET_ALL}")

    # 頁數
    label = f"  {Fore.GREEN}Pages:{Style.RESET_ALL}"
    if isinstance(num_pages, int):
        print(f"{label} {Fore.YELLOW}{num_pages}{Style.RESET_ALL}")
    else:
        if encrypted:
            print(f"{label} {Fore.RED}Encrypted / 無法取得{Style.RESET_ALL}")
        else:
            print(f"{label} {Fore.RED}Unknown{Style.RESET_ALL}")

    # 加密狀態
    label = f"  {Fore.GREEN}Encrypted:{Style.RESET_ALL}"
    if isinstance(encrypted, bool):
        status = "Yes" if encrypted else "No"
        color = Fore.RED if encrypted else Fore.YELLOW
        print(f"{label} {color}{status}{Style.RESET_ALL}")
    else:
        print(f"{label} {Fore.RED}Error{Style.RESET_ALL}")

    # 分隔線
    print(f"{Fore.MAGENTA}{'-'*40}{Style.RESET_ALL}")


def main(directory):
    init(autoreset=True)  # 初始化 Colorama，並自動在每次列印後重置顏色

    if not os.path.isdir(directory):
        print(f"{Fore.RED}錯誤：路徑 '{directory}' 非目錄 或 不存在。{Style.RESET_ALL}")
        sys.exit(1)

    # 遍歷指定目錄下所有 .pdf 檔案
    pdf_files = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, f))

    if not pdf_files:
        print(f"{Fore.YELLOW}在目錄 '{directory}' 下未找到任何 PDF 檔案。{Style.RESET_ALL}")
        sys.exit(0)

    # 依序處理每個 PDF
    for pdf_path in sorted(pdf_files):
        author, num_pages, encrypted = get_pdf_info(pdf_path)
        print_colored_info(pdf_path, author, num_pages, encrypted)


if __name__ == "__main__":
    # 若未傳入目錄參數，預設檢查當前工作目錄
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    main(target_dir)
