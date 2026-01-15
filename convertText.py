import configparser

mapping = {
    'Ա': 'І',
    'ա': 'і',
    'Բ': 'ґ',
    'բ': 'µ',
    'Գ': '¶',
    'գ': '·',
    'Դ': 'ё',
    'դ': '№',
    'Ե': 'є',
    'ե': '»',
    'Զ': 'ј',
    'զ': 'Ѕ',
    'Է': 'ѕ',
    'է': 'ї',
    'Ը': 'А',
    'ը': 'Б',
    'Թ': 'В',
    'թ': 'Г',
    'Ժ': 'Д',
    'ժ': 'Е',
    'Ի': 'Ж',
    'ի': 'З',
    'Լ': 'И',
    'լ': 'Й',
    'Խ': 'К',
    'խ': 'Л',
    'Ծ': 'М',
    'ծ': 'Н',
    'Կ': 'О',
    'կ': 'П',
    'Հ': 'Р',
    'հ': 'С',
    'Ձ': 'Т',
    'ձ': 'У',
    'Ղ': 'Ф',
    'ղ': 'Х',
    'Ճ': 'Ц',
    'ճ': 'Ч',
    'Մ': 'Ш',
    'մ': 'Щ',
    'Յ': 'Ъ',
    'յ': 'Ы',
    'Ն': 'Ь',
    'ն': 'Э',
    'Շ': 'Ю',
    'շ': 'Я',
    'Ո': 'а',
    'ո': 'б',
    'Չ': 'в',
    'չ': 'г',
    'Պ': 'д',
    'պ': 'е',
    'Ջ': 'ж',
    'ջ': 'з',
    'Ռ': 'и',
    'ռ': 'й',
    'Ս': 'к',
    'ս': 'л',
    'Վ': 'м',
    'վ': 'н',
    'Տ': 'о',
    'տ': 'п',
    'Ր': 'р',
    'ր': 'с',
    'Ց': 'т',
    'ց': 'у',
    'Ւ': 'ф',
    'ւ': 'х',
    'Փ': 'ц',
    'փ': 'ч',
    'Ք': 'ш',
    'ք': 'щ',
    'Օ': 'ъ',
    'օ': 'ы',
    'Ֆ': 'ь',
    'ֆ': 'э',
    '՚': 'ю',
    '։': 'Ј',
    ')': '¤',
    '(': 'Ґ',
    '»': '¦',
    '«': '§',
    'և': 'Ё',
    '․': '©',
    '՝': 'Є',
    '…': '®',
    '՟': 'Ї',
    '՛': '°',
    '՞': '±'
}

def openText(filepath):
    config = configparser.ConfigParser()
    config.read(filepath)
    
    result = {}
    
    for i in config:
        result[i] = {}
        for j in config[i]:
            result[i][j] = config[i][j]
    
    del result['DEFAULT']
    return result

def convertText(text, reverse=False):
    tempmap = mapping
    if reverse: tempmap = {v: k for k, v in tempmap.items()}
    text = list(text)
    for n, i in enumerate(text):
        if i in tempmap.keys():
            text[n] = tempmap[i]
    text = ''.join(text)
    return text

if __name__ == "__main__":
    print(openText('C:\\Games\\YD\\Menu\\menuam.ini'))
    
    userRev = False
    while True:
        user = input()
        if user == "r":
            userRev = not userRev
            continue
        print(f"\033[34m{convertText(user, userRev)}\033[0m")
