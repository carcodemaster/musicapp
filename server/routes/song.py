import uuid
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, Form, UploadFile
from middleware.auth_middleware import auth_middleware
from sqlalchemy.orm import Session
from database import get_db
from models.song import Song
from pydantic_schemas.favorite_song import FavoriteSong
from server.models.favorite import Favorite
from sqlalchemy.orm import joinedload

router = APIRouter()

# Configuration       
cloudinary.config( 
    cloud_name = "die2sgof3", 
    api_key = "864584442167257", 
    api_secret = "PFb_MWJTz7ftJbXYhFHkm6pbtVI",
    secure=True
)


@router.post('/upload', status_code=201)
def upload_song(
    song: UploadFile = File(...),
    thumbnail: UploadFile = File(...),
    artist: str = Form(...),
    song_name: str = Form(...),
    hex_code: str = Form(...),
    db: Session = Depends(get_db),
    auth_dict = Depends(auth_middleware)
    ):
    song_id = str(uuid.uuid4())
    song_res = cloudinary.uploader.upload(
        song.file,
        resource_type = 'auto',
        folder = f'songs/{song_id}')
    print(song_res['url'])
    thumbnail_res = cloudinary.uploader.upload(
        thumbnail.file,
        resource_type = 'image',
        folder = f'songs/{song_id}')
    print(thumbnail_res['url'])

    new_song = Song(
        id = song_id,
        song_name = song_name,
        artist = artist,
        hex_code = hex_code,
        song_url = song_res['url'],
        thumbnail_url = thumbnail_res['url']
    )

    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song

@router.get('/list')
def list_songs(db: Session = Depends(get_db),
            auth_details=Depends(auth_middleware)):
    songs = db.query(Song).all()
    return songs

@router.post('/favorite')
def favorite_song(fav_song: FavoriteSong, db: Session = Depends(get_db),
                   auth_details=Depends(auth_middleware)):
    user_id = auth_details['uid']

    fav_song = db.query(Favorite).filter(Favorite.song_id == fav_song.song_id, Favorite.user_id == user_id).first()

    if fav_song:
        db.delete(fav_song)
        db.commit()
        return {"message": False}
    else:
        new_fav = Favorite(
            id = str(uuid.uuid4()),
            song_id = fav_song.song_id,
            user_id = user_id
        )
        db.add(new_fav)
        db.commit()
        return {"message": True}
    
@router.get('/list/favorites')
def list_fav_songs(db: Session = Depends(get_db),
            auth_details=Depends(auth_middleware)):
    user_id = auth_details['uid']
    fav_songs = db.query(Favorite).filter(Favorite.user_id == user_id).options(
        joinedload(Favorite.song)
    ).all()
    return fav_songs