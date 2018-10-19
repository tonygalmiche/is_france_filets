# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import Warning


class IsTypePrestation(models.Model):
    _name='is.type.prestation'
    _order='name'

    name = fields.Char(u'Type de prestation')


class IsNacelle(models.Model):
    _name='is.nacelle'
    _order='name'

    name = fields.Char(u'Nacelle')


class IsEquipeAbsence(models.Model):
    _name='is.equipe.absence'
    _order='date_debut'

    equipe_id  = fields.Many2one('is.equipe', 'Equipe', required=True, ondelete='cascade', readonly=True)
    date_debut = fields.Date('Date début', index=True)
    date_fin   = fields.Date('Date fin')
    motif      = fields.Char('Motif absence')

class IsEquipeMessage(models.Model):
    _name='is.equipe.message'
    _order='date'

    equipe_id = fields.Many2one('is.equipe', 'Equipe', required=True, ondelete='cascade', readonly=True)
    date      = fields.Date('Date', index=True)
    message   = fields.Char('Message')


class IsEquipe(models.Model):
    _name='is.equipe'
    _order='name'

    name        = fields.Char(u'Equipe')
    absence_ids = fields.One2many('is.equipe.absence', 'equipe_id', u"Absences")
    message_ids = fields.One2many('is.equipe.message', 'equipe_id', u"Messages")


class IsSaleOrderPlanning(models.Model):
    _name='is.sale.order.planning'
    _order='order_id,date_debut'

    order_id       = fields.Many2one('sale.order', 'Commande', required=True, ondelete='cascade', readonly=True)
    date_debut     = fields.Date('Date début')
    date_fin       = fields.Date('Date fin')
    commentaire    = fields.Char('Commentaire planning')
    equipe_ids     = fields.Many2many('is.equipe','is_sale_order_planning_equipe_rel','order_id','equipe_id', string="Equipes")
    pose_depose    = fields.Selection([
        ('pose'  , 'Pose'),
        ('depose', 'Dépose'),
    ], 'Pose / Dépose')
    etat = fields.Selection([
        ('a_confirmer', 'A confirmer'),
        ('a_faire'    , 'A faire'),
        ('fait'       , 'Fait'),
    ], 'État', default='a_confirmer')
    realisation    = fields.Char('Réalisation', help=u'Réalisation du chantier')


    @api.onchange('date_debut','date_fin','equipe_ids')
    def onchange_date(self):
        messages=[]
        for obj in self:
            if obj.equipe_ids and obj.date_debut and obj.date_fin:
                d1=datetime.strptime(obj.date_debut, '%Y-%m-%d')
                d2=datetime.strptime(obj.date_fin, '%Y-%m-%d')
                jours=(d2-d1).days+1
                for d in range(0, jours):
                    for equipe in obj.equipe_ids:
                        date=d1.strftime('%d/%m/%Y')
                        #** Recherche s'il existe une absence ******************
                        message=self.env['is.creation.planning'].get_absence(equipe, date)
                        if message:
                            messages.append(equipe.name+u' est absent le '+date+u' ('+message+')')
                        #*******************************************************

                        #** Recherche s'il existe déja une autre affaire *******
                        chantiers=self.env['is.creation.planning'].get_chantiers(equipe, date, html=False)
                        if chantiers:
                            for chantier in chantiers:
                                if chantier!=obj.order_id.name:
                                    messages.append(u'Le chantier '+chantier+u" est déjà plannifié pour l'équipe "+equipe.name+u' le '+date)
                        #*******************************************************

                    d1=d1+timedelta(days=1)
        if messages: 
            raise Warning('\n'.join(messages))


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_nom_chantier        = fields.Char('Nom du chantier')
    is_date_previsionnelle = fields.Date('Date prévisionnelle du chantier')
    is_contact_id          = fields.Many2one('res.partner', u'Contact du client')
    is_distance_chantier   = fields.Integer('Distance du chantier (en km)')
    is_num_ancien_devis    = fields.Char('N°ancien devis')
    is_motif_archivage     = fields.Text('Motif archivage devis')
    is_entete_devis        = fields.Text('Entête devis')
    is_pied_devis          = fields.Text('Pied devis')
    is_superficie          = fields.Char('Superficie')
    is_hauteur             = fields.Char('Hauteur')
    is_nb_interventions    = fields.Char("Nombre d'interventions")
    is_type_chantier       = fields.Selection([
        ('neuf'           , 'Neuf'),
        ('renovation'     , 'Rénovation'),
        ('neuf_renovation', 'Neuf et Rénovation'),
    ], 'Type de chantier')
    is_type_prestation_id  = fields.Many2one('is.type.prestation', u'Type de prestation')
    is_nacelle_id          = fields.Many2one('is.nacelle', u'Nacelle')
    is_planning_ids        = fields.One2many('is.sale.order.planning', 'order_id', u"Planning")

    @api.multi
    def get_nacelles(self):
        nacelles = self.env['is.nacelle'].search([])
        return nacelles



