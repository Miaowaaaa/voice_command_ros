#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyaudio import PyAudio, paInt16
import json
import base64
import os
import sys
import requests
import thread
import wave
import rospy
import numpy as np
import array
import chunk
import time
import hashlib
from std_srvs.srv import Empty
from std_msgs.msg import String


class recoder():
    def __init__(self):
        
        self.voice_service = rospy.Service("voice_service", Empty,self.voice_service)
        self.voice_pub = rospy.Publisher('reg_result', String, queue_size=1)
        # judge the record button state
        self.is_release = True
        # set parameters
        self.define()
        rospy.spin()

    def voice_service(self, req):
        """
        service callback
        req:    an empty request msg
        creata a thread to process time-cost step
        """
        if self.is_release:
            self.is_release = False
            thread.start_new_thread(self.voice_reg,("reg",1,))
        else:
            self.is_release = True
        return []

    def voice_reg(self,thread_name,delay):
        """
        the thread for voice recognization
        thread_name:    the name of thread
        delay      :    the time of delay
        """
        if self.recode():
            self.savewav(self.fileName)
            words = self.reg()
            self.voice_pub.publish(words)
            # reset record state
            self.is_release = True
        else:
            # reset record state
            self.is_release = True
            rospy.logwarn("To few words can't be recognized!")
    
    def getHeader(self,aue,engineType):
        """
        create a http request header
        """
        curTime = str(int(time.time()))
        param = "{\"aue\":\"" + aue + "\"" + ",\"engine_type\":\"" + engineType + "\"}"
        paramBase64 = str(base64.b64encode(param.encode('utf-8')))
        m2 = hashlib.md5()
        m2.update((self.API_KEY + curTime + paramBase64).encode('utf-8'))
        checkSum = m2.hexdigest()
        # http请求头
        header = {
            'X-CurTime': curTime,
            'X-Param': paramBase64,
            'X-Appid': self.APPID,
            'X-CheckSum': checkSum,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        }
        return header
    
    def getBody(self,filepath):
        """
        read the record audio file and encode with base64
        """
        binfile = open(filepath, 'rb')
        data = {'audio': base64.b64encode(binfile.read())}
        return data    
    
    def reg(self):
        """
        the real recognition process
        """
        audioFilePath = self.audioFilePath + "/" + self.fileName + ".wav"
        r = requests.post(self.URL, 
                            headers = self.getHeader(self.aue, self.engineType),
                            data = self.getBody(audioFilePath))
        result = json.loads(r.content.decode('utf-8'))
        return result['data']
    
    def define(self):
        """
        define parameters
        """
        self.error_reason = {
            3300: '输入参数不正确',
            3301: '识别错误',
            3302: '验证失败',
            3303: '语音服务器后端问题',
            3304: '请求 GPS 过大，超过限额',
            3305: '产品线当前日请求数超过限额',
            3314: '语音时间太短'
        }
        self.URL = "http://api.xfyun.cn/v1/service/v1/iat"
        
        self.APPID = "5cef711c"
        
        self.API_KEY = "35be5779affe4fe4ad6a13adc1ea30f8"
        self.aue = "raw"
        self.engineType = "sms8k"
        self.nchannel = 1
        
        self.NUM_SAMPLES = rospy.get_param('~REG_NUM_SAMPLES',2000)  # default 2000 pyaudio内置缓冲大小
        self.SAMPLING_RATE = rospy.get_param('~REG_SAMPLING_RATE',8000)  # default 8000 取样频率
        self.COUNT_NUM = rospy.get_param('~REG_COUNT_NUM',20) # default 20 NUM_SAMPLES个取样之内出现COUNT_NUM个大于LOWER_LEVEL的取样则记录声音
        self.SAVE_LENGTH = rospy.get_param('~REG_SAVE_LENGTH',8)  # default 8 声音记录的最小长度：SAVE_LENGTH * NUM_SAMPLES 个取样
        self.NO_WORDS = rospy.get_param('~REG_NO_WORDS',6)  # default 6
        self.APPID = rospy.get_param('~REG_APP_ID',"5cef711c")
        self.API_KEY = rospy.get_param('~REG_API_KEY',"35be5779affe4fe4ad6a13adc1ea30f8")
        self.nchannel = rospy.get_param('~REG_nchannel',1)  # default 1
        self.audioFilePath = rospy.get_param('REG_AUDIO_SAVE_PATH',"/home/Miaow")   
        self.fileName = rospy.get_param('REG_AUDIN_SAVE_NAME','test')
        self.Voice_String = []

    def recode(self):
        """
        recode audio date
        """
        pa = PyAudio()
        stream = pa.open(format=paInt16,
                         channels=self.nchannel,
                         rate=self.SAMPLING_RATE,
                         input=True,
                         frames_per_buffer=self.NUM_SAMPLES)
        save_count = 0
        save_buffer = []
        word_count = 0              #record the word number
        rospy.loginfo("begin to record audio data")
        while not self.is_release:
            string_audio_data = stream.read(self.NUM_SAMPLES)  
            # convert to an array
            audio_data = np.fromstring(string_audio_data, dtype=np.short)

            # check if there audio input
            rospy.loginfo("np.max(audio_data)  %d", np.max(audio_data))

            # calculate the number of samples whose value higher than a threshold
            large_sample_count = np.sum(audio_data > 500)
            word_count = word_count + large_sample_count

            # if the number is bigger than COUNT_NUM, save SAE_LENGTH blocks at least
            if large_sample_count > self.COUNT_NUM:
                save_count = self.SAVE_LENGTH

            else:
                save_count -= 1
            #print 'save_count',save_count

            # save datas in save_buffer
            if save_count < 0:
                save_count = 0
            elif save_count > 0:
                save_buffer.append(string_audio_data)
            else:
                pass

        # write save_buffer into a .wav file
        if len(save_buffer) > 0:
            self.Voice_String = save_buffer
            save_buffer = []
            rospy.loginfo("Recode a piece of voice successfully!")
            #return self.Voice_String
        else:
            pass
        #rospy.loginfo( '\n\n')
        rospy.loginfo("Word count: %d",word_count)

        # warn few words
        if word_count < self.NO_WORDS:
            return False
        else:
            return True

    def savewav(self, filename):
        """
        save as a audio file
        """
        rospy.loginfo('save audio')
        file_path = '/home/Miaow'
        WAVE_FILE = '%s/%s.wav' % (file_path, filename)
        wf = wave.open(WAVE_FILE, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.SAMPLING_RATE)
        wf.writeframes("".join(self.Voice_String))
        wf.close()
        rospy.loginfo('audio data is saved')


if __name__ == "__main__":
    rospy.init_node('voice_command')
    rospy.loginfo("initialization system")
    recoder()
