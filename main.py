import sys
import xml.etree.ElementTree as ET
from mutagen.flac import FLAC
from datetime import timedelta
import os

def get_flac_metadata(file_path):
    """Extract metadata from FLAC file"""
    try:
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        audio = FLAC(file_path)
        
        metadata = {
            'artist': audio.get('artist', ['Unknown Artist'])[0],
            'album': audio.get('album', ['Unknown Album'])[0],
            'title': audio.get('title', [os.path.splitext(os.path.basename(file_path))[0]])[0],
            'date': audio.get('date', ['Unknown'])[0],
            'genre': audio.get('genre', ['Unknown'])[0],
            'tracknumber': audio.get('tracknumber', [''])[0],
            'length': audio.info.length,
        }
        return metadata
        
    except Exception as e:
        return {"error": str(e)}

def parse_only_flac_files(xml_file_path):
    """Parse XML and extract FLAC metadata ONLY for the .flac files"""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    flac_entries = []
    skipped_files = 0
    
    for entry in root.findall('Entry'):
        file_path = entry.find('Item').get('Path')
        
        # ONLY process FLAC files - skip everything else
        if file_path.lower().endswith('.flac'):
            entry_data = {
                'id': entry.get('ID'),
                'play_count': int(entry.get('Count', 0)),
                'first_played': entry.get('FirstPlayedFriendly'),
                'last_played': entry.get('LastPlayedFriendly'),
                'file_path': file_path,
                'metadata': get_flac_metadata(file_path)
            }
            flac_entries.append(entry_data)
        else:
            skipped_files += 1
    print(f"Processed {len(flac_entries)} FLAC files")
    print(f"Skipped {skipped_files} non-FLAC files")
    
    return flac_entries

#all checking and validating
def validate_flac(flac_entries):
    if not flac_entries:
        return []
    valid_entries = [entry for entry in flac_entries if 'error' not in entry.get('metadata', {})] #cull out the error'd metadata files
    if not valid_entries:
        return []
    return valid_entries

#RETURN TOP n SONGS
def most_played(flac_entries, n):
    #sort and return top n songs by playcount in the sorted entries
    sorted_entries = sorted(validate_flac(flac_entries), key=lambda x: x['play_count'], reverse=True)
    return sorted_entries[:n]


#RETURN TOP n ARTISTS
def most_played_artist(flac_entries, n):
    #agregate the list of artists and total plays
    artist_plays = {}
    valid_entries = validate_flac(flac_entries)
    for entry in valid_entries:
        artist = entry['metadata']['artist'] #gets artists name by 2 dict calls
        artist_plays[artist] = artist_plays.get(artist, 0) + entry['play_count'] #adds current plays (or 0 in first time) to the current entries playcount.
    #creates a tupled list to return so we can have both artist and playcount returned
    artist_list = [(artist, plays) for artist, plays in artist_plays.items()]
    return sorted(artist_list, key=lambda x: x[1], reverse=True)[:n]
    

#RETURN TOP n ALBUMS
def most_played_albums(flac_entries, n):
    album_plays = {}
    valid_entries = validate_flac(flac_entries)
    for entry in valid_entries:
        album = entry['metadata']['album'] #gets album name by 2 dict calls
        artist = entry['metadata']['artist']
        album_plays[artist, album] = album_plays.get((artist, album), 0) + entry['play_count'] #adds current plays (or 0 in first time) to the current entries playcount.
    #creates a tupled list to return so we can have both album and playcount returned
    album_list = [(artist, album, plays) for (artist, album), plays in album_plays.items()]
    return sorted(album_list, key=lambda x: x[2], reverse=True)[:n]

#RETURN TOTAL TIME LISTENED
def total_time_played(flac_entries):
    valid_entries = validate_flac(flac_entries)
    time = 0
    for entry in valid_entries:
        time = time + entry['metadata']['length']
    return time


# Test the function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        year = sys.argv[1]
        print(f"\n=== Processing Information ===")
        print(f"Processing year: {year}")
    else:
        print("Usage: python main.py <year>")
        print("Example: python main.py 2025")
        sys.exit(1)
    
    xml_file = "wrapped"+year+".xml" 
    if not os.path.exists(xml_file):
        print(f"Error: File {xml_file} not found! Please input a valid year.")
        sys.exit(1)
    
    flac_entries = parse_only_flac_files(xml_file)

    #TOP n SONGS
    top_n_songs = most_played(flac_entries, 5)
    if top_n_songs:
        print("\nHere are your Top 5 Songs " +year+":")
        for i, song in enumerate(top_n_songs, 1):
            metadata = song['metadata']
            print(f"{i}. {metadata['artist']} - {metadata['title']} ({song['play_count']} plays)")

    #TOP n ARTISTS
    top_n_artists = most_played_artist(flac_entries, 5)
    if top_n_artists:
        print("\nHere are your Top 5 Artists in " +year+":")
        for i, (artist, plays) in enumerate(top_n_artists, 1):
            print(f"{i}. {artist} ({plays} plays)")

    #TOP n ALBUMS
    top_n_albums = most_played_albums(flac_entries, 5)
    if top_n_albums:
        print("\nHere are your Top 5 Albums in " +year+":")
        for i, (artist, album, plays) in enumerate(top_n_albums, 1):
            print(f"{i}. {album} by {artist} ({plays} plays)")

    #TOTAL TIME LISTENED
    total_time = total_time_played(flac_entries)
    if total_time:
        print(f"\nYou have spent {timedelta(seconds=int(total_time))} in total listening on foobar2000.")
     
    # Show summary statistics
    if flac_entries:
        total_plays = sum(entry['play_count'] for entry in flac_entries)
        successful_reads = sum(1 for entry in flac_entries if 'error' not in entry['metadata'])
        
        print(f"\n=== Summary ===")
        print(f"Total FLAC files: {len(flac_entries)}")
        print(f"Successfully read metadata: {successful_reads}")
        print(f"Files with errors: {len(flac_entries) - successful_reads}")
        print(f"Total plays across all FLAC files: {total_plays}")