class IsCreationPlanning(models.Model):
    _name='is.creation.planning'
    _order='date_debut desc'

    date_debut     = fields.Date('Date de début', required=True)
    date_fin       = fields.Date('Date de fin'  , required=True)

    @api.multi
    def get_dates(self):
        cr = self._cr
        dates=[]
        for obj in self:
            d1=datetime.strptime(obj.date_debut, '%Y-%m-%d')
            d2=datetime.strptime(obj.date_fin, '%Y-%m-%d')
            jours=(d2-d1).days+1
            for d in range(0, jours):
                dates.append(d1.strftime('%d/%m/%Y'))
                d1=d1+timedelta(days=1)
        return dates


    @api.multi
    def get_equipes(self):
        equipes = self.env['is.equipe'].search([])
        return equipes


    @api.multi
    def get_absence(self,equipe,date):
        """Recherche des absences pour cette équipe et cette date"""
        cr = self._cr
        d=datetime.strptime(date, '%d/%m/%Y')
        absence=False
        SQL="""
            SELECT iea.motif 
            FROM is_equipe_absence iea
            WHERE 
                iea.date_debut<='"""+str(d)+"""' and 
                iea.date_fin>='"""+str(d)+"""' and
                iea.equipe_id="""+str(equipe.id)+"""
        """
        cr.execute(SQL)
        res = cr.fetchall()
        for row in res:
            absence=row[0]
        return absence


    @api.multi
    def get_message(self,equipe,date):
        """Recherche des messages pour cette équipe et cette date"""
        cr = self._cr
        d=datetime.strptime(date, '%d/%m/%Y')
        message=False
        for obj in self:
            SQL="""
                SELECT iem.message 
                FROM is_equipe_message iem
                WHERE 
                    iem.date='"""+str(d)+"""' and 
                    iem.equipe_id="""+str(equipe.id)+"""
            """
            cr.execute(SQL)
            res = cr.fetchall()
            for row in res:
                message=row[0]
        return message


    @api.multi
    def get_chantiers(self,equipe,date,html=True):
        cr = self._cr
        d=datetime.strptime(date, '%d/%m/%Y')
        chantiers=[]
        SQL="""
            SELECT
                so.name,
                rp.name,
                so.is_nom_chantier,
                so.is_type_chantier,
                so.is_superficie,
                isop.commentaire,
                isop.pose_depose,
                isop.etat
            FROM is_sale_order_planning isop inner join sale_order so on isop.order_id=so.id 
                                             inner join is_sale_order_planning_equipe_rel rel on isop.id=rel.order_id
                                             inner join is_equipe ie on rel.equipe_id=ie.id
                                             inner join res_partner rp on so.partner_id=rp.id
            WHERE 
                isop.date_debut<='"""+str(d)+"""' and 
                isop.date_fin>='"""+str(d)+"""' and
                ie.id="""+str(equipe.id)+"""
        """
        cr.execute(SQL)
        res = cr.fetchall()
        for row in res:
            if html:
                pose_depose=row[6]
                if pose_depose=='pose':
                    pose_depose='<span style="color:Red">Pose</span>'
                if pose_depose=='depose':
                    pose_depose=u'<span style="color:LawnGreen">Dépose</span>'
                html='<div>'
                etat=row[7]
                color='red'
                if etat=='a_confirmer':
                    color='red'
                if etat=='a_faire':
                    color='SteelBlue'
                if etat=='fait':
                    color='LawnGreen'
                html+='<b><span style="background-color:'+color+'">'+(row[0] or '')+'</span></b>'
                if pose_depose:
                    html+=' - <b>'+pose_depose+'</b>'
                html+='</div>'
                html+='<b>'+(row[1] or '')+'</b><br />'
                html+=(row[2] or '')+'<br />'
                html+=(row[3] or '')+' - '+(row[4] or '')+'<br />'
                html+=(row[5] or '')
                chantiers.append(html)
            else:
                chantiers.append(row[0])
        return chantiers



