import boto3
import json
import logging
import sys
sys.path.append('./skill/ask-sdk')
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.slu.entityresolution import status_code

sb = SkillBuilder()
client = boto3.client('lambda')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


def getKakugen(code):
    if not code:
        raise Exception('BAD CODE')

    # logger.debug(str(code))
    request = {
        'FunctionName': 'ShogiKakugenAPI',
        'InvocationType': 'RequestResponse',
        'LogType': 'None',
        'Payload': json.dumps({'id': code['id'], 'type': code['type']})
    }
    logger.info('request -> ' + str(request))

    try:
        response = client.invoke(**request)
        logger.debug('response -> ' + str(response))
    except Exception:
        raise Exception('FAILD REQUEST')

    kakugen = None

    if response.get('FunctionError'):
        raise Exception('ERROR!' + response['FunctionError'])
    else:
        kakugen = json.loads(response['Payload'].read().decode('unicode-escape'))

    return kakugen


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.object_type == "LaunchRequest"

    def handle(self, handler_input):
        speech_text = "ようこそ、将棋の格言へ。格言を教えて、と言ってみてください。"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("将棋の格言", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class AskIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AskIntent")

    def handle(self, handler_input):
        if not handler_input.request_envelope.session.attributes:
            handler_input.request_envelope.session.attributes = {'id': []}
        session = handler_input.request_envelope.session.attributes
        sessionid = session.get('id', 'ERROR')
        # logger.info('session -> ' + str(session))
        logger.info('sessionid -> ' + str(sessionid))
        code = {'id': sessionid, 'type': None}
        kakugen = getKakugen(code)

        title = '将棋の格言'
        id = kakugen['ID']
        text = kakugen['PHRASE']
        speak = kakugen['SPEAK']
        reprompt = "他の格言も聞きますか？"
        sessionid.append(id)

        logger.info('=======RESPONSE VALUE=======')
        logger.info('id:   ' + str(id))
        logger.info('text: ' + str(text))
        logger.info('speak:' + str(speak))
        handler_input.attributes_manager.session_attributes['id'] = sessionid
        handler_input.attributes_manager.session_attributes['type'] = None
        handler_input.response_builder.speak(speak).set_card(
            SimpleCard(title, text)).ask(reprompt)
        logger.info(handler_input.request_envelope.session.attributes)
        return handler_input.response_builder.response


class AskTypeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AskTypeIntent")

    def handle(self, handler_input):
        if not handler_input.request_envelope.session.attributes:
            handler_input.request_envelope.session.attributes = {'id': []}
        session = handler_input.request_envelope.session.attributes
        sessionid = session.get('id', 'ERROR')
        logger.info('sessionid -> ' + str(sessionid))
        request = handler_input.request_envelope.request
        # logger.debug(request)
        slot = request.intent.slots['Type']
        # logger.debug(slot.resolutions.resolutions_per_authority[0].status.code)
        resolution = slot.resolutions.resolutions_per_authority[0] if slot.resolutions.resolutions_per_authority[0].status.code == status_code.StatusCode.ER_SUCCESS_MATCH else None
        # logger.debug(resolution)
        code = {'id': sessionid, 'type': resolution.values[0].value.id}
        kakugen = getKakugen(code)
        title = '将棋の格言'
        id = kakugen['ID']
        text = kakugen['PHRASE']
        speak = kakugen['SPEAK']
        reprompt = "他の格言も聞きますか？"
        sessionid.append(id)

        logger.info('=======RESPONSE VALUE=======')
        logger.info('id:   ' + str(id))
        logger.info('text: ' + str(text))
        logger.info('speak:' + str(speak))
        handler_input.attributes_manager.session_attributes['id'] = sessionid
        handler_input.attributes_manager.session_attributes['type']
        handler_input.response_builder.speak(speak).set_card(
            SimpleCard(title, text)).ask(reprompt)
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AMAZON.YesIntent")

    def handle(self, handler_input):
        speak = "てすと"
        handler_input.response_builder.speak(speak).set_card(
            SimpleCard(speak,speak))
        return handler_input.response_builder.response


class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AMAZON.NoIntent")

    def handle(self, handler_input):
        speak = "てすと"
        handler_input.response_builder.speak(speak).set_card(
            SimpleCard(speak, speak))
        return handler_input.response_builder.response



class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and handler_input.request_envelope.request.intent.name == "AMAZON.HelpIntent")

    def handle(self, handler_input):
        speech_text = "将棋の格言をお伝えします。例えば、「将棋の格言を教えて」と、言ってみてください。\
        他にも、「玉の格言を教えて」や、「寄せの格言を教えて」等にも、お答えします。"

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
            SimpleCard("使い方", speech_text))
        return handler_input.response_builder.response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (handler_input.request_envelope.request.object_type == "IntentRequest"
                and (handler_input.request_envelope.request.intent.name == "AMAZON.CancelIntent"
                     or handler_input.request_envelope.request.intent.name == "AMAZON.StopIntent"))

    def handle(self, handler_input):
        speech_text = "あ、負けました。"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(speech_text, speech_text))
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.object_type == "SessionEndedRequest"

    def handle(self, handler_input):
        return handler_input.response_builder.response


class AllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(exception)

        speech = "例えば、格言を教えて、と言ってみてください。"
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response


sb.request_handlers.extend([
    LaunchRequestHandler(),
    YesIntentHandler(),
    NoIntentHandler(),
    AskIntentHandler(),
    AskTypeIntentHandler(),
    HelpIntentHandler(),
    CancelAndStopIntentHandler(),
    SessionEndedRequestHandler()])

sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()
