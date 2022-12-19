import time
import threading
from threading import Thread
import pytube
import os
import ctypes
from http.client import IncompleteRead


# https://www.youtube.com/playlist?list=PL4xLP4LLBa-vTucuR1vN5zRfrZHnpivWU

# Version 1.3
# ask for audio abr in get_audio_stream
# ask for video resolution
# add more detailed prompt for Incomplete read exception

# stream.filter().get_highest_resolution

lock = threading.Lock()

threads_num = 10

searching = True


def human_readable(num, suffix="B"):
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


def get_playlist_urls(playlist_url):
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


def get_youtube(url):
    return pytube.YouTube(url)


def get_audio_stream(youtube: pytube.YouTube) -> pytube.Stream:
    """ Currently only gets best audio available """
    try:
        return youtube.streams.filter(file_extension='mp4', progressive=False, type='audio').order_by('abr').last()
    except IncompleteRead as e:
        print(e)


def get_video_stream(youtube: pytube.YouTube) -> pytube.Stream:
    """  Currently only gets best video available """
    try:
        return youtube.streams.filter(file_extension='mp4', progressive=False, type='video').order_by('resolution').last()
    except IncompleteRead as e:
        print(e)


def download_audio(stream: pytube.Stream):
    """ Currently only downloads the .mp4 and renames it to mp3 file """

    try:
        # download the file
        out_file = stream.download(output_path=os.getcwd())

        # save the file in correct format
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


def download_video(stream: pytube.Stream):
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
        download_audio(stream)


def worker(urls: list, thread_id: int) -> None:
    while check[thread_id] < len(urls):
        url: str = urls[check[thread_id]]

        youtube = get_youtube(url)

        youtubes.append(youtube)

        try:
            check[thread_id] += 1
        except IndexError:
            pass


def worker2(youtubes: list, thread_id: int, files_size: list) -> None:
    while check2[thread_id] < len(youtubes):
        youtube: pytube.YouTube = youtubes[check2[thread_id]]

        # get the stream of audio with the best abr
        # takes mp4 audio with the best abr
        audio_stream = get_audio_stream(youtube)
        if audio_stream:
            streams.append(audio_stream)

        files_size.append(audio_stream.filesize)
        tprint(f'Found Stream || {audio_stream.title} || {audio_stream.abr} || {human_readable(audio_stream.filesize)}')

        try:
            check2[thread_id] += 1
        except IndexError:
            pass


def worker3(youtubes: list, thread_id: int, files_size: list) -> None:
    while check2[thread_id] < len(youtubes):
        youtube: pytube.YouTube = youtubes[check2[thread_id]]

        # get the stream of audio with the best abr
        # takes mp4 audio with the best abr
        video_stream = get_video_stream(youtube)
        if video_stream:
            streams.append(video_stream)

        files_size.append(video_stream.filesize)
        tprint(f'Found Stream || {video_stream.title} || {video_stream.resolution} || {human_readable(video_stream.filesize)}')

        try:
            check2[thread_id] += 1
        except IndexError:
            pass


def print_searching():
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


def main():
    set_title("Youtube Playlist Downloader")

    global youtubes
    global check
    global streams
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

            t: Thread = threading.Thread(target=worker, args=(sliced_urls, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # ASK TO DOWNLOAD VIDEO OR AUDIO
        choice = input(f"Do you want to download the audio or the video of the playlist (v/a)? ").lower()

        threads2 = []
        check2 = [0 for _ in range(threads_num)]
        streams = []
        files_size = []
        startTime1 = time.perf_counter()
        for i in range(threads_num):
            sliced_youtubes: list = youtubes[int(len(youtubes) / threads_num * i): int(
                len(youtubes) / threads_num * (i + 1))]

            if choice == "v" or choice == "":
                t2: Thread = threading.Thread(target=worker3, args=(sliced_youtubes, i, files_size))
            else:
                t2: Thread = threading.Thread(target=worker2, args=(sliced_youtubes, i, files_size))

            threads2.append(t2)
            t2.start()

        for t2 in threads2:
            t2.join()
        endTime1 = time.perf_counter()
        tprint(f'It took {endTime1 - startTime1:.2f}s to find {sum(check2)} songs')

        # proceed
        set_title("Youtube Playlist Downloader || Proceeding")
        tprint(f"Number of songs that are going to be downloaded: {len(files_size)}/{sum(check)}")
        tprint(f"Size of the download: {human_readable(sum(files_size))}")

        proceed = input("Are you sure you want to download the songs (y/n)? ").lower()
        tprint()

        if proceed == "y" or proceed == "":
            startTime = time.perf_counter()

            for i, stream in enumerate(streams):
                set_title(f"Youtube Playlist Downloader || Downloaded ({i}/{sum(check2)})")
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
            tprint(f"It took {(endTime - startTime):.2f}s to download all {sum(check)} songs!")

        set_title("Youtube Playlist Downloader")

        stay()


if __name__ == '__main__':
    main()
