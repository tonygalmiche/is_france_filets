# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import Warning


_ETAT_PLANNING=[
    ('a_confirmer', 'A confirmer'),
    ('a_faire'    , 'A faire'),
    ('fait'       , 'Fait'),
]


_TYPE_CHANTIER=[
    ('neuf'           , 'Neuf'),
    ('renovation'     , 'Rénovation'),
    ('neuf_renovation', 'Neuf et Rénovation'),
]


class IsMotifArchivage(models.Model):
    _name='is.motif.archivage'
    _order='name'

    name = fields.Char(u"Motif d'Archivage")


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
    date_debut = fields.Date(u'Date début', index=True)
    date_fin   = fields.Date(u'Date fin')
    motif      = fields.Char(u'Motif absence')

class IsEquipeMessage(models.Model):
    _name='is.equipe.message'
    _order='date'

    equipe_id = fields.Many2one('is.equipe', 'Equipe', required=True, ondelete='cascade', readonly=True)
    date      = fields.Date('Date', index=True)
    message   = fields.Char('Message')


class IsEquipe(models.Model):
    _name='is.equipe'
    _order='name'

    name        = fields.Char(u'Equipe', required=True)
    user_id     = fields.Many2one('res.users', u"Chef d'équipe", required=True)
    absence_ids = fields.One2many('is.equipe.absence', 'equipe_id', u"Absences")
    message_ids = fields.One2many('is.equipe.message', 'equipe_id', u"Messages")


