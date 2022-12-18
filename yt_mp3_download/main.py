import time
import threading
from threading import Thread
import pytube
import os
import ctypes
from http.client import IncompleteRead

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

            time.sleep(0.5)
            print(f"\rPlaylist ... has been found\n")

    except SystemExit:
        searching = False

        time.sleep(0.5)
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


def download_video(stream: pytube.Stream):
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
        download_video(stream)


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
        stream = youtube.streams.filter(file_extension='mp4', progressive=False, type='audio').order_by('abr').last()  #(stream should be in a try like line 83)')
        streams.append(stream)

        files_size.append(stream.filesize)
        tprint(f'Found Stream || {stream.title} || {stream.abr} || {human_readable(stream.filesize)}')

        try:
            check2[thread_id] += 1
        except IndexError:
            pass


def print_searching():
    global searching

    while searching:
        if not searching:
            break
        time.sleep(0.5)
        tprint("\rsearching", end='')

        if not searching:
            break
        time.sleep(0.5)
        tprint("\rsearching.", end='')

        if not searching:
            break
        time.sleep(0.5)
        tprint("\rsearching..", end='')

        if not searching:
            break
        time.sleep(0.5)
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

        threads2 = []
        check2 = [0 for _ in range(threads_num)]
        streams = []
        files_size = []
        startTime1 = time.perf_counter()
        for i in range(threads_num):
            sliced_youtubes: list = youtubes[int(len(youtubes) / threads_num * i): int(
                len(youtubes) / threads_num * (i + 1))]
            t2: Thread = threading.Thread(target=worker2, args=(sliced_youtubes, i, files_size))
            threads2.append(t2)
            t2.start()

        for t2 in threads2:
            t2.join()
        endTime1 = time.perf_counter()
        tprint(f'It took {endTime1 - startTime1}s to find {sum(check2)} songs')

        time.sleep(0.5)
        tprint('Task Completed')
        tprint('Created all Threads\n')

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

                download_video(stream)

            endTime = time.perf_counter()

            tprint("\nDone!")
            tprint(f"It took {(endTime - startTime):.2f}s to download all {sum(check)} songs!")

        set_title("Youtube Playlist Downloader")

        stay()


if __name__ == '__main__':
    main()

# https://www.youtube.com/playlist?list=PL4xLP4LLBa-vTucuR1vN5zRfrZHnpivWU

# MAKE OPTIONS
#  ask to download video or audio

# line 121 stream needs except
