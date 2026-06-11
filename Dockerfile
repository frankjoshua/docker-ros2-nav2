FROM frankjoshua/ros2:humble

USER root
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
   && apt-get -y install --no-install-recommends ros-$ROS_DISTRO-navigation2 ros-$ROS_DISTRO-nav2-* \
   #
   # Clean up
   && apt-get autoremove -y \
   && apt-get clean -y \
   && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

# Run nav2 composed: all nodes in one process / one DDS participant. Separate-process
# bringup balloons memory on a busy graph (each participant builds full discovery state)
# and OOM-kills inside a memory-limited container; composition pays that cost once and
# keeps startup memory low. See nav2_composed.launch.py.
COPY nav2_composed.launch.py /root/nav2_composed.launch.py
CMD ["/bin/bash", "-i", "-c", "ros2 launch /root/nav2_composed.launch.py"]