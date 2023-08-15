from app.extensions import db
from app.models import Device, DeviceConfig, Policy
from app.constants import PolicyType, DefaultPolicyValues
from flask import current_app
from app.policy_engine.database_sync import sync_policies_to_pihole


def evaluate_monitoring_data(dataset: list):
    current_app.logger.info("Evaluating monitoring data")
    device_to_domains = transform_dataset(dataset)
    device_ips = device_to_domains.keys()
    for device_ip in device_ips:
        device, new_policies = evaluate_device_policies(device_ip, device_to_domains[device_ip])
        if device is not None and new_policies is not None and len(new_policies) > 0:
            insert_policy_rows(device, new_policies)
    with current_app.app_context():
        sync_policies_to_pihole()


def evaluate_device_policies(device_ip: str, domains: set) -> (int, list):
    try:
        device = db.session.execute(db.select(Device).join(Device.device_configs).where(
            DeviceConfig.ip_address == device_ip and DeviceConfig.valid_to == None)).scalars().one_or_none() # noqa E711
        if device is None:
            raise Exception(f"Device with ip {device_ip} not found")
        device_policies = device.policies
        default_policy = None
        new_domains = domains.copy()
        for policy in device_policies:
            if policy.policy_type == PolicyType.DEFAULT_POLICY.value:
                default_policy = policy.item
            elif policy.policy_type == PolicyType.ALLOW.value or policy.policy_type == PolicyType.BLOCK.value:
                if policy.item in domains:
                    new_domains.remove(policy.item)
        if default_policy is None:
            raise Exception(f"Default policy for device {device_ip} not found")
        else:
            insert_policies = []
            for domain in new_domains:
                policy_type = None
                if default_policy == DefaultPolicyValues.ALLOW_ALL.value:
                    policy_type = PolicyType.ALLOW.value
                elif default_policy == DefaultPolicyValues.BLOCK_ALL.value:
                    policy_type = PolicyType.BLOCK.value
                item = domain
                insert_policies.append(Policy(policy_type=policy_type, item=item))
            return device, insert_policies
    except Exception as e:
        current_app.logger.error(f"Error while evaluating device policies: {e}")
        return None, None


def insert_policy_rows(device, new_policies):
    try:
        device.policies.extend(new_policies)
        db.session.add(device)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error while inserting policy rows: {e}")
        db.session.rollback()


def transform_dataset(dataset: list):
    client_to_domains = dict()
    for datapoint in dataset:
        client = datapoint[1]
        domain = datapoint[3]
        if client not in client_to_domains:
            client_to_domains[client] = set()
        client_to_domains[client].add(domain)
    return client_to_domains
