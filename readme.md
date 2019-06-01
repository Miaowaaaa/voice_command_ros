# Voice Command
![](https://img.shields.io/badge/ROS-Kinetic-brightgreen.svg) ![](https://img.shields.io/badge/Qt-5.5.1-orange.svg)   

A ROS package for recognize the voice command for robot.

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

