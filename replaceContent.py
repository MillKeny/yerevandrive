from extractContent import *
from convertDDS import *
from ydUtils import *

def replace_yd(replacefile, gamefile, userfile, outdir):
    if not os.path.exists(replacefile + '.bak'):
        shutil.copy2(replacefile, replacefile + '.bak')
    
    files = getfiles(replacefile)
    # print(*files, sep='\n')
    
    for n, i in enumerate(files):
        if i[0] == gamefile:
            start = i[1]
            size = i[2]
            posinfo = i[3]
            posinlist = n
    
    if check_suffix_list(replacefile, ['.tex', '.atx']):
        with open(replacefile, 'rb') as d:
            data = d.read()
        if Path(userfile).suffix in convert_supported:
            gamefiletype = Path(gamefile).suffix.lower()
            if Path(userfile).suffix.lower() != gamefiletype:
                
                def match_convert(suffix, format):
                    with Image.open(userfile) as img:
                        img.save(outdir + '/' + Path(userfile).stem + suffix, format)
                        with open(outdir + '/' + Path(userfile).stem + suffix, 'rb') as d:
                            return d.read()
                
                if gamefiletype == '.dds':
                    hasmipmaps = check_dds_mipmaps(dds_file=data[start:start+size], is_data=True)
                    checkdxt = check_dxt(dds_file=data[start:start+size], is_data=True)
                    errorcode = convert_yd(userfile, outdir, hasmipmaps, checkdxt)
                    if errorcode != 0:
                        return [0, errorcode]
                
                    with open(outdir + '/' + Path(userfile).stem + '.dds', 'rb') as d:
                        newdata = d.read()
                elif gamefiletype == '.bmp':
                    newdata = match_convert('.bmp', 'BMP')
                elif gamefiletype == '.tga':
                    newdata = match_convert('.tga', 'TGA')
                elif gamefiletype == '.jpg':
                    newdata = match_convert('.jpg', 'JPEG')
            else:
                with open(userfile, 'rb') as d:
                    newdata = d.read()
        else:
            return [0, "Format not supported :("]
    elif check_suffix(replacefile, '.snd'):
        with open(replacefile, 'rb') as d:
                data = d.read()
        with open(userfile, 'rb') as d:
                newdata = d.read()
    
    if len(newdata) == size:
        with open(replacefile, 'r+b') as f:
            f.seek(start)
            bytes_written = f.write(newdata)
            return [1, f"Successfully wrote {bytes_written} bytes"]
    else:
        newsize = len(newdata).to_bytes(4, byteorder="little", signed=True)
        sizediff = len(newdata) - size
        
        towrite = data[:8]
        for n, i in enumerate(files):
            towrite += bytes(i[0], 'ascii')
            towrite += b'\x00'*(i[4]-8)
            if n < posinlist:
                towrite += i[1].to_bytes(4, byteorder="little", signed=True)
                towrite += i[2].to_bytes(4, byteorder="little", signed=True)
            elif n == posinlist:
                towrite += i[1].to_bytes(4, byteorder="little", signed=True)
                towrite += newsize
            elif n > posinlist:
                towrite += (i[1]+sizediff).to_bytes(4, byteorder="little", signed=True)
                towrite += i[2].to_bytes(4, byteorder="little", signed=True)
        
        for n, i in enumerate(files):
            if n == posinlist:
                towrite += newdata
            else:
                towrite += data[i[1]:i[1]+i[2]]
        
        with open(replacefile, 'wb') as f:
            bytes_written = f.write(towrite)
            
        return [1, f"Successfully repacked archive!\nNew size: {bytes_written} bytes"]

if __name__ == "__main__":
    replace_yd('menu.snd', 'select1.wav', 'qaq.wav', '.')