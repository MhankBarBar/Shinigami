from Shinigami.commands import BaseCommand
from Shinigami.utils.message import SimplifiedMessage


class Test(BaseCommand):

    @staticmethod
    def execute(**opts):
        c = opts.get("c")
        sm = opts.get("sm")
        me = SimplifiedMessage.jid_to_string(c.get_me().JID)
        if x := sm.get_mention():
            for i in x:
                if i == me:
                    c.reply_message(SimplifiedMessage.string_to_jid(opts.get("sm").chat), "Naon cuy!", opts.get("m"))
