import logging


__all__ = ['logger', 'task_logger']

if 'alphafed' in logging.Logger.manager.loggerDict.keys():
    logger = logging.getLogger('alphafed')

else:
    format = '%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|%(lineno)d:\n%(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        filename='alphafed.log',
                        filemode='w',
                        format=format)
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format))
    logger.addHandler(console_handler)

if 'task' in logging.Logger.manager.loggerDict.keys():
    task_logger = logging.getLogger('task')
else:
    task_logger = logger
