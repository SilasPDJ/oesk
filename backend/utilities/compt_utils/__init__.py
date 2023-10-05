from datetime import date
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from backend.utilities.default.sets import Now


def compt_to_date_obj(compt) -> date:
    return Now.str_to_date(compt, "%m-%Y")


def calc_date_compt_offset(m_cont=-1, y_cont=0, past_only=True) -> date:
    """ - returns `date` object based on the two first arguments
    Args:
        m_cont (int, optional): referes to month before/after now. Defaults to -1.
        y_cont (int, optional): refers to year before/after now. Defaults to 0.
        past_only (bool, optional): only returns the past, because of competencia.
        Defaults to True.
    Returns:
        date: datetime.date making the counters with relativedelta
    """
    month = datetime.now().month
    year = datetime.now().year

    now_date = date(year, month, 1)

    if past_only:
        m_cont = m_cont * (-1) if m_cont > 0 else m_cont
        y_cont = y_cont * (-1) if y_cont > 0 else y_cont
        # force to be negative

    now_date = now_date + relativedelta(months=m_cont)
    now_date = now_date + relativedelta(years=y_cont)
    return now_date


def get_compt(m_cont=-1, y_cont=0, past_only=True, format_str='-') -> str:
    """ - returns `str` based on the two first arguments with the format option,
    calls compt_as_date first,
    Args:
        m_cont (int, optional): referes to month before/after now. Defaults to -1.
        y_cont (int, optional): refers to year before/after now. Defaults to 0.
        past_only (bool, optional): only returns the past, because of competencia.
        Defaults to True.
        format (str, optional): if len(format) > 2 it retuns what is set on the string.
        Defaults to 2 characters + '%m-%Y'
    Returns:
        str: A string representing the month and year in the specified format.
    """
    now_date = calc_date_compt_offset(m_cont, y_cont, past_only)
    if len(format_str) <= 2:
        return now_date.strftime(f'%m{format_str}%Y')
    else:
        return now_date.strftime(format_str)


def get_all_valores(sem_ret, com_ret, anexo, valor_tot) -> list:
    def split_sep_vals(val, withme=';'):
        val = str(val)
        try:
            return val.split(withme)
            # print('valorA;valorB___valorC;valorD  valorTotal')

        except AttributeError:
            return list(val)

    def greater_than(l1, l2):
        return len(l1) > len(l2)

    sem_ret = split_sep_vals(sem_ret)
    com_ret = split_sep_vals(com_ret)
    anexo = split_sep_vals(anexo)

    # retorna False para não prosseguir, pois o número de anexos não bate com o número de valores entre ;
    if greater_than(sem_ret, com_ret):
        if greater_than(anexo, sem_ret) or greater_than(sem_ret, anexo):
            return False
    elif greater_than(com_ret, sem_ret):
        if greater_than(anexo, com_ret) or greater_than(com_ret, anexo):
            return False
    else:
        # tanto faz porque com_ret == sem_ret
        if greater_than(anexo, sem_ret) or greater_than(sem_ret, anexo):
            return False

    all_valores = []
    soma_total = 0
    for c in range(len(anexo)):
        try:
            sr = sem_ret[c]
        except IndexError:
            sr = 0
        try:
            cr = com_ret[c]
        except IndexError:
            cr = 0
        # Se o valor não foi escrito, é considerado 0

        anx = anexo[c]
        try:
            soma_total += float(sr) + float(cr)
        except ValueError:
            return False
        all_valores.append({'valor_n_retido': sr,
                            'valor_retido': cr, 'anexo': anx})

    if float(soma_total) == float(valor_tot):
        return all_valores
    else:
        print(soma_total, type(soma_total), valor_tot, type(valor_tot))
        print('Vou retornar None')


def ate_atual_compt(compt_atual, first_compt=None):
    # yield list_compts
    if first_compt is None or first_compt == compt_atual:
        yield compt_atual
    else:
        first_compt = first_compt.split('-')
        if len(first_compt) == 1:
            first_compt = first_compt.split('/')
        first_compt = [int(val) for val in first_compt]
        first_compt = date(first_compt[1], first_compt[0], 1)

        # next_date = first_compt + relativedelta.relativedelta(months=1)

        last_compt = compt_atual.split('-')
        # compt = [int(c) for c in compt]
        last_compt = [int(v) for v in last_compt]
        last_compt = date(last_compt[1], last_compt[0], 1)

        # list_compts = []
        while first_compt <= last_compt:
            compt = first_compt
            first_compt = first_compt + \
                          relativedelta.relativedelta(months=1)
            compt_appended = f'{compt.month:02d}-{compt.year}'
            # list_compts.append(compt_appended)
            yield compt_appended
    # O objetivo dessa função é retornar yildar um range de compt, partindo do first_compt
