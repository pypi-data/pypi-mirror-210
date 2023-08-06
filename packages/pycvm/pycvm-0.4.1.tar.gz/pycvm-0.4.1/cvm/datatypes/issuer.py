import dataclasses
import typing
import datetime
from enum import IntEnum, auto
from cvm  import datatypes

__all__ = [
    'IssuerStatus',
    'IssuerCompany'
]

class IssuerStatus(IntEnum):
    PRE_OPERATIONAL_PHASE           = auto()
    OPERATIONAL_PHASE               = auto()
    JUDICIAL_RECOVERY_OR_EQUIVALENT = auto()
    EXTRAJUDICIAL_RECOVERY          = auto()
    BANKRUPT                        = auto()
    EXTRAJUDICIAL_LIQUIDATION       = auto()
    JUDICIAL_LIQUIDATION            = auto()
    STALLED                         = auto()

@dataclasses.dataclass(init=True)
class IssuerCompany:
    """Implements a data structure for Item 1 of CVM Instruction 480/2009."""

    corporate_name: str
    """(1.1) 'Nome empresarial'"""

    corporate_name_last_changed: typing.Optional[datetime.date]
    """(1.2) 'Data da última alteração do nome empresarial'"""

    previous_corporate_name: typing.Optional[str]
    """(1.3) 'Nome empresarial anterior'"""

    establishment_date: datetime.date
    """(1.4) 'Data de constituição'"""

    cnpj: datatypes.CNPJ
    """(1.5) 'CNPJ'"""

    cvm_code: str
    """1.6 Código CVM"""

    cvm_registration_date: datetime.date
    """(1.7) 'Data de registro na CVM'"""

    cvm_registration_category: datatypes.RegistrationCategory
    """(1.8) 'Categoria de registro na CVM'"""

    cvm_registration_category_started: datetime.date
    """(1.9) 'Data de registro na atual categoria CVM'"""

    cvm_registration_status: datatypes.RegistrationStatus
    """(1.10) 'Situação de registro na CVM'"""

    cvm_registration_status_started: datetime.date
    """(1.11) 'Data de início da situação do registro na CVM'"""

    home_country: typing.Optional[str]
    """(1.12) 'País de origem'"""

    securities_custody_country: typing.Optional[str]
    """(1.13) 'País em que os valores mobiliários estão custodiados'"""

    trading_admissions: typing.List[datatypes.TradingAdmission]
    """(1.14, 1.15) Collection of foreign countries admitted to trading and date of admission."""

    industry: datatypes.Industry
    """(1.16) 'Setor de atividade'"""

    issuer_status: IssuerStatus
    """(1.17) 'Situação do emissor'"""

    issuer_status_started: datetime.date
    """(1.18) 'Data de início da situação do emissor'"""

    controlling_interest: datatypes.ControllingInterest
    """(1.19) 'Espécie de controle acionário'"""

    controlling_interest_last_changed: typing.Optional[datetime.date]
    """(1.20) 'Data da última alteração da espécie de controle acionário'"""

    fiscal_year_end_day: int
    """(1.21) 'Data de encerramento do exercício social' (day)"""

    fiscal_year_end_month: int
    """(1.21) 'Data de encerramento do exercício social' (month)"""

    fiscal_year_last_changed: typing.Optional[datetime.date]
    """(1.22) 'Data da última alteração do exercício social'"""

    webpage: str
    """(1.23) 'Página do emissor na rede mundial de computadores'"""

    communication_channels: typing.List[datatypes.CommunicationChannel]
    """(1.24) 'Canais de comunicação utilizados pelo emissor'"""

    addresses: typing.List[datatypes.Address]
    """(1.25) 'Endereço'"""

    contact: datatypes.Contact
    """(1.26, 1.27, 1.28, 1.29, 1.30) Contact data"""

    __slots__ = (
        'corporate_name',
        'corporate_name_last_changed',
        'previous_corporate_name',
        'establishment_date',
        'cnpj',
        'cvm_code',
        'cvm_registration_date',
        'cvm_registration_category',
        'cvm_registration_category_started',
        'cvm_registration_status',
        'cvm_registration_status_started',
        'home_country',
        'securities_custody_country',
        'trading_admissions',
        'industry',
        'issuer_status',
        'issuer_status_started',
        'controlling_interest',
        'controlling_interest_last_changed',
        'fiscal_year_end_day',
        'fiscal_year_end_month',
        'fiscal_year_last_changed',
        'webpage',
        'communication_channels',
        'addresses',
        'contact'
    )