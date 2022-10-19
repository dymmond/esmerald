from esmerald import Esmerald

app = Esmerald(
    routes=[...],
    enable_scheduler=True,
    scheduler_tasks={
        "collect_market_data": "accounts.tasks",
        "send_email_newsletter": "accounts.tasks",
    },
)
