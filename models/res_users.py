# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.multi
    def get_chantiers(self):
        """Retourne pour l'application mobile, la liste des chantiers pour le chef de chantier et les 28 prochains jours"""
        equipes = self.env['is.equipe'].search([('user_id','=',self._uid)])
        equipe= False
        if len(equipes)>0:
            equipe = equipes[0]
        ids=[]
        if equipe:
            plannings = self.env['is.planning'].sudo().search([('equipe_id','=',equipe.id)])
            for planning in plannings:
                date_debut = planning.creation_planning_id.date_debut
                date_fin   = planning.creation_planning_id.date_fin
                debut = datetime.today()
                fin   = debut + timedelta(days=28)
                if date_fin >= str(debut) and date_fin<=str(fin):
                    for chantier in planning.chantier_ids:
                        ids.append(chantier.chantier_id.id)
        ids.sort()
        return ids


