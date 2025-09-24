#!/usr/bin/env python3
"""
MFCC Compressor - MyFirstCoolCodec компрессор
Сжимает любые файлы в формат .mfcc с разделителями
"""

import os
import sys
import argparse
from MFCC import MFCC

def compress_file(input_path, output_path=None):
    """
    Сжимает файл в формат MFCC
    
    Args:
        input_path: Путь к исходному файлу
        output_path: Путь для сохранения (если None, то input_path.mfcc)
    """
    if not os.path.exists(input_path):
        print(f"❌ Файл не найден: {input_path}")
        return False
    
    if output_path is None:
        output_path = input_path + '.mfcc'
    
    print(f"🎯 Сжатие файла: {input_path}")
    return MFCC.encode_file(input_path, output_path)

def compress_directory(directory_path, recursive=False):
    """
    Сжимает все файлы в директории
    """
    if not os.path.exists(directory_path):
        print(f"❌ Директория не найдена: {directory_path}")
        return False
    
    success_count = 0
    total_count = 0
    
    if recursive:
        # Рекурсивный обход
        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                if not filename.endswith('.mfcc'):  # Не сжимаем уже сжатые файлы
                    file_path = os.path.join(root, filename)
                    total_count += 1
                    if compress_file(file_path):
                        success_count += 1
                    print("─" * 60)
    else:
        # Только текущая директория
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path) and not filename.endswith('.mfcc'):
                total_count += 1
                if compress_file(file_path):
                    success_count += 1
                print("─" * 60)
    
    print(f"📊 Итог: успешно сжато {success_count}/{total_count} файлов")
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(
        description='MFCC Compressor - сжимает файлы в формат .mfcc',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  python compressor.py document.txt          # Сжать файл
  python compressor.py image.jpg -o img.mfcc # Сжать с указанием имени
  python compressor.py ./folder -r           # Сжать всю папку рекурсивно
        '''
    )
    
    parser.add_argument('input', help='Путь к файлу или директории для сжатия')
    parser.add_argument('-o', '--output', help='Путь для сохранения сжатого файла')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='Рекурсивное сжатие всех файлов в директории')
    parser.add_argument('-v', '--version', action='version', version='MFCC Compressor 2.0')
    
    args = parser.parse_args()
    
    print("🎉 === MFCC Compressor ===")
    print("🚀 MyFirstCoolCodec - Ultimate Compression Technology")
    print("📁 Формат с разделителями: COUNT|HEX|")
    print("=" * 60)
    
    if os.path.isfile(args.input):
        compress_file(args.input, args.output)
    
    elif os.path.isdir(args.input):
        compress_directory(args.input, args.recursive)
    
    else:
        print(f"❌ Ошибка: '{args.input}' не является файлом или директорией")

if __name__ == "__main__":
    main()