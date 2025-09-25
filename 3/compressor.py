#!/usr/bin/env python3
"""
MFCC Compressor с автоопределением режима и многопоточностью
"""

import os
import sys
import argparse
from MFCC import MFCC

def compress_file(input_path, output_path=None):
    """Умное сжатие с автоопределением режима"""
    if not os.path.exists(input_path):
        print(f"❌ Файл не найден: {input_path}")
        return False
    
    if output_path is None:
        output_path = input_path + '.mfcc'
    
    file_size = os.path.getsize(input_path)
    print(f"🎯 Сжатие файла: {input_path}")
    print(f"📊 Размер: {file_size/(1024*1024):.1f} MB")
    
    # Используем автоматический режим
    return MFCC.encode_file_auto(input_path, output_path)

def main():
    parser = argparse.ArgumentParser(description='MFCC Compressor с многопоточностью')
    parser.add_argument('input', help='Путь к файлу для сжатия')
    parser.add_argument('-o', '--output', help='Путь для сохранения сжатого файла')
    parser.add_argument('-t', '--threads', type=int, default=4, 
                       help='Количество потоков (по умолчанию: 4)')
    
    args = parser.parse_args()
    
    print("🎉 === MFCC Compressor ===")
    print("🚀 Умное сжатие с многопоточностью")
    print("🎥 Специальная поддержка MP4")
    print("=" * 50)
    
    compress_file(args.input, args.output)

if __name__ == "__main__":
    main()
