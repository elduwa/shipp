from blinker import Namespace
from app.policy_engine.database_sync import sync_policies_to_pihole
from app.policy_engine.policy_engine import evaluate_monitoring_data

sigs = Namespace()

sync_policies_signal = sigs.signal("sync_policy_signal")

evaluate_monitoring_signal = sigs.signal("evaluate_monitoring_signal")

background_tasks = set()


@sync_policies_signal.connect
def on_sync_policies_signal(sender, **extra):
    sync_policies_to_pihole()


@evaluate_monitoring_signal.connect
def on_evaluate_monitoring_signal(sender, **extra):
    evaluate_monitoring_data(extra["dataset"])
