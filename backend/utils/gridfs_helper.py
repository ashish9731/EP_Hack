from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from fastapi import UploadFile
import uuid

async def save_video_to_gridfs(db, file: UploadFile) -> str:
    fs = AsyncIOMotorGridFSBucket(db)
    video_id = f"video_{uuid.uuid4().hex}"
    
    file_data = await file.read()
    
    await fs.upload_from_stream(
        video_id,
        file_data,
        metadata={
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(file_data)
        }
    )
    
    return video_id

async def get_video_from_gridfs(db, video_id: str) -> bytes:
    fs = AsyncIOMotorGridFSBucket(db)
    
    grid_out = await fs.open_download_stream_by_name(video_id)
    video_data = await grid_out.read()
    
    return video_data

async def delete_video_from_gridfs(db, video_id: str):
    fs = AsyncIOMotorGridFSBucket(db)
    
    cursor = fs.find({"filename": video_id})
    async for grid_data in cursor:
        await fs.delete(grid_data._id)
        break