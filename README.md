# Youtube-Playlist-Downloader
This is a script to download all the audio of every video in a youtube playlist. 

Feel free to suggest changes in the code. 

This project was initially made to practice multithreading. You can borrow all the code you want

## Version 1.1
- Finds video streams using multithread
- Downloads the best quality of audio automatically
- Prints out the size of the download before proceeding

## Version 1.2
- fixed searching bug
- asks to download video or audio
- downloads the mp4 video with the best resolution
- get_audio_stream/get_video_stream Incomplete read exception created

## Version 1.3
- find available audio formats
- find available video formats
- find available video resolutions
- find available audio abrs
- algorith to find all the wanted information (song number, stream number, abr, res, abr/res total count, abr/res count)
- find number of found streams
- ask for audio format
- ask for video format
- ask for audio abr ()
- ask for video resolution
- find(make list) available audios abrs for the file_format asked
- find(make list) available videos resolutions for the file_format asked

# TODO 
- Implement documentation
- get rid of global variables 

## Late TODO
- make gui
- break down main.py in multiple files
