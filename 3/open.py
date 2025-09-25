#!/usr/bin/env python3
"""
MFCC Opener с автоопределением режима распаковки
"""

import os
import argparse
from MFCC import MFCC

def decompress_file(input_path, output_path=None):
    """Умная распаковка с автоопределением режима"""
    if not os.path.exists(input_path):
        print(f"❌ Файл не найден: {input_path}")
        return False
    
    if output_path is None:
        if input_path.endswith('.mfcc'):
            output_path = input_path[:-5]
        else:
            output_path = input_path + '.decompressed'
    
    print(f"🎯 Распаковка файла: {input_path}")
    
    # Используем автоматический режим
    return MFCC.decode_file_auto(input_path, output_path)

def main():
    parser = argparse.ArgumentParser(description='MFCC Opener с автоопределением')
    parser.add_argument('input', help='MFCC файл для распаковки')
    parser.add_argument('-o', '--output', help='Выходной файл')
    
    args = parser.parse_args()
    
    print("🎉 === MFCC File Opener ===")
    print("🚀 Умная распаковка с автоопределением режима")
    print("=" * 50)
    
    decompress_file(args.input, args.output)

if __name__ == "__main__":
    main()
