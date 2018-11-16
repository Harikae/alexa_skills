import json
import random
import logging
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


def lambda_handler(event, context):
    if not event:
        raise Exception('BAD_REQUEST_EVENT: event -> ' + str(event))
    logger.info('code  -> ' + str(event))

    id = event['id']
    type = event['type']

    with open('./resources/kakugens.json', 'r')as f:
        kakugens = json.load(f)
        if type:
            kakugens = [kakugen for kakugen in kakugens if type in kakugen['TYPE']]

    kakugen = None
    id_list = [kakugen["ID"] for kakugen in kakugens]
    logger.debug(id_list)

    if not id:
        newID = random.choice(id_list)
    else:
        logger.debug(list(set(range(1, len(kakugens))) ^ set(id)))
        newID = random.choice(list(set(id_list) ^ set(id)))
    
    kakugen = [
        kakugen for kakugen in kakugens if kakugen.get('ID') == newID][0]
    logger.info('output -> ' + str(kakugen))

    return kakugen
