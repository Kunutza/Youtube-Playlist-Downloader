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

# Version 1.5
# fix how the code looks
#  make more defs
#  fix the defs code

# http.client.RemoteDisconnected: Remote end closed connection without response (while trying to find stream)
# http.client.IncompleteRead

# add more detailed prompt for Incomplete read exception (if possible)

# make it so that when you download video it also downloads the audio
# ask for and find audio abr the same way it only asks for just audio
# fix the get_audio_stream and get_video_stream functions
# make it take only mp4 and webm

# add get higher/lower resolution option
# add get higher/lower abr option

# give 2 alternatives (fill with the highest/lowest/none res/abr possible) [WILL NOT WORK IF OCCURENCES KEYS ARE NOT SORTED]

# fix the prompts

# after all this fix the set_title for each phase of the program

lock = threading.Lock()

threads_num = 10

searching = True


# add accuracy
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


# it could be done with yield
def search_prompt(prompt: str, end="") -> bool:
    global searching

    time.sleep(0.5)
    if not searching:
        return False

    tprint(f"\r{prompt}", end=end)
    return True


def print_searching() -> None:
    while True:
        if not search_prompt("searching"):
            break

        if not search_prompt("searching."):
            break

        if not search_prompt("searching.."):
            break

        if not search_prompt("searching..."):
            break


def choose(prompt: str, *choices: str):
    """ Choices should be in lower case """
    # may want to change inp if it is an int
    inp = input(prompt).lower()
    while inp not in choices:
        if inp == "":
            return choices[0]

        inp = input(f"Invalid input \"{inp}\". Please insert {choices}: ").lower()

    return inp


