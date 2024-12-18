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

def gerar_escala_turnos_por_funcao(funcionarios_por_funcao, data_inicio, afastamentos_info, dias_trabalho=5, dias_folga=1):
    escala_final = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    num_dias_no_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]
    domingos = obter_domingos(data_inicio)

    for funcao, funcionarios in funcionarios_por_funcao.items():
        escala = {nome: [] for nome in funcionarios.keys()}
        domingos_folga = {nome: domingos[i % len(domingos)] for i, nome in enumerate(funcionarios.keys())}
        
        # Inicializar contadores
        dias_trabalhados = {nome: 0 for nome in funcionarios.keys()}
        ultima_folga = {nome: -2 for nome in funcionarios.keys()}
        folgas_no_mes = {nome: 0 for nome in funcionarios.keys()}
        folgas_por_dia = {dia: [] for dia in range(num_dias_no_mes)}
        
        # Distribuir os inícios dos ciclos 5x1 de forma escalonada
        num_funcionarios = len(funcionarios)
        inicio_ciclo = {nome: i % 6 for i, nome in enumerate(funcionarios.keys())}

        for dia in range(num_dias_no_mes):
            data_turno = data_atual.replace(day=dia + 1)
            
            for nome in funcionarios.keys():
                turno_atual = funcionarios[nome]['turno']
                horario_atual = funcionarios[nome]['horario']
                domingo_folga = domingos_folga[nome]
                
                # Verifica afastamentos
                em_afastamento = False
                if nome in afastamentos_info:
                    afastamento = afastamentos_info[nome]
                    data_inicio_afastamento = afastamento['data_inicio']
                    data_fim_afastamento = afastamento['data_fim']
                    em_afastamento = data_inicio_afastamento <= data_turno.date() <= data_fim_afastamento

                if em_afastamento:
                    escala[nome].append("F/A")
                    dias_trabalhados[nome] = 0
                    continue

                # Verifica se é domingo de folga
                if data_turno.date() == domingo_folga.date():
                    if nome not in folgas_por_dia[dia]:
                        escala[nome].append("Folga (Domingo)")
                        ultima_folga[nome] = dia
                        folgas_no_mes[nome] += 1
                        folgas_por_dia[dia].append(nome)
                        dias_trabalhados[nome] = 0
                        continue

                # Verifica se completou o ciclo de 5 dias trabalhados
                if dias_trabalhados[nome] >= 5 and len(folgas_por_dia[dia]) < 1:
                    escala[nome].append("Folga")
                    ultima_folga[nome] = dia
                    folgas_no_mes[nome] += 1
                    folgas_por_dia[dia].append(nome)
                    dias_trabalhados[nome] = 0
                else:
                    # Dia normal de trabalho
                    escala[nome].append(f"{turno_atual}: {horario_atual}")
                    dias_trabalhados[nome] += 1

        escala_final[funcao] = escala

    return escala_final

def gerar_escala_folguistas(folguistas_info, data_inicio, afastamentos_info):
    escala = {}
    data_atual = datetime.strptime(data_inicio, '%Y-%m-%d')
    num_dias_no_mes = calendar.monthrange(data_atual.year, data_atual.month)[1]
    
    # Inicializar escala para cada folguista
    for nome in folguistas_info.keys():
        escala[nome] = []
        
        # Para cada dia do mês
        for dia in range(num_dias_no_mes):
            data_turno = data_atual.replace(day=dia + 1)
            
            # Verifica se está em afastamento (férias ou atestado)
            em_afastamento = False
            if nome in afastamentos_info:
                afastamento = afastamentos_info[nome]
                data_inicio_afastamento = afastamento['data_inicio']
                data_fim_afastamento = afastamento['data_fim']
                em_afastamento = data_inicio_afastamento <= data_turno.date() <= data_fim_afastamento
            
            if em_afastamento:
                escala[nome].append("F/A")
            else:
                # Lógica para folgas e dias disponíveis
                if data_turno.weekday() == 6:  # Domingo
                    escala[nome].append("Folga")
                else:
                    escala[nome].append("")  # Espaço vazio
    
    return escala