import pandas as pd
import requests
import time
import sys

def consultar_cnpj(cnpj):
    # Remover o prefixo "BR" se existir
    cnpj = cnpj.replace("BR", "").strip()
    
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                if 'situacao' in data:
                    return data['situacao']
                else:
                    return data.get('message', 'Erro desconhecido')
            except ValueError:
                return 'Resposta inválida da API'
        else:
            return f"Erro {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {str(e)}"

def atualizar_planilha(input_path, output_path):
    # Ler a planilha do Excel
    df = pd.read_excel(input_path)

    # Verificar se a coluna 'CNPJ' existe
    if 'CNPJ' not in df.columns:
        raise ValueError("A coluna 'CNPJ' não foi encontrada na planilha.")

    # Adicionar uma coluna para o status dos CNPJs
    df['Status'] = None

    # Processar em lotes de 3 e esperar 1 minuto entre os lotes
    batch_size = 3
    wait_time = 60  # 1 minuto em segundos
    num_rows = len(df)
    num_batches = (num_rows + batch_size - 1) // batch_size

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = min(start_index + batch_size, num_rows)
        
        df.loc[start_index:end_index-1, 'Status'] = df.loc[start_index:end_index-1, 'CNPJ'].apply(consultar_cnpj)
        
        # Mensagem de progresso
        sys.stdout.write(f"\rProcessando lote {batch_index + 1}/{num_batches}... {end_index}/{num_rows} linhas processadas")
        sys.stdout.flush()
        
        if end_index < num_rows:  # Não esperar após o último lote
            time.sleep(wait_time)

    # Mensagem final
    sys.stdout.write("\nProcessamento concluído. Salvando planilha...\n")
    sys.stdout.flush()

    # Salvar a nova planilha formatada
    df.to_excel(output_path, index=False)

    # Mensagem final após salvar
    sys.stdout.write("Planilha salva com sucesso!\n")
    sys.stdout.flush()

# Caminhos para a planilha de entrada e saída
input_path = r'C:\Users\Jose Alexandre\Desktop\planilhas\prospects.xlsx'
output_path = r'C:\Users\Jose Alexandre\Desktop\planilhas\prospects-novo.xlsx'

# Atualizar a planilha
atualizar_planilha(input_path, output_path)

