#include "rviz_record_button.h"
#include <QVBoxLayout>
#include <std_srvs/Empty.h>
#include <QPushButton>
#include <boost/thread.hpp>

namespace voice_command
{

VoiceRecordButton::VoiceRecordButton(QWidget* parent)
    :rviz::Panel(parent)
{

    QVBoxLayout *root = new QVBoxLayout;
    _record_b = new QPushButton("Voice Command");;
    root->addWidget(_record_b);
    setLayout(root);
    connect( _record_b, SIGNAL(pressed()),this,SLOT(record_voice()));
    connect( _record_b, SIGNAL(released()),this,SLOT(stop_record()));
}

void VoiceRecordButton::record_voice()
{
    boost::thread thread(boost::bind(&VoiceRecordButton::call_voi_service,this));
}

void VoiceRecordButton::stop_record()
{
    std_srvs::Empty::Request req;
    std_srvs::Empty::Response resp;
    ros::service::call("voice_service",req,resp);
    _record_b->setText("Voice Command");
}
void VoiceRecordButton::call_voi_service()
{
    ROS_INFO("Begining record voice...");
    _record_b->setText("Recording...");
    std_srvs::Empty::Request req;
    std_srvs::Empty::Response resp;

    // check if the service exists
    if(!ros::service::exists("voice_service",true))
    {
        _record_b->setText("Voice Command");
        ROS_WARN("no such service!");
        return;
    }
    //call
    bool success = ros::service::call("voice_service",req,resp);
    if(success)
    {
        
        ROS_INFO("End Recording...");
        return;
    }
    else
    {

        ROS_WARN("Something error in voice recording");
    }
}

//Override
void VoiceRecordButton::save(rviz::Config config) const
{
    rviz::Panel::save(config);
}

//Override
void VoiceRecordButton::load(const rviz::Config& config)
{
    rviz::Panel::load(config);
}

}
// A rviz plugin statement
#include <pluginlib/class_list_macros.h>
PLUGINLIB_EXPORT_CLASS(voice_command::VoiceRecordButton,rviz::Panel )