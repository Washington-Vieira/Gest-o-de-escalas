import pandas as pd
from datetime import datetime
import calendar

def traduzir_dia_semana(dia_ingles, formato_completo=False):
    """Traduz o dia da semana para português"""
    traducao_completa = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    traducao_curta = {
        'Mon': 'Seg',
        'Tue': 'Ter',
        'Wed': 'Qua',
        'Thu': 'Qui',
        'Fri': 'Sex',
        'Sat': 'Sáb',
        'Sun': 'Dom'
    }
    return traducao_completa.get(dia_ingles, dia_ingles) if formato_completo else traducao_curta.get(dia_ingles, dia_ingles)

def transformar_escala_para_dataframe(escala_por_funcao, num_dias):
    dataframes = []
    
    for funcao, escala in escala_por_funcao.items():
        # Criar lista de colunas com dias e dias da semana
        data_atual = datetime.now().replace(day=1)
        colunas = ['Funcionário']
        
        for dia in range(1, num_dias + 1):
            data = data_atual.replace(day=dia)
            dia_semana = traduzir_dia_semana(data.strftime('%a'))
            colunas.append(f"{dia}\n{dia_semana}")
        
        # Criar DataFrame
        dados = []
        for nome, escala_func in escala.items():
            linha = [nome] + escala_func
            dados.append(linha)
        
        df = pd.DataFrame(dados, columns=colunas)
        dataframes.append(df)
    
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    return pd.DataFrame()

def transformar_escala_folguistas_para_dataframe(escala_folguistas, data_inicio):
    # Criar lista de colunas com dias e dias da semana
    num_dias = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
    colunas = ['Folguista']
    
    for dia in range(1, num_dias + 1):
        data = data_inicio.replace(day=dia)
        dia_semana = traduzir_dia_semana(data.strftime('%a'))
        colunas.append(f"{dia}\n{dia_semana}")
    
    # Criar DataFrame
    dados = []
    for nome, escala in escala_folguistas.items():
        linha = [nome] + escala
        dados.append(linha)
    
    return pd.DataFrame(dados, columns=colunas)

funcoes_familias = {
    "Caixa": "C",
    "Frentista": "F",
    "Gerente": "G",
    "Subgerente": "SG",
    "Lubrificador": "L",
    "Zelador": "Z"
}

turnos_funcionarios = ["T1", "T2", "T3"]