class IsSaleOrderPlanning(models.Model):
    _name='is.sale.order.planning'
    _order='order_id,date_debut'

    order_id       = fields.Many2one('sale.order', 'Commande', required=True, ondelete='cascade', readonly=True,index=True)
    date_debut     = fields.Date(u'Date début',index=True)
    date_fin       = fields.Date(u'Date fin')
    commentaire    = fields.Char('Commentaire planning')
    equipe_ids     = fields.Many2many('is.equipe','is_sale_order_planning_equipe_rel','order_id','equipe_id', string="Equipes")
    pose_depose    = fields.Selection([
        ('pose'  , 'Pose'),
        ('depose', 'Dépose'),
    ], u'Pose / Dépose')
    etat = fields.Selection(_ETAT_PLANNING, u'État', default='a_confirmer')
    realisation    = fields.Text(u'Réalisation', help=u'Réalisation du chantier', readonly=True)



    def get_avertissements(self,obj,equipe,date):
        avertissements=[]

        date=date.strftime('%d/%m/%Y')
        #** Recherche s'il existe une absence ******************
        message=self.env['is.creation.planning'].get_absence(equipe, date)
        if message:
            avertissements.append(equipe.name+u' est absent le '+date+u' ('+message+')')
        #*******************************************************

        #** Recherche s'il existe déja une autre affaire *******
        chantiers=self.env['is.creation.planning'].get_chantiers(equipe, date, retour='order')
        if chantiers:
            for chantier in chantiers:
                if chantier!=obj.order_id.name:
                    avertissements.append(u'Le chantier '+chantier+u" est déjà plannifié pour l'équipe "+equipe.name+u' le '+date)
        #*******************************************************

        return avertissements


    @api.onchange('date_debut','date_fin','equipe_ids')
    def onchange_date(self):
        avertissements=False
        for obj in self:
            if obj.equipe_ids and obj.date_debut and obj.date_fin:
                d1=datetime.strptime(obj.date_debut, '%Y-%m-%d')
                d2=datetime.strptime(obj.date_fin, '%Y-%m-%d')
                jours=(d2-d1).days+1
                for d in range(0, jours):
                    for equipe in obj.equipe_ids:
                        res=self.get_avertissements(obj,equipe,d1)
                        if res:
                            if avertissements:
                                avertissements.extend(res)
                            else:
                                avertissements=res
                    d1=d1+timedelta(days=1)
        if avertissements: 
            raise Warning('\n'.join(avertissements))


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.depends('is_planning_ids')
    def _compute(self):
        for obj in self:
            etat=[]
            for line in obj.is_planning_ids:
                if line.etat and line.date_debut and line.date_fin:
                    x=dict(_ETAT_PLANNING)[line.etat]
                    etat.append(x)
            if etat:
                etat=', '.join(etat)
            else:
                etat=''
            obj.is_etat_planning=etat


    def _compute_ca_m2(self):
        for obj in self:
            if obj.is_superficie_m2:
                obj.is_ca_m2=obj.amount_untaxed/obj.is_superficie_m2


    is_nom_chantier        = fields.Char(u'Nom du chantier')
    is_date_previsionnelle = fields.Date(u'Date prévisionnelle du chantier')
    is_contact_id          = fields.Many2one('res.partner', u'Contact du client')
    is_distance_chantier   = fields.Integer(u'Distance du chantier (en km)')
    is_num_ancien_devis    = fields.Char(u'N°ancien devis')
    is_ref_client          = fields.Char(u'Référence client')
    is_motif_archivage_id  = fields.Many2one('is.motif.archivage', u'Motif archivage devis')
    is_motif_archivage     = fields.Text(u'Motif archivage devis (commentaire)')
    is_entete_devis        = fields.Text(u'Entête devis')
    is_pied_devis          = fields.Text(u'Pied devis')
    is_superficie          = fields.Char(u'Superficie', help="Champ utilisé pour le devis client")
    is_superficie_m2       = fields.Integer(u'Superficie (m2)', help="Champ utilisé pour les calculs du CA/m2")
    is_ca_m2               = fields.Float("CA / m2", digits=(14,2), compute='_compute_ca_m2', readonly=True)
    is_hauteur             = fields.Char(u'Hauteur')
    is_nb_interventions    = fields.Char(u"Nombre d'interventions")
    is_type_chantier       = fields.Selection(_TYPE_CHANTIER, u'Type de chantier')
    is_type_prestation_id  = fields.Many2one('is.type.prestation', u'Type de prestation')
    is_nacelle_id          = fields.Many2one('is.nacelle', u'Nacelle')
    is_planning_ids        = fields.One2many('is.sale.order.planning', 'order_id', u"Planning")
    is_etat_planning       = fields.Char(u"Etat planning", compute='_compute', readonly=True, store=True)
    is_info_fiche_travail  = fields.Text(u'Informations fiche de travail')
    is_piece_jointe_ids    = fields.Many2many('ir.attachment', 'sale_order_piece_jointe_attachment_rel', 'order_id', 'attachment_id', u'Pièces jointes')
    is_region_id           = fields.Many2one('is.region'          , u'Région'            , related='partner_id.is_region_id'          , readonly=True)
    is_secteur_activite_id = fields.Many2one('is.secteur.activite', u"Secteur d'activité", related='partner_id.is_secteur_activite_id', readonly=True)


    @api.multi
    def get_nacelles(self):
        nacelles = self.env['is.nacelle'].search([])
        return nacelles


class IsCreationPlanningPreparation(models.Model):
    _name='is.creation.planning.preparation'
    _order='date,equipe_id,order_id'

    planning_id  = fields.Many2one('is.creation.planning', u'Planning', required=True, ondelete='cascade')
    date         = fields.Date(u'Date', index=True)
    equipe_id    = fields.Many2one('is.equipe', u'Equipe')
    order_id     = fields.Many2one('sale.order', u'Chantier')
    nom_chantier = fields.Char(u'Nom du chantier')
    partner_id   = fields.Many2one('res.partner', u'Client')
    pose_depose  = fields.Selection([
        ('pose'  , 'Pose'),
        ('depose', 'Dépose'),
    ], u'Pose / Dépose')
    etat    = fields.Selection(_ETAT_PLANNING, u'État')
    message = fields.Text('Message')


