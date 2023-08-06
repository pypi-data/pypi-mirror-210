import os
import yt_dlp
import asyncio
from typing import Union


async def formats(link: str):
    if "&" in link:
        link = link.split("&")[0]
    ytdl_opts = {"quiet": True}
    ydl = yt_dlp.YoutubeDL(ytdl_opts)
    with ydl:
        formats = []
        r = ydl.extract_info(link, download=False)
        for format in r["formats"]:
            try:
                str(format["format"])
            except:
                continue
            if not "dash" in str(format["format"]).lower():
                try:
                    format["format"]
                    format["filesize"]
                    format["format_id"]
                    format["ext"]
                    format["format_note"]
                except:
                    continue
                formats.append(
                    {
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "ext": format["ext"],
                        "format_note": format["format_note"],
                        "url": link,
                    }
                )
    return formats, link


async def getid(link: str):
    if "&" in link:
        link = link.split("&")[0]
    ytdl_opts = {"quiet": True}
    ydl = yt_dlp.YoutubeDL(ytdl_opts)
    with ydl:
        x = ydl.extract_info(link, download=False)
        videoid = x["id"]
    return videoid


async def download(
    link: str,
    video: Union[bool, str] = None,
    format_id: Union[bool, str] = None,
) -> str:
    loop = asyncio.get_running_loop()
    
    def vid_dl():
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

    def video_dl():
        formats = f"{format_id}+140"
        ydl_optssx = {
            "format": formats,
            "outtmpl": "downloads/%(title)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "prefer_ffmpeg": True,
            "merge_output_format": "mp4",
        }
        x = yt_dlp.YoutubeDL(ydl_optssx)
        info = x.extract_info(link, False)
        xyz = os.path.join(
            "downloads", f"{info['title']}.mp4"
        )
        if os.path.exists(xyz):
            return xyz
        x.download([link])
        return xyz

    if video:
        downloaded_file = await loop.run_in_executor(None, vid_dl)
    else:
        downloaded_file = await loop.run_in_executor(None, video_dl)
    return downloaded_file