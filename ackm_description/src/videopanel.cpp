#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/int32.hpp"

#include <opencv2/highgui/highgui.hpp>
#include <ament_index_cpp/get_package_share_directory.hpp>

cv::Mat image[6];

int current = 3;
bool updated = false;

// --------------------------------------------------
// RESPAWN VIA CLI (ROBUSTO NO HARMONIC)
// --------------------------------------------------
void respawn_panel()
{
    system("gz service -s /world/default/remove --reqtype gz.msgs.Entity --reptype gz.msgs.Boolean --timeout 2000 --req 'name: \"videopanel\", type: MODEL'");
	usleep(500000);
    system("gz service -s /world/default/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 2000 --req 'sdf_filename: \"model://ackm_description/models/videopanel\", name: \"videopanel\", pose: {position: {x: 0, y: -1.55, z: 0.1}, orientation: {z: 0.7071068, w: 0.7071068}}'");
}

// --------------------------------------------------
void topic_callback(const std_msgs::msg::Int32::SharedPtr msg)
{
    if (msg->data >= 0 && msg->data <= 5)
    {
        current = msg->data;
        updated = true;
        std::cout << "NEW IMAGE: " << current << std::endl;
    }
}

// --------------------------------------------------
int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("videopanel");

    // PARAMETERS
    node->declare_parameter("source_package", "ackm_description");
    node->declare_parameter("source_folder", "models/videopanel/images");

    node->declare_parameter("name_pic0", "left");
    node->declare_parameter("name_pic1", "right");
    node->declare_parameter("name_pic2", "up");
    node->declare_parameter("name_pic3", "stop");
    node->declare_parameter("name_pic4", "parking");
    node->declare_parameter("name_pic5", "chess");

    node->declare_parameter("default_pic", 3);

    std::string source_package = node->get_parameter("source_package").as_string();
    std::string source_folder  = node->get_parameter("source_folder").as_string();

    std::string name_pic0 = node->get_parameter("name_pic0").as_string();
    std::string name_pic1 = node->get_parameter("name_pic1").as_string();
    std::string name_pic2 = node->get_parameter("name_pic2").as_string();
    std::string name_pic3 = node->get_parameter("name_pic3").as_string();
    std::string name_pic4 = node->get_parameter("name_pic4").as_string();
    std::string name_pic5 = node->get_parameter("name_pic5").as_string();

    current = node->get_parameter("default_pic").as_int();

    // PATHS
    std::string path = ament_index_cpp::get_package_share_directory(source_package);
    std::string tex_path = path + "/models/videopanel/materials/textures/";

    std::cout << "PACKAGE: " << path << std::endl;
    std::cout << "TEXTURES: " << tex_path << std::endl;

    // LOAD IMAGES
    image[0] = cv::imread(path + "/" + source_folder + "/" + name_pic0 + ".png");
    image[1] = cv::imread(path + "/" + source_folder + "/" + name_pic1 + ".png");
    image[2] = cv::imread(path + "/" + source_folder + "/" + name_pic2 + ".png");
    image[3] = cv::imread(path + "/" + source_folder + "/" + name_pic3 + ".png");
    image[4] = cv::imread(path + "/" + source_folder + "/" + name_pic4 + ".png");
    image[5] = cv::imread(path + "/" + source_folder + "/" + name_pic5 + ".png");

    for (int i = 0; i < 6; i++)
    {
        if (image[i].empty())
        {
            std::cout << "ERROR loading image " << i << std::endl;
            return 0;
        }
    }

    // WRITE DEFAULT
    cv::imwrite(tex_path + "screen1.png", image[current]);
    cv::imwrite(tex_path + "screen2.png", image[current]);

    system("sync");
    respawn_panel();

    // SUBSCRIBER
    auto sub = node->create_subscription<std_msgs::msg::Int32>(
        "/videopanel/select", 10, topic_callback);

    rclcpp::Rate loop_rate(10);

    while (rclcpp::ok())
    {
        if (updated)
        {
            bool ok1 = cv::imwrite(tex_path + "screen1.png", image[current]);
            bool ok2 = cv::imwrite(tex_path + "screen2.png", image[current]);

            std::cout << "WRITE: " << current << " " << ok1 << " " << ok2 << std::endl;

            system("sync");
            respawn_panel();

            updated = false;
        }

        rclcpp::spin_some(node);
        loop_rate.sleep();
    }

    rclcpp::shutdown();
    return 0;
}
