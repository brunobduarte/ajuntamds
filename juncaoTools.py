import math
import time

from dbtools import Dbtool
from similaridade import Similaridade


class JuncaoTools:
    def __init__(self):
        self.bd = Dbtool("localhost", "5432", "mds-cad-unico", "postgres", "2631")
        self.similar = Similaridade()

    def printarLista(self, lista):
        print("==>> Resutados finais :")
        for int in lista:
            print(int)

    def juncaoTabelas(self, nomeSchemaCadUnic, tabelaCadUnic, nomeScehemaCnefe, tabelaCnefe):

        print("Buscando os dados do  cad unico no baco.")

        self.conjuntoCadUnic = self.bd.selecionarTabela(nomeSchemaCadUnic, [tabelaCadUnic], ["*"], '', 0)

        print("Buscando Indexadores.")

        self.indexColCadUnic = self.bd.retornarColunasIndex(nomeSchemaCadUnic, tabelaCadUnic)
        self.tiposColCadUnic = self.bd.retornarColunasTypes(nomeSchemaCadUnic, tabelaCadUnic)

        print("Criando grupos de cidades.")
        nometabelagrupoAux = tabelaCadUnic + "aux"

        self.bd.criarTabelaDeGrupos(nomeSchemaCadUnic, nometabelagrupoAux, tabelaCadUnic, "cod_munic_ibge_5_fam", 1)

        self.numInstancidadesCadUnicDic = dict(
            self.bd.selecionarTabela(nomeSchemaCadUnic, [nometabelagrupoAux], ["*"], '', 0))
        self.codCidadesOrdenadaslist = list(self.numInstancidadesCadUnicDic.keys())

        cidadeCorrente = 0
        self.conjuntoCidadeCnefe = []

        mascaraEnderecoCadUnic = [self.indexColCadUnic["nom_tip_logradouro_fam"],
                                  self.indexColCadUnic["nom_tit_logradouro_fam"],
                                  self.indexColCadUnic["nom_logradouro_fam"],
                                  self.indexColCadUnic["num_logradouro_fam"],
                                  # self.indexColCadUnic["des_complemento_fam"],
                                  self.indexColCadUnic["nom_localidade_fam"],
                                  self.indexColCadUnic["cod_munic_ibge_5_fam"],
                                  self.indexColCadUnic["cod_munic_ibge_2_fam"]
                                  ]

        self.indexColCnefe = self.bd.retornarColunasIndex(nomeScehemaCnefe, tabelaCnefe)
        self.tiposColCnefe = self.bd.retornarColunasTypes(nomeScehemaCnefe, tabelaCnefe)

        mascaraEnderecoCnefe = [self.indexColCnefe["nom_tipo_seglogr"],
                                self.indexColCnefe["nom_titulo_seglogr"],
                                self.indexColCnefe["nom_seglogr"],
                                self.indexColCnefe["num_endereco"],
                                # self.indexColCnefe["dsc_modificador"],
                                self.indexColCnefe["dsc_localidade"],
                                self.indexColCnefe["cod_municipio"],
                                self.indexColCnefe["cod_uf"]
                                ]

        resultadosPar = (1, 1, 0.0)

        arq = open('saida2.csv', 'w')
        arq.write("cod_familiar_fam; cod_unico_endereco; Dice_coeficiente\n")
        arq.close()

        arq = open('saida2.csv', 'a')
        arq2 = open('log-erro.csv', 'w')
        diceCoef=0.0

        for familia in self.conjuntoCadUnic:

            if int(familia[5]) != cidadeCorrente:

                cidadeCorrente = int(familia[5])
                print("buscando a Cidade " + str(cidadeCorrente))
                nometabelaCnefeCorrente = tabelaCnefe + "_" + str(cidadeCorrente)
                self.conjuntoCidadeCnefe = self.bd.selecionarTabela(nomeScehemaCnefe, [nometabelaCnefeCorrente], ["*"],
                                                                    '', 0)

                self.conjuntoCidadeCnefeDic = {}
                self.quantidadeConjCnefe = {}

                print("Montando arvore para cidade " + str(cidadeCorrente))
                for linha in self.conjuntoCidadeCnefe:
                    preCepCnefe = str(int(linha[self.indexColCnefe["cep"]]) // 1000)
                    #lprefcep = str(int(familia[self.indexColCadUnic["num_cep_logradouro_fam"]])/1000)

                    if preCepCnefe in self.conjuntoCidadeCnefeDic:
                        self.conjuntoCidadeCnefeDic[preCepCnefe].append(linha)
                        self.quantidadeConjCnefe[preCepCnefe] = self.quantidadeConjCnefe[preCepCnefe] + 1
                    else:
                        self.conjuntoCidadeCnefeDic[preCepCnefe] = [linha]
                        self.quantidadeConjCnefe[preCepCnefe] = 1
                print("comparando enderecos na cidade " + str(cidadeCorrente))

            enderecoCadUnic = [familia[mascaraEnderecoCadUnic[0]], familia[mascaraEnderecoCadUnic[1]],
                               familia[mascaraEnderecoCadUnic[2]], str(familia[mascaraEnderecoCadUnic[3]]),
                               familia[mascaraEnderecoCadUnic[4]]
                               ]
            idfamilia = int(familia[self.indexColCadUnic["cod_familiar_fam"]])
            resultadosPar = (idfamilia, 0, 0.0)

            preCepCad = str(int(familia[self.indexColCadUnic["num_cep_logradouro_fam"]])//1000)

            i = 0
            diceCoef = 0
            if preCepCad in self.conjuntoCidadeCnefeDic:

                while not(math.isclose(diceCoef, 1.0)) and i < self.quantidadeConjCnefe[preCepCad]:
                #for endereco in self.conjuntoCidadeCnefeDic[preCepCad]:
                    endereco = self.conjuntoCidadeCnefeDic[preCepCad][i]

                    enderecoCnefe = [endereco[mascaraEnderecoCnefe[0]], endereco[mascaraEnderecoCnefe[1]],
                                 endereco[mascaraEnderecoCnefe[2]], str(endereco[mascaraEnderecoCnefe[3]]),
                                 endereco[mascaraEnderecoCnefe[4]]
                                 ]

                    idEndereco = int(endereco[self.indexColCnefe["cod_unico_endereco"]])

                    diceCoef = self.similar.dice_coefficient2(','.join(enderecoCadUnic), ','.join(enderecoCnefe))

                    if diceCoef > resultadosPar[2]:
                        resultadosPar = (idfamilia, idEndereco, diceCoef)

                    i = i+1

            else:
                arq2.write(str(idfamilia) + ";" + preCepCad + "\n")


            resp = str(resultadosPar[0]) + "," + str(resultadosPar[1]) + "," + str(resultadosPar[2]) + "\n"
            arq.write(resp)
        arq.close()
        arq2.close()



        #
        # self.conjuntoB = self.bd.selecionarTabela([tabelaB], ["*"], '', 0)
        #
        # #print("tamanho A:", len(self.conjuntoA))
        # #print("tamanho B:", len(self.conjuntoB))
        #
        #
        #
        # self.indexColB = self.bd.retornarColunasIndex(tabelaB)
        # self.tiposColB = self.bd.retornarColunasTypes(tabelaB)
        #
        # resultadosPar = (1, 1, 0.0)
        #
        # resultadosFin = []
        #
        # #IBGE

        #
        # #CNEFE
        #
        # print ("Fazendo a juncao.")
        # count = 0
        # for rowA in self.conjuntoA:
        #     resultadosPar = (1, 1, 0.0)
        #     enderecoA = [str(rowA[mEndA[0]]).replace("'",""), str(rowA[mEndA[1]]).replace("'",""), str(rowA[mEndA[2]]).replace("'",""),
        #                  str(rowA[mEndA[3]]).replace("'",""), str(rowA[mEndA[4]]).replace("'",""), str(rowA[mEndA[5]]).replace("'",""),
        #                  str(rowA[mEndA[6]]).replace("'","")
        #                  ]
        #
        #     idA = int(rowA[self.indexColA["cod_familiar_fam"]])
        #     print("dados processados: " + str(count))
        #     for rowB in self.conjuntoB:
        #
        #         enderecoB = [str(rowB[mEndB[0]]).replace("'",""), str(rowB[mEndB[1]]).replace("'",""), str(rowB[mEndB[2]]).replace("'",""),
        #                      str(rowB[mEndB[3]]).replace("'",""), str(rowB[mEndB[4]]).replace("'",""), str(rowB[mEndB[5]]).replace("'",""),
        #                      str(rowB[mEndB[6]]).replace("'","")
        #                      ]
        #         idb = int(rowB[self.indexColB["cod_unico_endereco"]])
        #
        #         #print("END A:", ', '.join(enderecoA))
        #         #print("END B:", ', '.join(enderecoB))
        #         diceCoef = self.similar.dice_coefficient2(','.join(enderecoA), ','.join(enderecoB))
        #
        #         if diceCoef > resultadosPar[2]:
        #             resultadosPar = (idA, idb, diceCoef)
        #     count = count + 1
        #
        #     resultadosFin.append(resultadosPar)
        #
        # #self.printarLista(resultadosFin)
        #
        # arq = open('saida2.csv', 'w')
        #
        #
        # arq.write("cod_familiar_fam; cod_unico_endereco; Dice_coeficiente\n")
        # for lin in resultadosFin:
        #     arq.write(str(lin[0]) + ";" + str(lin[1]) + ";" + str(lin[2]) +"\n")
        # arq.close()


j = JuncaoTools()


ini = time.time()
j.juncaoTabelas("cad_unic_2019", "base_cad_unic_2019_14", "cnefe_rr_14", "14_rr")
fim = time.time()

print("\n=========================================\n")
print("Tempo: " + str(fim-ini))
## 1 traz a tabela do CAD do estado MG;
## 2 tras a tabela agrupada por cidade e quantiade de familhas do CAD
## for cidade da tabela agrupada traz a tabela da cidade do CNEFE no banco
## para cada instancia do CAD bucar na tabela do cnefe cidade
## sempre pegar o maior dice
