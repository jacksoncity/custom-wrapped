import os
import xml.etree.ElementTree as ET
from mutagen.flac import FLAC
from flask import Flask, render_template, url_for, request, jsonify
import xml.etree.ElementTree as ET
import tempfile


app = Flask(__name__)
@app.route("/", methods=["POST", "GET"])

def index():
    if request.method=="POST":

        if 'wrappedUpload' not in request.files:
            return jsonify({'success': False, 'error': 'No file part in the request'}), 400
        
        uploaded_file = request.files['wrappedUpload']

        if uploaded_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
            
        if not uploaded_file.filename.endswith('.xml'):
            return jsonify({'success': False, 'error': 'Please upload an XML file'}), 400

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
                uploaded_file.save(tmp_file.name)
                xml_file_path = tmp_file.name
            
            flac_entries = parse_only_flac_files(xml_file_path)
            os.unlink(xml_file_path)
            
            # Process all the statistics
            results = process_statistics(flac_entries)

            return jsonify({
                'success': True,
                'filename': uploaded_file.filename,
                'results': results
            })

        
        except ET.ParseError:
            return jsonify({'success': False, 'error': 'Invalid XML file format'}), 400
        
        except Exception as e:
            return jsonify({'success': False, 'error': f'Processing error: {str(e)}'}), 500
    else:
        return render_template("index.html")


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
        return {"error": f"Could not read metadata: {str(e)}"}

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
    album_list = [        
        {
            'artist': artist,
            'album': album,
            'plays': plays,
        } 
        for (artist, album), plays in album_plays.items()
    ]
    return sorted(album_list, key=lambda x: x['plays'], reverse=True)[:n]

#RETURN TOTAL TIME LISTENED
def total_time_played(flac_entries):
    valid_entries = validate_flac(flac_entries)
    time = 0
    for entry in valid_entries:
        time = time + entry['metadata']['length'] * entry['play_count']
    return time // 60   #return in minutes


def process_statistics(flac_entries):
    # Format top songs
    top_songs = most_played(flac_entries, 15)
    formatted_songs = []
    for i, song in enumerate(top_songs, 1):
        metadata = song['metadata']
        formatted_songs.append({
            'rank': i,
            'artist': metadata['artist'],
            'title': metadata['title'],
            'album': metadata['album'],
            'plays': song['play_count'],
            'first_played': song.get('first_played', 'N/A'),
            'last_played': song.get('last_played', 'N/A')
        })
    
    # Format top artists
    top_artists = most_played_artist(flac_entries, 10)
    formatted_artists = []
    for i, (artist, plays) in enumerate(top_artists, 1):
        formatted_artists.append({
            'rank': i,
            'artist': artist,
            'plays': plays
        })
    
    # Format top albums
    top_albums = most_played_albums(flac_entries, 10)
    formatted_albums = []
    for i, album_data in enumerate(top_albums, 1):
        formatted_albums.append({
            'rank': i,
            'artist': album_data['artist'],
            'album': album_data['album'],
            'plays': album_data['plays'],
        })
    

    # Calculate statistics
    total_time_minutes = total_time_played(flac_entries)

    total_plays = sum(entry['play_count'] for entry in flac_entries)
    total_files = len(flac_entries)
    
    # Count successful reads
    valid_entries = validate_flac(flac_entries)
    successful_reads = len(valid_entries)
    files_with_errors = total_files - successful_reads
    
    return {
        'top_songs': formatted_songs,
        'top_artists': formatted_artists,
        'top_albums': formatted_albums,
        'total_time_minutes': total_time_minutes,
        'total_plays': total_plays,
        'total_files': total_files,
        'successful_reads': successful_reads,
        'files_with_errors': files_with_errors
    }


# Test the function
if __name__ == "__main__":
    app.run(debug=True)
