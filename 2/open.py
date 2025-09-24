#!/usr/bin/env python3
"""
MFCC Opener с поддержкой двух режимов
"""

import os
import argparse
from MFCC import MFCC

def decompress_file(input_path, output_path=None, mode=None):
    """Распаковывает MFCC файл с автоопределением режима"""
    if not os.path.exists(input_path):
        print(f"❌ Файл не найден: {input_path}")
        return False
    
    # Автоопределение режима
    if mode is None:
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Пробуем определить по содержимому
            try:
                MFCC.decode_split(content)
                mode = 'split'
            except:
                mode = 'nosplit'
            
            print(f"🔍 Автоопределен режим: {mode}")
            
        except Exception as e:
            print(f"❌ Ошибка определения режима: {e}")
            return False
    
    # Распаковка в зависимости от режима
    if mode == 'nosplit':
        if output_path is None:
            if input_path.endswith('.mfcc'):
                output_path = input_path[:-5]
            else:
                output_path = input_path + '.decompressed'
        
        print(f"🎯 Распаковка NOSPLIT: {input_path} → {output_path}")
        return MFCC.decode_file_nosplit(input_path, output_path)
    
    else:  # split mode
        if output_path is None:
            if input_path.endswith('.mfcc'):
                output_path = input_path[:-5] + '_extracted'
            else:
                output_path = 'extracted_files'
        
        print(f"🎯 Распаковка SPLIT: {input_path} → {output_path}")
        return MFCC.decode_file_split(input_path, output_path)

def main():
    parser = argparse.ArgumentParser(
        description='MFCC Opener с поддержкой двух режимов',
        epilog='''
Примеры:
  python open.py file.mfcc                    # Автоопределение режима
  python open.py archive.mfcc -m split        # Явно указать режим
  python open.py file.mfcc -o output.txt      # Указать выходной файл
  python open.py file.mfcc -a                 # Анализ без распаковки
        '''
    )
    
    parser.add_argument('input', help='MFCC файл для распаковки')
    parser.add_argument('-o', '--output', help='Выходной файл или папка')
    parser.add_argument('-m', '--mode', choices=['split', 'nosplit'],
                       help='Явное указание режима')
    parser.add_argument('-a', '--analyze', action='store_true',
                       help='Анализ файла без распаковки')
    
    args = parser.parse_args()
    
    print("🎉 === MFCC File Opener ===")
    print("🚀 Два режима: SPLIT (архив) и NOSPLIT (один файл)")
    print("=" * 60)
    
    if args.analyze:
        MFCC.analyze_file(args.input)
        return
    
    decompress_file(args.input, args.output, args.mode)

if __name__ == "__main__":
    main()
