import ssl
ssl._create_default_https_context = ssl._create_stdlib_context

import os
import yaml
import json
import argparse
from pytube import YouTube
import whisper
from monitor.folder import folder_exists

parse = argparse.ArgumentParser()
parse.add_argument("--mode", type = str, default = "development", help = "development or production")
args = parse.parse_args()

@folder_exists
def store_file(
    folder_path: str,
    file_name: str,
    json_content: dict
):
    
    with open(os.path.join(folder_path, file_name), "w", encoding = "utf-8") as f:
        if file_name[-5:] == ".json":
            json.dump(json_content, f, ensure_ascii = False)

    return 

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

if args.mode == "development":
    yt_link_list = config["yt-video-link"][1:2]

else:
    yt_link_list = config["yt-video-link"]

for one_yt_link in yt_link_list:
    try:
        yt = YouTube(one_yt_link)

        yt_title = yt.title # 影片標題，用來當作檔案名稱
        yt_author = yt.author # 影片作者，用來分類資料夾
        yt.streams.filter().get_audio_only().download(filename = "./test.mp3")

        model = whisper.load_model("large-v1")
    
        result = model.transcribe(
            audio = "./test.mp3",
            initial_prompt = "這是一段與人類身體健康飲食相關的音訊，解析文字後一定要加上標點符號（諸如：逗號、問號、句號、問號等）。",
            verbose = True
        )
    except:
        print("Error", one_yt_link)
        continue

    store_file(
        folder_path = yt_author.replace("/", "_"),
        file_name = "{}.json".format(yt_title.replace("/", "_")),
        json_content = {
            "title": yt_title,
            "url": one_yt_link,
            "content": result["text"].replace(",", "，")
        }
    )