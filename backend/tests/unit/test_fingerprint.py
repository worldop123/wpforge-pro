"""
指纹模块测试 - 音频、存储、性能、WebRTC、地理位置、传感器指纹伪造器
"""
import pytest

from app.services.proxy.fingerprint.audio_fingerprint import AudioFingerprint
from app.services.proxy.fingerprint.storage_fingerprint import StorageFingerprint
from app.services.proxy.fingerprint.performance_fingerprint import PerformanceFingerprint
from app.services.proxy.fingerprint.webrtc_fingerprint import WebRTCFingerprint
from app.services.proxy.fingerprint.geolocation_fingerprint import GeolocationFingerprint
from app.services.proxy.fingerprint.sensor_fingerprint import SensorFingerprint


# ==================== AudioFingerprint 测试 ====================

class TestAudioFingerprint:
    """音频指纹伪造器测试"""

    def test_creation(self):
        fp = AudioFingerprint()
        assert fp._sample_rate == 44100
        assert fp._base_latency == 0.01

    def test_generate_random_config(self):
        fp = AudioFingerprint()
        fp.generate_random_config()
        assert fp._sample_rate in AudioFingerprint.SAMPLE_RATES
        assert fp._base_latency in AudioFingerprint.BASE_LATENCIES

    def test_generate_random_config_with_seed(self):
        fp = AudioFingerprint()
        fp.generate_random_config(seed="test-seed")
        # 相同 seed 应产生相同结果
        fp2 = AudioFingerprint()
        fp2.generate_random_config(seed="test-seed")
        assert fp._sample_rate == fp2._sample_rate

    def test_set_config(self):
        fp = AudioFingerprint()
        fp.set_config(sample_rate=48000, base_latency=0.02,
                      output_latency=0.04, max_channels=6)
        assert fp._sample_rate == 48000
        assert fp._base_latency == 0.02
        assert fp._output_latency == 0.04
        assert fp._max_channels == 6

    def test_generate_fingerprint_hash(self):
        fp = AudioFingerprint()
        hash_val = fp.generate_fingerprint_hash()
        assert isinstance(hash_val, str)
        assert len(hash_val) == 64  # SHA-256

    def test_generate_fingerprint_hash_with_seed(self):
        fp = AudioFingerprint()
        h1 = fp.generate_fingerprint_hash(seed="abc")
        h2 = fp.generate_fingerprint_hash(seed="abc")
        assert h1 == h2

    def test_get_injection_script(self):
        fp = AudioFingerprint()
        script = fp.get_injection_script("somehash")
        assert isinstance(script, str)
        assert "AudioContext" in script
        assert "sampleRate" in script

    def test_get_audio_fingerprint_test_script(self):
        fp = AudioFingerprint()
        script = fp.get_audio_fingerprint_test_script()
        assert isinstance(script, str)
        assert "AudioContext" in script


# ==================== StorageFingerprint 测试 ====================

class TestStorageFingerprint:
    """存储指纹伪造器测试"""

    def test_creation(self):
        fp = StorageFingerprint()
        assert fp._local_storage_enabled is True
        assert fp._websql_enabled is False

    def test_generate_random_config(self):
        fp = StorageFingerprint()
        fp.generate_random_config()
        assert fp._local_storage_enabled is True
        assert fp._storage_quota in [2000000000, 5000000000, 10000000000]

    def test_generate_random_config_with_seed(self):
        fp = StorageFingerprint()
        fp.generate_random_config(seed="test")
        fp2 = StorageFingerprint()
        fp2.generate_random_config(seed="test")
        assert fp._storage_quota == fp2._storage_quota

    def test_set_config(self):
        fp = StorageFingerprint()
        fp.set_config(local_storage_enabled=False, cookie_enabled=False)
        assert fp._local_storage_enabled is False
        assert fp._cookie_enabled is False

    def test_get_injection_script(self):
        fp = StorageFingerprint()
        script = fp.get_injection_script()
        assert isinstance(script, str)
        assert "localStorage" in script

    def test_get_storage_test_script(self):
        fp = StorageFingerprint()
        script = fp.get_storage_test_script()
        assert isinstance(script, str)
        assert "localStorage_supported" in script


