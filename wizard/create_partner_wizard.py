from odoo import api, fields, models, _

class NstCreatePartnerWizard(models.TransientModel):
    _name = 'nst.create.partner.wizard'
    _description = 'Create Partner Wizard'

    name = fields.Char(string='Name', required=True)
    is_company = fields.Boolean(string='Is Company?', required=True)

    def action_create_partner(self):
        self.ensure_one()
        partner = self.env['res.partner'].create({
            'name': self.name,
            'is_company': self.is_company,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner'),
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }
