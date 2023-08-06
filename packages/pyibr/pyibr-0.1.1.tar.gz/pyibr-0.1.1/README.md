# Sobre

`ibr` é uma biblioteca Python que calcula os indicadores de análise
fundamentalista de companhias brasileiras registradas na CVM.

O motivo para a criação dessa biblioteca é que coisas da CVM devem
pertencer à biblioteca [cvm][repo-pycvm], ao passo que indicadores fundamentalistas,
na medida em que são algo maior do que a CVM, devem ser separados.

Além do mais, indicadores de valuation dependem de dados de mercado,
o que está além da responsabilidade de CVM, já que a CVM não é uma
bolsa de valores.

# Uso

## Indicadores Financeiros

O código abaixo abre um documento DFP/ITR e lista os indicadores
financeiros das companhias nesse documento:

```py
import ibr

for result in ibr.reader('/caminho/para/dfp_ou_itr.zip', (ibr.Indebtedness, ibr.Profitability, ibr.Efficiency)):
    indebtedness, profitability, efficiency = result.indicators

    print('----------------------------')
    print('Companhia:', result.dfpitr.company_name)
    
    print('\nEndividamento:')
    print(indebtedness)
    
    print('\nEficiência:')
    print(efficiency)
    
    print('\nRentabilidade:')
    print(profitability)
```

## Indicadores de Valuation

Quanto a indicadores de valuation, eles precisam de dados de mercado. Visto
que dados de mercado não são fornecidos num arquivo DFP/ITR, pois isso está
além do escopo da CVM, esses dados devem ser obtidos da internet ou alguma
outra fonte.

Para isso, a biblioteca `ibr` fornece a classe `YfinanceValuation`, que é
baseada nas bibliotecas [b3][repo-pybov] e [yfinance][repo-yfinance]:

```py
import ibr

for result in ibr.reader('/caminho/para/dfp_ou_itr.zip', [ibr.YfinanceValuation]):
    print('------------------')
    print('Companhia:', result.dfpitr.company_name)
    
    valuations = result.indicators[0]

    for valuation in valuations:
        print('\nValuation:')
        print(valuation)
```

Repare que os indicadores de valuation retornam uma lista, pois é possível
que uma companhia tenha mais de um valor mobiliário. Um exemplo disso é a
companhia Eletrobrás, que possui três valores mobiliários na B3: ELET3,
ELET5 e ELET6. Como cada valor mobiliário resulta em indicadores de valuation
diferentes, `valuations` teria 3 objetos para a companhia Eletrobrás.

Outro ponto é que usar `YfinanceValuation` é bastante lento. Isso porque a
biblioteca `yfinance` leva um tempo para obter o total de ações em circulação
de uma companhia, que é necessário para o cálculo.

## Exemplos

Exemplos mais elaborados de uso estão no diretório `samples`:

```sh
python -m samples.financial '/caminho/para/dfp_ou_itr.zip'
python -m samples.valuation '/caminho/para/dfp_ou_itr.zip'
```

  [repo-pycvm]: <https://github.com/callmegiorgio/pycvm>
  [repo-pybov]: <https://github.com/callmegiorgio/pybov>
  [repo-yfinance]: <https://pypi.org/project/yfinance/>