# -*- coding: utf-8 -*-
from openerp import models,fields,api
import datetime


class is_filet(models.Model):
    _name='is.filet'
    _order='name desc'

    name = fields.Char(u"N°Filet", readonly=True)
    type_filet = fields.Selection([
        ('simple'     , u'Filet simple'),
        ('pare-gravat', u'Filet doublé pare-gravât'),
    ], 'Type de filet', default='simple',required=True)
    dimensions       = fields.Char(u"Dimensions", required=True)
    fabriquant       = fields.Char(u"Fabriquant", required=True)
    num_serie        = fields.Char(u"N°de série", required=True)
    date_fabrication = fields.Date(u"Date de fabrication", required=True)
    etat_filet = fields.Selection([
        ('conforme' , u'Conforme'),
        ('a-reparer', u'A réparer'),
        ('hs'       , u'HS'),
    ], u'État du filet', default='conforme',required=True)
    mouvement_ids = fields.One2many('is.filet.mouvement', 'filet_id', u"Mouvements")


    @api.model
    def create(self, vals):
        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_filet_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_filet, self).create(vals)
        return res


class is_filet_mouvement(models.Model):
    _name='is.filet.mouvement'
    _order='name desc'


    filet_id = fields.Many2one('is.filet', 'Filet', required=True, ondelete='cascade',index=True)
    name = fields.Datetime(u"Heure du mouvement", default=lambda self: fields.Datetime.now(),required=True)
    position = fields.Selection([
        ('depot'      , u'Dépôt'),
        ('camionnette', u'Camionnette'),
        ('chantier'   , u'Chantier'),
    ], 'Position', default='depot',required=True)
    chantier_id = fields.Many2one('is.chantier', u'Chantier')

