import itertools
from itertools import repeat
import time
import threading
from threading import Thread
import pytube
import os
import ctypes
from http.client import IncompleteRead
from pytube import itags

# for incomplete read https://github.com/pytube/pytube/issues/1266 (dongyouhong's post)

# https://www.youtube.com/playlist?list=PL4xLP4LLBa-vTucuR1vN5zRfrZHnpivWU
# https://github.com/pytube/pytube/blob/master/pytube/itags.py

# Version 1.4
# print alternatives for download if not all res/abr are there (make and ask for alternative before this step)
# print size of that alternative
# fix how the code looks

# if there is not enough videos or audios that satisfy one spesific res/abr then fill the gap
#  find the number of stream that is not included and try to find it in the closest values

# http.client.RemoteDisconnected: Remote end closed connection without response (while trying to find stream)
# number of videos/audio is not right (files_size fixes it)

# add more detailed prompt for Incomplete read exception

# Version 1.5
# make it so that when you download video it also downloads the audio
# ask for and find audio abr the same way it only asks for just audio
# fix the get_audio_stream and get_video_stream functions
# make it take only mp4 and webm

# add get higher/lower resolution option
# add get higher/lower abr option

# after all this fix the set_title for each phase of the program

lock = threading.Lock()

threads_num = 10

searching = True


def human_readable(num, suffix="B") -> str:
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0

    return f"{num:.1f}Yi{suffix}"


def stay() -> None:
    input()
    quit()


def tprint(message="", end="\n") -> None:
    lock.acquire()
    print(message, end=end)
    lock.release()


def set_title(message) -> None:
    ctypes.windll.kernel32.SetConsoleTitleW(message)


def get_playlist_urls(playlist_url) -> list:
    global searching
    urls = []

    try:
        playlist_urls = pytube.Playlist(playlist_url)

        if not playlist_urls:
            raise SystemExit
        else:
            searching = False
            for url in playlist_urls:
                urls.append(url)

            print(f"\rPlaylist ... has been found\n")

    except SystemExit:
        searching = False

        print("\rPlaylist not Found!")
        input("Press any key to exit ")

    except KeyboardInterrupt:
        pass

    except:
        searching = False

        print("\rSomething went wrong! Please try again.")
        stay()

    return urls


def get_youtube(url) -> pytube.YouTube:
    return pytube.YouTube(url)


def get_audio_stream(youtube: pytube.YouTube) -> pytube.Stream:
    """ Currently only gets the best audio available """
    # stream.filter().get_highest_resolution
    try:
        return youtube.streams.filter(progressive=False, type='audio').order_by('abr')
    except IncompleteRead as e:
        print(e)


def get_video_stream(youtube: pytube.YouTube) -> pytube.Stream:
    """  Currently only gets the best video available """
    # stream.filter().get_highest_resolution
    try:
        return youtube.streams.filter(progressive=False, type='video').order_by('resolution')
    except IncompleteRead as e:
        print(e)


def download_audio(stream: pytube.Stream) -> None:
    """ Currently only downloads the .mp4 and renames it to mp3 file """

    try:
        # download the file
        out_file = stream.download(output_path=os.getcwd())

        # save the file in correct file_format
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        try:
            os.rename(out_file, new_file)
        except FileExistsError as e:
            print(e)

    except KeyboardInterrupt:
        quit()

    except Exception as e:
        print(e)
        download_audio(stream)


def download_video(stream: pytube.Stream) -> None:
    """ Currently only downloads the .mp4 file """
    try:
        # currently only downloads the .mp4 file
        stream.download(output_path=os.getcwd())

    except KeyboardInterrupt:
        quit()

    except FileExistsError as e:
        print(e)

    except Exception as e:
        print(e)
        download_video(stream)


def make_youtubes_list(urls: list, thread_id: int) -> None:
    while check[thread_id] < len(urls):
        url: str = urls[check[thread_id]]

        youtube = get_youtube(url)

        youtubes.append(youtube)

        try:
            check[thread_id] += 1
        except IndexError:
            pass


