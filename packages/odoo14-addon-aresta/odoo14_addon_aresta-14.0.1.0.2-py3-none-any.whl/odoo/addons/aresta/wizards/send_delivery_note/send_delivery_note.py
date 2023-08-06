from odoo import models, fields, api, exceptions, _
import base64


class SendDeliveryNoteWizard(models.TransientModel):
    _name = 'send.delivery.note.wizard'
    _description = 'Send delivery note by email'

    stock_picking_id = fields.Many2one('stock.picking')

    partner_id = fields.Many2one(
        'res.partner',
        related='stock_picking_id.partner_id'
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['stock_picking_id'] = self.env.context['active_id']
        return defaults


    def send_mail(self):
        email_to = self.partner_id.email
        if email_to:
            report = self.env.ref(
                'aresta.action_report_delivery_note'
            )
            picking_ids = self.env.context['active_ids']
            report_binary = report.render_qweb_pdf(picking_ids)
            pdf = base64.encodebytes(report_binary[0])
            email_values = {
                'email_to': email_to,
                'attachments': [[_('Delivery Note'), pdf]]
            }
            template_id = self.env.ref(
                'aresta.delivery_note_mail_template_view'
            ).id
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(
                picking_ids[0], email_values=email_values, force_send=True
            )
        else:
            raise exceptions.ValidationError(_('The email could not be sent. Please add an email address to the contact.'))
