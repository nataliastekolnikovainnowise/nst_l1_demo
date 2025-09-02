from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class NstL1Demo(models.Model):
    _name = "nst.l1.demo"
    _description = "L1 Demo Model"
    _order = "create_date desc"

    # ---- Базовые поля из задания ----
    name = fields.Char(string="Name", required=True, default=lambda self: _("New L1 Record"))
    text = fields.Text(string="Text")

    check1 = fields.Boolean(string="Test 1")
    check2 = fields.Boolean(string="Test 2")
    check_all = fields.Boolean(string="Select all")

    select1 = fields.Selection(
        selection=[("1", "1"), ("2", "2"), ("3", "3")],
        string="Select 1"
    )
    select2 = fields.Selection(
        selection=[("4", "4"), ("5", "5"), ("6", "6")],
        string="Select 2"
    )

    boolean1 = fields.Boolean(string="1")
    boolean2 = fields.Boolean(string="2")
    boolean3 = fields.Boolean(string="3")
    boolean4 = fields.Boolean(string="4")
    boolean5 = fields.Boolean(string="5")
    boolean6 = fields.Boolean(string="6")
    boolean7 = fields.Boolean(string="7")
    boolean8 = fields.Boolean(string="8")
    boolean9 = fields.Boolean(string="9")

    # ---- Доп. поле из Задачи 6 ----
    is_company = fields.Boolean(string="Is a Company?")

    # ---- ПОЛНЫЙ СПЕКТР ТИПОВ ПОЛЕЙ (Задача 1.1) ----
    char_demo = fields.Char(string="Char")
    html_demo = fields.Html(string="HTML")
    integer_demo = fields.Integer(string="Integer")
    float_demo = fields.Float(string="Float")
    monetary_demo = fields.Monetary(string="Monetary")
    currency_id = fields.Many2one('res.currency', string='Currency')
    date_demo = fields.Date(string="Date")
    datetime_demo = fields.Datetime(string="Datetime")
    binary_demo = fields.Binary(string="Binary")
    selection_demo = fields.Selection([
        ('a','A'),('b','B'),('c','C')
    ], string='Selection demo')

    # Relational
    m2o_partner_id = fields.Many2one('res.partner', string='M2O Partner')
    o2m_child_ids = fields.One2many('nst.l1.demo.child', 'parent_id', string='O2M Children')
    m2m_tags = fields.Many2many('res.partner.category', string='M2M Tags')

    # compute + inverse пример: собираем лейблы отмеченных чекбоксов
    labels_combined = fields.Char(
        string="Labels Combined",
        compute="_compute_labels_combined",
        inverse="_inverse_labels_combined",
        store=False
    )

    # технические поля для порядка отметок check1/check2
    check1_ts = fields.Datetime(string="Check1 TS")
    check2_ts = fields.Datetime(string="Check2 TS")

    # пример вычисляемого поля с depends (БЕЗ bool() операций)
    checked_count = fields.Integer(string="Checked Count",
                                   compute="_compute_checked_count",
                                   store=False)

    @api.depends('check1', 'check2', 'boolean1', 'boolean2', 'boolean3',
                 'boolean4', 'boolean5', 'boolean6', 'boolean7', 'boolean8', 'boolean9')
    def _compute_checked_count(self):
        for r in self:
            r.checked_count = sum([
                r.check1, r.check2, r.boolean1, r.boolean2, r.boolean3,
                r.boolean4, r.boolean5, r.boolean6, r.boolean7, r.boolean8, r.boolean9
            ])

    @api.depends('check1', 'check2', 'check1_ts', 'check2_ts')
    def _compute_labels_combined(self):
        for r in self:
            parts = []
            order = []
            if r.check1:
                order.append(('check1', r.check1_ts or fields.Datetime.now()))
            if r.check2:
                order.append(('check2', r.check2_ts or fields.Datetime.now()))
            order.sort(key=lambda x: x[1])
            for key, _ts in order:
                if key == 'check1':
                    parts.append('[Test 1]')
                else:
                    parts.append('{Test 2}')
            r.labels_combined = ' '.join(parts)

    def _inverse_labels_combined(self):
        # Пример inverse: парсим строку и выставляем check1/check2
        for r in self:
            s = (r.labels_combined or '').strip()
            r.check1 = '[Test 1]' in s
            r.check2 = '{Test 2}' in s
            now = fields.Datetime.now()
            r.check1_ts = now if r.check1 else False
            r.check2_ts = now if r.check2 else False
            r._sync_text_from_checks()

    # ------------ ДЕКОРАТОРЫ: onchange ------------
    @api.onchange('check_all')
    def _onchange_check_all(self):
        for r in self:
            if r.check_all:
                r.check1 = True
                r.check2 = True
                now = fields.Datetime.now()
                r.check1_ts = now
                r.check2_ts = now
            else:
                r.check1 = False
                r.check2 = False
                r.check1_ts = False
                r.check2_ts = False
            r._sync_text_from_checks()

    @api.onchange('check1')
    def _onchange_check1(self):
        for r in self:
            if r.check1:
                r.check1_ts = fields.Datetime.now()
            else:
                r.check1_ts = False
            if r.check1 and r.check2:
                r.check_all = True
            if (not r.check1) and r.check_all:
                r.check_all = False
            r._sync_text_from_checks()

    @api.onchange('check2')
    def _onchange_check2(self):
        for r in self:
            if r.check2:
                r.check2_ts = fields.Datetime.now()
            else:
                r.check2_ts = False
            if r.check1 and r.check2:
                r.check_all = True
            if (not r.check2) and r.check_all:
                r.check_all = False
            r._sync_text_from_checks()

    def _sync_text_from_checks(self):
        for r in self:
            parts = []
            order = []
            if r.check1:
                order.append(('check1', r.check1_ts or fields.Datetime.now()))
            if r.check2:
                order.append(('check2', r.check2_ts or fields.Datetime.now()))
            order.sort(key=lambda x: x[1])
            for key, _ts in order:
                if key == 'check1':
                    parts.append('[Test 1]')
                else:
                    parts.append('{Test 2}')
            r.text = ' '.join(parts)

    @api.onchange('select1', 'select2')
    def _onchange_selects(self):
        """Задача 5: Логика отображения boolean1-9"""
        # Сначала скрываем все
        for i in range(1, 10):
            setattr(self, f"boolean{i}", False)

        # Логика по select1 (строки матрицы)
        if self.select1 == "1":
            self.boolean1 = self.boolean2 = self.boolean3 = True
        elif self.select1 == "2":
            self.boolean4 = self.boolean5 = self.boolean6 = True
        elif self.select1 == "3":
            self.boolean7 = self.boolean8 = self.boolean9 = True

        # Логика по select2 (столбцы матрицы)
        if self.select2 == "4":
            self.boolean1 = self.boolean4 = self.boolean7 = True
        elif self.select2 == "5":
            self.boolean2 = self.boolean5 = self.boolean8 = True
        elif self.select2 == "6":
            self.boolean3 = self.boolean6 = self.boolean9 = True

    # ------------ ДЕКОРАТОРЫ: constrains ------------
    @api.constrains('name')
    def _check_name_len(self):
        for r in self:
            if r.name and len(r.name) < 3:
                raise ValidationError(_("Name must be at least 3 characters."))

    # Кнопки в хедере (Задача 6)
    def action_open_partner_form_person(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Person'),
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_is_company': False,
            }
        }

    def action_open_partner_form_company(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Company'),
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_is_company': True,
            }
        }


class NstL1DemoChild(models.Model):
    _name = 'nst.l1.demo.child'
    _description = 'Child demo for O2M'

    name = fields.Char(required=True)
    parent_id = fields.Many2one('nst.l1.demo', ondelete='cascade')
    note = fields.Text()