# ==================== PerformanceFingerprint 测试 ====================

class TestPerformanceFingerprint:
    """性能指纹伪造器测试"""

    def test_creation(self):
        fp = PerformanceFingerprint()
        assert fp._hardware_concurrency == 8
        assert fp._device_memory == 8

    def test_generate_random_config(self):
        fp = PerformanceFingerprint()
        fp.generate_random_config()
        assert fp._hardware_concurrency in [4, 6, 8, 12, 16]
        assert fp._memory_total > 0

    def test_generate_random_config_with_seed(self):
        fp = PerformanceFingerprint()
        fp.generate_random_config(seed="test")
        fp2 = PerformanceFingerprint()
        fp2.generate_random_config(seed="test")
        assert fp._hardware_concurrency == fp2._hardware_concurrency

    def test_match_device_memory(self):
        fp = PerformanceFingerprint()
        assert fp._match_device_memory(4) in [4, 8]
        assert fp._match_device_memory(8) in [8, 16]
        assert fp._match_device_memory(16) in [16, 32]
        assert fp._match_device_memory(32) in [32, 64]

    def test_set_config(self):
        fp = PerformanceFingerprint()
        fp.set_config(hardware_concurrency=12, device_memory=16)
        assert fp._hardware_concurrency == 12
        assert fp._device_memory == 16

    def test_get_injection_script(self):
        fp = PerformanceFingerprint()
        script = fp.get_injection_script()
        assert isinstance(script, str)
        assert "hardwareConcurrency" in script

    def test_get_performance_test_script(self):
        fp = PerformanceFingerprint()
        script = fp.get_performance_test_script()
        assert isinstance(script, str)
        assert "hardware_concurrency" in script


# ==================== WebRTCFingerprint 测试 ====================

class TestWebRTCFingerprint:
    """WebRTC 指纹伪造器测试"""

    def test_creation(self):
        fp = WebRTCFingerprint()
        assert fp._prevent_leak is True
        assert fp._camera_count == 1

    def test_generate_random_config_desktop(self):
        fp = WebRTCFingerprint()
        fp.generate_random_config(device_type="desktop")
        assert fp._camera_count in [0, 1, 2]

    def test_generate_random_config_mobile(self):
        fp = WebRTCFingerprint()
        fp.generate_random_config(device_type="mobile")
        assert fp._camera_count in [1, 2]
        assert fp._microphone_count in [1, 2]

    def test_generate_random_config_with_seed(self):
        fp = WebRTCFingerprint()
        fp.generate_random_config(seed="test")
        fp2 = WebRTCFingerprint()
        fp2.generate_random_config(seed="test")
        assert fp._camera_count == fp2._camera_count

    def test_set_config(self):
        fp = WebRTCFingerprint()
        fp.set_config(camera_count=2, microphone_count=3)
        assert fp._camera_count == 2
        assert fp._microphone_count == 3

    def test_get_injection_script(self):
        fp = WebRTCFingerprint()
        script = fp.get_injection_script()
        assert isinstance(script, str)
        assert "RTCPeerConnection" in script

    def test_get_webrtc_test_script(self):
        fp = WebRTCFingerprint()
        script = fp.get_webrtc_test_script()
        assert isinstance(script, str)
        assert "webrtc_supported" in script


# ==================== GeolocationFingerprint 测试 ====================

