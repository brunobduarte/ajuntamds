from juncaoTools import JuncaoTools
from preProcessamento import PreProcessamento

import time
import sys
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Argumentos do Ajunta mds', argument_default=1)


    parser.add_argument('--cadunic', "-ca", required=True, metavar='nome_esquema.nome_tabela',
                        help="Entrada das tabelas de dados do Cadastro Unico.")

    parser.add_argument('--cnefe', "-cn", required=True, metavar='nome_esquema.nome_tabela',
                        help="Entrada das tabelas de dados do CNEFE")

    parser.add_argument('--threads', "-t", required=False, metavar='numero_threads', type=int, default=4,
                        help="Número de Thread que o programa irá ultilizar para processar os dados.")

    parser.add_argument('--preprocess', "-p", required=False, metavar='', nargs='?', default=0, const=1,
                        help="Força o pre-processamento dos dados.")

    parser.add_argument('--saida', "-s", required=False, metavar='nome_tabela', nargs='?', default=0, const=1,
                        help = "Saida padrão do programa. A tabela resultado será gravada no proprio banco de dados dentro do esquema resultados.")

    parser.add_argument('--saidacsv', "-sc", required=False, metavar='nome_arquivo.csv', nargs='?', default=0,
                        help="A saída do programa sera em formato em arquivo csv. A tabela resultado será gravada no proprio banco de dados dentro do esquema resultados.")

    parser.add_argument('--saidamult', "-sm", required=False, metavar='nome_arquivo.csv', nargs='?', default = 0, const = 1,
                        help="Multiplas saídas. O programa irá gerar a tabela de resultados dentro do banco de dados quanto em formato csv.")

    args = parser.parse_args()

    j = JuncaoTools(args.threads)

    prep = PreProcessamento()

    cadunicoEsquema = str(args.cadunic).split(".")[0]
    cadunicoTabela = str(args.cadunic).split(".")[1]

    cnefeEsquema = str(args.cnefe).split(".")[0]
    cnefeTabela = str(args.cnefe).split(".")[1]

    nomeTabelaResultado =""

   # print(args.preprocess)
    ini = time.time()
    if args.preprocess == 1:

        prep.testarseProcessado(cadunicoEsquema, cadunicoTabela)
        prep.preProcessarBaseCadUnico(cadunicoEsquema, cadunicoTabela)

        prep.testarseProcessado(cnefeEsquema, cnefeTabela)
        prep.preProcessarBaseCnefe(cnefeEsquema, cnefeTabela)

    if not prep.testarseProcessado(cadunicoEsquema, cadunicoTabela):
        prep.preProcessarBaseCadUnico(cadunicoEsquema, cadunicoTabela)

    if not prep.testarseProcessado(cnefeEsquema, cnefeTabela):
        prep.preProcessarBaseCnefe(cnefeEsquema, cnefeTabela)

    if args.saida == 0 and args.saidacsv == 0 and args.saidamult == 0:
        nomeTabelaResultado = cnefeTabela + cadunicoTabela

        #tipoResultado: 0 se saida padrão, dentro do banco
        #1: se for saida somente em formato CSV
        #2: se for resultado em tabela no banco e em formato csv
        j.juntarTabelas(cadunicoEsquema, cadunicoTabela, cnefeEsquema, cnefeTabela, nomeTabelaResultado, 0)

    if args.saida != 0 and args.saida != 1 and args.saidacsv == 0 and args.saidamult == 0:

        nomeTabelaResultado = args.saida
        j.juntarTabelas(cadunicoEsquema, cadunicoTabela, cnefeEsquema, cnefeTabela, nomeTabelaResultado, 0)


    if args.saida == 0 and args.saidacsv != 0 and args.saidamult == 0:

        #pre processando o pach.

        nomeTabelaResultado = str(args.saidacsv).replace("\\", "/")
        print(nomeTabelaResultado)
        j.juntarTabelas(cadunicoEsquema, cadunicoTabela, cnefeEsquema, cnefeTabela, nomeTabelaResultado, 1)

    if args.saida == 0 and args.saidacsv == 0 and args.saidamult != 0:
        # pre processando o pach.

        nomeTabelaResultado = str(args.saidamult).replace("\\", "/")
        print(nomeTabelaResultado)

        j.juntarTabelas(cadunicoEsquema, cadunicoTabela, cnefeEsquema, cnefeTabela, nomeTabelaResultado, 2)






   # j.juntarTabelas(cadunicoEsquema, cadunicoTabela, cnefeEsquema, cnefeTabela)



    #nomeTabelaResult = "resultado_" + nomeSchemaCadUnic.split("_")[2] + "_" + tabelaCnefe




    #j.juntarTabelas("cad_unic_2019", "rr10000", "cnefe_rr_14", "14_rr")
    ##Por enquanto estou chamando as funções manualmente pois o programa ainda está em faze de teste.
    #j.juntarTabelas("cad_unic_2019", "base_cad_unic_2019_35", "cnefe_sp_35", "35_sp")
    fim = time.time()
    print("\n=========================================\n")
    print("Tempo: " + str(fim - ini))