import os
import binascii
from typing import Union

class MFCC:
    """
    MyFirstCoolCodec (MFCC) Ultimate Version с разделителями
    Формат: [count]|[hex_char]| например "04|F|" = F F F F
    """
    
    @staticmethod
    def encode(data: Union[bytes, str]) -> str:
        """Сжимает данные используя RLE с разделителями"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Конвертируем в HEX строку
        hex_str = data.hex().upper()
        if not hex_str:
            return ""
        
        encoded = []
        count = 1
        current_char = hex_str[0]
        
        # Проходим по всем символам HEX строки
        for i in range(1, len(hex_str)):
            if hex_str[i] == current_char and count < 255:  # Максимум 255 повторов
                count += 1
            else:
                # Если повторов больше 3 - используем RLE сжатие
                if count > 3:
                    encoded.append(f"{count:02X}|{current_char}|")
                else:
                    # Иначе записываем как есть
                    for _ in range(count):
                        encoded.append(current_char)
                count = 1
                current_char = hex_str[i]
        
        # Обрабатываем последнюю последовательность
        if count > 3:
            encoded.append(f"{count:02X}|{current_char}|")
        else:
            for _ in range(count):
                encoded.append(current_char)
            
        result = "".join(encoded)
        print(f"Кодирование: {len(data)} байт -> {len(result)} символов")
        return result
    
    @staticmethod
    def decode(compressed_data: str) -> bytes:
        """Восстанавливает оригинальные данные из MFCC-формата с разделителями"""
        if not compressed_data:
            return b""
        
        decoded_hex = []
        i = 0
        length = len(compressed_data)
        
        print(f"Декодирование: {length} символов")
        
        while i < length:
            # Если осталось достаточно символов для RLE блока (XX|Y|)
            if (i + 4 <= length and 
                compressed_data[i+2] == '|' and 
                compressed_data[i+4] == '|'):
                
                # Проверяем, что первые два символа - HEX цифры
                if (compressed_data[i] in '0123456789ABCDEF' and 
                    compressed_data[i+1] in '0123456789ABCDEF' and
                    compressed_data[i+3] in '0123456789ABCDEF'):
                    
                    try:
                        # Извлекаем счетчик и символ
                        count_hex = compressed_data[i:i+2]
                        count = int(count_hex, 16)
                        symbol = compressed_data[i+3]
                        
                        # Добавляем символ count раз
                        decoded_hex.append(symbol * count)
                        i += 5  # Пропускаем весь блок XX|Y|
                        continue
                    except (ValueError, IndexError):
                        pass
            
            # Если это обычный HEX символ
            current_char = compressed_data[i]
            if current_char in '0123456789ABCDEF':
                decoded_hex.append(current_char)
            
            i += 1
        
        # Собираем HEX строку
        hex_str = "".join(decoded_hex)
        print(f"Восстановлено HEX символов: {len(hex_str)}")
        
        # Проверяем четность длины HEX строки
        if len(hex_str) % 2 != 0:
            print("⚠️  Предупреждение: HEX строка нечетной длины. Добавляем '0' в конец.")
            hex_str += '0'
        
        try:
            result = bytes.fromhex(hex_str)
            print(f"Декодировано байт: {len(result)}")
            return result
        except Exception as e:
            print(f"❌ Ошибка преобразования HEX в байты: {e}")
            print(f"Проблемный участок HEX: {hex_str[max(0, len(hex_str)-100):]}")
            raise
    
    @staticmethod
    def encode_file(input_path: str, output_path: str) -> bool:
        """Сжимает файл и сохраняет в формате MFCC"""
        try:
            if not os.path.exists(input_path):
                print(f"❌ Файл не найден: {input_path}")
                return False
            
            # Читаем исходный файл
            with open(input_path, 'rb') as f:
                original_data = f.read()
            
            print(f"📁 Прочитано файлов: {len(original_data)} байт")
            
            # Сжимаем данные
            compressed_data = MFCC.encode(original_data)
            
            # Сохраняем сжатые данные
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(compressed_data)
            
            # Сравниваем размеры
            original_size = len(original_data)
            compressed_size = len(compressed_data)
            ratio = (1 - compressed_size / (original_size * 2)) * 100
            
            print(f"✅ Файл сжат: {input_path} -> {output_path}")
            print(f"📊 Эффективность: {ratio:.1f}%")
            print(f"📦 Оригинал: {original_size} байт")
            print(f"🔰 Сжатый: {compressed_size} символов")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сжатии файла: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def decode_file(input_path: str, output_path: str) -> bool:
        """Восстанавливает файл из MFCC-формата"""
        try:
            if not os.path.exists(input_path):
                print(f"❌ Файл не найден: {input_path}")
                return False
            
            # Читаем сжатый файл
            with open(input_path, 'r', encoding='utf-8') as f:
                compressed_data = f.read().strip()
            
            print(f"📁 Прочитано MFCC: {len(compressed_data)} символов")
            
            # Анализируем структуру
            pipe_count = compressed_data.count('|')
            rle_blocks = pipe_count // 2
            print(f"🔍 RLE блоков: {rle_blocks}")
            
            # Восстанавливаем данные
            decoded_data = MFCC.decode(compressed_data)
            
            # Сохраняем восстановленные данные
            with open(output_path, 'wb') as f:
                f.write(decoded_data)
            
            print(f"✅ Файл восстановлен: {input_path} -> {output_path}")
            print(f"📦 Восстановлено: {len(decoded_data)} байт")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при распаковке файла: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def analyze_file(file_path: str):
        """Анализирует структуру MFCC файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔍 Анализ MFCC файла: {file_path}")
            print(f"📊 Общий размер: {len(content)} символов")
            print(f"📍 Разделителей '|': {content.count('|')}")
            print(f"🔢 RLE блоков: {content.count('|') // 2}")
            
            # Статистика символов
            hex_count = sum(1 for c in content if c in '0123456789ABCDEF')
            other_count = len(content) - hex_count - content.count('|')
            
            print(f"🔡 HEX символов: {hex_count}")
            print(f"📝 Прочих символов: {other_count}")
            
            # Находим RLE блоки
            import re
            rle_pattern = r'([0-9A-F]{2})\|([0-9A-F])\|'
            rle_matches = re.findall(rle_pattern, content)
            
            if rle_matches:
                print(f"🎯 Найдено RLE блоков: {len(rle_matches)}")
                print("📋 Примеры RLE блоков:")
                for i, (count, char) in enumerate(rle_matches[:5]):
                    print(f"   {count}|{char}| = {char} * {int(count, 16)}")
            
            # Превью содержимого
            print(f"\n👀 Первые 300 символов:")
            print(content[:300])
            print(f"\n👁️ Последние 200 символов:")
            print(content[-200:] if len(content) > 200 else content)
            
        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")

