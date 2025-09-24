#!/usr/bin/env python3
"""
MFCC Opener - MyFirstCoolCodec декомпрессор
Открывает файлы .mfcc и извлекает оригинальные файлы
"""

import os
import sys
import argparse
from MFCC import MFCC

def decompress_file(input_path, output_path=None):
    """
    Распаковывает файл из формата MFCC
    
    Args:
        input_path: Путь к .mfcc файлу
        output_path: Путь для сохранения (если None, убирает .mfcc расширение)
    """
    if not os.path.exists(input_path):
        print(f"❌ Файл не найден: {input_path}")
        return False
    
    if not input_path.endswith('.mfcc'):
        print(f"⚠️  Предупреждение: Файл не имеет расширения .mfcc: {input_path}")
    
    if output_path is None:
        # Убираем .mfcc расширение
        if input_path.endswith('.mfcc'):
            output_path = input_path[:-5]
        else:
            output_path = input_path + '.decompressed'
    
    print(f"🎯 Распаковка файла: {input_path}")
    return MFCC.decode_file(input_path, output_path)

def decompress_directory(directory_path, recursive=False):
    """
    Распаковывает все .mfcc файлы в директории
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
                if filename.endswith('.mfcc'):
                    file_path = os.path.join(root, filename)
                    total_count += 1
                    if decompress_file(file_path):
                        success_count += 1
                    print("─" * 60)
    else:
        # Только текущая директория
        for filename in os.listdir(directory_path):
            if filename.endswith('.mfcc'):
                file_path = os.path.join(directory_path, filename)
                total_count += 1
                if decompress_file(file_path):
                    success_count += 1
                print("─" * 60)
    
    print(f"📊 Итог: успешно распаковано {success_count}/{total_count} файлов")
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(
        description='MFCC Opener - открывает файлы .mfcc',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  python open.py document.txt.mfcc          # Распаковать файл
  python open.py image.mfcc -o restored.jpg # Распаковать с указанием имени
  python open.py ./folder -r                # Распаковать всю папку рекурсивно
  python open.py file.mfcc -a               # Проанализировать файл
        '''
    )
    
    parser.add_argument('input', help='Путь к .mfcc файлу или директории')
    parser.add_argument('-o', '--output', help='Путь для сохранения распакованного файла')
    parser.add_argument('-a', '--analyze', action='store_true', 
                       help='Проанализировать структуру MFCC файла без распаковки')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Рекурсивная распаковка всех .mfcc файлов в директории')
    parser.add_argument('-v', '--version', action='store_true', 
                       help='Показать версию')
    
    args = parser.parse_args()
    
    if args.version:
        print("MFCC Opener 2.0")
        return
    
    print("🎉 === MFCC File Opener ===")
    print("🚀 MyFirstCoolCodec - Ultimate Decompression Technology")
    print("🔍 Формат с разделителями: COUNT|HEX|")
    print("=" * 60)
    
    if args.analyze and os.path.isfile(args.input):
        MFCC.analyze_file(args.input)
        return
    
    if os.path.isfile(args.input):
        decompress_file(args.input, args.output)
    
    elif os.path.isdir(args.input):
        decompress_directory(args.input, args.recursive)
    
    else:
        print(f"❌ Ошибка: '{args.input}' не является файлом или директорией")

if __name__ == "__main__":
    main()
