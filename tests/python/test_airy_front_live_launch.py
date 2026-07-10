from pathlib import Path

import yaml


ROOT = Path(__file__).parents[2]
LIO_CONFIG = ROOT / "config" / "rko_lio_airy_front.yaml"
RSLIDAR_CONFIG = ROOT / "config" / "rslidar_airy_front.yaml"
SCRIPT = ROOT / "scripts" / "run_airy_front_live.sh"


def test_airy_front_lio_config_does_not_embed_rslidar_sdk_config():
    config = yaml.safe_load(LIO_CONFIG.read_text())
    assert "rslidar_sdk" not in config
    assert config["imu_topic"] == "/imu/airy_front"
    assert config["lidar_topic"] == "/pointcloud/airy_front"
    assert config["base_frame"] == "front_lidar_link"


def test_rslidar_airy_front_config_contains_front_driver():
    sdk = yaml.safe_load(RSLIDAR_CONFIG.read_text())

    assert sdk["common"]["msg_source"] == 1
    assert sdk["common"]["send_point_cloud_ros"] is True
    assert sdk["common"]["send_packet_ros"] is False

    assert len(sdk["lidar"]) == 1
    front = sdk["lidar"][0]
    assert front["driver"]["lidar_type"] == "RSAIRY"
    assert front["driver"]["msop_port"] == 6701
    assert front["driver"]["difop_port"] == 7790
    assert front["driver"]["imu_port"] == 6690
    assert front["driver"]["use_lidar_clock"] is True
    assert front["driver"]["ts_first_point"] is True
    assert front["ros"]["ros_frame_id"] == "front_lidar_link"
    assert front["ros"]["ros_send_imu_data_topic"] == "/imu/airy_front"
    assert front["ros"]["ros_send_point_cloud_topic"] == "/pointcloud/airy_front"
    assert front["ros"]["ros_imu_ned_to_flu"] is False


def test_live_launch_script_uses_only_rko_lio_airy_front_config():
    text = SCRIPT.read_text()
    assert "config/rko_lio_airy_front.yaml" in text
    assert "config/rslidar_airy_front.yaml" in text
    assert "rslidar_multi.yaml" not in text
    assert "iRail-Rookie_Articulated" not in text
    assert "rslidar_sdk_node" in text
    assert "odometry.launch.py" in text
