from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import CollectionInvalid
from bson import ObjectId
from datetime import datetime, timezone
import sys

# ── Configuração ─────────────────────────────────────────────────────────────
CONN_STRING = "mongodb+srv://admin_cinehub:SENHA@cinehub.3rawcki.mongodb.net/?appName=cinehub"
DB_NAME     = "cinehub"

# ── IDs fixos para manter referências cruzadas nos exemplos ──────────────────
ID_FILME_CIDADE    = ObjectId("64a1f2b3c4d5e6f7a8b9c001")
ID_FILME_TROPA     = ObjectId("64a1f2b3c4d5e6f7a8b9c002")
ID_PESSOA_MEIRELLES = ObjectId("64a1f2b3c4d5e6f7a8b9c021")
ID_PESSOA_PADILHA   = ObjectId("64a1f2b3c4d5e6f7a8b9c022")
ID_PESSOA_ALEX      = ObjectId("64a1f2b3c4d5e6f7a8b9c011")
ID_PESSOA_LEANDRO   = ObjectId("64a1f2b3c4d5e6f7a8b9c012")
ID_PESSOA_WAGNER    = ObjectId("64a1f2b3c4d5e6f7a8b9c013")
ID_USER1 = ObjectId("64a1f2b3c4d5e6f7a8b9c201")
ID_USER2 = ObjectId("64a1f2b3c4d5e6f7a8b9c202")
ID_USER3 = ObjectId("64a1f2b3c4d5e6f7a8b9c203")

def now():
    return datetime.now(timezone.utc)

# ── Validators ───────────────────────────────────────────────────────────────
VALIDATOR_FILMES = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["titulo", "ano", "duracao_min", "sinopse", "generos", "avaliacao", "elenco", "direcao"],
        "properties": {
            "titulo":             {"bsonType": "string"},
            "titulo_original":    {"bsonType": "string"},
            "ano":                {"bsonType": "int", "minimum": 1888},
            "duracao_min":        {"bsonType": "int", "minimum": 1},
            "sinopse":            {"bsonType": "string"},
            "poster_url":         {"bsonType": "string"},
            "classificacao_etaria": {"bsonType": "string","enum": ["Livre","10","12","14","16","18"]},
            "generos":  {"bsonType": "array","items": {"bsonType": "string"}},
            "paises":   {"bsonType": "array","items": {"bsonType": "string"}},
            "idiomas":  {"bsonType": "array","items": {"bsonType": "string"}},
            "avaliacao": {
                "bsonType": "object","required": ["media","total_votos"],
                "properties": {
                    "media":       {"bsonType": "double","minimum": 0,"maximum": 10},
                    "total_votos": {"bsonType": "int","minimum": 0},
                    "metascore":   {"bsonType": "int","minimum": 0,"maximum": 100},
                }
            },
            "elenco": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object","required": ["pessoa_id","nome","personagem","ordem"],
                    "properties": {
                        "pessoa_id":  {"bsonType": "objectId"},
                        "nome":       {"bsonType": "string"},
                        "personagem": {"bsonType": "string"},
                        "ordem":      {"bsonType": "int"},
                        "foto_url":   {"bsonType": "string"},
                    }
                }
            },
            "direcao": {
                "bsonType": "object","required": ["pessoa_id","nome"],
                "properties": {
                    "pessoa_id": {"bsonType": "objectId"},
                    "nome":      {"bsonType": "string"},
                }
            },
            "premios": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object","required": ["cerimonia","ano","categoria","resultado"],
                    "properties": {
                        "cerimonia": {"bsonType": "string"},
                        "ano":       {"bsonType": "int"},
                        "categoria": {"bsonType": "string"},
                        "resultado": {"bsonType": "string","enum": ["Vencedor","Indicado"]},
                    }
                }
            },
        }
    }
}

VALIDATOR_AVALIACOES = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["filme_id","usuario_id","nota","created_at"],
        "properties": {
            "filme_id":       {"bsonType": "objectId"},
            "usuario_id":     {"bsonType": "objectId"},
            "nome_usuario":   {"bsonType": "string"},
            "nota":           {"bsonType": "double","minimum": 0,"maximum": 10},
            "comentario":     {"bsonType": "string","maxLength": 2000},
            "titulo_resenha": {"bsonType": "string","maxLength": 200},
            "contem_spoiler": {"bsonType": "bool"},
            "curtidas":       {"bsonType": "int","minimum": 0},
            "created_at":     {"bsonType": "date"},
            "updated_at":     {"bsonType": "date"},
        }
    }
}

