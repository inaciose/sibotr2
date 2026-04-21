#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Util.hh>
#include <gz/sim/components/Visual.hh>
#include <gz/sim/components/Name.hh>

#include <gz/rendering/RenderingIface.hh>
#include <gz/rendering/Scene.hh>
#include <gz/rendering/Visual.hh>
#include <gz/rendering/Material.hh>

#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/image.pb.h>

#include <opencv2/opencv.hpp>

#include <string>

namespace gz
{
namespace sim
{

class DynamicTexturePlugin :
  public System,
  public ISystemConfigure,
  public ISystemPostUpdate
{
private:
  std::string visualName;
  transport::Node node;

  rendering::ScenePtr scene;
  rendering::VisualPtr visual;

  std::string lastTexture;

public:

  void Configure(const Entity &,
                 const std::shared_ptr<const sdf::Element> &_sdf,
                 EntityComponentManager &,
                 EventManager &) override
  {
    this->visualName = _sdf->Get<std::string>("visual_name", "").first;

    std::string topic = "/image";
    if (_sdf->HasElement("topic"))
      topic = _sdf->Get<std::string>("topic");

    this->node.Subscribe(topic, &DynamicTexturePlugin::OnImage, this);
  }

  void PostUpdate(const UpdateInfo &,
                  const EntityComponentManager &_ecm) override
  {
    
    
	for (auto v : this->scene->Visuals())
	  std::cout << v->Name() << std::endl;
    
    
    if (!this->scene)
    {
      this->scene = rendering::sceneFromFirstRenderEngine();
      if (!this->scene)
        return;
    }

    if (!this->visual)
    {
      _ecm.Each<components::Visual, components::Name>(
        [&](const Entity &entity,
            const components::Visual *,
            const components::Name *name) -> bool
        {
          if (name->Data() == this->visualName)
          {
            this->visual = rendering::sceneFromFirstRenderEngine()
              ->VisualByName(this->visualName);
            return false;
          }
          return true;
        });
    }

    if (!this->visual || this->lastTexture.empty())
      return;

    // cria material novo (força reload)
    auto mat = this->scene->CreateMaterial();
    mat->SetTexture(this->lastTexture);

    this->visual->SetMaterial(mat);

    this->lastTexture.clear();
  }

  void OnImage(const msgs::Image &_msg)
  {
    int w = _msg.width();
    int h = _msg.height();

    cv::Mat img(h, w, CV_8UC3, (void*)_msg.data().data());

    static int counter = 0;
    std::string path = "/tmp/frame_" + std::to_string(counter++) + ".png";

    cv::imwrite(path, img);

    this->lastTexture = path;
  }
};

GZ_ADD_PLUGIN(
  DynamicTexturePlugin,
  System,
  DynamicTexturePlugin::ISystemConfigure,
  DynamicTexturePlugin::ISystemPostUpdate
)

}
}
