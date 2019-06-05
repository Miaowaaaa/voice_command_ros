# Voice Command
![](https://img.shields.io/badge/ROS-Kinetic-brightgreen.svg) ![](https://img.shields.io/badge/Qt-5.5.1-orange.svg)   

A ROS package for recognize the voice command for robot.  

- branch
  - master: use a record button to record voice and recognition
  - realtime: auto recognition for voice

# Reference

The code is referred to [baidu_speech](https://github.com/Miaowaaaa/baidu_speech) and extend package by using [xfyun](https://www.xfyun.cn/).

# Prepare

- 1. Regist a developer account in [xfyun](https://www.xfyun.cn/).
- 2. Add a voice recognition application in your control board.
- 3. Get APP_ID and API_KEY and use them in `voice_command.launch`.
- 4. Add you ip address in white list.

# How to use

```
1. modify the filepath in `voice_command.launch`
2. roslaunch voice_command voice_command.launch
3. push the button on the left_right corner of rviz to record voice.
4. release the button to recognize.
5. result will be shown in console.
```

# Publish Topic

- /reg_result  
  - The type of message is `std_msgs/String` and the result can be access by `msg.data`.

