import os
import json
from typing import Union, List, Dict

class MFCC:
    """
    MyFirstCoolCodec (MFCC) Ultimate Version с двумя режимами
    - nosplit: обычное сжатие (один файл → один .mfcc)
    - split: архивация (папка/файлы → один .mfcc с метаданными)
    """
    
    # === NOSPLIT MODE ===
    @staticmethod
    def encode_nosplit(data: Union[bytes, str]) -> str:
        """Сжимает данные используя RLE с разделителями (одиночный файл)"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hex_str = data.hex().upper()
        if not hex_str:
            return ""
        
        encoded = []
        count = 1
        current_char = hex_str[0]
        
        for i in range(1, len(hex_str)):
            if hex_str[i] == current_char and count < 255:
                count += 1
            else:
                if count > 3:
                    encoded.append(f"{count:02X}|{current_char}|")
                else:
                    encoded.append(current_char * count)
                count = 1
                current_char = hex_str[i]
        
        if count > 3:
            encoded.append(f"{count:02X}|{current_char}|")
        else:
            encoded.append(current_char * count)
            
        return "".join(encoded)
    
    @staticmethod
    def decode_nosplit(compressed_data: str) -> bytes:
        """Восстанавливает данные из nosplit формата"""
        if not compressed_data:
            return b""
        
        decoded_hex = []
        i = 0
        
        while i < len(compressed_data):
            if (i + 4 <= len(compressed_data) and 
                compressed_data[i+2] == '|' and 
                compressed_data[i+4] == '|'):
                
                if (compressed_data[i] in '0123456789ABCDEF' and 
                    compressed_data[i+1] in '0123456789ABCDEF' and
                    compressed_data[i+3] in '0123456789ABCDEF'):
                    
                    try:
                        count = int(compressed_data[i:i+2], 16)
                        symbol = compressed_data[i+3]
                        decoded_hex.append(symbol * count)
                        i += 5
                        continue
                    except ValueError:
                        pass
            
            if compressed_data[i] in '0123456789ABCDEF':
                decoded_hex.append(compressed_data[i])
            i += 1
        
        hex_str = "".join(decoded_hex)
        if len(hex_str) % 2 != 0:
            hex_str += '0'
        
        return bytes.fromhex(hex_str)
    
    # === SPLIT MODE ===
    @staticmethod
    def encode_split(files_data: Dict[str, bytes]) -> str:
        """
        Архивирует несколько файлов в один MFCC
        
        Args:
            files_data: {путь_к_файлу: данные}
            
        Returns:
            MFCC строка с метаданными
        """
        archive = {
            "metadata": {
                "version": "MFCC-SPLIT-1.0",
                "file_count": len(files_data),
                "files": {}
            },
            "content": {}
        }
        
        # Сжимаем каждый файл и добавляем метаданные
        for file_path, data in files_data.items():
            compressed = MFCC.encode_nosplit(data)
            file_name = os.path.basename(file_path)
            
            archive["metadata"]["files"][file_name] = {
                "original_size": len(data),
                "compressed_size": len(compressed),
                "path": file_path
            }
            
            archive["content"][file_name] = compressed
        
        # Конвертируем в JSON и затем в HEX
        archive_json = json.dumps(archive, ensure_ascii=False, indent=2)
        return MFCC.encode_nosplit(archive_json.encode('utf-8'))
    
    @staticmethod
    def decode_split(compressed_archive: str) -> Dict[str, bytes]:
        """
        Распаковывает архив MFCC обратно в файлы
        """
        # Сначала распаковываем архив
        archive_data = MFCC.decode_nosplit(compressed_archive)
        archive_json = archive_data.decode('utf-8')
        archive = json.loads(archive_json)
        
        # Затем распаковываем каждый файл внутри архива
        result = {}
        for file_name, compressed_content in archive["content"].items():
            file_data = MFCC.decode_nosplit(compressed_content)
            result[file_name] = file_data
        
        return result
    
    # === FILE OPERATIONS ===
    @staticmethod
    def encode_file_nosplit(input_path: str, output_path: str) -> bool:
        """Сжимает один файл в режиме nosplit"""
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            compressed = MFCC.encode_nosplit(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(compressed)
            
            orig_size = len(data)
            comp_size = len(compressed)
            ratio = (1 - comp_size / (orig_size * 2)) * 100
            
            print(f"✅ Nosplit: {input_path} → {output_path}")
            print(f"📊 Эффективность: {ratio:.1f}%")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка nosplit: {e}")
            return False
    
    @staticmethod
    def encode_file_split(input_paths: List[str], output_path: str) -> bool:
        """Создает архив из нескольких файлов/папок в режиме split"""
        try:
            files_data = {}
            
            # Собираем все файлы
            for path in input_paths:
                if os.path.isfile(path):
                    with open(path, 'rb') as f:
                        files_data[path] = f.read()
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'rb') as f:
                                # Сохраняем относительный путь
                                rel_path = os.path.relpath(file_path, os.path.dirname(path))
                                files_data[rel_path] = f.read()
            
            if not files_data:
                print("❌ Нет файлов для архивации")
                return False
            
            # Создаем архив
            compressed_archive = MFCC.encode_split(files_data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(compressed_archive)
            
            total_size = sum(len(data) for data in files_data.values())
            print(f"✅ Split: {len(files_data)} файлов → {output_path}")
            print(f"📊 Общий размер: {total_size} байт")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка split: {e}")
            return False
    
    @staticmethod
    def decode_file_nosplit(input_path: str, output_path: str) -> bool:
        """Распаковывает nosplit файл"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                compressed_data = f.read()
            
            decoded_data = MFCC.decode_nosplit(compressed_data)
            
            with open(output_path, 'wb') as f:
                f.write(decoded_data)
            
            print(f"✅ Nosplit распакован: {input_path} → {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка распаковки nosplit: {e}")
            return False
    
    @staticmethod
    def decode_file_split(input_path: str, output_dir: str) -> bool:
        """Распаковывает split архив"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                compressed_archive = f.read()
            
            files_data = MFCC.decode_split(compressed_archive)
            
            # Создаем директорию если нужно
            os.makedirs(output_dir, exist_ok=True)
            
            # Сохраняем файлы
            for file_name, data in files_data.items():
                file_path = os.path.join(output_dir, file_name)
                
                # Создаем поддиректории если нужно
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'wb') as f:
                    f.write(data)
                
                print(f"📁 Извлечен: {file_name}")
            
            print(f"✅ Split распакован: {input_path} → {output_dir}")
            print(f"📊 Извлечено файлов: {len(files_data)}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка распаковки split: {e}")
            return False
    
    @staticmethod
    def analyze_file(file_path: str):
        """Анализирует MFCC файл и определяет режим"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔍 Анализ MFCC файла: {file_path}")
            print(f"📊 Размер: {len(content)} символов")
            
            # Пробуем определить режим
            try:
                # Пробуем распаковать как split архив
                files_data = MFCC.decode_split(content)
                print("🎯 Режим: SPLIT (архив)")
                print(f"📁 Файлов в архиве: {len(files_data)}")
                for name, data in files_data.items():
                    print(f"   📄 {name}: {len(data)} байт")
                    
            except:
                # Если не split, то nosplit
                print("🎯 Режим: NOSPLIT (один файл)")
                decoded_size = len(MFCC.decode_nosplit(content))
                print(f"📄 Размер файла: {decoded_size} байт")
            
            print(f"🔢 RLE блоков: {content.count('|') // 2}")
            
        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")
