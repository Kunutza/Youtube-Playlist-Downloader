import time
import threading
from threading import Thread
import pytube
import os
import ctypes

lock = threading.Lock()

threads_num = 10

loading = True


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
    global loading
    urls = []

    try:
        playlist_urls = pytube.Playlist(playlist_url)

        if not playlist_urls:
            raise SystemExit
        else:
            loading = False
            for url in playlist_urls:
                urls.append(url)

            time.sleep(0.5)
            print(f"\rPlaylist ... has been found\n")

    except SystemExit:
        loading = False

        time.sleep(0.5)
        print("\rPlaylist not Found!")
        input("Press any key to exit ")

    except KeyboardInterrupt:
        pass

    except:
        loading = False

        print("\rSomething went wrong! Please try again.")
        stay()

    return urls


def get_youtube(url):
    return pytube.YouTube(url)


def download_video(youtube: pytube.YouTube):
    try:
        # extract only audio
        stream = youtube.streams.filter(only_audio=True).first()

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

    except:
        print("Connection timed out. Trying again ...")
        download_video(youtube)


def worker(urls: list, thread_id: int) -> None:
    while check[thread_id] < len(urls):
        url: str = urls[check[thread_id]]

        youtube = get_youtube(url)

        youtubes.append(youtube)

        try:
            check[thread_id] += 1
        except IndexError:
            pass


def print_loading():
    global loading

    while loading:
        if not loading:
            return
        time.sleep(0.5)
        tprint("\rloading", end='')

        if not loading:
            return
        time.sleep(0.5)
        tprint("\rloading.", end='')

        if not loading:
            return
        time.sleep(0.5)
        tprint("\rloading..", end='')

        if not loading:
            return
        time.sleep(0.5)
        tprint("\rloading...", end='')


def main():
    set_title("Youtube Playlist Downloader")

    global youtubes
    global check

    playlist_url = input("Insert playlist url: ")

    print()

    set_title("Youtube Playlist Downloader || Loading")
    threading.Thread(target=print_loading, daemon=True).start()

    urls = get_playlist_urls(playlist_url)

    # threading.Thread(target=cpmCounter, daemon=True).start()
    # threading.Thread(target=updateTitle, args=[startTime], daemon=True).start()

    if urls:
        threads = []
        youtubes = []
        check = [0 for _ in range(threads_num)]
        for i in range(threads_num):
            sliced_urls: list = urls[int(len(urls) / threads_num * i): int(
                len(urls) / threads_num * (i + 1))]
            t: Thread = threading.Thread(target=worker, args=(sliced_urls, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        time.sleep(0.5)
        tprint('Task Completed')
        tprint('Created all Threads\n')

        # proceed
        set_title("Youtube Playlist Downloader || Proceeding")
        tprint(f"Number of songs that are going to be downloaded: {sum(check)}")

        proceed = input("Are you sure you want to download the songs (y/n)? ").lower()
        tprint()

        if proceed == "y" or proceed == "":
            startTime = time.perf_counter()

            for i, youtube in enumerate(youtubes):
                set_title(f"Youtube Playlist Downloader || Downloaded ({i}/{sum(check)})")
                tprint(f"Downloading | {youtube.title}")

                download_video(youtube)

            endTime = time.perf_counter()

            tprint("\nDone!")
            tprint(f"It took {(endTime - startTime):.2f}s to download all {sum(check)} songs!")

        set_title("Youtube Playlist Downloader")

        stay()


if __name__ == '__main__':
    main()
