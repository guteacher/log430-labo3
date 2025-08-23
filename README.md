# Labo 03 – REST APIs, GraphQL

<img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Ets_quebec_logo.png" width="250">    
ÉTS - LOG430 - Architecture logicielle - Chargé de laboratoire: Gabriel C. Ullmann, Automne 2025.

## 🎯 Objectifs d'apprentissage

- Comprendre ce qu'est une API REST et les principes RESTful.
- Comprendre comment une API peut contribuer à l'extensibilité d'une application et faciliter l'intégration de nouveaux clients.
- Apprendre comment utiliser GraphQL pour créer une API plus flexible offrant aux clients la possibilité de requêter exactement les données dont ils ont besoin.
- Comparer les avantages et inconvénients des approches REST et GraphQL selon différents contextes d'utilisation.
- Maîtriser la gestion d'état et de cache avec Redis dans un contexte d'API moderne.
- Comprendre l'utilisation des jointures SQL avec SQLAlchemy pour optimiser les requêtes de base de données.

## ⚙️ Setup

Dans ce laboratoire, nous poursuivrons le développement de notre application de gestion de magasin. Nous ajoutons maintenant la gestion du stock des articles, en complément de la gestion des commandes, des articles et des utilisateurs.

- Chaque fois qu'une commande est passée, le stock des articles concernés est diminué.
- Si une commande est supprimée, les articles correspondants sont réintégrés dans le stock.

> 📝 **NOTE** : À ce stade, nous ne mettons pas en place de gestion du statut des commandes, des limites minimums/maximums de stock ni de mécanisme d'authentification pour l'API. L'objectif est de nous concentrer sur les aspects architecturaux, et non sur les aspects métier ou de sécurité. La logique de l'application sera donc volontairement simplifiée.

Nous ajouterons également un nouvel endpoint permettant à nos fournisseurs de consulter l'état de notre stock et nous envoyer de nouveaux articles pour le réapprovisionnement. Pour cet endpoint en particulier, nous permettrons l'utilisation de GraphQL, afin que le client puisse choisir précisément les colonnes qu'il souhaite chercher dans la base de données. Cela permet de résoudre un problème classique des API REST : renvoyer trop ou pas assez de données.

### 1. Faites un fork et clonez le dépôt GitLab
```bash
git clone https://github.com/guteacher/log430-a25-labo3
cd log430-a25-labo3
```

### 2. Créez un réseau Docker
Éxecutez dans votre terminal:
```bash
docker network create labo03-network
```

### 3. Préparez l'environnement de développement
Suivez les mêmes étapes que dans le laboratoire 00. Créez un fichier .env.

### 4. Installez Postman
Installez Postman et importez la collection disponible dans /docs/collections.

### 5. Comprenez les principes REST
À ce stade, notre application est une API qui respecte presque tous les principes REST définis par Roy Fielding dans sa thèse de doctorat (2000) :

- ✅ **Client–Serveur** : séparation claire entre client et serveur.
- ✅ **Système en couches** : notre application comporte trois couches (front-end, back-end, base de données).
- ✅ **Sans état (stateless)** : chaque requête est indépendante, le serveur ne « se souvient » pas des requêtes précédentes.
- ⛔ **Cache** : il n'y a pas de mécanisme de cache côté client (nous utilisons Postman, mais cela serait possible avec un vrai front-end).
- ✅ **Interface uniforme** : les endpoints sont bien nommés et utilisent les bonnes méthodes HTTP (POST /orders, GET /products/:id, etc.).

Une API qui respecte l'ensemble de ces principes est appelée une API RESTful. Pour l'instant, nous travaillons uniquement avec une API REST.

## 🧪 Activités pratiques

### 1. Permettez l'accès à l'API

Ouvrez les ports nécessaires dans le fichier docker-compose.yml afin de permettre l'accès à l'API (port 5000) :

```yaml
store_manager:
  build: .
  volumes:
    - .:/app
  ports:
    - "5000:5000"  # REST API
```

### 2. Testez le processus de stock complet

Dans `src/tests/test_store_manager.py`, dans la méthode `test_stock_flow()`, écrivez les smoke tests pour que nous puissions observer comment le processus de stock fonctionne, et aussi nous assurer qu'il fonctionne de manière consistante. Testez les endpoints suivants :

- Créez un article (`POST /products`)
- Ajoutez 5 unités au stock de cet article (`POST /products_stocks`)
- Vérifiez le stock, votre article devra avoir 5 unités dans le stock (`GET /product_stocks/:id`)
- Faites une commande de l'article que vous avez créé, 2 unités (`POST /orders`)
- Vérifiez le stock encore une fois (`GET /product_stocks/:id`)