class IsCreationPlanning(models.Model):
    _name='is.creation.planning'
    _order='date_debut desc'

    date_debut   = fields.Date(u'Date de début', required=True)
    date_fin     = fields.Date(u'Date de fin'  , required=True)
    equipe_id    = fields.Many2one('is.equipe', u'Equipe')
    planning_ids = fields.One2many('is.creation.planning.preparation', 'planning_id', u"Planning")


    @api.multi
    def name_get(self):
        res=[]
        for obj in self:
            res.append((obj.id, obj.date_debut))
        return res


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
        message=[]
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
                message.append(row[0])
        return '<br />'.join(message)


    @api.multi
    def get_orders(self,date_debut,date_fin):
        """Retourne les commandes pour les fiches de travail"""
        cr = self._cr
        SQL="""
            SELECT DISTINCT so.id, so.name
            FROM is_sale_order_planning isop inner join sale_order so on isop.order_id=so.id
            WHERE 
                isop.date_debut<='"""+str(date_fin)+"""' and 
                isop.date_fin>='"""+str(date_debut)+"""'
            ORDER BY so.name
        """
        cr.execute(SQL)
        res = cr.fetchall()
        orders=[]
        for row in res:
            if row[0]:
                order = self.env['sale.order'].browse(row[0])
                if order:
                    if order not in orders:
                        orders.append(order)
        return orders


    @api.multi
    def get_chantiers(self,equipe,date,retour='html'):
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
                isop.etat,
                so.id,
                isop.id
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
            if retour=='html':
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
            if retour=='order':
                chantiers.append(row[0])
            if retour=='planning':
                vals={
                    'order_id'   : row[8],
                    'planning_id': row[9],
                }
                chantiers.append(vals)
        return chantiers


    @api.multi
    def mail_planning_action(self):
        """Mail du planning"""
        mails=[]
        for obj in self:

            for planning in obj.planning_ids:
                mail=planning.equipe_id.user_id.partner_id.email
                if mail and mail not in mails:
                    mails.append(mail)
            print(mails)
            email_to=','.join(mails)

            subject=u'Planning du '+str(obj.date_debut)+u' au '+str(obj.date_fin)
            user  = self.env['res.users'].browse(self._uid)
            email_from = user.email
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url=base_url+u'/web'

            print(url)

            body_html=u"""
                <p>Bonjour,</p>
                <p>Le nouveau <a href='"""+url+u"""'>Planning</a> est disponible.</p>
                <p>Merci d'en prendre connaissance.</p>
            """
            vals={
                'email_from'    : email_from, 
                'email_to'      : email_to, 
                'email_cc'      : email_from,
                'subject'       : subject,
                'body_html'     : body_html, 
            }
            email=self.env['mail.mail'].create(vals)
            if email:
                self.env['mail.mail'].send(email)


    @api.multi
    def preparer_planning_action(self):
        """Préparation du planning"""
        for obj in self:
            obj.planning_ids.unlink()
            equipes = obj.get_equipes()
            dates   = obj.get_dates()

            orders=[]

            for equipe in equipes:
                for date in dates:
                    chantiers   = obj.get_chantiers(equipe,date,retour='planning')
                    for chantier in chantiers:
                        order_id    = chantier['order_id']
                        planning_id = chantier['planning_id']
                        order    = self.env['sale.order'].browse(order_id)
                        planning = self.env['is.sale.order.planning'].browse(planning_id)
                        d=datetime.strptime(date, '%d/%m/%Y')
                        message=self.env['is.sale.order.planning'].get_avertissements(planning,equipe,d)

                        if order not in orders:
                            orders.append(order)

                        #self.creation_chantier(equipe,order,planning)
                        if message:
                            message='\n'.join(message)
                        else:
                            message=False
                        #if order and planning.etat!='fait':

                        if order:
                            vals={
                                'planning_id' : obj.id,
                                'date'        : date,
                                'order_id'    : order_id,
                                'equipe_id'   : equipe.id,
                                'nom_chantier': order.is_nom_chantier,
                                'partner_id'  : order.partner_id.id,
                                'pose_depose' : planning.pose_depose,
                                'etat'        : planning.etat,
                                'message'     : message,
                            }
                            self.env['is.creation.planning.preparation'].create(vals)



            #** Création des plannings pour chaque équipe **********************
            equipes = obj.get_equipes()
            for equipe in equipes:
                plannings = self.env['is.planning'].search([('creation_planning_id','=',obj.id),('equipe_id','=',equipe.id)])
                name=u'Planning du '+str(obj.date_debut)+' au '+str(obj.date_fin)+u' pour '+equipe.name
                if not plannings:
                    vals={
                        'name'                : name,
                        'equipe_id'           : equipe.id,
                        'creation_planning_id': obj.id,
                    }
                    planning=self.env['is.planning'].create(vals)
                else:
                    planning=plannings[0]
                vals={
                        'name'                : name,
                }
                planning.write(vals)
            #*******************************************************************


            #** Création des chantiers *****************************************
            self.env['is.chantier.planning'].search([('sale_order_planning_id','=',False)]).unlink()
            for order in orders:
                chantiers = self.env['is.chantier'].search([('order_id','=',order.id)])
                if not chantiers:
                    vals={
                        'order_id'         : order.id,
                    }
                    chantier=self.env['is.chantier'].create(vals)
                else:
                    chantier=chantiers[0]
                piece_jointe_ids=[]
                for attachment in order.is_piece_jointe_ids:
                    piece_jointe_ids.append(attachment.id)
                vals={
                    'name'               : order.name,
                    'client'             : order.partner_id.name,
                    'contact_client'     : order.is_contact_id.name,
                    'nom_chantier'       : order.is_nom_chantier,
                    'superficie'         : order.is_superficie,
                    'hauteur'            : order.is_hauteur,
                    'type_chantier'      : order.is_type_chantier,
                    'informations'       : order.is_info_fiche_travail,
                    'piece_jointe_ids'   : [(6,0,piece_jointe_ids)],
                }
                chantier.write(vals)
                user_ids=[]
                for line in order.is_planning_ids:
                    plannings = self.env['is.chantier.planning'].search([('sale_order_planning_id','=',line.id)])
                    if not plannings:
                        vals={
                            'chantier_id'           : chantier.id,
                            'sale_order_planning_id': line.id,
                        }
                        planning=self.env['is.chantier.planning'].create(vals)
                    else:
                        planning=plannings[0]

                    for l in line.equipe_ids:
                        user_ids.append(l.user_id.id)
                    vals={
                        'date_debut'            : line.date_debut,
                        'date_fin'              : line.date_fin,
                        'commentaire'           : line.commentaire,
                        'pose_depose'           : line.pose_depose,
                        'etat'                  : line.etat,
                    }
                    planning.write(vals)
                vals={
                    'user_ids': [(6,0,user_ids)],
                }
                chantier.write(vals)
            #*******************************************************************

            #** Ajout des chantiers sur le planning ****************************
            plannings = self.env['is.planning'].search([('creation_planning_id','=',obj.id)])
            for planning in plannings:
                planning.chantier_ids.unlink()
                for order in orders:
                    test=False
                    for line in obj.planning_ids:
                        if planning.equipe_id==line.equipe_id and line.order_id==order:
                            test=True
                    if test:
                        chantiers = self.env['is.chantier'].search([('order_id','=',order.id)])
                        if chantiers:
                            chantier=chantiers[0]
                            vals={
                                'planning_id': planning.id,
                                'chantier_id': chantier.id,
                            }
                            self.env['is.planning.line'].create(vals)
            #*******************************************************************

            #** Suppression des plannings sans chantier ************************
            plannings = self.env['is.planning'].search([('creation_planning_id','=',obj.id)])
            for planning in plannings:
                if not planning.chantier_ids:
                    planning.unlink()
            #*******************************************************************

            #** Ajout des planning PDF en pièce jointe *************************
            plannings = self.env['is.planning'].search([('creation_planning_id','=',obj.id)])
            equipe_id=obj.equipe_id.id
            for planning in plannings:
                obj.equipe_id=planning.equipe_id.id
                pdf = self.env['report'].get_pdf([obj.id], 'is_france_filets.is_planning_report')
                model=planning._name
                name='planning.pdf'
                attachment_obj = self.env['ir.attachment']
                attachments = attachment_obj.search([('res_model','=',model),('res_id','=',planning.id),('name','=',name)])
                vals = {
                    'name':        name,
                    'datas_fname': name,
                    'type':        'binary',
                    'res_model':   model,
                    'res_id':      planning.id,
                    'datas':       pdf.encode('base64'),
                }
                if attachments:
                    for attachment in attachments:
                        attachment.write(vals)
                else:
                    attachment = attachment_obj.create(vals)
            obj.equipe_id=equipe_id
            #*******************************************************************

            return {
                'name': u'Préparation planning '+str(obj.date_debut),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'is.creation.planning.preparation',
                'domain': [
                    ('planning_id','=',obj.id),
                ],
                'context':{
                    'default_planning_id': obj.id,
                },
                'type': 'ir.actions.act_window',
            }


