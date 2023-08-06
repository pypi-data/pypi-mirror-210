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


async def download(
    link: str,
    format_id: Union[bool, str],
) -> str:
    loop = asyncio.get_running_loop()

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
    return await loop.run_in_executor(None, video_dl)
