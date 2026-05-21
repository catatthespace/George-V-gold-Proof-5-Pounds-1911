#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHTMLファイルからLot情報を抽出してCSVに変換するスクリプト
"""

import csv
import re
from pathlib import Path
from email.parser import BytesParser
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class MHTMLExtractor:
    """MHTMLファイルからHTMLコンテンツを抽出"""
    
    @staticmethod
    def extract_html_from_mhtml(mhtml_path: str) -> str:
        """MHTMLファイルからHTML本体を抽出"""
        with open(mhtml_path, 'rb') as f:
            msg = BytesParser().parsebytes(f.read())
        
        # multipart メッセージから text/html パートを取得
        html_content = None
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True)
                break
        
        if html_content:
            return html_content.decode('utf-8', errors='ignore')
        else:
            raise ValueError("HTML content not found in MHTML file")


class LotParser:
    """HTMLからLot情報を抽出"""
    
    @staticmethod
    def parse_lots(html_content: str) -> List[Dict]:
        """HTMLコンテンツからLot情報を抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        lots = []
        
        # Lot要素を検索 (class="item-block list"を持つli要素)
        lot_items = soup.find_all('li', {'class': re.compile(r'item-block.*list')})
        
        for item in lot_items:
            lot_info = LotParser._extract_lot_info(item)
            if lot_info:
                lots.append(lot_info)
        
        return lots
    
    @staticmethod
    def _extract_lot_info(item) -> Optional[Dict]:
        """単一のLot要素から情報を抽出"""
        try:
            # Auction No と Lot No をURLから抽出
            link = item.find('a', href=re.compile(r'saleNo.*lotNo'))
            if not link:
                return None
            
            href = link.get('href', '')
            auction_no = LotParser._extract_param(href, 'saleNo')
            lot_no = LotParser._extract_param(href, 'lotNo')
            
            if not auction_no or not lot_no:
                return None
            
            # 名称を抽出
            title_elem = item.find('a', {'class': re.compile(r'item-title')})
            name = ''
            if title_elem:
                # b タグのテキストを結合
                b_tags = title_elem.find_all('b')
                name_parts = [b.get_text(strip=True) for b in b_tags]
                # その他のテキスト
                other_text = title_elem.get_text(strip=True)
                # b タグのテキストを削除した残り
                for part in name_parts:
                    other_text = other_text.replace(part, '', 1)
                name = ' '.join(name_parts + [other_text.strip()]).strip()
                if not name:
                    name = title_elem.get_text(strip=True)
            
            # Service と Grade を抽出
            service = ''
            grade = ''
            data_blocks = item.find_all('strong', {'class': 'block-item'})
            if len(data_blocks) >= 2:
                service = data_blocks[0].get_text(strip=True)
                grade = data_blocks[1].get_text(strip=True)
            
            # Auction Ended を抽出
            auction_ended = ''
            time_elem = item.find('strong', {'class': 'time-remaining'})
            if time_elem:
                auction_ended = time_elem.get_text(strip=True)
            
            # Sold For を抽出
            sold_for = ''
            price_elem = item.find('span', {'class': re.compile(r'bot-price-data')})
            if price_elem:
                sold_for_text = price_elem.get_text(strip=True)
                sold_for = sold_for_text
                
                # 不成立判定：金額以外の文字列が入っているかチェック
                # 金額は $ と数字、コンマ、ドットのみで構成される
                if not re.match(r'^\$[\d,]+\.?\d*$', sold_for_text):
                    # 不成立と判定
                    sold_for = f"{sold_for_text} [不成立]"
            
            return {
                'auction_no': auction_no,
                'lot_no': lot_no,
                'name': name,
                'service': service,
                'grade': grade,
                'auction_ended': auction_ended,
                'sold_for': sold_for
            }
        
        except Exception as e:
            print(f"Error extracting lot info: {e}")
            return None
    
    @staticmethod
    def _extract_param(url: str, param_name: str) -> Optional[str]:
        """URLからパラメータ値を抽出"""
        pattern = rf'{param_name}=(\d+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None


class CSVWriter:
    """Lot情報をCSVに書き込み"""
    
    @staticmethod
    def write_csv(lots: List[Dict], output_path: str) -> None:
        """Lot情報をCSVファイルに書き込み"""
        if not lots:
            print("No lots to write")
            return
        
        headers = [
            'Auction No.',
            'Lot No.',
            'Name',
            'Service',
            'Grade',
            'Auction Ended',
            'Sold For'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for lot in lots:
                writer.writerow({
                    'Auction No.': lot['auction_no'],
                    'Lot No.': lot['lot_no'],
                    'Name': lot['name'],
                    'Service': lot['service'],
                    'Grade': lot['grade'],
                    'Auction Ended': lot['auction_ended'],
                    'Sold For': lot['sold_for']
                })
        
        print(f"CSV written to {output_path}")


def main():
    """メイン処理"""
    # MHTML ファイルパス
    mhtml_file = 'Search_ Great Britain George V gold Proof 5 Pounds 1911.mhtml'
    output_csv = 'auction_results.csv'
    
    try:
        # MHTML からHTMLを抽出
        print(f"Extracting HTML from {mhtml_file}...")
        html_content = MHTMLExtractor.extract_html_from_mhtml(mhtml_file)
        
        # HTMLからLot情報を解析
        print("Parsing lot information...")
        lots = LotParser.parse_lots(html_content)
        
        print(f"Found {len(lots)} lots")
        
        # CSVに書き込み
        print(f"Writing to {output_csv}...")
        CSVWriter.write_csv(lots, output_csv)
        
        print("Done!")
        
        # 最初の5件を表示（確認用）
        print("\n=== First 5 lots ===")
        for i, lot in enumerate(lots[:5], 1):
            print(f"\n{i}. Auction {lot['auction_no']}, Lot {lot['lot_no']}")
            print(f"   Name: {lot['name']}")
            print(f"   Service: {lot['service']}, Grade: {lot['grade']}")
            print(f"   Ended: {lot['auction_ended']}")
            print(f"   Sold For: {lot['sold_for']}")
    
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == '__main__':
    main()