class IsPlanningLine(models.Model):
    _name='is.planning.line'
    _order='chantier_id'

    planning_id = fields.Many2one('is.planning', u'Planning', required=True, ondelete='cascade', readonly=True)
    chantier_id = fields.Many2one('is.chantier', u"Chantier")


class IsPlanning(models.Model):
    _name='is.planning'
    _order='name desc'

    name                 = fields.Char(u'Planning', required=True,index=True)
    creation_planning_id = fields.Many2one('is.creation.planning', u"Préparation Planning", required=True, index=True)
    equipe_id            = fields.Many2one('is.equipe', u"Equipe")
    chantier_ids         = fields.One2many('is.planning.line', 'planning_id', u"Chantiers")


class IsChantierPlanning(models.Model):
    _name='is.chantier.planning'
    _order='chantier_id,date_debut'

    chantier_id            = fields.Many2one('is.chantier', u'Chantier', required=True, ondelete='cascade', readonly=True,index=True)
    sale_order_planning_id = fields.Many2one('is.sale.order.planning', u"Ligne planning commande", readonly=True,index=True)
    date_debut             = fields.Date(u'Date début', readonly=True,index=True)
    date_fin               = fields.Date(u'Date fin', readonly=True)
    commentaire            = fields.Char(u'Commentaire planning', readonly=True)
    equipe_ids             = fields.Many2many('is.equipe','is_chantier_planning_equipe_rel','chantier_id','equipe_id', string=u"Equipes", readonly=True)
    pose_depose            = fields.Selection([
        ('pose'  , 'Pose'),
        ('depose', 'Dépose'),
    ], u'Pose / Dépose', readonly=True)
    etat = fields.Selection(_ETAT_PLANNING, u'État', default='a_confirmer', readonly=True)
    realisation    = fields.Text(u'Réalisation', help=u'Réalisation du chantier')


    @api.multi
    def write(self,vals):
        for obj in self:
            if 'realisation' in vals:
                obj.sudo().sale_order_planning_id.realisation=vals['realisation']
        res = super(IsChantierPlanning, self).write(vals)


