import os
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Union, List, Dict

class MFCC:
    """
    MyFirstCoolCodec (MFCC) с многопоточностью и поддержкой MP4
    """
    
    # === БАЗОВЫЕ ФУНКЦИИ ===
    @staticmethod
    def encode_nosplit(data: Union[bytes, str]) -> str:
        """Сжимает данные используя RLE с разделителями"""
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
    
    # === МНОГОПОТОЧНОСТЬ ДЛЯ БОЛЬШИХ ФАЙЛОВ ===
    @staticmethod
    def encode_large_file_parallel(input_path: str, output_path: str, chunk_size=10*1024*1024, max_workers=4) -> bool:
        """Многопоточное сжатие больших файлов"""
        try:
            file_size = os.path.getsize(input_path)
            total_chunks = (file_size + chunk_size - 1) // chunk_size
            
            print(f"🔧 Многопоточное сжатие: {file_size/(1024*1024):.1f} MB")
            print(f"📦 Чанков: {total_chunks}, Потоков: {max_workers}")
            
            results = []
            lock = threading.Lock()
            
            def process_chunk(chunk_id, start_pos, chunk_size):
                try:
                    with open(input_path, 'rb') as f:
                        f.seek(start_pos)
                        chunk_data = f.read(chunk_size)
                    
                    compressed = MFCC.encode_nosplit(chunk_data)
                    
                    with lock:
                        results.append((chunk_id, compressed))
                    
                    return True
                except Exception as e:
                    print(f"❌ Ошибка в чанке {chunk_id}: {e}")
                    return False
            
            # Запускаем потоки
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for i in range(total_chunks):
                    start_pos = i * chunk_size
                    actual_chunk_size = min(chunk_size, file_size - start_pos)
                    future = executor.submit(process_chunk, i, start_pos, actual_chunk_size)
                    futures.append(future)
                
                # Ждем завершения
                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    if completed % 10 == 0:
                        print(f"📊 Прогресс: {completed}/{total_chunks} чанков")
            
            # Сортируем и сохраняем результаты
            results.sort(key=lambda x: x[0])
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Записываем метаданные для многопоточного формата
                metadata = {
                    "format": "MFCC_PARALLEL",
                    "chunks": total_chunks,
                    "original_size": file_size
                }
                f.write(json.dumps(metadata) + "\n")
                
                for chunk_id, compressed in results:
                    f.write(f"{compressed}\n")
            
            print(f"✅ Многопоточное сжатие завершено: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка многопоточного сжатия: {e}")
            return False
    
    @staticmethod
    def decode_large_file_parallel(input_path: str, output_path: str, max_workers=4) -> bool:
        """Многопоточная распаковка больших файлов"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines or len(lines) < 2:
                print("❌ Неверный формат многопоточного файла")
                return False
            
            # Читаем метаданные
            metadata = json.loads(lines[0].strip())
            total_chunks = metadata["chunks"]
            
            print(f"🔧 Многопоточная распаковка: {total_chunks} чанков")
            
            if len(lines) != total_chunks + 1:
                print("❌ Несоответствие количества чанков")
                return False
            
            results = []
            lock = threading.Lock()
            
            def process_chunk(chunk_id, compressed_data):
                try:
                    decoded = MFCC.decode_nosplit(compressed_data)
                    
                    with lock:
                        results.append((chunk_id, decoded))
                    
                    return True
                except Exception as e:
                    print(f"❌ Ошибка распаковки чанка {chunk_id}: {e}")
                    return False
            
            # Запускаем потоки для распаковки
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for i in range(1, len(lines)):  # Пропускаем метаданные
                    future = executor.submit(process_chunk, i-1, lines[i].strip())
                    futures.append(future)
                
                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    if completed % 10 == 0:
                        print(f"📊 Прогресс: {completed}/{total_chunks} чанков")
            
            # Сортируем и собираем данные
            results.sort(key=lambda x: x[0])
            
            with open(output_path, 'wb') as f:
                for chunk_id, data in results:
                    f.write(data)
            
            print(f"✅ Многопоточная распаковка завершена: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка многопоточной распаковки: {e}")
            return False
    
    # === СПЕЦИАЛЬНАЯ ОБРАБОТКА MP4 ===
    @staticmethod
    def encode_mp4(input_path: str, output_path: str) -> bool:
        """Специальная обработка MP4 файлов"""
        try:
            file_size = os.path.getsize(input_path)
            print(f"🎥 Обработка MP4: {file_size/(1024*1024):.1f} MB")
            
            # Для MP4 используем многопоточность с оптимизированными параметрами
            return MFCC.encode_large_file_parallel(
                input_path, 
                output_path, 
                chunk_size=5*1024*1024,  # 5MB чанки для MP4
                max_workers=2  # Меньше потоков для стабильности
            )
        except Exception as e:
            print(f"❌ Ошибка обработки MP4: {e}")
            return False
    
    @staticmethod
    def decode_mp4(input_path: str, output_path: str) -> bool:
        """Распаковка MP4 файлов"""
        try:
            return MFCC.decode_large_file_parallel(input_path, output_path, max_workers=2)
        except Exception as e:
            print(f"❌ Ошибка распаковки MP4: {e}")
            return False
    
    # === АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ РЕЖИМА ===
    @staticmethod
    def encode_file_auto(input_path: str, output_path: str) -> bool:
        """Автоматически выбирает оптимальный метод сжатия"""
        file_size = os.path.getsize(input_path)
        file_ext = os.path.splitext(input_path)[1].lower()
        
        # Большие файлы (>900MB) - многопоточность
        if file_size > 900 * 1024 * 1024:
            print("🚀 Используем многопоточный режим для большого файла")
            return MFCC.encode_large_file_parallel(input_path, output_path)
        
        # MP4 файлы - специальная обработка
        elif file_ext == '.mp4':
            print("🎥 Используем MP4 режим")
            return MFCC.encode_mp4(input_path, output_path)
        
        # Обычные файлы - стандартный метод
        else:
            print("📄 Используем стандартный режим")
            return MFCC.encode_file_nosplit(input_path, output_path)
    
    @staticmethod
    def decode_file_auto(input_path: str, output_path: str) -> bool:
        """Автоматически определяет метод распаковки"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
            
            # Проверяем формат многопоточного файла
            if first_line.startswith('{"format": "MFCC_PARALLEL"'):
                return MFCC.decode_large_file_parallel(input_path, output_path)
            else:
                return MFCC.decode_file_nosplit(input_path, output_path)
                
        except Exception as e:
            print(f"❌ Ошибка автоопределения: {e}, используем стандартный метод")
            return MFCC.decode_file_nosplit(input_path, output_path)
    
    # === СТАНДАРТНЫЕ МЕТОДЫ ===
    @staticmethod
    def encode_file_nosplit(input_path: str, output_path: str) -> bool:
        """Стандартное сжатие для маленьких файлов"""
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            compressed = MFCC.encode_nosplit(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(compressed)
            
            print(f"✅ Сжатие завершено: {input_path} → {output_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сжатия: {e}")
            return False
    
    @staticmethod
    def decode_file_nosplit(input_path: str, output_path: str) -> bool:
        """Стандартная распаковка"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                compressed_data = f.read()
            
            decoded_data = MFCC.decode_nosplit(compressed_data)
            
            with open(output_path, 'wb') as f:
                f.write(decoded_data)
            
            print(f"✅ Распаковка завершена: {input_path} → {output_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка распаковки: {e}")
            return False
