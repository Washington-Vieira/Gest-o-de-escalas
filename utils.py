import pandas as pd

def transformar_escala_para_dataframe(escala_por_funcao, num_dias_no_mes):
    colunas = ['Funcionário'] + [f'Dia {i+1}' for i in range(num_dias_no_mes)]
    dados = []

    for funcao, escala in escala_por_funcao.items():
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