VALIDATOR_PESSOAS = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["nome","funcoes"],
        "properties": {
            "nome":          {"bsonType": "string"},
            "nome_completo": {"bsonType": "string"},
            "nacionalidade": {"bsonType": "string"},
            "biografia":     {"bsonType": "string"},
            "foto_url":      {"bsonType": "string"},
            "funcoes": {
                "bsonType": "array",
                "items": {"bsonType": "string","enum": ["ator","diretor","roteirista","produtor"]}
            },
            "filmografia": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object","required": ["filme_id","titulo","ano","funcao"],
                    "properties": {
                        "filme_id":   {"bsonType": "objectId"},
                        "titulo":     {"bsonType": "string"},
                        "ano":        {"bsonType": "int"},
                        "funcao":     {"bsonType": "string"},
                        "personagem": {"bsonType": "string"},
                    }
                }
            },
        }
    }
}

# ── Dados de exemplo ─────────────────────────────────────────────────────────
FILMES = [
    {
        "_id": ID_FILME_CIDADE,
        "titulo": "Cidade de Deus","titulo_original": "City of God",
        "ano": 2002,"duracao_min": 130,
        "sinopse": "Dois jovens crescem na Cidade de Deus, conjunto habitacional do Rio de Janeiro, durante as décadas de 1960 a 1980. Um quer ser fotógrafo; o outro torna-se um dos traficantes mais temidos da região.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/pt/0/02/Poster-CidadedeDeus.jpg",
        "classificacao_etaria": "18","generos": ["Crime","Drama"],"paises": ["Brasil"],"idiomas": ["Português"],
        "avaliacao": {"media": 8.6,"total_votos": 742000,"metascore": 79},
        "elenco": [
            {"pessoa_id": ID_PESSOA_ALEX,    "nome": "Alexandre Rodrigues","personagem": "Buscapé",    "ordem": 1},
            {"pessoa_id": ID_PESSOA_LEANDRO, "nome": "Leandro Firmino",    "personagem": "Zé Pequeno","ordem": 2},
        ],
        "direcao": {"pessoa_id": ID_PESSOA_MEIRELLES,"nome": "Fernando Meirelles"},
        "roteiro": [{"pessoa_id": ObjectId(),"nome": "Bráulio Mantovani"}],
        "premios": [
            {"cerimonia": "Oscar", "ano": 2004,"categoria": "Melhor Diretor",          "resultado": "Indicado"},
            {"cerimonia": "Oscar", "ano": 2004,"categoria": "Melhor Roteiro Adaptado", "resultado": "Indicado"},
            {"cerimonia": "BAFTA", "ano": 2004,"categoria": "Melhor Filme Estrangeiro","resultado": "Vencedor"},
        ],
        "created_at": now(),"updated_at": now(),
    },
    {
        "_id": ID_FILME_TROPA,
        "titulo": "Tropa de Elite","titulo_original": "Elite Squad",
        "ano": 2007,"duracao_min": 115,
        "sinopse": "No Rio de Janeiro de 1997, o Capitão Nascimento, do BOPE, precisa encontrar um substituto antes do nascimento de seu filho, enquanto dois amigos lutam para entrar na elite policial.",
        "poster_url": "https://upload.wikimedia.org/wikipedia/pt/3/3e/TropaDeEliteCartaz.jpg",
        "classificacao_etaria": "18","generos": ["Ação","Crime","Drama"],"paises": ["Brasil"],"idiomas": ["Português"],
        "avaliacao": {"media": 8.0,"total_votos": 215000,"metascore": 65},
        "elenco": [
            {"pessoa_id": ID_PESSOA_WAGNER,"nome": "Wagner Moura","personagem": "Capitão Nascimento","ordem": 1},
        ],
        "direcao": {"pessoa_id": ID_PESSOA_PADILHA,"nome": "José Padilha"},
        "roteiro": [{"pessoa_id": ObjectId(),"nome": "Bráulio Mantovani"}],
        "premios": [
            {"cerimonia": "Berlinale","ano": 2008,"categoria": "Urso de Ouro","resultado": "Vencedor"},
        ],
        "created_at": now(),"updated_at": now(),
    },
]

