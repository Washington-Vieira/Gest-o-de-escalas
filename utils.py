import pandas as pd

def transformar_escala_para_dataframe(escala, num_dias):
    """
    Transforma o dicionário de escala em um DataFrame
    """
    dados = []
    for funcao, funcionarios in escala.items():
        for nome, turnos in funcionarios.items():
            linha = [nome] + turnos
            dados.append(linha)
    
    colunas = ['Funcionário'] + [f'Dia {i+1}' for i in range(num_dias)]
    return pd.DataFrame(dados, columns=colunas)

def transformar_escala_folguistas_para_dataframe(escala, data_inicio):
    """
    Transforma o dicionário de escala dos folguistas em um DataFrame
    """
    num_dias = len(next(iter(escala.values())))
    colunas = ['Folguista'] + [f'Dia {i+1}' for i in range(num_dias)]
    dados = []
    
    for nome, dias in escala.items():
        linha = [nome] + dias
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
