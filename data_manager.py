import json
import os
import streamlit as st
from modelsss import Empresa, Funcionario
from datetime import datetime, date

# Atualize o caminho do arquivo
arquivo_empresas = os.path.join('data', 'empresas.json')

def carregar_empresas():
    try:
        with open('empresa.json', 'r') as f:
            dados = json.load(f)
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON. Criando um novo arquivo.")
        dados = {}
    except FileNotFoundError:
        print("Arquivo não encontrado. Criando um novo arquivo.")
        dados = {}

    empresas = {}
    for nome, empresa_dados in dados.items():
        empresa = Empresa(nome)
        for turno, funcionarios in empresa_dados['funcionarios'].items():
            empresa.funcionarios[turno] = [criar_funcionario(func) for func in funcionarios]
        empresa.funcionarios_em_ferias = [criar_funcionario(func) for func in empresa_dados.get('funcionarios_em_ferias', [])]
        empresa.folguistas = [criar_funcionario(func) for func in empresa_dados.get('folguistas', [])]
        empresa.folguistas_escala = empresa_dados.get('folguistas_escala')
        empresas[nome] = empresa
    
    return empresas

def salvar_empresas(empresas):
    dados = {}
    for nome, empresa in empresas.items():
        dados[nome] = {
            'nome': empresa.nome,
            'funcionarios': {
                turno: [func.to_dict() for func in funcionarios]
                for turno, funcionarios in empresa.funcionarios.items()
            },
            'funcionarios_em_ferias': [func.to_dict() for func in empresa.funcionarios_em_ferias],
            'folguistas': [func.to_dict() for func in empresa.folguistas],
            'folguistas_escala': empresa.folguistas_escala
        }
    
    with open('empresa.json', 'w') as f:
        json.dump(dados, f, indent=4, default=json_serial)

def criar_funcionario(dados):
    funcionario = Funcionario(
        dados['nome'],
        dados['funcao'],
        dados['familia_letras'],
        dados['horario_turno'],
        datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date(),
        dados['turno']
    )
    if dados['ferias_atual']:
        funcionario.ferias_atual = {
            'inicio': datetime.strptime(dados['ferias_atual']['inicio'], '%Y-%m-%d').date(),
            'fim': datetime.strptime(dados['ferias_atual']['fim'], '%Y-%m-%d').date()
        }
    else:
        funcionario.ferias_atual = None
    funcionario.historico_ferias = [
        {
            'inicio': datetime.strptime(ferias['inicio'], '%Y-%m-%d').date(),
            'fim': datetime.strptime(ferias['fim'], '%Y-%m-%d').date()
        }
        for ferias in dados['historico_ferias']
    ]
    return funcionario

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
