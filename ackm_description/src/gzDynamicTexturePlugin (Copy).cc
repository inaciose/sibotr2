#include <gz/sim/System.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/image.pb.h>
#include <gz/plugin/Register.hh>

#include <opencv2/opencv.hpp>

using namespace gz;
using namespace sim;

class DynamicTexturePlugin :
  public System,
  public ISystemConfigure,
  public ISystemPostUpdate
{
public:
	void Configure(const Entity &,
				 const std::shared_ptr<const sdf::Element> &,
				 EntityComponentManager &,
				 EventManager &) override
	{
		bool ok = this->node.Subscribe("/image", &DynamicTexturePlugin::OnImage, this);
		gzmsg << "Subscribed topic: " << ok << std::endl;
	}
  
	void PostUpdate(const UpdateInfo &, const EntityComponentManager &) override
	{
	  if (this->latestPath.empty())
		return;

	  // força refresh do material via transport
	  gz::msgs::Material msg;
	  msg.set_script_uri(this->latestPath);

	  this->node.Request("/world/default/visual_config", msg);

	  this->latestPath.clear();
	}

private:
	bool toggle = false;

	void OnImage(const gz::msgs::Image &_msg)
	{
	  int w = _msg.width();
	  int h = _msg.height();

	  if (_msg.data().size() != w*h*3) {
		gzerr << "Invalid image size\n";
		return;
	  }

	  cv::Mat img(h, w, CV_8UC3, (void*)_msg.data().data());

	  std::string path = toggle ? "/ws/frame_a.png" : "/ws/frame_b.png";
	  toggle = !toggle;

	  if (!cv::imwrite(path, img)) {
		gzerr << "Failed to write image\n";
		return;
	  }

	  this->latestPath = path;
	}

private:
  transport::Node node;
};

GZ_ADD_PLUGIN(
  DynamicTexturePlugin,
  System,
  DynamicTexturePlugin::ISystemConfigure,
  DynamicTexturePlugin::ISystemPostUpdate
)