def main():
    global youtubes
    global check
    global streams_list
    global check2

    set_title("Youtube Playlist Downloader")

    playlist_url = input("Insert playlist url: ")
    print()

    set_title("Youtube Playlist Downloader || Loading")

    threading.Thread(target=print_searching, daemon=True).start()

    urls = get_playlist_urls(playlist_url)

    # if url is invalid exit the program
    if not urls:
        return

    # setup to find the youtubes of the playlist
    threads = []
    youtubes = []
    check = [0 for _ in range(threads_num)]

    # get all the youtubes of the playlist inside the youtubes list
    # this part does not need to be in threads (it executes quickly)
    for i in range(threads_num):
        sliced_urls: list = urls[int(len(urls) / threads_num * i): int(len(urls) / threads_num * (i + 1))]

        t: Thread = threading.Thread(target=make_youtubes_list, args=(sliced_urls, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # ask to download video or audio
    choice = choose("Do you want to download the audio or the video of the playlist (v/a)? ", "v", "a")

    # setup to find the streams of the youtubes
    threads2 = []
    check2 = [0 for _ in range(threads_num)]
    streams_list = []
    start_time1 = time.perf_counter()

    # get all the available streams for the youtubes inside the streams_list list
    # 10 streams seem to be optimal
    # more streams make no difference because internet speed becomes a limiting factor
    # MAY NEED TO CONSIDER ADDING MORE STREAMS WHEN HIGHER INTERNET SPEEDS ARE AVAILABLE
    for i in range(threads_num):
        sliced_youtubes: list = youtubes[int(len(youtubes) / threads_num * i): int(len(youtubes) / threads_num * (i + 1))]

        if choice == "v" or choice == "":
            t2: Thread = threading.Thread(target=make_video_streams_list, args=(sliced_youtubes, i))
        else:
            t2: Thread = threading.Thread(target=make_audio_streams_list, args=(sliced_youtubes, i))

        threads2.append(t2)
        t2.start()

    for t2 in threads2:
        t2.join()

    end_time1 = time.perf_counter()
    print(f'It took {end_time1 - start_time1:.2f}s to search for {sum(check2)} youtubes')

    # Get position of streams and format,res,abr/format,abr
    streams = [[] for _ in repeat(None, sum(check))]

    # 3gpp is always progressive, mp4 is sometimes, webm is never
    if choice == "v" or choice == "":
        for i, _streams in enumerate(streams_list):
            for j, stream in enumerate(_streams):
                # WILL NEED TO DELETE PRINT
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
    # WILL NEED TO DELETE PRINT
    print(streams)

    # setup of where res/abr occures
    # occurrences["mp4"].keys() WILL NOT BE SORTED IF THEY ARE NOT IN THE CORRECT ORDER FROM THE STREAMS
    occurrences = {
        "mp4": {},
        "webm": {},
    }

    # occurrences[item[0]][item[1]] = [(item[2], item[3])] | occurences["mp4"][144] = [(2, 1)]
    for stream in streams:
        for item in stream:
            if occurrences[item[0]].get(item[1]):
                occurrences[item[0]][item[1]].append((item[2], item[3]))
            else:
                occurrences[item[0]][item[1]] = [(item[2], item[3])]
    print(occurrences)

    # get total streams for each res/abr
    streams_total_count = {
        "mp4": dict.fromkeys(occurrences["mp4"].keys(), 0),
        "webm": dict.fromkeys(occurrences["webm"].keys(), 0)
    }

    for file_ext, values in occurrences.items():
        for value, cords in values.items():
            streams_total_count[file_ext][value] = len(cords)
    print(streams_total_count)

    # get the amount of youtubes that have available streams for each res/abr
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

    print(f"Number of youtubes found: {sum(check) - streams.count([])}")
    print(len(streams))
    print(streams.count([]))

    # print streams_total_count and streams_count info for user
    for file_ext in occurrences.keys():
        print(f"{file_ext}")
        for value in occurrences[file_ext].keys():
            print(f"    {str(value):4s} total streams: {str(streams_total_count[file_ext][value]):4s}, found streams for {str(streams_count[file_ext][value]):4s}/{str(sum(check)):4s} videos")

    # ask use for file format, res/abr
    print("If all streams can not be downloaded using only one option then at least one alternative is to be suggested.")
    file_format = choose("What type of file do you want to download (m/w)? ", "m", "w")

    if file_format == "m" or file_format == "":
        file_format = "mp4"
    else:
        file_format = "webm"

    if choice == "v" or choice == "":
        quality = choose("Insert a resolution: ", *(str(k) for k in occurrences[file_format].keys()))
    else:
        quality = choose("Insert an abr: ", *(str(k) for k in occurrences[file_format].keys()))

    # inititalise downloads list according to wanted format, res/abr
    # {'mp4': {144: [(0, 1), (0, 3), (1, 1), (1, 3), (2, 1), (3, 1), (3, 3), (4, 1), (4, 3), (5, 1), (6, 1) ...
    downloads = occurrences[file_format][int(quality)]

    # remove duplicates (you don't want to download the same youtube more than once)
    downloads = [cords for i, cords in enumerate(downloads) if i == 0 or cords[0] != downloads[i - 1][0]]
    print(downloads)

    # setup to search if any youtubes are missing from selected res/abr
    # find out what is missing (found_num = sum(check) - streams.count([]))
    # if all songs where found, the found set would look like this (0, 1, 2, 3, ... , 30)
    found = set(x[0] for x in downloads)
    not_found = [i for i in range(sum(check) - streams.count([])) if i not in found]
    print(found)
    print(not_found)

    if not_found:
        print(f"Not all streams have a quality of {quality}.\n"
              f"Streams {not_found} did not provide the wanted quality.")
        fill = choose(f"Do you want to fill the gaps with highest/lowest or none quality (h/l/n)? ", "h", "l", "n")

        # to_remove list is a list where if a youtube is found it then removes it from the not_found list and then
        # adds it to the download list
        to_remove = []

        # if fill == h , for j, k in reversed(occurrences[file_format].items()):
        # that is the only difference between the two iterations
        if fill == "h" or fill == "":
            for i, nf in enumerate(not_found):
                for j, k in reversed(occurrences[file_format].items()):
                    if j == quality:
                        continue

                    else:
                        for p, (a, b) in enumerate(k):
                            if a == nf:
                                to_remove.append((a, b))

                                # if a == nf then it breaks from the loops else it continues searching
                                break
                        else:
                            continue
                        break

        elif fill == "l":
            for i, nf in enumerate(not_found):
                for j, k in occurrences[file_format].items():
                    if j == quality:
                        continue

                    else:
                        for p, (a, b) in enumerate(k):
                            if a == nf:
                                to_remove.append((a, b))

                                # if a == nf then it breaks from the loops else it continues searching
                                break
                        else:
                            continue
                        break

        # do the intented job with the to_remove list of tuples
        for (a, b) in to_remove:
            downloads.append((a, b))

            not_found.remove(a)

        del to_remove

    print(found)
    # download list of tuples is not sorted if to_remove is used
    print(downloads)

    files_size = [streams_list[tup[0]][tup[1]].filesize for tup in downloads]

    # proceed
    set_title("Youtube Playlist Downloader || Proceeding")
    print(f"Number of youtubes that are going to be downloaded: {len(files_size)}/{sum(check)}")
    print(f"Total size of the download: {human_readable(sum(files_size))}")

    proceed = choose("Are you sure you want to download the songs (y/n)? ", "y", "n")
    print()

    if proceed == "y" or proceed == "":
        startTime = time.perf_counter()

        for i, cords in enumerate(downloads):
            set_title(f"Youtube Playlist Downloader || Downloading ({i + 1}/{len(files_size)})")

            # streams_list is the list that contains all the streams
            stream = streams_list[cords[0]][cords[1]]

            try:
                print(f"Downloading || {stream.title} || {human_readable(files_size[i])}")
            except IncompleteRead:
                print(f'Something went wrong while trying to find song number {i + 1}')

            if choice == "v" or choice == "":
                download_video(stream)
            else:
                download_audio(stream)

        endTime = time.perf_counter()

        print("\nDone!")
        # IF EXCEPT HAPPENS THIS NUMBER IS INVALID
        print(f"It took {(endTime - startTime):.2f}s to download all {len(files_size)} songs!")

    set_title("Youtube Playlist Downloader")

    stay()


if __name__ == '__main__':
    main()