def test_mfcc():
    """Тестирует работу кодекса"""
    print("=== 🧪 Тест MFCC с разделителями ===\n")
    
    # Тест 1: Простые данные с повторениями
    print("1. 🔢 Тест с повторениями:")
    test_data = bytes.fromhex("FFFFFFFFAAAAABBBBBBBBBCCDDDD")
    compressed = MFCC.encode(test_data)
    decompressed = MFCC.decode(compressed)
    
    print(f"   Оригинал: {test_data.hex().upper()}")
    print(f"   Сжатый:   {compressed}")
    print(f"   Восстановлен: {decompressed.hex().upper()}")
    print(f"   ✅ Совпадает: {test_data == decompressed}\n")
    
    # Тест 2: Текст
    print("2. 📝 Тест с текстом:")
    text = "Hello MFCC! This is amazing compression!!!"
    text_compressed = MFCC.encode(text)
    text_decompressed = MFCC.decode(text_compressed).decode('utf-8')
    
    print(f"   Оригинал: {text}")
    print(f"   Сжатый: {text_compressed}")
    print(f"   Восстановлен: {text_decompressed}")
    print(f"   ✅ Совпадает: {text == text_decompressed}\n")
    
    # Тест 3: Создание тестового файла
    print("3. 📁 Тест с файлами:")
    try:
        # Создаем тестовый файл
        test_content = "TEST " * 50 + "A" * 100 + "B" * 50
        with open('test_file.txt', 'w') as f:
            f.write(test_content)
        
        # Сжимаем
        MFCC.encode_file('test_file.txt', 'test_file.mfcc')
        
        # Распаковываем
        MFCC.decode_file('test_file.mfcc', 'test_file_decompressed.txt')
        
        # Проверяем
        with open('test_file.txt', 'r') as f:
            orig = f.read()
        with open('test_file_decompressed.txt', 'r') as f:
            decomp = f.read()
        
        print(f"   ✅ Файлы идентичны: {orig == decomp}")
        
        # Анализируем
        MFCC.analyze_file('test_file.mfcc')
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_mfcc()
