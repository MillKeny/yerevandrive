from pathlib import Path
import struct
import subprocess
import os

convert_supported = [ ".tga", ".bmp", ".gif", ".ppm", ".jpg", ".tif", ".cel", ".dds", ".png", ".psd", ".rgb", ".bw", ".rgba" ]

def check_dds_mipmaps(dds_file, is_data=True):
    if not is_data:
        with open(dds_file, 'rb') as f:
            dds_data = f.read()
            
    dds_data = dds_file
    
    if len(dds_data) < 128:
        return 0
  
    mipmap_count = struct.unpack('<I', dds_data[28:32])[0]
  
    flags = struct.unpack('<I', dds_data[8:12])[0]
    has_mipmaps = flags & 0x20000 
  
    if has_mipmaps:
        return True
    return False

def check_dxt(dds_file, is_data=True):
    if not is_data:
        with open(dds_file, 'rb') as f:
            dds_data = f.read()
            
    dds_data = dds_file
    if b'DXT1' in dds_data:
        return 'DXT1'
    elif b'DXT3' in dds_data:
        return 'DXT3'
    else:
        return False

def convert_yd(file, outdir, mipmaps=False, dxt='DXT3'):
    filepath = Path(file)
    
    if filepath.exists():
        if filepath.suffix in convert_supported:
            os.makedirs(outdir, exist_ok=True)
            command = f'data/nvdxt.exe -file {file} -output {outdir}/{filepath.stem}.dds -quick -timestamp -overwrite'
            if not mipmaps: command += ' -nomipmap'
            
            if dxt == 'DXT1':
                command += ' -dxt1 -32 dxt1'
            elif dxt == 'DXT3':
                command += ' -dxt3 -32 dxt3'
            else:
                return 'Invalid DDS file :('
            
            subprocess.run(command)
            if not os.path.exists(f'{outdir}/{filepath.stem}.dds'):
                return 'Failed to convert :('
        else:
            return filepath.suffix + " is not supported :("
    else:
        return str(filepath) + " - no such a file :("
    
    return 0

if __name__ == "__main__":
    convert_yd("bg.png")