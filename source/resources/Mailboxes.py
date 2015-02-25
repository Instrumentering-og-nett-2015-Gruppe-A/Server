from flask_restful import marshal_with, Resource, fields, abort
from flask_restful.reqparse import RequestParser
from source.models import Mailbox as MailboxModel , MailboxKey, Session
from source.utils import get_or_404

mailbox_key_fields = {
    'rfid':     fields.String
}
detailed_mailbox_fields = {
    'id':           fields.String,
    'keys':         fields.List(fields.Nested(mailbox_key_fields)),
    'has_mail':     fields.Boolean,
    'is_closed':    fields.Boolean,
    'opens_in':     fields.Integer,
    'display_text': fields.String
}

list_mailbox_fields = {
    'id':           fields.Integer,
    'has_mail':     fields.Boolean,
    'is_closed':    fields.Boolean
}


class Mailbox(Resource):

    def __init__(self):
        super(Mailbox, self).__init__()
        self.parser = RequestParser()
        self.parser.add_argument('rfid', type=str, dest='rfid', location='json')
        self.parser.add_argument('has_mail', type=bool, dest='has_mail', location='json')

    @marshal_with(detailed_mailbox_fields)
    def post(self):
        session = Session()
        mailbox = MailboxModel()
        session.add(mailbox)
        session.commit()
        return mailbox

    def get(self, mailbox_id=None):
        if mailbox_id == None:
            return self.get_list()
        return self.get_single(mailbox_id)

    @marshal_with(detailed_mailbox_fields)
    def get_single(self, mailbox_id):
        session = Session()
        return get_or_404(session.query(MailboxModel), mailbox_id)

    @marshal_with(list_mailbox_fields)
    def get_list(self):
        session = Session()
        return session.query(MailboxModel).all()

    @marshal_with(detailed_mailbox_fields)
    def put(self, mailbox_id):
        args = self.parser.parse_args()
        new_rfid = args.rfid
        has_mail = args.has_mail
        session = Session()

        mailbox = get_or_404(session.query(MailboxModel), mailbox_id)
        if new_rfid:
            if not new_rfid in [key.rfid for key in mailbox.keys]:
                key = MailboxKey()
                key.mailbox = mailbox
                key.rfid = new_rfid
        if has_mail != None:
            mailbox.has_mail = has_mail

        session.commit()
        return mailbox