AVALIACOES = [
    {"filme_id": ID_FILME_CIDADE,"usuario_id": ID_USER1,"nome_usuario": "cinefilo_br","nota": 9.5,
     "titulo_resenha": "Uma obra-prima do cinema brasileiro",
     "comentario": "Fernando Meirelles entregou um dos filmes mais impactantes da história do cinema nacional. A narrativa não-linear e a fotografia são simplesmente geniais.",
     "contem_spoiler": False,"curtidas": 342,"created_at": now(),"updated_at": now()},
    {"filme_id": ID_FILME_CIDADE,"usuario_id": ID_USER2,"nome_usuario": "ana_filmes","nota": 8.0,
     "titulo_resenha": "Impactante e necessário",
     "comentario": "A realidade retratada é brutal, mas o filme é essencial. Narrativa incrível, elenco preciso.",
     "contem_spoiler": False,"curtidas": 128,"created_at": now(),"updated_at": now()},
    {"filme_id": ID_FILME_TROPA,"usuario_id": ID_USER1,"nome_usuario": "cinefilo_br","nota": 8.5,
     "titulo_resenha": "Wagner Moura entrega uma atuação memorável",
     "comentario": "José Padilha criou um retrato perturbador da violência urbana e da corrupção policial no Rio. Wagner Moura está extraordinário.",
     "contem_spoiler": False,"curtidas": 89,"created_at": now(),"updated_at": now()},
    {"filme_id": ID_FILME_TROPA,"usuario_id": ID_USER3,"nome_usuario": "pedro_vaz","nota": 7.5,
     "titulo_resenha": "Bom, mas esperava mais",
     "comentario": "Ótima atuação do Wagner Moura. A narrativa em primeira pessoa funciona bem, mas o ritmo cai um pouco no meio.",
     "contem_spoiler": False,"curtidas": 44,"created_at": now(),"updated_at": now()},
]

PESSOAS = [
    {"_id": ID_PESSOA_MEIRELLES,"nome": "Fernando Meirelles","nome_completo": "Fernando Meirelles",
     "nacionalidade": "Brasileiro",
     "biografia": "Diretor e produtor brasileiro, mundialmente reconhecido após Cidade de Deus (2002), que recebeu quatro indicações ao Oscar.",
     "funcoes": ["diretor","produtor"],
     "filmografia": [{"filme_id": ID_FILME_CIDADE,"titulo": "Cidade de Deus","ano": 2002,"funcao": "diretor"}],
     "created_at": now(),"updated_at": now()},
    {"_id": ID_PESSOA_PADILHA,"nome": "José Padilha","nome_completo": "José Padilha",
     "nacionalidade": "Brasileiro",
     "biografia": "Diretor brasileiro conhecido por Tropa de Elite e pela série Narcos: México.",
     "funcoes": ["diretor","produtor"],
     "filmografia": [{"filme_id": ID_FILME_TROPA,"titulo": "Tropa de Elite","ano": 2007,"funcao": "diretor"}],
     "created_at": now(),"updated_at": now()},
    {"_id": ID_PESSOA_ALEX,"nome": "Alexandre Rodrigues","nacionalidade": "Brasileiro",
     "biografia": "Ator brasileiro revelado em Cidade de Deus, onde interpretou o protagonista Buscapé.",
     "funcoes": ["ator"],
     "filmografia": [{"filme_id": ID_FILME_CIDADE,"titulo": "Cidade de Deus","ano": 2002,"funcao": "ator","personagem": "Buscapé"}],
     "created_at": now(),"updated_at": now()},
    {"_id": ID_PESSOA_LEANDRO,"nome": "Leandro Firmino","nacionalidade": "Brasileiro",
     "biografia": "Ator brasileiro conhecido pelo papel icônico de Zé Pequeno em Cidade de Deus.",
     "funcoes": ["ator"],
     "filmografia": [{"filme_id": ID_FILME_CIDADE,"titulo": "Cidade de Deus","ano": 2002,"funcao": "ator","personagem": "Zé Pequeno"}],
     "created_at": now(),"updated_at": now()},
    {"_id": ID_PESSOA_WAGNER,"nome": "Wagner Moura","nacionalidade": "Brasileiro",
     "biografia": "Ator baiano, um dos mais premiados do Brasil. Conhecido internacionalmente por Pablo Escobar em Narcos e pelo Capitão Nascimento em Tropa de Elite.",
     "funcoes": ["ator"],
     "filmografia": [{"filme_id": ID_FILME_TROPA,"titulo": "Tropa de Elite","ano": 2007,"funcao": "ator","personagem": "Capitão Nascimento"}],
     "created_at": now(),"updated_at": now()},
]

