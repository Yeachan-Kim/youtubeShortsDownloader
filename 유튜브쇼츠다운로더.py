from tkinter import *
from googleapiclient.discovery import build
from pytube import YouTube
import ffmpeg
import os


#구글 api를 사용하는 버전으로 credentials 필요
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"


def startHandler():
    ids = []
    if entry1.get() != "":
        ids.append(entry1.get().strip())
    if entry2.get() != "":
        ids.append(entry2.get().strip())
    if entry3.get() != "":
        ids.append(entry3.get().strip())
    if entry4.get() != "":
        ids.append(entry4.get().strip())
    if entry5.get() != "":
        ids.append(entry5.get().strip())

    entry1.delete(0, "end")
    entry2.delete(0, "end")
    entry3.delete(0, "end")
    entry4.delete(0, "end")
    entry5.delete(0, "end")
    return ids


def download_shorts(channel_id):
    i = 0
    youtube = build("youtube", "v3")

    # 채널 아이디를 통해 채널 정보 가져오기
    channel_response = (
        youtube.channels().list(part="contentDetails", id=channel_id).execute()
    )

    # 채널 정보에서 빼온 정보로 플레이리스트 아이디 가져오기
    uploads_playlist_id = channel_response["items"][0]["contentDetails"][
        "relatedPlaylists"
    ]["uploads"]

    # UU를 UUSH로 바꿔서 쇼츠만 가져오기
    uploads_playlist_id = str(uploads_playlist_id).replace("UU", "UUSH")

    # 플레이리스트 아이디로 플레이리스트 항목 50개 가져오기
    playlistitems_request = youtube.playlistItems().list(
        part="snippet", playlistId=uploads_playlist_id, maxResults=50
    )

    # 채널 이름 가져오기
    channel_response = youtube.channels().list(part="snippet", id=channel_id).execute()
    channelName = channel_response["items"][0]["snippet"]["title"]

    # 채널 id로 저장위치 파일 만들고 위치 설정하기
    savePath = os.getcwd() + "\\" + channelName
    while True:
        num = 1
        if os.path.isdir(savePath):
            savePath = savePath + str(num)
            num += 1
        else:
            break
    if not os.path.exists(savePath):
        os.mkdir(savePath)

    while playlistitems_request is not None:
        playlistitems_response = playlistitems_request.execute()

        # 플레이 리스트 아이템 하나씩 돌면서 비디오 id 가져오기
        for playlist_item in playlistitems_response["items"]:
            video_id = playlist_item["snippet"]["resourceId"]["videoId"]

            print(f"Downloading {video_id}")
            try:  # 19금 영상일 경우 오류 발생해서 try except 넣음
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                yt = YouTube(video_url)

                # 1080p 영상만 다운로드
                yt.streams.filter(
                    adaptive=True, file_extension="mp4", only_video=True
                ).first().download(savePath)

                # 음성만 다운로드
                # fileName => 비디오만 있는 파일 이름
                fileName = (
                    yt.streams.filter(
                        adaptive=True, file_extension="mp4", only_video=True
                    )
                    .first()
                    .default_filename
                )
                audioName = "audio" + fileName  # audio만 있는 파일 이름
                yt.streams.filter(
                    adaptive=True, file_extension="mp4", only_audio=True
                ).first().download(savePath, filename=audioName)
                outputName = "final" + fileName  # 합친 후 파일 이름

                # ffmpeg를 이용하여 영상 음성 합치기
                videoPath = savePath + "\\" + fileName
                audioPath = savePath + "\\" + audioName
                outputPath = savePath + "\\" + outputName
                input_video = ffmpeg.input(videoPath)
                input_audio = ffmpeg.input(audioPath)
                ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
                    outputPath
                ).run()

                # 필요없어진 합치기 전 영상들 삭제
                os.remove(videoPath)
                os.remove(audioPath)

                # 720p로 하면 음성있는 영상 가능
                # yt.streams.get_highest_resolution().download()
                i += 1
            except:
                playlistitems_request = youtube.playlistItems().list_next(
                    playlistitems_request, playlistitems_response
                )

        playlistitems_request = youtube.playlistItems().list_next(
            playlistitems_request, playlistitems_response
        )
    outputTxt.insert(END, channelName + "채널 동영상" + str(i) + "개 다운로드 완료\n")


def startDownload():
    if os.path.isfile(os.getcwd() + "credentials.json"):
        outputTxt.insert(END, "credentials.json 파일이 없습니다\n")
        return
    ids = startHandler()
    if len(ids) == 0:
        outputTxt.insert(END, "아이디를 입력해주세요\n")
    else:
        btn1["text"] = "다운로드 중"
        for id in ids:
            outputTxt.insert(END, id + "채널 다운로드 중\n")
            download_shorts(id)
        outputTxt.insert(END, "다운로드 완료")
        btn1["text"] = "다운로드 시작"


tk = Tk()
tk.title("쇼츠 다운로더")
tk.geometry("640x400+100+100")

label1 = Label(tk, text="채널 id 1").grid(row=0, column=0)
label2 = Label(tk, text="채널 id 2").grid(row=1, column=0)
label3 = Label(tk, text="채널 id 3").grid(row=2, column=0)
label4 = Label(tk, text="채널 id 4").grid(row=3, column=0)
label5 = Label(tk, text="채널 id 5").grid(row=4, column=0)

outputTxt = Text(tk, bg="light cyan")
outputTxt.place(x=300, width=300, height=300)

# 각 단위 입력받는 부분 만들기
entry1 = Entry(tk)
entry2 = Entry(tk)
entry3 = Entry(tk)
entry4 = Entry(tk)
entry5 = Entry(tk)

entry1.grid(row=0, column=1)
entry2.grid(row=1, column=1)
entry3.grid(row=2, column=1)
entry4.grid(row=3, column=1)
entry5.grid(row=4, column=1)

btn1 = Button(tk, text="다운로드 시작", bg="black", fg="white", command=startDownload)
btn1.grid(row=5, column=1)

tk.mainloop()
