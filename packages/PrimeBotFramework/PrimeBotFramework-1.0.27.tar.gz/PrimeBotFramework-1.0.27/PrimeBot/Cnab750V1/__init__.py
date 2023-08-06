import os

class Cnab750V1():
    """
        Métodos de leitura de dados do CNAB 750 - Pagamentos Instantâneos
    """

    def retornar_arquivos_diretorio(self, caminho_diretorio: str) -> list:
        """Retorna os arquivos de um diretorio

        Args:
            caminho_diretorio (str): caminho do diretorio

        Returns:
            list: caminho dos arquivos encontrados
        """
        arquivos = []
        for filename in os.listdir(caminho_diretorio):
            file_path = os.path.join(caminho_diretorio, filename)
            if os.path.isfile(file_path):
                arquivos.append(file_path)
        return arquivos

    def ler_arquivo(self, caminho_arquivo: str) -> list:
        """Efetua a leitura do arquivo de retorno

        Args:
            caminho_arquivo (str): path do arquivo de retorno

        Returns:
            list: linhas do arquivo
        """
        with open(caminho_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()
        return linhas

    def identificar_versao_arquivo(self, linhas: list) -> str:
        """Identificar qual a versão do arquivo

        Args:
            linhas (list): conteudo do arquivo

        Returns:
            str: versão do arquivo cnab 750
        """
        return self.extrair_campo(linhas[0], 741, 744)

    def identificar_codigo_registro(self, linha: str) -> str:
        """Identificar qual o tipo de registro

        Args:
            linha (str): linha do arquivo lido

        Returns:
            str: codigo de registro
        """
        codigo_registro = self.extrair_campo(linha, 0, 0)
        if codigo_registro == '0':
            return 'HEADER'
        elif codigo_registro == '1':
            return 'DETALHE'
        if codigo_registro == '4':
            return 'EMV'
        if codigo_registro == '9':
            return 'TRAILER'
        else:
            return ''
        
    def extrair_campo(self, linha: str, index_ini: int, index_fim: int) -> str:
        """Extrai um valor de um campo

        Args:
            linha (str): linha com as informações
            index_ini (int): indice do início
            index_fim (int): indice do fim

        Returns:
            str: dado
        """
        if index_ini == index_fim:
            return linha[index_ini].strip()
        else:
            return linha[index_ini:index_fim].strip()
    
    def extrair(self, tipo_arquivo: str, linhas: list) -> list:
        """Extrai os dados do arquivo

        Args:
            tipo_arquivo (str): tipo 'remessa' ou tipo 'retorno'
            linhas (list): linhas do arquivo

        Returns:
            list[dict]: lista de dicionarios contendo a informação de cada linha
        """
        dados = []
        for linha in linhas:
            versao_arquivo = self.identificar_versao_arquivo(linhas)
            codigo_registro = self.identificar_codigo_registro(linha)
            if codigo_registro == 'HEADER':
                dados.append(self.leitura_header(versao_arquivo, tipo_arquivo, linha))
            elif codigo_registro == 'DETALHE':
                dados.append(self.leitura_detalhe(versao_arquivo, tipo_arquivo, linha))
            elif codigo_registro == 'TRAILER':
                dados.append(self.leitura_trailer(versao_arquivo, tipo_arquivo, linha))
            else:
                raise('Erro ao realizar a leitura! COdigo de Registro de retorno não identificado.')
        return dados
            
    def leitura_header(self, versao_arquivo: str, tipo_arquivo: str, linha: str) -> dict:
        """Efetua a leitura do header

        Args:
            versao_arquivo (str): versão do layout CNAB750
            tipo_arquivo (str): tipo 'remessa' ou tipo 'retorno'
            linha (str): dados da linha

        Returns:
            dict: dados do header
        """
        if versao_arquivo == '001' and tipo_arquivo == 'retorno':
            dict_dados = {'TIPO_DE_REGISTRO':self.extrair_campo(linha, 0, 0),
                        'CODIGO_DE_RETORNO':self.extrair_campo(linha, 1, 1),
                        'LITERAL_DE_RETORNO':self.extrair_campo(linha, 2, 9),
                        'CODIGO_DO_SERVIÇO':self.extrair_campo(linha, 9, 11),
                        'LITERAL_DE_SERVIÇO':self.extrair_campo(linha, 11, 26),
                        'ISPB_PARTICIPANTE':self.extrair_campo(linha, 26, 34),
                        'CODIGO_DE_INSCRIÇAO':self.extrair_campo(linha, 34, 36),
                        'CPF_CNPJ':self.extrair_campo(linha, 36, 50),
                        'AGÊNCIA':self.extrair_campo(linha, 50, 54),
                        'CONTA':self.extrair_campo(linha, 54, 74),
                        'TIPO_CONTA':self.extrair_campo(linha, 74, 78),
                        'CHAVE_PIX':self.extrair_campo(linha, 78, 155),
                        'DATA_DE_GERAÇAO':self.extrair_campo(linha, 155, 163),
                        'CODIGO_DO_CONVENIO':self.extrair_campo(linha, 163, 193),
                        'EXCLUSIVO_PSP_RECEBEDOR':self.extrair_campo(linha, 193, 253),
                        'CODIGOS_DE_ERRO':self.extrair_campo(linha, 253, 283),
                        'BRANCOS':self.extrair_campo(linha, 283, 741),
                        'VERSAO_DO_ARQUIVO':self.extrair_campo(linha, 741, 744),
                        'NUMERO_SEQÜENCIAL_DO_ARQUIVO':self.extrair_campo(linha, 744, 750)}
        return dict_dados
    
    def leitura_detalhe(self, versao_arquivo: str, tipo_arquivo: str, linha: str) -> dict:
        """Efetua a leitura do detalhe

        Args:
            versao_arquivo (str): versão do layout CNAB750
            tipo_arquivo (str): tipo 'remessa' ou tipo 'retorno'
            linha (str): dados da linha

        Returns:
            dict: dados do detalhe
        """
        if versao_arquivo == '001' and tipo_arquivo == 'retorno':
            dict_dados = {'TIPO_DE_REGISTRO':self.extrair_campo(linha, 0, 0),
                        'ISPB_PARTICIPANTE':self.extrair_campo(linha, 1, 9),
                        'CODIGO_DE_INSCRIÇAO':self.extrair_campo(linha, 9, 11),
                        'CPF_CNPJ':self.extrair_campo(linha, 11, 25),
                        'AGÊNCIA':self.extrair_campo(linha, 25, 29),
                        'CONTA':self.extrair_campo(linha, 29, 49),
                        'TIPO_CONTA':self.extrair_campo(linha, 49, 53),
                        'CHAVE_PIX':self.extrair_campo(linha, 53, 130),
                        'TIPO_COBRANÇA':self.extrair_campo(linha, 130, 130),
                        'COD._DO_MOVIMENTO':self.extrair_campo(linha, 131, 133),
                        'DATA_DO_MOVIMENTO':self.extrair_campo(linha, 133, 141),
                        'IDENTIFICADOR':self.extrair_campo(linha, 141, 176),
                        'EXPIRAÇAO':self.extrair_campo(linha, 176, 191),
                        'DATA_DE_VENCIMENTO':self.extrair_campo(linha, 191, 199),
                        'VALOR ORIGINAL':self.extrair_campo(linha, 199, 216),
                        'VALOR JUROS':self.extrair_campo(linha, 216, 233),
                        'VALOR MULTA':self.extrair_campo(linha, 233, 250),
                        'VALOR_DESCONTO/ABATIMENTO':self.extrair_campo(linha, 250, 267),
                        'VALOR_FINAL':self.extrair_campo(linha, 267, 284),
                        'VALOR_PAGO':self.formata_valor(self.extrair_campo(linha, 284, 301), 2),
                        'TARIFA_DE_COBRANÇA':self.extrair_campo(linha, 301, 318),
                        'CODIGO_DE_INSCRIÇAO_DEVEDOR':self.extrair_campo(linha, 318, 320),
                        'CPF_CNPJ_DEVEDOR':self.extrair_campo(linha, 320, 334),
                        'MENSAGEM_PAGADOR_FINAL':self.extrair_campo(linha, 334, 474),
                        'CODIGO_DE_INSCRIÇAO_PAGADOR_FINAL':self.extrair_campo(linha, 474, 476),
                        'CPF_CNPJ_PAGADOR_FINAL':self.extrair_campo(linha, 476, 490),
                        'NOME_PAGADOR_FINAL':self.extrair_campo(linha, 490, 630),
                        'COD._DE_LIQUIDAÇAO':self.extrair_campo(linha, 630, 632),
                        'END_TO_END_ID':self.extrair_campo(linha, 632, 667),
                        'CODIGOS_DE_ERRO':self.extrair_campo(linha, 667, 697),
                        'BRANCOS':self.extrair_campo(linha, 697, 744),
                        'NUMERO_SEQÜENCIAL':self.extrair_campo(linha, 744, 750)}
        return dict_dados

    def leitura_trailer(self, versao_arquivo: str, tipo_arquivo: str, linha: str) -> dict:
        """Efetua a leitura do trailer

        Args:
            versao_arquivo (str): versão do layout CNAB750
            tipo_arquivo (str): tipo 'remessa' ou tipo 'retorno'
            linha (str): dados da linha

        Returns:
            dict: dados do trailer
        """
        if versao_arquivo == '001' and tipo_arquivo == 'retorno':
            dict_dados = {'TIPO_DE_REGISTRO':self.extrair_campo(linha, 0, 0),
                        'CODIGO_DE_RETORNO':self.extrair_campo(linha, 1, 1),
                        'CODIGO_DE_SERVIÇO':self.extrair_campo(linha, 2, 4),
                        'ISPB':self.extrair_campo(linha, 4, 12),
                        'CODIGOS_DE_ERRO':self.extrair_campo(linha, 12, 42),
                        'BRANCOS':self.extrair_campo(linha, 42, 729),
                        'QTDE_DE_DETALHES':self.extrair_campo(linha, 729, 744),
                        'NUMERO_SEQÜENCIAL':self.extrair_campo(linha, 745, 750)}
        return dict_dados
    
    def formata_valor(self, valor: str, qtd_decimais: int) -> str:
        """Formata um valor para eliminar os zeros a esquerda e inserir a vírgula para marcação dos decimais.

        Args:
            valor (str): valor a ser formatado
            qtd_decimais (int): quantidade de decimais

        Returns:
            str: valor formatado
        """
        valor_sem_zero_esquerda = valor.lstrip('0')
        return valor_sem_zero_esquerda[:-qtd_decimais] + "," + valor_sem_zero_esquerda[-qtd_decimais:]
