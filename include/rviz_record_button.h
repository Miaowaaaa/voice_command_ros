#ifndef RVIZ_RECORD_BUTTON
#define RVIZ_RECORD_BUTTON

#include <ros/ros.h>
#include <ros/console.h>
#include <rviz/panel.h>

class QPushButton;

namespace voice_command
{

class VoiceRecordButton: public rviz::Panel
{
Q_OBJECT

public:
    VoiceRecordButton(QWidget *parent = 0);

    //Override
    virtual void save(rviz::Config conifg) const;

    //Override
    virtual void load(const rviz::Config &Config);

public Q_SLOTS:

    //record voice
    void record_voice();

    //stop record
    void stop_record();


protected:

    void call_voi_service();

protected:

    QPushButton *_record_b;

};

}

#endif
