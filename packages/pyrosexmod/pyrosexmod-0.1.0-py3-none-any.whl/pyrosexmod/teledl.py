import os
import yt_dlp
import asyncio


async def download(link: str) -> str:
    loop = asyncio.get_running_loop()
    
    def video_dl():
        ydl_optssx = {
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
        }
        x = yt_dlp.YoutubeDL(ydl_optssx)
        info = x.extract_info(link, False)
        xyz = os.path.join(
            "downloads", f"{info['id']}.{info['ext']}"
        )
        if os.path.exists(xyz):
            return xyz
        x.download([link])
        return xyz

    return  await loop.run_in_executor(None, video_dl)