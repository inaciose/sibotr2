#include <gz/sim/System.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/image.pb.h>
#include <gz/plugin/Register.hh>
#include <gz/msgs/visual.pb.h>

#include <opencv2/opencv.hpp>

using namespace gz;
using namespace sim;

class DynamicTexturePlugin :
  public System,
  public ISystemConfigure
{
public:
  void Configure(const Entity &,
                 const std::shared_ptr<const sdf::Element> &,
                 EntityComponentManager &,
                 EventManager &) override
  {
    this->node.Subscribe("/image", &DynamicTexturePlugin::OnImage, this);
    this->pub = node.Advertise<gz::msgs::Visual>("/world/default/visual_config");
    gzmsg << "Subscribed\n";
  }

private:
  void OnImage(const gz::msgs::Image &_msg)
  {
    int w = _msg.width();
    int h = _msg.height();

    if (_msg.data().size() != w*h*3)
      return;

    cv::Mat img(h, w, CV_8UC3, (void*)_msg.data().data());

    std::string path = "/ws/frame.png";
    cv::imwrite(path, img);


    gz::msgs::Visual msg;
    msg.set_name("screen");

    auto *mat = msg.mutable_material();
    auto *script = mat->mutable_script();

    script->set_name("Gazebo/DynamicTexture");
    script->add_uri("file:///ws/frame.png");   // <- isto é o truque

    this->pub.Publish(msg);
    gzmsg << "UPDATED\n";
  }

private:
  transport::Node node;
  transport::Node::Publisher pub;
};

GZ_ADD_PLUGIN(
  DynamicTexturePlugin,
  System,
  DynamicTexturePlugin::ISystemConfigure
)
