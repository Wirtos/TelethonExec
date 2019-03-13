import re
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename
from telethon.errors import MessageIdInvalidError
import time
import traceback
from rprintlib import rprint
import html
import sys
import asyncio
import logging

api_id = 1111
api_hash = 'os3294rawr.__owo'

exec_name = 'Exec'
exec_cmd = '!exc'
message_match = f'^{exec_name}\s?(.*){{:|^{exec_cmd}'

re_one = re.compile(f'^{exec_cmd}\s?(.*?)?\s?\n(.*)',
                      flags=re.MULTILINE | re.DOTALL)
re_two = re.compile(f'^{exec_name}\s?(.*?){{:\n(.*?)(Result|Processing...){{',
                      flags=re.MULTILINE | re.DOTALL)

client = TelegramClient('tl-exec', api_hash=api_hash, api_id=api_id)


async def asyncexec(event, code):
    on_time = 'async def __exec(event, client):' + ''.join(
        '\n {}'.format(l) for l in code.splitlines())
    exec(on_time)
    return await locals()['__exec'](event, client)


@client.on(events.NewMessage(
    pattern=message_match,
    outgoing=True))
@client.on(
    events.MessageEdited(
        pattern=message_match,
        outgoing=True))
async def exc_handler(event: events.NewMessage.Event):
    arguments_state = {
        'r': None,  # restart script one more time
        't': None,  # show execution time
        'd': None,  # delete message after executing script
    }
    case_one = re_one.findall(event.raw_text)
    case_two = re_two.findall(event.raw_text)
    if case_one:
        case_one = case_one[0]
        exec_input = case_one[1].strip()
        arguments = case_one[0]
    else:
        case_two = case_two[0]
        exec_input = case_two[1].strip()
        arguments = case_two[0]
    if arguments:
        for i in arguments.split('-'):
            arguments_state[i] = True if i else None
    try:
        await event.edit(f'<b>{exec_name}{{:</b>\n<pre>{exec_input}</pre>\n<b>Processing...{{</b>', parse_mode='html')
    except MessageIdInvalidError:
        pass
    st = time.process_time()
    try:
        result = await asyncexec(event, exec_input)
        rprint_res = str(rprint)
        if result is None and not rprint_res:
            result = 'Success'
        elif rprint_res and result is not None:
            result = f"{rprint_res}\n{result}"
        elif rprint_res:
            result = rprint_res
        elif result:
            result = str(result)
        elif rprint_res:
            result = rprint_res

        if arguments_state['d']:
            await event.delete()
            return

    except SyntaxError as err:
        rprint_res = str(rprint)
        error_class = err.__class__.__name__
        try:
            detail = err.args[0]
        except IndexError:
            detail = ''
        line_number = err.lineno
        if rprint_res:
            result = rprint_res
        else:
            result = ''
        result += f"{error_class} at line {line_number - 1 if err.lineno else '<unknown>'} of <string>: {detail}"
        rprint.flush()

    except Exception as err:
        rprint_res = str(rprint)
        error_class = err.__class__.__name__
        try:
            detail = err.args[0]
        except IndexError:
            detail = ''
        cl, exc, tb = sys.exc_info()
        trbk = traceback.extract_tb(tb)
        tr = {}
        for i in trbk:
            tr[i.name] = i
        trbk_res = tr.get('__exec')
        line_number = trbk_res[1] if trbk_res else None
        if rprint_res:
            result = rprint_res
        else:
            result = ''
        result += f"{error_class} at line {line_number - 1 if line_number else '<unknown>'} of <string>: {detail}"
        rprint.flush()

    en = time.process_time()
    tm = en - st
    result = html.escape(result)
    text = '<b>{exec_name}{{:</b>\n<pre>{input}</pre>\n<b>{time}</b>\n<pre>{res}</pre>'.format(
        exec_name=exec_name,
        time="Result{{ in {}".format(tm) if arguments_state.get('t') else 'Result{{:',
        input=exec_input,
        res=result)
    try:
        if len(text) > 4096:
            raise ValueError
        else:
            try:
                await event.edit(text, parse_mode='html')
            except MessageIdInvalidError:
                text = '<b>{exec_name}{{:</b>\n<pre>{input}</pre>\n<b>{time}</b>\n<pre>{res}</pre>'.format(
                    exec_name=exec_name,
                    time="Result{{ MD in {}:".format(tm) if arguments_state.get('t') else 'Result{ MD:',
                    input=exec_input,
                    res=result)
                if len(text) > 4096:
                    raise ValueError
                await event.reply(text, parse_mode='html')

    except ValueError:
        attrs = [DocumentAttributeFilename('exec.html')]
        await client.send_file(await event.get_input_chat(), text.encode(), attributes=attrs)
        text = '<b>{exec_name}{{:</b>\n<pre>{input}</pre>\n<b>{time}</b>\n<pre>{res}</pre>'.format(
            exec_name=exec_name,
            time="Result{{ in {}:".format(tm) if arguments_state.get('t') else 'Result{:',
            input=exec_input,
            res=html.escape('<exec.html>'))
        try:
            await event.edit(text, parse_mode='html')
        except MessageIdInvalidError:
            text = '<b>{exec_name}{{:</b>\n<pre>{input}</pre>\n<b>{time}</b>\n<pre>{res}</pre>'.format(
                exec_name=exec_name,
                time="Result{{ MD in {}:".format(tm) if arguments_state.get('t') else 'Result{ MD:',
                input=exec_input,
                res=html.escape('<exec.html>'))
            await event.reply(text, parse_mode='html')


async def main():
    await client.start()
    await client.run_until_disconnected()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    l_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    l_handler.setFormatter(formatter)
    logger.addHandler(l_handler)

    asyncio.get_event_loop().run_until_complete(main())
