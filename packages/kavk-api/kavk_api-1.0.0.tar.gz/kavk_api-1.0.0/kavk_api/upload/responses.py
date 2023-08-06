from pydantic import BaseModel as BS

class VideoSaveResponse(BS):
    video_hash:str
    size:int
    direct_link:str
    owner_id:int
    video_id:int
