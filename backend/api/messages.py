from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from database import get_db
from models import Message, User
import socketio

router = APIRouter(prefix="/messages", tags=["messages"])

# Socket.IO Setup - In a real app, this might be separate, but here for MVP simplicity
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

class MessageCreate(BaseModel):
    channel: str
    content: str
    is_bot: bool = False

class MessageOut(BaseModel):
    id: int
    channel: str
    content: str
    sender_id: Optional[int]
    is_bot: bool
    timestamp: datetime
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    
    class Config:
        orm_mode = True

@router.get("/{channel}", response_model=List[MessageOut])
async def get_messages(channel: str, db: AsyncSession = Depends(get_db)):
    # Join with User to get sender details
    if channel not in ["general", "dev", "code-review"]:
         raise HTTPException(status_code=400, detail="Invalid channel")
         
    stmt = select(Message, User).outerjoin(User, Message.sender_id == User.id).where(Message.channel == channel).order_by(Message.timestamp.asc())
    result = await db.execute(stmt)
    
    messages = []
    for row in result:
        msg: Message = row[0]
        user: User = row[1]
        
        msg_out = MessageOut.from_orm(msg)
        if user:
            msg_out.sender_name = user.username
            msg_out.sender_avatar = user.avatar_url
        else:
            msg_out.sender_name = "Bot" if msg.is_bot else "Unknown"
            
        messages.append(msg_out)
        
    return messages

@router.post("/", response_model=MessageOut)
async def create_message(message: MessageCreate, background_tasks: BackgroundTasks, user_id: int = None, db: AsyncSession = Depends(get_db)):
    # Note: user_id should come from auth dependency normally
    # For bot messages, user_id can be None
    
    db_message = Message(
        channel=message.channel,
        content=message.content,
        sender_id=user_id if not message.is_bot else None,
        is_bot=message.is_bot
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    
    await db.refresh(db_message)
    
    # Broadcast via Socket.IO
    msg_out = MessageOut.from_orm(db_message)
    # We need to manually populate sender info if we want, but for now ID is okay or we fetch it.
    # To keep it fast, we just emit what we have. Frontend can re-fetch or use this.
    # Ideally we'd join user here, but let's just emit the basic data.
    data = msg_out.dict()
    # Serialize datetime
    data['timestamp'] = data['timestamp'].isoformat()
    
    await sio.emit("new_message", data)
    
    return db_message

# We will mount this in main.py