# ── Helpers ──────────────────────────────────────────────────────────────────
def criar_colecao(db, nome, validator):
    try:
        db.create_collection(nome, validator=validator)
        print(f"  ✅ Coleção '{nome}' criada")
    except CollectionInvalid:
        print(f"  ⚠️  Coleção '{nome}' já existe — atualizando validator")
        db.command("collMod", nome, validator=validator)

def main():
    print("\n🎬 CineHub — Setup MongoDB Atlas")
    print("=" * 40)
    print("\n📡 Conectando ao Atlas...")
    client = MongoClient(CONN_STRING, serverSelectionTimeoutMS=8000)
    try:
        client.admin.command("ping")
        print("  ✅ Conexão estabelecida!")
    except Exception as e:
        print(f"  ❌ Falha: {e}")
        sys.exit(1)

    db = client[DB_NAME]

    print("\n📂 Criando coleções com validators...")
    criar_colecao(db, "filmes",     VALIDATOR_FILMES)
    criar_colecao(db, "avaliacoes", VALIDATOR_AVALIACOES)
    criar_colecao(db, "pessoas",    VALIDATOR_PESSOAS)

    print("\n🔍 Criando índices...")
    f = db["filmes"]
    f.create_index([("titulo", TEXT), ("sinopse", TEXT)], name="idx_texto_busca")
    f.create_index([("generos", ASCENDING)],              name="idx_generos")
    f.create_index([("ano", DESCENDING)],                 name="idx_ano")
    f.create_index([("avaliacao.media", DESCENDING)],     name="idx_nota_media")
    f.create_index([("direcao.pessoa_id", ASCENDING)],    name="idx_diretor")
    print("  ✅ filmes")

    a = db["avaliacoes"]
    a.create_index([("filme_id", ASCENDING), ("created_at", DESCENDING)], name="idx_avaliacoes_por_filme")
    a.create_index([("usuario_id", ASCENDING)],                            name="idx_avaliacoes_por_usuario")
    a.create_index([("filme_id", ASCENDING), ("nota", DESCENDING)],        name="idx_nota_por_filme")
    a.create_index([("filme_id", ASCENDING), ("usuario_id", ASCENDING)],
                   name="idx_unico_usuario_filme", unique=True)
    print("  ✅ avaliacoes")

    p = db["pessoas"]
    p.create_index([("nome", TEXT)],               name="idx_busca_nome")
    p.create_index([("funcoes", ASCENDING)],       name="idx_funcoes")
    p.create_index([("nacionalidade", ASCENDING)], name="idx_nacionalidade")
    print("  ✅ pessoas")

    print("\n📄 Inserindo dados de exemplo...")
    for col_name, docs in [("pessoas", PESSOAS), ("filmes", FILMES), ("avaliacoes", AVALIACOES)]:
        col = db[col_name]; ok = 0
        for doc in docs:
            try:
                col.insert_one(doc); ok += 1
            except Exception as e:
                print(f"  ⚠️  {col_name}: {e}")
        if ok:
            print(f"  ✅ {col_name}: {ok} documento(s) inserido(s)")

    print("\n🎉 Setup concluído!")
    print(f"   Filmes:     {db['filmes'].count_documents({})}")
    print(f"   Pessoas:    {db['pessoas'].count_documents({})}")
    print(f"   Avaliações: {db['avaliacoes'].count_documents({})}")
    client.close()

if __name__ == "__main__":
    main()
