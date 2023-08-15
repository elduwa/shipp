from datetime import datetime
from uuid import UUID

def test_device_create(app):
    with app.app_context():
        from app.models import Device
        # Create a device and save it to the database
        device = Device(mac_address="00:11:22:33:44:55", device_name="Test Device")
        device.insert_device()

        # Retrieve the device from the database and check if it matches the created one
        retrieved_device = Device.query.filter_by(mac_address="00:11:22:33:44:55").first()
        assert retrieved_device is not None
        assert retrieved_device.device_name == "Test Device"


def test_device_get_current_config(app):
    with app.app_context():
        from app.models import Device, DeviceConfig
        # Create a device and its configurations
        device = Device(mac_address="11:22:33:44:55:66")
        device.insert_device()

        config1 = DeviceConfig(device_id=device.id, ip_address="192.168.1.100", valid_to=datetime.now())
        config1.insert_device_config()

        config2 = DeviceConfig(device_id=device.id, ip_address="192.168.1.101")
        config2.insert_device_config()

        assert device.get_current_config() == config2


def test_device_delete(app):
    with app.app_context():
        from app.models import Device, DeviceConfig, Policy
        # Create a device and save it to the database
        device = Device(mac_address="AA:BB:CC:DD:EE:FF")
        device.insert_device()

        # Create and associate device configurations with the device
        config1 = DeviceConfig(device_id=device.id, ip_address="192.168.1.100")
        config2 = DeviceConfig(device_id=device.id, ip_address="192.168.1.101")
        config1.insert_device_config()
        config2.insert_device_config()

        # Create and associate policies with the device
        policy1 = Policy(device_id=device.id, policy_type=UUID("cb40c57d-dc14-4140-977c-3f033751b035"), item="item1", active=True)
        policy2 = Policy(device_id=device.id, policy_type=UUID("23a0a231-d24e-48ab-9421-ae9f9b0b3f70"), item="item2", active=True)
        policy1.insert_policy()
        policy2.insert_policy()

        # Delete the device and check if it's deleted from the database
        device.delete_device()
        assert Device.query.filter_by(mac_address="AA:BB:CC:DD:EE:FF").first() is None

        # Check if associated DeviceConfig and Policy objects are also deleted
        assert DeviceConfig.query.filter_by(device_id=device.id).count() == 0
        assert Policy.query.filter_by(device_id=device.id).count() == 0
