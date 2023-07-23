from app.extensions import db
from app.models import Device, DeviceConfig, Policy
from app.constants import PolicyType, DefaultPolicyValues
from flask import current_app
from sqlalchemy.orm import close_all_sessions
from app.policy_engine.database_sync import sync_policies_to_pihole


def evaluate_monitoring_data(dataset: list):
    current_app.logger.info("Evaluating monitoring data")
    device_to_domains = transform_dataset(dataset)
    device_ips = device_to_domains.keys()
    bulk_insert_rows = dict()
    for device_ip in device_ips:
        device_id, rows = evaluate_device_policies(device_ip, device_to_domains[device_ip])
        if device_id is not None and rows is not None and len(rows) > 0:
            bulk_insert_rows[device_id] = rows
    insert_policy_rows(bulk_insert_rows)
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
            insert_rows = []
            for domain in new_domains:
                row = dict()
                if default_policy == DefaultPolicyValues.ALLOW_ALL.value:
                    row["policy_type"] = PolicyType.ALLOW.value
                elif default_policy == DefaultPolicyValues.BLOCK_ALL.value:
                    row["policy_type"] = PolicyType.BLOCK.value
                row["item"] = domain
                insert_rows.append(row)
            return device.id, insert_rows
    except Exception as e:
        current_app.logger.error(f"Error while evaluating device policies: {e}")
        return None, None


def insert_policy_rows(bulk_insert_rows: dict):
    for device_id in bulk_insert_rows.keys():
        close_all_sessions()
        rows = bulk_insert_rows[device_id]
        try:
            device = db.session.execute(db.select(Device).where(Device.id == device_id)).scalars().one()
            new_policies = db.session.scalars(db.insert(Policy).returning(Policy), rows).all()
            #db.session.flush()
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
