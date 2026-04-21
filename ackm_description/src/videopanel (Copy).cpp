#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/int32.hpp"

#include <opencv2/highgui/highgui.hpp>
#include <ament_index_cpp/get_package_share_directory.hpp>

#include <termios.h>
#include <unistd.h>
#include <fstream>

cv::Mat image[6];

int getch()
{
  struct termios oldt, newt;
  tcgetattr(STDIN_FILENO, &oldt);

  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);
  newt.c_cc[VMIN] = 1;
  newt.c_cc[VTIME] = 0;

  tcsetattr(STDIN_FILENO, TCSANOW, &newt);

  int c = getchar();

  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
  return c;
}

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("videopanel");

    // parameters
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
    std::string source_folder = node->get_parameter("source_folder").as_string();

    std::string name_pic0 = node->get_parameter("name_pic0").as_string();
    std::string name_pic1 = node->get_parameter("name_pic1").as_string();
    std::string name_pic2 = node->get_parameter("name_pic2").as_string();
    std::string name_pic3 = node->get_parameter("name_pic3").as_string();
    std::string name_pic4 = node->get_parameter("name_pic4").as_string();
    std::string name_pic5 = node->get_parameter("name_pic5").as_string();

    int current = node->get_parameter("default_pic").as_int();
    bool dirty = true;

    // path
    std::string path = ament_index_cpp::get_package_share_directory(source_package);
    std::string tex_path = path + "/models/videopanel/materials/textures/";

    std::cout << "PATH: " << path << std::endl;
    std::cout << "TEX: " << tex_path << std::endl;

    // load images
    image[0] = cv::imread(path + "/" + source_folder + "/" + name_pic0 + ".png");
    image[1] = cv::imread(path + "/" + source_folder + "/" + name_pic1 + ".png");
    image[2] = cv::imread(path + "/" + source_folder + "/" + name_pic2 + ".png");
    image[3] = cv::imread(path + "/" + source_folder + "/" + name_pic3 + ".png");
    image[4] = cv::imread(path + "/" + source_folder + "/" + name_pic4 + ".png");
    image[5] = cv::imread(path + "/" + source_folder + "/" + name_pic5 + ".png");

    for (int i = 0; i < 6; i++) {
        if (image[i].empty()) {
            std::cout << "Error loading image " << i << std::endl;
            return 0;
        }
    }

    // subscriber
    auto sub = node->create_subscription<std_msgs::msg::Int32>(
        "/videopanel/cmd", 10,
        [&](const std_msgs::msg::Int32::SharedPtr msg)
        {
            if (msg->data >= 0 && msg->data < 6) {
                current = msg->data;
                dirty = true;
                std::cout << "TOPIC -> " << current << std::endl;
            }
        });

    rclcpp::Rate loop_rate(10);

    while (rclcpp::ok()) {

        // teclado (continua funcional)
        int opt = -1;
        if (isatty(STDIN_FILENO)) {
            opt = getch();
        }

        if (opt == 27) exit(0);

        switch (opt) {
            case '0': current = 0; dirty = true; break;
            case '1': current = 1; dirty = true; break;
            case '2': current = 2; dirty = true; break;
            case '3': current = 3; dirty = true; break;
            case '4': current = 4; dirty = true; break;
            case '5': current = 5; dirty = true; break;
            default: break;
        }

        // escrita só quando muda
        if (dirty) {
            bool ok1 = cv::imwrite(tex_path + "screen1.png", image[current]);
            bool ok2 = cv::imwrite(tex_path + "screen2.png", image[current]);

            std::cout << "WRITE: " << current << " " << ok1 << " " << ok2 << std::endl;
            system("sync");

            dirty = false;
        }

        rclcpp::spin_some(node);
        loop_rate.sleep();
    }

    rclcpp::shutdown();
    return 0;
}
