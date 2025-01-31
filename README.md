# YAML TRANSLATOR

## USAGE & EXAMPLE
- Usage: python translate_yaml.py -i INPUTFILENAME.YML -o OUTPUTFILENAME.YML -s SOURCELANGUAGE -t TARGETLANGUAGE -w WORKERTHREADS
- Example: python translate_yaml.py -i input.yml -o output.yml -s en -t tr -w 10
- Put the input file to the directory and use the command in terminal.

## PROTECTED KEYS
- If you don't want to translate some keys' values, add the key name to the protected keys list in the protected_keys.yml

## COMMAND INFORMATION
- INPUTFILENAME.YML example: input.yml
- OUTPUTFILENAME.YML example: output.yml
- SOURCELANGUAGE example: en for english, ko for korean
- TARGETLANGUAGE example: en for english, ko for korean
- WORKERTHREADS example: 5 (5 message will be translated every second)

## RATE LIMIT
You are allowed to make 5 requests per secondand up to 200k requests per day.