def make_audio_streams_list(youtubes: list, thread_id: int) -> None:
    while check2[thread_id] < len(youtubes):
        youtube: pytube.YouTube = youtubes[check2[thread_id]]

        # get the stream of audio with the best abr
        # takes mp4 audio with the best abr
        audio_stream = get_audio_stream(youtube)

        if audio_stream:
            streams_list.append(audio_stream)
            tprint(f"Found Streams for audio {youtube.title}")

        try:
            check2[thread_id] += 1
        except IndexError:
            pass


def make_video_streams_list(youtubes: list, thread_id: int) -> None:
    while check2[thread_id] < len(youtubes):
        youtube: pytube.YouTube = youtubes[check2[thread_id]]

        # get the stream of audio with the best abr
        # takes mp4 audio with the best abr
        video_stream = get_video_stream(youtube)

        if video_stream:
            streams_list.append(video_stream)
            tprint(f"Found Streams for video {youtube.title}")

        try:
            check2[thread_id] += 1
        except IndexError:
            pass


def print_searching() -> None:
    global searching

    while searching:
        time.sleep(0.5)
        if not searching:
            break
        tprint("\rsearching", end='')

        time.sleep(0.5)
        if not searching:
            break
        tprint("\rsearching.", end='')

        time.sleep(0.5)
        if not searching:
            break
        tprint("\rsearching..", end='')

        time.sleep(0.5)
        if not searching:
            break
        tprint("\rsearching...", end='')


def choose(prompt: str, *choices: str):
    """ Choices should be in lower case """
    inp = input(prompt).lower()
    while inp not in choices:
        if inp == "":
            return choices[0]


        inp = input(f"Invalid input \"{inp}\". Please insert {choices}: ").lower()

    return inp


