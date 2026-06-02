## CINEHUB

O sistema tem como objetivo permitir que usuários consultem filmes previamente cadastrados na plataforma, realizem avaliações por meio de notas e comentários e visualizem opiniões de outros usuários, criando um ambiente colaborativo de recomendação cinematográfica.

A principal funcionalidade que agrega valor ao usuário é o sistema de avaliações e recomendações, no qual cada usuário pode registrar sua experiência com determinado filme, contribuindo para a formação de rankings e médias de avaliação. Dessa forma, a plataforma auxilia outros usuários na tomada de decisão sobre quais filmes assistir, utilizando informações coletivas e atualizadas em tempo real.


*Coleções do sistema*

filmes é a coleção principal. Cada documento representa um filme e concentra, de forma agregada, tudo que é necessário para exibir sua página completa sem precisar consultar outras coleções. É o agregado central do sistema.

avaliações é uma coleção separada. Cada documento representa a avaliação de um usuário sobre um filme, referenciando o filme pelo campo filme_id.  A nota média já fica embutida em filmes para exibição rápida.

pessoas é uma coleção separada. Cada documento representa um ator, diretor ou roteirista, com sua biografia e filmografia. Foi separada porque uma mesma pessoa aparece em muitos filmes, e embutir todos os seus dados em cada filme causaria duplicação massiva e dificultaria atualizações.



*Hierarquia e agregações dentro de filmes*

campos simples: título, ano, duração, sinopse, poster, classificação, gêneros, países e idiomas. São os dados básicos do filme, sempre exibidos na página.

avaliacao { } é agregação :média, número de votos e metascore ficam embutidos dentro do filme porque são exibidos em toda consulta. Atualizam periodicamente mas são lidos com muito mais frequência do que escrito.

elenco [ { } ] é agregação: array com os atores principais, contendo nome, personagem e ordem de crédito. Fica embutido porque a página do filme sempre exibe o elenco. Cada item guarda também um pessoa_id que referencia a coleção pessoas, permitindo navegar para o perfil do ator.

direcao { } é agregação: objeto com o nome do diretor embutido no filme. Assim como o elenco, é exibido em toda página de filme. Contém pessoa_id como referência para a coleção pessoas.

premios [ { } ] é agregação: lista de prêmios e indicações do filme, com cerimônia, ano, categoria e resultado. Fica embutida porque é uma lista finita que não cresce de forma significativa ao longo do tempo.




*Justificativa das decisões de modelagem*

Por que elenco, direção e prêmios são embutidos em filmes?
Porque toda vez que um usuário abre a página de um filme, ele quer ver essas informações juntas. Embutir evita múltiplas consultas e entrega tudo de uma vez.

Por que avaliações são uma coleção separada?
Porque crescem indefinidamente. Um filme popular pode ter milhões de avaliações, se eu embutisse tudo isso num único documento tornaria ele enorme e lento de carregar, mesmo quando o usuário só quer ver o título e a nota média.

Por que pessoas é uma coleção separada?
Porque um ator aparece em dezenas de filmes. Se os dados dele fossem embutidos em cada filme, qualquer atualização (ex: uma foto nova) teria que ser feita em todos os documentos. Separando, atualiza em um lugar só.

Por que pessoa_id aparece dentro de elenco e direção em filmes?
Para não duplicar todos os dados da pessoa dentro do filme, então apenas o necessário para exibir na página (nome, personagem) fica embutido. O restante (biografia, filmografia completa) fica em pessoas e é buscado só quando o usuário clica no ator.
