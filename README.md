# Youtube-Playlist-Downloader
This is a script to download all the audio of every video in a youtube playlist. 

Feel free to suggest changes in the code. 

This project was initially made to practice multithreading. You can borrow all the code you want

If you want to use the script to download some songs I recommend you only download the audio. Downloading video or video with sound is a work in progress.

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
- finds available video resolutions for mp4/webm
- finds available audio abrs mp4/webm
- finds all the wanted information (song number, stream number, abr, res, abr/res total count, abr/res count)
- finds number of found streams
- asks for what audio format is going to be downloaded
- asks for video format is going to be downloaded
- asks for what audio abr to download
- asks for what video resolution to download
- find(make list) available audios abrs for the file_format and abr asked
- find(make list) available videos resolutions for the file_format and resolution asked

# TODO 
- Implement documentation
- get rid of global variables 

## Late TODO
- make gui
- break down main.py in multiple files
