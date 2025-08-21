# Labo 03 – REST APIs, GraphQL

<img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Ets_quebec_logo.png" width="250">    
ÉTS - LOG430 - Architecture logicielle - Chargé de laboratoire: Gabriel C. Ullmann, Automne 2025.

## 🎯 Objectifs d'apprentissage

- Comprendre ce qu'est une API REST.
- Comprendre comment une API peut contribuer à l'extensibilité d'une application et faciliter l'intégration de nouveaux clients.
- Apprendre comment utiliser GraphQL pour créer une API plus flexible offrant aux clients la possibilité de requêter exactement les données dont ils ont besoin.
- Comparer les avantages et inconvénients des approches REST et GraphQL selon différents contextes d'utilisation.
- Maîtriser la gestion d'état et de cache avec Redis dans un contexte d'API moderne.

## ⚙️ Setup

Dans ce laboratoire, nous poursuivrons le développement de notre application de gestion de magasin. Nous ajoutons maintenant la gestion du stock des articles, en complément de la gestion des commandes, des articles et des utilisateurs.

- Chaque fois qu’une commande est passée, le stock des articles concernés est diminué.
- Si une commande est supprimée, les articles correspondants sont réintégrés dans le stock.

> 📝 NOTE : à ce stade, nous ne mettons pas en place de gestion du statut des commandes, des limites minimums/maximums de stock ni de mécanisme d’authentification pour l’API. L’objectif est de nous concentrer sur les aspects architecturaux, et non sur les aspects métier ou de sécurité. La logique de l’application sera donc volontairement simplifiée.

Nous ajouterons également une nouveau endpoint permettant à nos fournisseurs de consulter l’état de notre stock et nous envoyer de nouveaux articles pour le réapprovisionner. Pour cette endpoint en particulier, nous permettrons l’utilisation de GraphQL, afin que le client puisse choisir précisément les colonnes qu’il souhaite checher dans la base de données. Cela permet de résoudre un problème classique des API REST : renvoyer trop ou pas assez de données.

### 1. Faites un fork et clonez le dépôt GitLab

```bash
git clone https://github.com/guteacher/log430-a25-labo3
cd log430-a25-labo3
```

### 2. Préparez l'environnement de développement

Suivez les mêmes étapes que dans le laboratoire 00.

### 3. Installez Postman

Installez Postman et importez la collection disponible dans /docs/collections.

### 4. Comprenez les principes REST

À ce stade, notre application est une API qui respecte presque tous les principes REST définis par Roy Fielding dans sa thèse de doctorat (2000) :

- ✅ Client–Serveur : séparation claire entre client et serveur.
- ✅ Système en couches : notre application comporte trois couches (front-end, back-end, base de données).
- ✅ Sans état (stateless) : chaque requête est indépendante, le serveur ne « se souvient » pas des requêtes précédentes.
- ⛔ Cache : il n’y a pas de mécanisme de cache côté client (nous utilisons Postman, mais cela serait possible avec un vrai front-end).
- ✅ Interface uniforme : les endpoints sont bien nommés et utilisent les bonnes méthodes HTTP (POST /orders, GET /products/:id, etc.).

Une API qui respecte l’ensemble de ces principes est appelée une API RESTful. Pour l’instant, nous travaillons uniquement avec une API REST.

## 🧪 Activités pratiques

### 1. Permettez l'accès à l'API
Ouvrez les ports nécessaires dans le fichier docker-compose.yml afin de permettre l'accès à l'API (port 5000) :

```yaml
store_manager:
  build: .
  volumes:
    - .:/app
  ports:
    - "5000:5000" # REST API
```

### 2. Testez le processus de stock complet
Dans `src/tests/test_store_manager.py`, dans la méthode `test_stock_flow.py`, écrivez les smoke tests pour que nous puissons observer comment le processus de stock fonctione, et aussi nous assure qu'il fonctionne de maniére consistent. Testez les endpoints suivantes:
- Créez un article (`POST /products`)
- Ajoutez 5 unités au stock de ce article (`POST /products_stocks`)
- Checkez le stock, votre article devra avoir 5 unités dans le stock (`GET /product_stocks/:id`)
- Faire une commande de l'article que vous avez créez, 2 unités (`POST /orders`)
- Checkez le stock encore une fois (`GET /product_stocks/:id`)

```python
# Code pour commencer l'activité
```

> 💡 **Question 1** : Quel nombre d'unités de stock pour votre article avez vous obtenu au fin du test? Et pour l'article avec `id=2`? Veuillez inclure la sortie de votre Postman pour illustrer votre réponse.

### 3. Créer un rapport de stock
Notre directeur de magazin a besoin de savoir l'état du stock. Dans `src/queries/read_product_stock.py`, il y a une methode `get_stock_for_all_products`, qui est utilisé par l'endpoint `/product_stocks/reports/overview` pour donner les stocks de chaque articles, mais il n'y a pas beaucoup d'information. Ajoutez les champs `name`, `sku` et `price` de l'article en utilsant la méthode [join à SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join). Ça vous permettra de joindre l'information du tableau `ProductStock` avec `Product`.

> 💡 **Question 2** : Décrivez lutilsation de la méthode join dans ce cas. Utilisez les méthode tel quels décrits à `Simple Relationship Joins` et `Joins to a Target with an ON Clause` dans la documentation à SQLAclhemy pour ajouter les champs démandes dans cette activité. Veuillez inclure le code pour illustrer votre réponse.

### 4. Utilisez l'endpoint GraphQL
Dans lactivité 2, nous avons ajoutez des nouveaux champs à un endpoint. Si a lavenir nous aorns des nouveaux champs, ou le besoin de conserver des differents endpoints avec champs distincts, il va falloir que nous creons de differents endpoints. Pour nous aider à mieux gérer l'heteregeneite des endpoints, on peut créer un endpoint GraphQL.
```python
    data = request.get_json()
    schema = Schema(query=Query)
    result = schema.execute(data['query'], variables=data.get('variables'))
    return jsonify({
        'data': result.data,
        'errors': [str(e) for e in result.errors] if result.errors else None
    })
```

 GraphQL est une langage que nous permettrre de donner la possibilité aux client q'utilisent notre API REST de continuer à utiliser les endpoints avec les noms et méthode fixés, mais en passant les noms des champs qu'il veulent, et mêmes les filtres en utilisant la langage graphQL. Par example:
```graphql
{
  product(id: "1") {
    id
    quantity
  }
}
```

### 5. Ajoutez plus d'information à l'endpoint GraphQL
La correspondance entre les champs GraphQL et Redis est faites dans `src/schemas/query.py`, dans la méthode `resolve_product`. Ajoutes aussi les champs `name`, `sku` et `price`.

## 📦 Livrables

- Un fichier .zip contenant l'intégralité du code source du projet Labo 03.
- Un rapport en .pdf répondant aux 5 questions présentées dans ce document. Il est obligatoire d'illustrer vos réponses avec du code ou des captures d'écran/terminal.