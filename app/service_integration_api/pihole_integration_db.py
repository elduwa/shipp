from app.extensions import db
from app.models import Group, DomainList, Client
from app.models import Device, DeviceConfig


def init_pihole_device(device: Device) -> Group:
    """Create a pihole client and group for a device"""
    device_config = device.get_current_config()
    if device_config is None:
        raise Exception(f"Device {device.device_name} has no current config")
    client = Client(ip=device_config.ip_address)
    group = Group(name=device.mac_address, description=device.device_name)
    group.clients.append(client)
    db.session.add(group)
    db.session.commit()
    return group


def _is_device_initialized(device: Device) -> bool:
    """Check if a pihole client and group for a device exists"""
    mac_address = device.mac_address
    ip = device.get_current_config().ip_address
    group = db.session.execute(db.select(Group).where(Group.name == mac_address)).scalars().first()
    client = db.session.execute(
        db.select(Client).where(Client.ip == ip)).scalars().first()
    if client is not None and group is not None:
        return client in group.clients
    else:
        return False


def update_pihole_device(updated_device: Device, old_config: DeviceConfig):
    """Update a pihole client and group for a device"""
    if not _is_device_initialized(updated_device):
        init_pihole_device(updated_device)
    else:
        group = db.session.execute(db.select(Group).where(Group.name == updated_device.mac_address)).scalars().one_or_none()
        client = db.session.execute(db.select(Client).where(Client.ip == old_config.ip_address)).scalars().one_or_none()
        # db.session.delete(old_client)
        # db.session.flush()
        group.name = updated_device.mac_address
        group.description = updated_device.device_name
        client.ip = updated_device.get_current_config().ip_address
        db.session.add_all([group, client])
        db.session.commit()


def delete_pihole_device(device: Device):
    """Delete a pihole client and group for a device"""
    group = db.session.execute(db.select(Group).where(Group.name == device.mac_address)).scalars().one_or_none()
    client = db.session.execute(
        db.select(Client).where(Client.ip == device.get_current_config().ip_address)).scalars().one_or_none()
    db.session.delete(group)
    db.session.flush()
    db.session.delete(client)
    db.session.commit()


def block_domain(device: Device, domain_name: str):
    """Block a domain for a device"""
    domain = DomainList(type=1, domain=domain_name)
    _add_domain_to_device_group(device, domain)


def whitelist_domain(device: Device, domain_name: str):
    """Allow a domain for a device"""
    domain = DomainList(type=0, domain=domain_name)
    _add_domain_to_device_group(device, domain)


def _add_domain_to_device_group(device: Device, domain: DomainList):
    """Add a domain to a pihole group"""
    if not _is_device_initialized(device):
        init_pihole_device(device)
    group = db.session.execute(db.select(Group).where(Group.name == device.mac_address)).scalars().one_or_none()
    group.domains.append(domain)
    db.session.add(group)
    db.session.commit()
