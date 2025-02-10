FROM frankjoshua/ros2

USER root
ENV DEBIAN_FRONTEND=noninteractive

# Install Navigation2 and development libraries
RUN apt-get update \
   && apt-get -y install --no-install-recommends \
      ros-$ROS_DISTRO-navigation2 \
      ros-$ROS_DISTRO-nav2-bringup \
      ros-$ROS_DISTRO-nav2-simple-commander \
      python3-colcon-common-extensions \
      python3-pip \
   #
   # Clean up
   && apt-get autoremove -y \
   && apt-get clean -y \
   && rm -rf /var/lib/apt/lists/*


ENV DEBIAN_FRONTEND=dialog

CMD ["/bin/bash", "-i", "-c", "ros2 launch nav2_bringup navigation_launch.py"]
