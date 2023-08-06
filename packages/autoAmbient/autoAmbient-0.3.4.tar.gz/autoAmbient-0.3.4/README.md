# auto-enviroment

auto-enviroment é uma biblioteca Python que fornece modelos automatizados para facilitar o desenvolvimento de automações que interagem com interfaces de usuário em desktops, clicando, procurando e esperando quando solicitado

## Instalação

Para realisar a instalação basta executar o seguinte comando via pip:

```bash
pip install autoAmbient
```

## Modo de usar

Para começar a usar o auto-enviroment basta executar o comando no seu terminal :

```bash
createAmbient
```

A partir daí seram criados todos os arquivos base para que você comece a produzir e automatizar o que quiser.
Escolha um local que você queira clicar, tire uma print, e coloque a imagem na pasta resouces com um bom nome, logo após isso execute:

```bash
createTagsFile
```

Após a criação da referencia à imagem no arquivo de tags você deve escrever o seu fluxo em run.py como no exemplo a seguir:

```python
from ambient.tolls.utils import take_click_types
import tags as tg  # tags é um arquivo que contém referências a todas as imagens
import ambient.tolls.clicks as cl
from ambient.tolls.utils import remove_self_necessity


def run():
    class Bot(DesktopBot):
        def action(self, execution=None):
            nf = take_click_types(
                tuple([remove_self_necessity(self, f) for f in cl.click_functions])
            )
            find, click, clickIfPossible = nf

            click(tg.btn_name) #o lugar que você que clicar

    Bot.main()
```

Depois disso é só executar o main.py e ver a mágica acontecer

O auto-enviroment conta com diversas maneiras de corrigir erros como as GUIs para quando a respectiva imagem não for encontrada

![Captura de tela de 2023-05-23 22-57-20](https://github.com/luisArthurRodriguesDaSilva/auto-enviroment/assets/66787949/76c89f66-bcfa-432e-83c6-85bb2e56d766)

## Contribuindo

Se você quiser contribuir com a biblioteca AutoAmbient, você deve seguir as seguintes etapas:

1. Fork o repositório
2. Crie sua branch de features (`git checkout -b feature/fooBar`)
3. Realize o commit de suas alterações (`git commit -am 'Add some fooBar'`)
4. Faça o push das alterações (`git push origin feature/fooBar`)
5. Crie um novo Pull Request

## Licença

Este projeto está sob a licença MIT. Para mais informações acesse o arquivo `LICENSE`.
