import functools
import typing

__all__ = [
    'cvm_codes'
]

@functools.lru_cache
def _cvm_codes() -> typing.List[str]:
    return [
        '24465', # BANCO AGIBANK S.A.
        '1023',  # BCO BRASIL S.A.
        '1120',  # BCO ESTADO DE SERGIPE S.A. - BANESE
        '1155',  # BANESTES S.A. - BCO EST ESPIRITO SANTO
        '1171',  # BCO ESTADO DO PARA S.A.
        '1201',  # BANCO BERJ S.A.
        '1210',  # BCO ESTADO DO RIO GRANDE DO SUL S.A.
        '1228',  # BCO NORDESTE DO BRASIL S.A.
        '1309',  # BCO MERCANTIL DE INVESTIMENTOS S.A.
        '1325',  # BCO MERCANTIL DO BRASIL S.A.
        '1384',  # BCO ALFA DE INVESTIMENTO S.A.
        '14052', # BFB LEASING S.A. ARRENDAMENTO MERCANTIL
        '14206', # BRB BCO DE BRASILIA S.A.
        '14214', # DIBENS LEASING S.A. - ARREND.MERCANTIL
        '15121', # CCB BRASIL ARRENDAMENTO MERCANTIL S.A.
        '15890', # MERCANTIL DO BRASIL LEASING SA
        '1724',  # BMG LEASING S.A. - ARREND. MERCANTIL
        '18554', # PAN ARRENDAMENTO MERCANTIL S.A.
        '19348', # ITAU UNIBANCO HOLDING S.A.
        '19640', # BRADESCO LEASING S.A. ARREND MERCANTIL
        '19755', # HSBC LEASING ARRENDAMENTO MERCANTIL (BRASIL) S/A
        '19844', # SAFRA LEASING SA ARRENDAMENTO MERCANTIL
        '20133', # BV LEASING - ARRENDAMENTO MERCANTIL S.A.
        '20532', # BCO SANTANDER (BRASIL) S.A.
        '20559', # SANTANDER LEASING S.A. ARRENDAMENTO MERCANTIL
        '20567', # BCO PINE S.A.
        '20680', # BANCO SOFISA SA
        '20729', # PARANA BCO S.A.
        '20753', # BANCO CRUZEIRO DO SUL SA
        '20796', # BCO DAYCOVAL S.A.
        '20885', # BCO INDUSVAL S.A.
        '20958', # BCO ABC BRASIL S.A.
        '21113', # BANCO INDUSTRIAL E COMERCIAL S/A
        '21199', # BCO PAN S.A.
        '21377', # BANCO INDUSTRIAL DO BRASIL
        '21466', # BANCO RCI BRASIL S.A.
        '21512', # ÁQUILLA SECURITIZADORA S.A.
        '22616', # BCO BTG PACTUAL S.A.
        '22950', # AR CAPITAL SECURITIES COMPANHIA SECURITIZADORA S.A.
        '22993', # COMPANHIA DE CRÉDITO FINANCIAMENTO E INVESTIMENTO RCI BRASIL
        '23477', # LOGOS COMPANHIA SECURITIZADORA S/A
        '24406', # BANCO INTER S.A.
        '24600', # BANCO BMG S/A
        '3891',  # FINANCEIRA ALFA S.A.- CRED FINANC E INVS
        '6076',  # FINANSINOS S.A.- CREDITO FINANC E INVEST
        '80063', # BCO PATAGONIA S.A.
        '80152', # PPLA PARTICIPATIONS LTD.
        '80160', # BANCO SANTANDER S.A.
        '8540',  # MERCANTIL BRASIL FINANC S.A. C.F.I.
        '906',   # BCO BRADESCO S.A.
        '922'    # BCO AMAZONIA S.A.
    ]

def cvm_codes() -> typing.List[str]:
    """
    Returns CVM codes of companies that use the
    account layout of financial institutions.
    """

    return _cvm_codes().copy()