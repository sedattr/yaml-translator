import re
import argparse
import time
from deep_translator import GoogleTranslator
from ruamel.yaml import YAML
from concurrent.futures import ThreadPoolExecutor

yaml = YAML()
yaml.preserve_quotes = True

variable_placeholders = {}

def load_protected_keys(filename="protected_keys.yml"):
    with open(filename, 'r', encoding='utf-8') as file:
        data = yaml.load(file)
        return data.get("protected_keys", [])

protected_keys = load_protected_keys("protected_keys.yml")

def mask_variables(text):
    if not isinstance(text, str):  
        return text
    text = re.sub(r"(\{[^\}]+\})", lambda m: store_variable(m.group()), text)
    text = re.sub(r"(%[^\%]+%)", lambda m: store_variable(m.group()), text)
    text = re.sub(r"(<[^\%]+>)", lambda m: store_variable(m.group()), text)
    return text

def unmask_variables(text):
    if not isinstance(text, str):
        return text
    for placeholder, original in variable_placeholders.items():
        text = text.replace(placeholder, original)
    return text

def store_variable(variable):
    placeholder = f"[[VAR{len(variable_placeholders)}]]"
    variable_placeholders[placeholder] = variable
    return placeholder

def translate_text(key, text, target, source):
    try:
        if key in protected_keys:
            print(f"⏭️ Skipped: {key} = {text}")
            return text

        original_text = text
        text = mask_variables(text)

        print(f"🔄 Translating: {original_text} -> {text} ({source} -> {target})")  
        translated_text = GoogleTranslator(source=source, target=target).translate(text)

        translated_text = unmask_variables(translated_text)
        print(f"✅ Translated: {translated_text}")  
        
        return translated_text
    except Exception as e:
        print(f"❌ Translation Error: {text} -> {e}")
        return text  

def translate_yaml_content(obj, source_lang, target_lang, workers, parent_key=None):
    if isinstance(obj, dict):
        return {key: translate_yaml_content(value, source_lang, target_lang, workers, key) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [translate_yaml_content(item, source_lang, target_lang, workers, parent_key) for item in obj]
    elif isinstance(obj, str):
        return translate_text(parent_key, obj, target_lang, source_lang)

    return obj

def translate_yaml(input_file, output_file, source_lang, target_lang, workers):
    with open(input_file, 'r', encoding='utf-8') as stream:
        try:
            yaml_content = yaml.load(stream)
            print("📂 YAML file is successfully loaded!")
        except Exception as exc:
            print(f"❌ YAML load error: {exc}")
            return
    
    print(f"🔄 YAML is translating with {workers} workers...")
    
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_key = {}
        translated_content = {}

        for key, value in yaml_content.items():
            future_to_key[executor.submit(translate_yaml_content, value, source_lang, target_lang, workers, key)] = key

        for future in future_to_key:
            key = future_to_key[future]
            translated_content[key] = future.result()

    end_time = time.time()

    print(f"✅ Translation is completed! Took: {round(end_time - start_time, 2)} seconds")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        yaml.dump(translated_content, outfile)
        print(f"📁 Translated file is saved: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translate YAML file values')
    parser.add_argument('-i', '--input', required=True, help='Input YAML file path')
    parser.add_argument('-o', '--output', required=True, help='Output YAML file path')
    parser.add_argument('-s', '--source', required=True, help='Source language (example: en)')
    parser.add_argument('-t', '--target', required=True, help='Target language (example: tr)')
    parser.add_argument('-w', '--workers', type=int, default=1, help='Worker thread amount (Default: 1)')
    args = parser.parse_args()

    translate_yaml(args.input, args.output, args.source, args.target, args.workers)