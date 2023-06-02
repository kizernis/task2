import os

# DB_ADDRESS = 'localhost'
DB_ADDRESS = 'db'
DB_USER_NAME = os.environ.get('DB_USER_NAME')
with open('/run/secrets/db_password') as f:
    DB_PASSWORD = f.read()
DB_DATABASE_NAME = os.environ.get('DB_DATABASE_NAME')
WEB_ADDRESS = 'localhost'
WEB_PORT = 8000
AUDIO_FILES_PATH = 'audio_files'
MP3_BITRATE = '192k'

import re
import uuid
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, inspect, Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import uvicorn

app = FastAPI()

SQLALCHEMY_DATABASE_URL = f'postgresql://{DB_USER_NAME}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_DATABASE_NAME}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    token = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False, unique=True)

class AudioRecord(Base):
    __tablename__ = 'audio_record'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    filename_local = Column(String, nullable=False, unique=True)
    filename_orig = Column(String, nullable=False)

class CreateUserRequest(BaseModel):
    name: str

@app.post('/create-user/')
async def create_user_handler(request: CreateUserRequest):
    db = SessionLocal()
    try:
        user = User(name=request.name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {'id': user.id, 'token': str(user.token)}
    finally:
        db.close()

def save_audio(db: SessionLocal, user_id: int, audio_file: UploadFile):
    filename_local: str = uuid.uuid4().hex
    filename_orig: str = re.sub(r'\.wav$', '.mp3', audio_file.filename)
    try:
        sound = AudioSegment(audio_file.file)
        sound.export(os.path.join(AUDIO_FILES_PATH, filename_local), format='mp3', bitrate=MP3_BITRATE)
    except CouldntDecodeError:
        raise HTTPException(status_code=422, detail='Bad audio file')
    record = AudioRecord(user_id=user_id, filename_local=filename_local, filename_orig=filename_orig)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record.id

# в случае указания нескольких user_id или token, или audio_file используется последнее значение
@app.post('/add-audio/')
async def add_audio_handler(user_id: int=Form(...), token: str=Form(...), audio_file: UploadFile=File(...)):
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.id == user_id, User.token == token).first(): # !
            raise HTTPException(status_code=401, detail='Invalid id or token')
        record_id = save_audio(db, user_id, audio_file)
        return {'url': f'http://{WEB_ADDRESS}:{WEB_PORT}/record?id={str(record_id)}&user={user_id}'}
    finally:
        db.close()

@app.get('/record')
async def download_audio_handler(id: str, user: int):
    db = SessionLocal()
    try:
        record = db.query(AudioRecord).filter(AudioRecord.id == id, AudioRecord.user_id == user).first()
        if not record:
            raise HTTPException(status_code=404, detail='Record not found')
        return FileResponse(os.path.join(AUDIO_FILES_PATH, record.filename_local), media_type='audio/mpeg', filename=record.filename_orig)
    finally:
        db.close()

if __name__ == '__main__':
    if not inspect(engine).has_table('user'):
        Base.metadata.create_all(bind=engine)
    # uvicorn.run('main:app', host='0.0.0.0', port=WEB_PORT, reload=True)
    uvicorn.run(app, host='0.0.0.0', port=WEB_PORT)
