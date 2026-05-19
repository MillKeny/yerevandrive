import os
import shutil

def selectTrack(gamepath, track):
    tracks_dest = os.path.join(gamepath, 'Tracks')
    
    source_file = os.path.join('tracks', track)
    
    if not os.path.exists(source_file):
        return [0, f"Track file not found: {source_file}"]
    
    for i in range(28):
        dest_file = os.path.join(tracks_dest, f'track{i}.trc')
        shutil.copy2(source_file, dest_file)
    
    return [1, f"Successfully replaced all tracks with '{track}'"]


def restoreTracks(gamepath):
    tracks_source = 'tracks'
    tracks_dest = os.path.join(gamepath, 'Tracks')

    if not os.path.exists(tracks_source):
        return [0, f"Source tracks folder not found: {tracks_source}"]
    
    for i in range(28):
        source_file = os.path.join(tracks_source, f'track{i}.trc')
        dest_file = os.path.join(tracks_dest, f'track{i}.trc')
        
        if not os.path.exists(source_file):
            return [0, f"Original track file not found: {source_file}"]
        
        shutil.copy2(source_file, dest_file)
    
    return [1, "Successfully restored all original tracks"]