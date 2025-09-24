#!/usr/bin/env python3
"""
MFCC Compressor с двумя режимами: split и nosplit
"""

import os
import sys
import argparse
from MFCC import MFCC

def compress_nosplit(input_path, output_path=None):
    """Режим nosplit: один файл → один .mfcc"""
    if not os.path.exists(input_path):
        print(f"❌ Файл не найден: {input_path}")
        return False
    
    if output_path is None:
        output_path = input_path + '.mfcc'
    
    print(f"🎯 Режим NOSPLIT: {input_path}")
    return MFCC.encode_file_nosplit(input_path, output_path)

def compress_split(input_paths, output_path=None):
    """Режим split: несколько файлов → один .mfcc архив"""
    if output_path is None:
        if len(input_paths) == 1 and os.path.isfile(input_paths[0]):
            output_path = input_paths[0] + '.mfcc'
        else:
            output_path = 'archive.mfcc'
    
    print(f"🎯 Режим SPLIT: {len(input_paths)} объектов → {output_path}")
    return MFCC.encode_file_split(input_paths, output_path)

def main():
    parser = argparse.ArgumentParser(
        description='MFCC Compressor с двумя режимами',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  
NOSPLIT режим (один файл):
  python compressor.py file.txt                    # Сжать файл
  python compressor.py image.jpg -m nosplit        # Явно указать режим

SPLIT режим (архивация):
  python compressor.py folder -m split            # Архивировать папку
  python compressor.py file1.txt file2.jpg -m split # Архивировать файлы
  python compressor.py . -m split -o my_archive.mfcc # Текущая папка в архив
        '''
    )
    
    parser.add_argument('inputs', nargs='+', help='Файлы или папки для сжатия')
    parser.add_argument('-m', '--mode', choices=['split', 'nosplit'], 
                       help='Режим работы: split (архив) или nosplit (один файл)')
    parser.add_argument('-o', '--output', help='Выходной файл')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Рекурсивная обработка папок (только для split)')
    
    args = parser.parse_args()
    
    print("🎉 === MFCC Compressor ===")
    print("🚀 Два режима: SPLIT (архив) и NOSPLIT (один файл)")
    print("=" * 60)
    
    # Автоопределение режима если не указан
    if args.mode is None:
        if len(args.inputs) == 1 and os.path.isfile(args.inputs[0]):
            args.mode = 'nosplit'
        else:
            args.mode = 'split'
        print(f"🔍 Автоопределен режим: {args.mode}")
    
    # Обработка в зависимости от режима
    if args.mode == 'nosplit':
        if len(args.inputs) > 1:
            print("❌ Nosplit режим работает только с одним файлом!")
            return
        
        compress_nosplit(args.inputs[0], args.output)
    
    else:  # split mode
        # Проверяем что все пути существуют
        valid_paths = []
        for path in args.inputs:
            if os.path.exists(path):
                valid_paths.append(path)
            else:
                print(f"⚠️  Путь не существует: {path}")
        
        if valid_paths:
            compress_split(valid_paths, args.output)
        else:
            print("❌ Нет валидных путей для архивации!")

if __name__ == "__main__":
    main()
