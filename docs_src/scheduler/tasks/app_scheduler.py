from esmerald import Esmerald

app = Esmerald(
    routes=[...],
    enable_scheduler=True,
    scheduler_tasks={
        "collect_market_data": "accounts.tasks",
        "send_newsletter": "accounts.tasks",
    },
)
