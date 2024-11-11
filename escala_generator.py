from datetime import datetime, timedelta
import calendar
from functools import lru_cache

@lru_cache(maxsize=None)
def obter_domingos(data_inicio):
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    domingos = []

    for dia in range(1, calendar.monthrange(data_atual.year, data_atual.month)[1] + 1):
        data_dia = data_atual.replace(day=dia)
        if data_dia.weekday() == 6:  # Domingo é o dia 6 da semana
            domingos.append(data_dia)

    return domingos

def gerar_escala_turnos_por_funcao(funcionarios_por_funcao, data_inicio, ferias, dias_trabalho=5, dias_folga=1):
    escala_final = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')

    domingos = obter_domingos(data_inicio)
    num_dias_no_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]

    for funcao, funcionarios in funcionarios_por_funcao.items():
        # Filtra funcionários que não estão de férias ou atestado
        funcionarios_ativos = {nome: dados for nome, dados in funcionarios.items() 
                             if nome not in ferias}
        
        escala = {nome: [] for nome in funcionarios_ativos.keys()}
        
        domingos_folga = {nome: domingos[i % len(domingos)] for i, nome in enumerate(funcionarios_ativos.keys())}

        for i, nome in enumerate(funcionarios_ativos.keys()):
            turno_atual = funcionarios_ativos[nome]['turno']
            horario_atual = funcionarios_ativos[nome]['horario']

            inicio_folga = (i // (dias_trabalho + dias_folga)) * (dias_trabalho + dias_folga) + (i % (dias_trabalho + dias_folga))
            domingo_folga = domingos_folga[nome]

            for dia in range(num_dias_no_mes):
                data_turno = data_atual.replace(day=dia + 1)
                ciclo_dia = (dia + inicio_folga) % (dias_trabalho + dias_folga)
                dia_na_escala = ciclo_dia < dias_trabalho

                if data_turno.date() == domingo_folga.date():
                    escala[nome].append(f"Folga (Domingo)")
                elif data_turno.weekday() == 6:  # É domingo, mas não é o domingo de folga
                    escala[nome].append(f"{turno_atual}: {horario_atual}")
                elif dia_na_escala:
                    escala[nome].append(f"{turno_atual}: {horario_atual}")
                else:
                    escala[nome].append(f"Folga")

        escala_final[funcao] = escala

    return escala_final