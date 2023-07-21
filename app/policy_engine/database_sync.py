from app.models import Group, Device, DomainList
from app.extensions import db
from app.constants import PolicyType
from flask import current_app


def sync_policies_to_pihole():
    devices = db.session.execute(db.select(Device)).scalars().all()
    db.session.commit()
    for device in devices:
        sync_device_policies(device)


def sync_device_policies(device):
    try:
        policies = device.policies
        db.session.commit()
        pi_group = db.session.execute(db.select(Group).where(Group.name == Device.mac_address)).scalars().one()
        pi_domains = pi_group.domains
        max_date_modified = max(pi_domains, key=lambda domain: domain.date_modified).date_modified
        db.session.commit()
        newer_policies = [policy for policy in policies if policy.date_modified > max_date_modified]
        new_pi_domains = []
        for policy in newer_policies:
            type = None
            if policy.policy_type == PolicyType.DEFAULT.value:
                continue
            elif policy.policy_type == PolicyType.BLOCK.value:
                type = 1
            elif policy.policy_type == PolicyType.ALLOW.value:
                type = 0
            domain = policy.item
            new_pi_domains.append(DomainList(type=type, domain=domain))
        if len(new_pi_domains) > 0:
            pi_group.domains.extend(new_pi_domains)
            db.session.add(pi_group)
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error while syncing device {device.id}'s policies to pihole: {e}")
        db.session.rollback()

