from sqlalchemy import orm, UniqueConstraint

from viggocore.database import db
from viggocore.common.subsystem import entity

from viggolocal.subsystem.common import endereco


class Parceiro(entity.Entity, db.Model):

    attributes = ['domain_id', 'cpf_cnpj', 'doc_estrangeiro', 'rg_insc_est',
                  'nome_razao_social', 'apelido_nome_fantasia',
                  'observacao']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    cpf_cnpj = db.Column(db.CHAR(14), nullable=True)
    doc_estrangeiro = db.Column(db.CHAR(20), nullable=True)
    rg_insc_est = db.Column(db.String(20), nullable=True)
    nome_razao_social = db.Column(db.String(60), nullable=False)
    apelido_nome_fantasia = db.Column(db.String(60), nullable=True)
    observacao = db.Column(db.String(500), nullable=True)
    enderecos = orm.relationship(
        "ParceiroEndereco", backref=orm.backref('parceiro'),
        cascade='delete,delete-orphan,save-update')
    contatos = orm.relationship(
        "ParceiroContato", backref=orm.backref('parceiro'),
        cascade='delete,delete-orphan,save-update')

    __table_args__ = (
        UniqueConstraint('domain_id', 'cpf_cnpj',
                         name='parceiro_domain_id_cpf_cnpj_uk'),
        UniqueConstraint('domain_id', 'doc_estrangeiro',
                         name='parceiro_domain_id_doc_estrangeiro_uk'),
        UniqueConstraint('domain_id', 'rg_insc_est',
                         name='parceiro_domain_id_rg_insc_est_uk'),)

    def __init__(self, id, domain_id, nome_razao_social, cpf_cnpj=None,
                 doc_estrangeiro=None, rg_insc_est=None,
                 apelido_nome_fantasia=None, observacao=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.cpf_cnpj = cpf_cnpj
        self.doc_estrangeiro = doc_estrangeiro
        self.nome_razao_social = nome_razao_social
        self.apelido_nome_fantasia = apelido_nome_fantasia
        self.rg_insc_est = rg_insc_est
        self.observacao = observacao

    def is_stable(self):
        if self.cpf_cnpj is not None and self.doc_estrangeiro is None:
            return (len(self.cpf_cnpj) == 11) or (len(self.cpf_cnpj) == 14)
        elif self.cpf_cnpj is None and self.doc_estrangeiro is not None:
            return True
        else:
            return False

    @classmethod
    def individual(cls):
        return 'parceiro'

    @classmethod
    def embedded(cls):
        return ['enderecos', 'contatos']


class ParceiroEndereco(endereco.resource.Endereco, db.Model):

    attributes = ['id', 'pais_id', 'municipio_nome', 'municipio_sigla_uf']
    attributes += endereco.resource.Endereco.attributes
    municipio_id = db.Column(
        db.CHAR(32), db.ForeignKey('municipio.id'), nullable=False)
    municipio = orm.relationship(
        'Municipio', backref=orm.backref('parceiro_municipio'))

    pais_id = db.Column(
        db.CHAR(32), db.ForeignKey('pais.id'), nullable=True)
    pais = orm.relationship(
        'Pais', backref=orm.backref('parceiro_endereco_pais'))

    parceiro_id = db.Column(
        db.CHAR(32), db.ForeignKey("parceiro.id"), nullable=False)

    def __init__(self, id, parceiro_id, logradouro, numero, bairro,
                 municipio_id, cep, complemento=None, ponto_referencia=None,
                 pais_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, logradouro, numero, bairro, municipio_id, cep,
                         complemento, ponto_referencia, active, created_at,
                         created_by, updated_at, updated_by, tag)
        self.parceiro_id = parceiro_id
        self.pais_id = pais_id

    @property
    def municipio_nome(self):
        if self.municipio is not None:
            return self.municipio.nome
        else:
            return None

    @property
    def municipio_sigla_uf(self):
        if self.municipio is not None:
            return self.municipio.sigla_uf
        else:
            return None


class ParceiroContato(entity.Entity, db.Model):

    attributes = ['id', 'contato', 'tag']

    parceiro_id = db.Column(
        db.CHAR(32), db.ForeignKey("parceiro.id"), nullable=False)
    contato = db.Column(db.String(100), nullable=False)

    def __init__(self, id, parceiro_id, contato,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.parceiro_id = parceiro_id
        self.contato = contato
