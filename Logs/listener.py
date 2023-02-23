import multiprocessing, logging, logging.handlers


def listener_configurer():
    logger = logging.getLogger()
    logger.setLevel( logging.DEBUG )
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(processName)s %(funcName)s: %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S',)
    handler = logging.FileHandler('//var/log/email-preprocessing', mode='w')
    handler.setFormatter( formatter )
    logger.addHandler(handler)
    logger.info("Parsing Process Beginning")



def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)  # No level or filter logic applied - just do it!
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.DEBUG)