Exécutez vos tests pour vous assurer que le flux de stock fonctionne correctement.

> 💡 **Question 1** : Quel nombre d'unités de stock pour votre article avez-vous obtenu à la fin du test ? Et pour l'article avec `id=2` ? Veuillez inclure la sortie de votre Postman pour illustrer votre réponse.

### 3. Créer un rapport de stock

Le directeur du magasin q'utilise notre application a besoin de connaître l'état des articles dans le stock. Dans `src/queries/read_product_stock.py`, il y a une méthode `get_stock_for_all_products`, qui est utilisée par l'endpoint `/product_stocks/reports/overview` pour donner les stocks de chaque article, mais il n'y a pas beaucoup d'informations. Ajoutez les colonnes `name`, `sku` et `price` de l'article en utilisant la méthode [join à SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join). Cela vous permettra de joindre l'information du tableau `ProductStock` avec `Product`.

> 💡 **Question 2** : Décrivez l'utilisation de la méthode join dans ce cas. Utilisez les méthodes telles que décrites à `Simple Relationship Joins` et `Joins to a Target with an ON Clause` dans la documentation SQLAlchemy pour ajouter les colonnes demandés dans cette activité. Veuillez inclure le code pour illustrer votre réponse.

### 4. Utilisez l'endpoint GraphQL

Dans l'activité 3, nous avons ajouté de nouveaux colonnes `Product` à un endpoint `ProductStock`. Si à l'avenir nous avons de nouveaux colonnes dans `Product` ou `ProductStock`, ou le besoin de conserver différents endpoints avec des colonnes distincts, il faudra que nous créions différents endpoints. Pour nous aider à mieux gérer l'hétérogénéité des endpoints, on peut créer un endpoint GraphQL.

GraphQL est un langage qui nous permet de donner la possibilité aux clients qui utilisent notre API REST de continuer à utiliser les endpoints avec les noms et méthodes fixés, mais en passant les noms des colonnes qu'ils veulent. Par exemple :

```graphql
{
  product(id: "1") {
    id
    quantity
  }
}
```

L'endpoint GraphQL est accessible via `POST /product_stocks/graphql`.

> 💡 **Question 3** : Quels résultats avez-vous obtenus en utilisant l’endpoint POST /product_stocks/graphql avec la requête suggérée ? Veuillez joindre la sortie de votre requête dans Postman afin d’illustrer votre réponse.

### 5. Ajoutez plus d'informations à l'endpoint GraphQL

La correspondance entre les colonnes GraphQL et les données est définie dans `/schemas/query.py`, au sein de la méthode `resolve_product`. Ajoutez également les colonnes `name`, `sku` et `price` afin que les clients puissent les interroger via GraphQL. Si nécessaire, adaptez la méthode `update_stock_redis` (fichier `src/commands/write_product_stock.py`) afin d’enregistrer davantage d’informations manquantes sur l’article dans Redis.

> 💡 **Question 4** : Quelles lignes avez-vous changez dans `update_stock_redis`? Veuillez joindre du code afin d’illustrer votre réponse.

> 💡 **Question 5** : Quels résultats avez-vous obtenus en utilisant l’endpoint POST /product_stocks/graphql avec les améliorations ? Veuillez joindre la sortie de votre requête dans Postman afin d’illustrer votre réponse.

### 6. Créez un autre conteneur pour effectuer un test de charge 
Pour simuler un scénario plus proche de la réalité, exécutez `scripts/supplier_app.py` dans un conteneur séparé. Si vous avez besoin de précisions supplémentaires, référez-vous au diagramme `docs/uml/deployment.puml`. Vous pouvez vous appuyer sur les `Dockerfile` et le `docker-compose.yml` déjà présents dans le répertoire `scripts`.

> 💡 **Question 6** : Examinez attentivement le fichier `docker-compose.yml` du répertoire `scripts`, ainsi que celui situé à la racine du projet. Qu’ont-ils en commun ? Par quel mécanisme ces conteneurs peuvent-ils communiquer entre eux ? Veuillez joindre du code YAML afin d’illustrer votre réponse.

## 📦 Livrables

- Un fichier .zip contenant l'intégralité du code source du projet Labo 03.
- Un rapport en .pdf répondant aux 6 questions présentées dans ce document. Il est obligatoire d'illustrer vos réponses avec du code ou des captures d'écran/terminal.