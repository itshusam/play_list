from flask import Flask, request, jsonify

class Song:
    def __init__(self, title, artist, genre):
        self.title = title
        self.artist = artist
        self.genre = genre

    def __repr__(self):
        return f"{self.title} by {self.artist} [{self.genre}]"


class Playlist:
    def __init__(self, name):
        self.name = name
        self.songs = []

    def add_song(self, song):
        self.songs.append(song)

    def remove_song(self, song):
        self.songs.remove(song)

    def get_songs(self):
        return self.songs

    def sort_songs(self, attribute):
        if attribute == 'title':
            self.songs.sort(key=lambda song: song.title)
        elif attribute == 'artist':
            self.songs.sort(key=lambda song: song.artist)
        elif attribute == 'genre':
            self.songs.sort(key=lambda song: song.genre)

    def search_song(self, title):
        return [song for song in self.songs if song.title.lower() == title.lower()]


app = Flask(__name__)

playlists = {}

@app.route('/playlist', methods=['POST'])
def create_playlist():
    name = request.json.get('name')
    if name in playlists:
        return jsonify({"message": "Playlist already exists"}), 400
    playlists[name] = Playlist(name)
    return jsonify({"message": "Playlist created", "name": name}), 201

@app.route('/playlist/<string:name>', methods=['GET'])
def get_playlist(name):
    if name in playlists:
        return jsonify({"name": name, "songs": [str(song) for song in playlists[name].get_songs()]}), 200
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/playlist/<string:name>', methods=['DELETE'])
def delete_playlist(name):
    if name in playlists:
        del playlists[name]
        return jsonify({"message": "Playlist deleted"}), 200
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/playlist/<string:name>/add_song', methods=['POST'])
def add_song_to_playlist(name):
    if name in playlists:
        song_data = request.json
        if not all(k in song_data for k in ("title", "artist", "genre")):
            return jsonify({"message": "Missing song data"}), 400
        song = Song(song_data['title'], song_data['artist'], song_data['genre'])
        playlists[name].add_song(song)
        return jsonify({"message": "Song added", "song": str(song)}), 200
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/playlist/<string:name>/remove_song', methods=['DELETE'])
def remove_song_from_playlist(name):
    if name in playlists:
        song_title = request.json.get('title')
        song = playlists[name].search_song(song_title)
        if song:
            playlists[name].remove_song(song[0])
            return jsonify({"message": "Song removed", "song": str(song[0])}), 200
        return jsonify({"message": "Song not found in playlist"}), 404
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/playlist/<string:name>/sort', methods=['POST'])
def sort_songs_in_playlist(name):
    if name in playlists:
        attribute = request.json.get('attribute')
        if attribute not in ['title', 'artist', 'genre']:
            return jsonify({"message": "Invalid attribute for sorting"}), 400
        playlists[name].sort_songs(attribute)
        return jsonify({"message": "Songs sorted", "sorted_songs": [str(song) for song in playlists[name].get_songs()]}), 200
    return jsonify({"message": "Playlist not found"}), 404

@app.route('/playlist/<string:name>/search', methods=['GET'])
def search_song_in_playlist(name):
    if name in playlists:
        song_title = request.args.get('title')
        songs = playlists[name].search_song(song_title)
        if songs:
            return jsonify({"message": "Song found", "songs": [str(song) for song in songs]}), 200
        return jsonify({"message": "Song not found in playlist"}), 404
    return jsonify({"message": "Playlist not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
