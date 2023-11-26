import sys
import traceback


def handle_exception(loop, context):
    exception = context.get("exception")
    if exception:
        print("Caught exception: ", exception, file=sys.stderr)
        traceback.print_tb(exception.__traceback__, file=sys.stderr)
    else:
        loop.default_exception_handler(context)
