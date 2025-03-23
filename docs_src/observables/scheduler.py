from esmerald.utils.decorators import observable


@observable(send=["daily_cleanup"])
async def trigger_cleanup():
    print("Daily cleanup event triggered!")


@observable(listen=["daily_cleanup"])
async def delete_old_records():
    print("Deleting old database records...")


@observable(listen=["daily_cleanup"])
async def clear_cache():
    print("Clearing application cache...")
