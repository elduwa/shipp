from app.models import Group, Device, Domainlist
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
        pi_group = db.session.execute(db.select(Group).where(Group.name == device.mac_address)).scalars().one()
        pi_domains = pi_group.domains.all()
        pi_domain_map = dict()
        policy_type_to_pi_type = {PolicyType.ALLOW.value: 0, PolicyType.BLOCK.value: 1}
        for pi_domain in pi_domains:
            pi_domain_map[pi_domain.domain] = (pi_domain.id, pi_domain.type)
        max_date_modified = 0
        if len(pi_domains) > 0:
            max_date_modified = max(pi_domains, key=lambda domain: domain.date_modified).date_modified
        db.session.commit()
        newer_policies = {policy for policy in policies if policy.date_modified > max_date_modified}
        brand_new_policies = set()
        update_policies = set()
        for policy in newer_policies:
            if policy.policy_type == PolicyType.DEFAULT_POLICY.value:
                continue
            elif policy.item in pi_domain_map:
                if policy_type_to_pi_type[policy.policy_type] != pi_domain_map[policy.item][1]:
                    update_policies.add(policy)
            else:
                brand_new_policies.add(policy)

        new_pi_domains = []

        for policy in brand_new_policies:
            type = policy_type_to_pi_type[policy.policy_type]
            domain = policy.item
            new_pi_domains.append(Domainlist(type=type, domain=domain))

        if len(new_pi_domains) > 0:
            pi_group.domains.extend(new_pi_domains)
            db.session.add(pi_group)
            db.session.flush()

        if len(update_policies):
            update_pi_domains = []
            for policy in update_policies:
                id = pi_domain_map[policy.item][0]
                pi_domain = pi_group.domains.filter_by(id=id).one()
                pi_domain.type = policy_type_to_pi_type[policy.policy_type]
                update_pi_domains.append(pi_domain)
            db.session.add_all(update_pi_domains)

        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error while syncing device {device.id}'s policies to pihole: {e}")
        db.session.rollback()
