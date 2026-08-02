def group_by_album(songs):
    """
    アルバム単位にグループ化
    """
    albums = []

    current_album = None

    for song in songs:
        album_name = song["album_name"] or "アルバム未設定"

        if current_album != album_name:
            current_album = album_name

            albums.append({
                "album_name": album_name,
                "songs": []
            })
        albums[-1]["songs"].append(song)
    return albums
