# vk-autoposter


<strong><span style="color: green">UPD. THIS SCRIPT DOESN'T WORK ANYMORE DUE TO CHANGE OF VK'S API POLICY. DO NOT USE IT.</span></strong>


A simple script that automatically sends messages in social network service VK at regular intervals.
Features:
- Posting messages to someone's wall, to VK community or to your own wall
- Attaching a picture from your directory

## How to use
1. Install Python 3.6+
2. Install required Python packages, which you can grab via pip:

`$ pip3 install -r requirements.txt`

3. Add a txt-file with your messages (you can use test.txt for testing purpose)
4. Create your standalone app in VK (https://vk.com/editapp?act=create)
5. Edit config.ini
6. Run autoposter.py
7. ?????
8. PROFIT!

## Config.ini
- **TxtFile**: Location of text-file with your messages, separated by newline (e.g. `test.txt` or `D:\Documents\file.txt`)
- **RandomLine**: Options:
  - yes: sending random text lines from your file
  - no: sending text lines in order
- **LineMinimumLength**: Minimum length of a text line
- **OwnerID**: Where to post your messages. Accepts only an integer value. Options:
  - VK user ID (e.g. 123123123)
  - VK community ID. Use a negative value to designate a community ID, e.g. -60021060
  - Leave blank to post on your own wall
- **PostInterval**: Post intervals in seconds
- **PhotoSource**: Options:
  - mal: attach a random picture from MyAnimeList.net (this is for testing purposes and it's going to be removed later)
  - local: attach photos from your directory one by one, starting from the first file (sorted by filename)
  - rand-local: attach a random photo from your directory
- **PhotoLocation**: Specify the absolute or relative path to photos (e.g. `C:\Pictures\photos` or `pics`)
