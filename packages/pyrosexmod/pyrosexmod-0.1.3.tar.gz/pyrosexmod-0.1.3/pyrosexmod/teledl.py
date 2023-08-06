import os
import asyncio
import yt_dlp as youtube_dl


async def download(link: str) -> str:
    loop = asyncio.get_running_loop()
    
    def video_dl():
        ydl_optssx = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "nooverwrites": True,
            "no_warnings": False,
            "ignoreerrors": True,
        }
        x = youtube_dl.YoutubeDL(ydl_optssx)
        info = x.extract_info(link, False)
        xyz = os.path.join(
            "downloads", f"{info['id']}.{info['ext']}"
        )
        if os.path.exists(xyz):
            return xyz
        x.download([link])
        return xyz

    return  await loop.run_in_executor(None, video_dl)