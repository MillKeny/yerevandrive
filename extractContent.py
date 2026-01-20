import os
import shutil
import subprocess
from PIL import Image

targets = [b'.tga', b'.TGA', b'.bmp', b'.BMP', b'.dds', b'.DDS', b'.wav', b'.WAV', b'.jpg', b'.JPG']

def convert_detect(input, output):
    try:
        with Image.open(input) as img:
            img.save(output, 'PNG')
            return True
    except:
        return False

def convert_wav(input, output):
    subprocess.run(f'ffmpeg -i {input} -loglevel quiet {output}')

def getfiles(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    result = []
    lastfound = 0
    for i in range(len(data)):
        if data[i:i+4] in targets:
            start = i
            while start > 0 and data[start-1] != 0:
                start -= 1
                if i - start > 100:
                    break
                    
            try:
                name = data[start:i+4].decode('ascii').strip('\x00')
                if bytes(name, 'ascii') in targets: continue
                if bytes(name[-4:], 'ascii') in targets:
                    if i - lastfound > 100:
                        continue
                    lastfound = i
                    result.append([name])
            except:
                pass

    startpos = 0
    for i, v in enumerate(result):
        startpos = data.find(bytes(v[0], 'ascii'), startpos, len(data))
        if startpos != -1: startpos += len(v[0])
        if i < len(result)-1:
            endpos = data.find(bytes(result[i+1][0], 'ascii'), startpos, len(data))
        elif len(result) == 1:
            endpos = data.find(b'DDS', startpos, startpos+20)
            if endpos == -1:
                endpos = data.find(b'RIFF', startpos, startpos+20)
        else:
            endpos = result[0][1]
        thisdata = data[startpos:endpos]

        v.append(int.from_bytes(thisdata[-8:-4], byteorder='little', signed = True))
        v.append(int.from_bytes(thisdata[-4:], byteorder='little', signed = True))
        v.append(endpos)
        v.append(endpos-startpos)
        
    return result

def extract_yd(filepath, output_folder="extracted", just_read=False, selected="", preview=False, convert='Original'):
    if preview:
        if os.path.exists('.temp'): shutil.rmtree('.temp')
        os.makedirs('.temp', exist_ok=True)
        os.makedirs('.temp/original', exist_ok=True)
        os.makedirs('.temp/previews', exist_ok=True)
        os.makedirs('.temp/converted', exist_ok=True)
    else:
        if not just_read:
            os.makedirs(output_folder, exist_ok=True)
    
    with open(filepath, 'rb') as f:
        data = f.read()
        
    
    result = getfiles(filepath)
    
    if not just_read:
        for i in result:
            filename = i[0]
            if selected == "" or filename == selected:
                if preview:
                    filepath_orig = os.path.join('.temp/original', filename)
                    with open(filepath_orig, 'wb') as f:
                        f.write(data[i[1]:i[1]+i[2]])
                    convert_detect(filepath_orig.lower(), '.temp/previews/' + filename + '.png')
                else:
                    if convert == 'PNG':
                        filepath_orig = os.path.join('.temp/original', filename)
                        with open(filepath_orig, 'wb') as f:
                            f.write(data[i[1]:i[1]+i[2]])
                        filepath_conv = os.path.join(output_folder, filename[:-4] + '.png')
                        convert_detect(filepath_orig.lower(), filepath_conv)
                    else:
                        filepath_orig = os.path.join(output_folder, filename)
                        with open(filepath_orig, 'wb') as f:
                            f.write(data[i[1]:i[1]+i[2]])

    return result

if __name__ == "__main__":
    # print(*extract_yd(filepath='work/tex/menu.tex', just_read=False, preview=True), sep='\n')
    print(*getfiles('avto.snd'), sep='\n')