class IsChantier(models.Model):
    _name='is.chantier'
    _order='name'

    name              = fields.Char(u'Chantier / Commande', readonly=True)
    user_ids          = fields.Many2many('res.users','is_chantier_user_rel','chantier_id','user_id', string=u"Chefs d'équipes", readonly=True)
    order_id          = fields.Many2one('sale.order', u"Commande", readonly=True)
    client            = fields.Char(u'Client', readonly=True)
    contact_client    = fields.Char(u'Contact Client', readonly=True)
    nom_chantier      = fields.Char(u'Nom du chantier', readonly=True)
    superficie        = fields.Char(u'Superficie', readonly=True)
    hauteur           = fields.Char(u'Hauteur', readonly=True)
    type_chantier     = fields.Selection(_TYPE_CHANTIER, u'Type de chantier', readonly=True)
    planning_ids      = fields.One2many('is.chantier.planning', 'chantier_id', u"Planning")
    informations      = fields.Text(u'Informations diverses', readonly=True)
    piece_jointe_ids  = fields.Many2many('ir.attachment', 'is_chantier_piece_jointe_attachment_rel', 'is_chantier_id', 'attachment_id', u'Pièces jointes', readonly=True)
    fin_chantier_ids  = fields.Many2many('ir.attachment', 'is_chantier_fin_chantier_attachment_rel', 'is_chantier_id', 'attachment_id', u'Documents de fin de chantier')





