import time
from typing import Optional

import typer

from gdshoplib.packages.feed import Feed

app = typer.Typer()


@app.command()
def warm(platform_key=None, loop_iteration: Optional[int] = typer.Option(None)):
    while True:
        if platform_key:
            warm_platfrom_feed(platform_key)
            return

        for platform in [Feed, *[feed for feed in Feed.__subclasses__()]]:
            warm_platfrom_feed(platform.KEY)

        if loop_iteration:
            time.sleep(loop_iteration)
        else:
            break


###


def warm_platfrom_feed(key):
    platform = Feed.get_platform_class(key=key)
    platform().push_feed()
    print(platform)