class TestGeolocationFingerprint:
    """地理位置指纹伪造器测试"""

    def test_creation(self):
        fp = GeolocationFingerprint()
        assert fp._latitude == 40.7128
        assert fp._city == "New York"
        assert fp._country == "US"

    def test_city_coords_available(self):
        assert "US" in GeolocationFingerprint.CITY_COORDS
        assert "CN" in GeolocationFingerprint.CITY_COORDS
        assert len(GeolocationFingerprint.CITY_COORDS["US"]) >= 5

    def test_generate_random_config(self):
        fp = GeolocationFingerprint()
        fp.generate_random_config(country="CN")
        assert fp._country == "CN"
        assert fp._city in [c[0] for c in GeolocationFingerprint.CITY_COORDS["CN"]]

    def test_generate_random_config_unknown_country(self):
        fp = GeolocationFingerprint()
        fp.generate_random_config(country="XX")
        # 未知国家回退到 US
        assert fp._city in [c[0] for c in GeolocationFingerprint.CITY_COORDS["US"]]

    def test_generate_random_config_with_seed(self):
        fp = GeolocationFingerprint()
        fp.generate_random_config(country="US", seed="test")
        fp2 = GeolocationFingerprint()
        fp2.generate_random_config(country="US", seed="test")
        assert fp._city == fp2._city

    def test_set_config(self):
        fp = GeolocationFingerprint()
        fp.set_config(latitude=35.0, longitude=120.0, accuracy=20.0,
                      city="Shanghai", country="CN")
        assert fp._latitude == 35.0
        assert fp._longitude == 120.0
        assert fp._city == "Shanghai"

    def test_get_injection_script(self):
        fp = GeolocationFingerprint()
        script = fp.get_injection_script()
        assert isinstance(script, str)
        assert "geolocation" in script
        assert "getCurrentPosition" in script

    def test_get_injection_script_with_altitude(self):
        fp = GeolocationFingerprint()
        fp._altitude = 100.0
        fp._altitude_accuracy = 10.0
        script = fp.get_injection_script()
        assert "100.0" in script

    def test_get_geolocation_test_script(self):
        fp = GeolocationFingerprint()
        script = fp.get_geolocation_test_script()
        assert isinstance(script, str)
        assert "getCurrentPosition" in script


# ==================== SensorFingerprint 测试 ====================

class TestSensorFingerprint:
    """传感器指纹伪造器测试"""

    def test_creation(self):
        fp = SensorFingerprint()
        assert fp._battery_enabled is False
        assert fp._network_type == "4g"
        assert fp._speech_synthesis_enabled is True

    def test_generate_random_config_desktop(self):
        fp = SensorFingerprint()
        fp.generate_random_config(device_type="desktop")
        assert fp._battery_enabled is False
        assert fp._network_type in ["wifi", "ethernet"]
        assert fp._accelerometer is False

    def test_generate_random_config_mobile(self):
        fp = SensorFingerprint()
        fp.generate_random_config(device_type="mobile")
        assert fp._battery_enabled is True
        assert fp._accelerometer is True
        assert fp._gyroscope is True
        assert fp._network_type in ["4g", "3g", "5g", "wifi"]

    def test_generate_random_config_mobile_charging(self):
        fp = SensorFingerprint()
        fp.generate_random_config(device_type="mobile", seed="charge")
        # 电池状态应被设置
        assert fp._battery_level > 0

    def test_generate_random_config_with_seed(self):
        fp = SensorFingerprint()
        fp.generate_random_config(device_type="desktop", seed="test")
        fp2 = SensorFingerprint()
        fp2.generate_random_config(device_type="desktop", seed="test")
        assert fp._bluetooth_enabled == fp2._bluetooth_enabled

    def test_set_config(self):
        fp = SensorFingerprint()
        fp.set_config(battery_enabled=True, network_type="5g")
        assert fp._battery_enabled is True
        assert fp._network_type == "5g"

    def test_get_injection_script(self):
        fp = SensorFingerprint()
        script = fp.get_injection_script()
        assert isinstance(script, str)
        assert "getBattery" in script or "batteryEnabled" in script

    def test_get_sensor_test_script(self):
        fp = SensorFingerprint()
        script = fp.get_sensor_test_script()
        assert isinstance(script, str)
        assert "battery_supported" in script