def main():
    set_title("Youtube Playlist Downloader")

    global youtubes
    global check
    global streams_list
    global check2

    playlist_url = input("Insert playlist url: ")

    print()

    #  starts anyway no matter what the prompt is
    set_title("Youtube Playlist Downloader || Loading")
    threading.Thread(target=print_searching, daemon=True).start()

    urls = get_playlist_urls(playlist_url)

    if urls:

        threads = []
        youtubes = []
        check = [0 for _ in range(threads_num)]

        # this part does not need to be in threads
        for i in range(threads_num):
            sliced_urls: list = urls[int(len(urls) / threads_num * i): int(
                len(urls) / threads_num * (i + 1))]

            t: Thread = threading.Thread(target=make_youtubes_list, args=(sliced_urls, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # ask to download video or audio
        choice = choose("Do you want to download the audio or the video of the playlist (v/a)? ", "v", "a")

        threads2 = []
        check2 = [0 for _ in range(threads_num)]
        streams_list = []
        startTime1 = time.perf_counter()
        for i in range(threads_num):
            sliced_youtubes: list = youtubes[int(len(youtubes) / threads_num * i): int(
                len(youtubes) / threads_num * (i + 1))]

            if choice == "v" or choice == "":
                t2: Thread = threading.Thread(target=make_video_streams_list, args=(sliced_youtubes, i))
            else:
                t2: Thread = threading.Thread(target=make_audio_streams_list, args=(sliced_youtubes, i))

            threads2.append(t2)
            t2.start()

        for t2 in threads2:
            t2.join()
        endTime1 = time.perf_counter()
        tprint(f'It took {endTime1 - startTime1:.2f}s to search for {sum(check2)} songs')

        # GET FORMAT,RES,ABR/ FORMAT,ABR ACCORDING TO LIST THE RESULTS
        streams = [[] for _ in repeat(None, sum(check))]
        stream_num = 0
        # 3gpp is always progressive, mp4 is sometimes, webm is never
        if choice == "v" or choice == "":
            for i, _streams in enumerate(streams_list):
                for j, stream in enumerate(_streams):
                    print(stream)
                    print(stream.subtype, stream.resolution, stream.is_progressive)
                    if not stream.is_progressive:
                        streams[i].append((stream.subtype, int(stream.resolution[:-1]), i, j))
        else:
            for i, _streams in enumerate(streams_list):
                for j, stream in enumerate(_streams):
                    print(stream)
                    print(stream.subtype, stream.abr, stream.is_progressive)
                    if not stream.is_progressive:
                        streams[i].append((stream.subtype, int(stream.abr[:-4]), i, j))
        print(streams)

        occurrences = {
            "mp4": {},
            "webm": {},
        }

        for stream in streams:
            for item in stream:
                if occurrences[item[0]].get(item[1]):
                    occurrences[item[0]][item[1]].append((item[2], item[3]))
                else:
                    occurrences[item[0]][item[1]] = [(item[2], item[3])]
        print(occurrences)

        streams_total_count = {
            "mp4": dict.fromkeys(occurrences["mp4"].keys(), 0),
            "webm": dict.fromkeys(occurrences["webm"].keys(), 0)
        }
        for file_ext, values in occurrences.items():
            for value, cords in values.items():
                streams_total_count[file_ext][value] = len(cords)
        print(streams_total_count)

        streams_count = {
            "mp4": dict.fromkeys(occurrences["mp4"].keys(), 0),
            "webm": dict.fromkeys(occurrences["webm"].keys(), 0)
        }
        for file_ext, values in occurrences.items():
            for value, cords in values.items():
                count = 1
                current = cords[0][0]
                for cord in cords:
                    if cord[0] > current:
                        current = cord[0]
                        count += 1
                streams_count[file_ext][value] = count
        print(streams_count)

        print(f"Number of songs found: {sum(check) - streams.count([])}")
        print(len(streams))
        print(streams.count([]))

        for file_ext in occurrences.keys():
            print(f"{file_ext}")
            for value in occurrences[file_ext].keys():
                print(f"    {str(value):4s} total streams: {str(streams_total_count[file_ext][value]):4s}, found streams for {str(streams_count[file_ext][value]):4s}/{str(sum(check)):4s} videos")

        print("If all streams can not be downloaded using only one option alternatives are going to be suggested.")
        file_format = choose("What type of file do you want to download (m/w)? ", "m", "w")
        if file_format == "m" or file_format == "":
            if choice == "v" or choice == "":
                quality = choose("Insert a resolution: ", *(str(k) for k in occurrences["mp4"].keys()))
            else:
                quality = choose("Insert an abr: ", *(str(k) for k in occurrences["mp4"].keys()))

            # {'mp4': {144: [(0, 1), (0, 3), (1, 1), (1, 3), (2, 1), (3, 1), (3, 3), (4, 1), (4, 3), (5, 1), (6, 1) ...
            downloads = occurrences["mp4"][int(quality)]
        else:
            if choice == "v" or choice == "":
                quality = choose("Insert a resolution: ", *(str(k) for k in occurrences["webm"].keys()))
            else:
                quality = choose("Insert an abr: ", *(str(k) for k in occurrences["webm"].keys()))

            downloads = occurrences["webm"][int(quality)]

        # for i in range(len(downloads) - 1, 0, -1):
        #     if downloads[i][0] == downloads[i - 1][0]:
        #         downloads.pop(i)
        downloads = [cords for i, cords in enumerate(downloads) if i == 0 or cords[0] != downloads[i - 1][0]]
        print(downloads)

        files_size = [streams_list[tup[0]][tup[1]].filesize for tup in downloads]

        # proceed
        set_title("Youtube Playlist Downloader || Proceeding")
        tprint(f"Number of songs that are going to be downloaded: {len(files_size)}/{sum(check)}")
        tprint(f"Size of the download: {human_readable(sum(files_size))}")

        proceed = choose("Are you sure you want to download the songs (y/n)? ", "y", "n")
        print()

        if proceed == "y" or proceed == "":
            startTime = time.perf_counter()

            for i, cords in enumerate(downloads):
                set_title(f"Youtube Playlist Downloader || Downloading ({i + 1}/{len(files_size)})")

                stream = streams_list[cords[0]][cords[1]]

                try:
                    tprint(f"Downloading || {stream.title}")
                except IncompleteRead:
                    print(f'Something went wrong while trying to find song number {i + 1}')

                if choice == "v" or choice == "":
                    download_video(stream)
                else:
                    download_audio(stream)

            endTime = time.perf_counter()

            tprint("\nDone!")
            tprint(f"It took {(endTime - startTime):.2f}s to download all {len(files_size)} songs!")

        set_title("Youtube Playlist Downloader")

        stay()


if __name__ == '__main__':
    main()
